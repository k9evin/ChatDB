from typing import Optional

class DBExplorerService:
    def __init__(self, mysql_manager, mongo_manager):
        self.mysql_manager = mysql_manager
        self.mongo_manager = mongo_manager

    def get_mysql_tables(self, database_name: Optional[str] = None):
        return self.mysql_manager.get_tables(database_name)

    def get_mysql_columns(self, table_name, database_name: Optional[str] = None):
        return [col["name"] for col in self.mysql_manager.get_columns(table_name, database_name)]

    def get_mysql_sample_data(self, table_name, limit=5, database_name: Optional[str] = None):
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.mysql_manager.execute_query(query, database_name)

    def get_mongo_collections(self, database_name: Optional[str] = None):
        return self.mongo_manager.get_collections(database_name)

    def get_mongo_fields(self, collection_name, database_name: Optional[str] = None):
        return list(self.mongo_manager.get_fields(collection_name, database_name))

    def get_mongo_sample_data(self, collection_name, limit=5, database_name: Optional[str] = None):
        return self.mongo_manager.execute_query(collection_name, {}, database_name)[:limit]

    def get_all_tables_and_columns(self, db_type: str, database_name: Optional[str] = None):
        """Get all tables/collections and their columns/fields."""
        if db_type == "mysql":
            tables = self.get_mysql_tables(database_name)
            return {
                table: self.get_mysql_columns(table, database_name)
                for table in tables
            }
        else:  # mongodb
            collections = self.get_mongo_collections(database_name)
            return {
                collection: self.get_mongo_fields(collection, database_name)
                for collection in collections
            }
