from services.searchService import SearchService
from framework.data_source import DataSource
from logs.logs import get_fabric_logger
from typing import List
from configuration.appConfigProvider import AppConfigProvider
from knowledge.config_util import ConfigUtil


class JournalEventsSource(DataSource):
    def __init__(self):
        self.appConfigProvider = AppConfigProvider()
        self.search_service = SearchService()
        self.knowledge = ConfigUtil.get_knowledge_config(self)
        self.logger = get_fabric_logger(__name__)
        config = self.appConfigProvider.get_config("MAXID")
        self.config = config
        self.maxid = config.value

    def get_data(self, query):
        entity_id = self.knowledge[0]["entity_id"]
        db_name = self.knowledge[0]["db_name"]

        # Build query to get records with _id greater than current MAXID
        # Try integer comparison first, fallback to string if needed
        try:
            maxid_int = int(self.maxid)
            mongo_query = {"_id": {"$gt": maxid_int}}
        except (TypeError, ValueError):
            mongo_query = {"_id": {"$gt": str(self.maxid)}}
        
        results = self.search_service.mongo_service.search(
            db_name, entity_id, query=mongo_query
        )
        self.logger.info(f"Mongo returned {len(results)} JournalEvents records with _id > {self.maxid}")
        
        if not results:
            self.logger.info(f"No new records found after MAXID {self.maxid}")
            return results
        
        entity_ids: List[int] = []
        for doc in results:
            _id = doc.get("_id")
            if _id is None:
                continue
            try:
                entity_ids.append(int(_id))
            except (TypeError, ValueError):
                self.logger.warning(f"Non-numeric _id encountered: {_id}")

        new_maxid = max(entity_ids, default=int(self.maxid))

        if new_maxid > int(self.maxid):
            self.logger.info(f"Updating MAXID from {self.maxid} to {new_maxid}")
            self.maxid = str(new_maxid)
            self.config.value = str(new_maxid)
            self.appConfigProvider.update_config(config=self.config)
        else:
            self.logger.info(f"No new MAXID found (MAXID remains {self.maxid})")

        return results