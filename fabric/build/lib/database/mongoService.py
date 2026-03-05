from pymongo import MongoClient
from typing import List, Union
from logs.logs import get_fabric_logger


class MongoService:
    def __init__(self, hosts: Union[str, List[str]], **kwargs):
        self.client = MongoClient(hosts, **kwargs)
        self.logger = get_fabric_logger(__name__, "mongo_service.log")

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

    def search_by_id(self, db_name, entityid, ids):
        self.logger.info(
            f"Searching in DB: {db_name} for entityid: {entityid} and ids: {ids}"
        )
        db = self.client[db_name]
        collection_name = self.entityMapper(entityid)
        self.logger.info(f"Using collection: {collection_name}")
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
