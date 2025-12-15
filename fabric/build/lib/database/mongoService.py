from pymongo import MongoClient
from typing import List, Union


class MongoService:
    def __init__(self, hosts: Union[str, List[str]], **kwargs):
        self.client = MongoClient(hosts, **kwargs)

    @staticmethod
    def entityMapper(entityid):
        ENTITY_MAP = {
            "60": "JOURNALEVENTS",
            "8": "MEETINGS",
            "12": "PERSONS",
            "15": "VISITORS",
            # Add more mappings as needed
        }
        return ENTITY_MAP.get(str(entityid), "UNKNOWN_ENTITY")

    def search_by_id(self, db_name: str, entityid, ids):
        db = self.client[db_name]
        collection_name = self.entityMapper(entityid)
        collection = db[collection_name]
        qry = {"_id": {"$in": ids}}
        col = collection.find(qry)
        results = list(col)
        for r in results:
            if "_id" in r:
                r["_id"] = str(r["_id"])
        return results

    def search(self, db_name, entity_id, query=None):
        db = self.client[db_name]
        collection_name = self.entityMapper(entity_id)
        collection = db[collection_name]
        qry = query if query is not None else {}
        col = collection.find(qry).limit(20)
        results = list(col)
        for r in results:
            if "_id" in r:
                r["_id"] = str(r["_id"])
        return results
