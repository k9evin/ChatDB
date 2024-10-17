class DBExplorerService:
    def __init__(self, mysql_manager, mongo_manager):
        self.mysql_manager = mysql_manager
        self.mongo_manager = mongo_manager

    def get_mysql_tables(self):
        return self.mysql_manager.get_tables()

    def get_mysql_columns(self, table_name):
        return [col["name"] for col in self.mysql_manager.get_columns(table_name)]

    def get_mysql_sample_data(self, table_name, limit=5):
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.mysql_manager.execute_query(query)

    def get_mongo_collections(self):
        return self.mongo_manager.get_collections()

    def get_mongo_fields(self, collection_name):
        return list(self.mongo_manager.get_fields(collection_name))

    def get_mongo_sample_data(self, collection_name, limit=5):
        return self.mongo_manager.execute_query(collection_name, {})[:limit]
