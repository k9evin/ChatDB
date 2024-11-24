from pymongo import MongoClient
from typing import Optional, List, Dict, Any
from bson import ObjectId
import math


class MongoManager:
    def __init__(self, connection_string: str):
        self.client = MongoClient(connection_string)

    def get_database(self, database_name: str):
        if not database_name:
            raise ValueError("Database name is required")
        return self.client[database_name]

    def get_collections(self, database_name: str) -> List[str]:
        db = self.get_database(database_name)
        return db.list_collection_names()

    def get_fields(self, collection_name: str, database_name: str) -> List[str]:
        db = self.get_database(database_name)
        sample_doc = db[collection_name].find_one()
        if not sample_doc:
            return []
        # Remove _id from fields list
        fields = list(sample_doc.keys())
        if '_id' in fields:
            fields.remove('_id')
        return fields

    def execute_query(
        self, 
        collection_name: str, 
        query: Dict[str, Any], 
        database_name: str
    ) -> List[Dict]:
        db = self.get_database(database_name)
        collection = db[collection_name]
        
        # Check if the query is an aggregation pipeline
        if isinstance(query, list):
            results = list(collection.aggregate(query))
        else:
            results = list(collection.find(query))
            
        # Clean results by removing ObjectId and handling non-JSON values
        return self._clean_mongo_results(results)

    def _clean_mongo_results(self, results: List[Dict]) -> List[Dict]:
        """Clean MongoDB results by removing ObjectId and handling non-JSON values"""
        cleaned_results = []
        for doc in results:
            doc_copy = doc.copy()
            doc_copy.pop('_id', None)
            # Handle non-JSON compliant values
            cleaned_doc = self._handle_non_json_values(doc_copy)
            cleaned_results.append(cleaned_doc)
        return cleaned_results

    def _handle_non_json_values(self, obj: Any) -> Any:
        """Recursively handle non-JSON compliant values"""
        if isinstance(obj, dict):
            return {key: self._handle_non_json_values(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._handle_non_json_values(item) for item in obj]
        elif isinstance(obj, float):
            if math.isnan(obj):
                return "NaN"
            elif math.isinf(obj):
                return "Infinity" if obj > 0 else "-Infinity"
            return obj
        elif isinstance(obj, (ObjectId, bytes)):
            return str(obj)
        return obj
