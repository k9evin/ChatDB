import pandas as pd
import json
from sqlalchemy import Table, Column, Integer, String, Float, MetaData
from typing import Dict, Any, List, Type
from sqlalchemy.types import TypeEngine
import logging

logger = logging.getLogger(__name__)

class DataUploadService:
    TYPE_MAPPING = {
        'int64': Integer,
        'float64': Float,
        'object': String(255)
    }

    def __init__(self, mysql_manager, mongo_manager):
        self.mysql_manager = mysql_manager
        self.mongo_manager = mongo_manager

    def upload_to_mysql(self, file_path: str, table_name: str, database_name: str) -> Dict[str, Any]:
        try:
            if not file_path.lower().endswith('.csv'):
                raise ValueError("MySQL upload only supports CSV files")

            df = pd.read_csv(file_path)
            self.mysql_manager.create_database_if_not_exists(database_name)
            engine = self.mysql_manager.get_engine(database_name)

            metadata = MetaData()
            columns = [Column(name, self._get_sqlalchemy_type(dtype)) 
                      for name, dtype in df.dtypes.items()]
            
            table = Table(table_name, metadata, *columns)
            metadata.create_all(engine)

            with engine.connect() as conn:
                df.to_sql(table_name, conn, if_exists="replace", index=False)

            return {
                "message": f"Successfully uploaded data to {table_name} in database '{database_name}'",
                "row_count": df.shape[0],
                "columns": df.columns.tolist()
            }

        except pd.errors.ParserError as e:
            logger.error(f"Error parsing CSV file: {str(e)}")
            raise ValueError(f"Error parsing CSV file: {str(e)}")
        except Exception as e:
            logger.error(f"Error uploading to MySQL: {str(e)}")
            raise

    def upload_to_mongo(self, file_path: str, collection_name: str, database_name: str) -> Dict[str, Any]:
        if not file_path.lower().endswith('.json'):
            raise ValueError("MongoDB upload only supports JSON files")

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                records = data if isinstance(data, list) else [data]

            if not records:
                return {
                    "message": f"No data to upload to {collection_name}",
                    "row_count": 0,
                    "columns": []
                }

            db = self.mongo_manager.get_database(database_name)
            collection = db[collection_name]
            collection.drop()
            collection.insert_many(records)

            return {
                "message": f"Successfully uploaded data to {collection_name} in database '{database_name}'",
                "row_count": len(records),
                "columns": list(records[0].keys())
            }

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON file: {str(e)}")
            raise ValueError(f"Invalid JSON file: {str(e)}")
        except Exception as e:
            logger.error(f"Error uploading to MongoDB: {str(e)}")
            raise

    def _get_sqlalchemy_type(self, pandas_dtype) -> Type[TypeEngine]:
        return self.TYPE_MAPPING.get(str(pandas_dtype), String(255))

