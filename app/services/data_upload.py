import pandas as pd
import json
from sqlalchemy import Table, Column, Integer, String, Float, MetaData
from typing import Dict, Any


class DataUploadService:
    def __init__(self, mysql_manager, mongo_manager):
        self.mysql_manager = mysql_manager
        self.mongo_manager = mongo_manager

    def upload_to_mysql(self, file_path: str, table_name: str, database_name: str) -> Dict[str, Any]:
        if not file_path.lower().endswith('.csv'):
            raise ValueError("MySQL upload only supports CSV files")

        # Create database if it doesn't exist
        self.mysql_manager.create_database_if_not_exists(database_name)
        
        df = pd.read_csv(file_path)
        engine = self.mysql_manager.get_engine(database_name)
        metadata = MetaData()

        columns = [
            Column(name, self._get_sqlalchemy_type(dtype))
            for name, dtype in df.dtypes.items()
        ]
        table = Table(table_name, metadata, *columns)
        
        # Create table if it doesn't exist
        metadata.create_all(engine)

        with engine.connect() as conn:
            df.to_sql(table_name, conn, if_exists="replace", index=False)
        
        return {
            "message": f"Successfully uploaded data to MySQL table '{table_name}' in database '{database_name}'",
            "row_count": len(df),
            "columns": df.columns.tolist()
        }

    def upload_to_mongo(self, file_path: str, collection_name: str, database_name: str) -> Dict[str, Any]:
        if not file_path.lower().endswith('.json'):
            raise ValueError("MongoDB upload only supports JSON files")

        with open(file_path, 'r') as f:
            content = f.read()
            try:
                # Try parsing as JSON array
                records = json.loads(content)
                if not isinstance(records, list):
                    records = [records]  # Convert single object to list
            except json.JSONDecodeError:
                # Try parsing as JSONL (one JSON object per line)
                records = [json.loads(line) for line in content.splitlines() if line.strip()]

        db = self.mongo_manager.get_database(database_name)
        collection = db[collection_name]
        
        # Drop existing collection if it exists
        if collection_name in db.list_collection_names():
            collection.drop()
            
        # Insert the data
        if records:
            collection.insert_many(records)
            # Get columns from first record
            columns = list(records[0].keys())
        else:
            columns = []

        return {
            "message": f"Successfully uploaded data to MongoDB collection '{collection_name}' in database '{database_name}'",
            "row_count": len(records),
            "columns": columns
        }

    def _get_sqlalchemy_type(self, pandas_dtype):
        if pd.api.types.is_integer_dtype(pandas_dtype):
            return Integer
        elif pd.api.types.is_float_dtype(pandas_dtype):
            return Float
        else:
            return String(255)
