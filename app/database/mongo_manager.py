from pymongo import MongoClient


class MongoManager:
    def __init__(self, connection_string, db_name):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]

    def get_collections(self):
        return self.db.list_collection_names()

    def get_fields(self, collection_name):
        return self.db[collection_name].find_one().keys()

    def execute_query(self, collection_name, query):
        collection = self.db[collection_name]
        return list(collection.find(query))
