from services.searchService import SearchService
from framework.data_source import DataSource
from logs.logs import get_fabric_logger
from typing import List, Dict
from configuration.appConfigProvider import AppConfigProvider
from knowledge.config_util import ConfigUtil

class JournalEventsSource(DataSource):
    def __init__(self):
        appConfigProvider = AppConfigProvider()
        self.search_service = SearchService()
        self.knowledge = ConfigUtil.get_knowledge_config(self)
        self.logger = get_fabric_logger(__name__)
        config = appConfigProvider.get_config("MAXID")
        self.config = config
        self.maxid = config.value

    def get_data(self, query: any) -> List[Dict]:
        """
        Fetch journal events data using the provided query
        """
        page_size = self.knowledge[0]['page_size']
        es_index = self.knowledge[0]['index']

        for clause in query.get("query", {}).get("bool", {}).get("must", []):
            if "range" in clause and "entity.ID" in clause["range"]:
                clause["range"]["entity.ID"]["gt"] = int(self.maxid)
        
        self.logger.info("Updated query: %s", query)
        results = self.search_service.elastic_service.search(es_index, query, page_size)
        self.logger.info("Results: %s", results)
        entity_ids = [hit["entity"]["ID"] for hit in results if "entity" in hit and "ID" in hit["entity"]]
        max_id = max(entity_ids, default=self.maxid)

        if max_id == self.maxid:
            self.logger.info("No new data to fetch.")
        self.logger.info("MAXID %s", max_id)
        appconfig = AppConfigProvider()
        self.config.value = str(max_id)
        appconfig.update_config(config=self.config)

        return results