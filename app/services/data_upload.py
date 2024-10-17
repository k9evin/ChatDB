import pandas as pd
from sqlalchemy import Table, Column, Integer, String, Float, MetaData


class DataUploadService:
    def __init__(self, mysql_manager, mongo_manager):
        self.mysql_manager = mysql_manager
        self.mongo_manager = mongo_manager

    def upload_to_mysql(self, file_path, table_name):
        df = pd.read_csv(file_path)
        engine = self.mysql_manager.engine
        metadata = MetaData()

        columns = [
            Column(name, self._get_sqlalchemy_type(dtype))
            for name, dtype in df.dtypes.items()
        ]
        table = Table(table_name, metadata, *columns)
        metadata.create_all(engine)

        with engine.connect() as conn:
            df.to_sql(table_name, conn, if_exists="replace", index=False)

    def upload_to_mongo(self, file_path, collection_name):
        df = pd.read_csv(file_path)
        collection = self.mongo_manager.db[collection_name]
        collection.insert_many(df.to_dict("records"))

    def _get_sqlalchemy_type(self, pandas_dtype):
        if pd.api.types.is_integer_dtype(pandas_dtype):
            return Integer
        elif pd.api.types.is_float_dtype(pandas_dtype):
            return Float
        else:
            return String(255)
