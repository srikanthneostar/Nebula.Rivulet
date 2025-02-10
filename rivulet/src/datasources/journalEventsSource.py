from services.searchService import SearchService
from framework.data_source import DataSource
from logs.logs import get_fabric_logger
from typing import List, Dict, Any, Generic, TypeVar


class JournalEventsSource(DataSource):
    def __init__(self):
        self.search_service = SearchService()
        self.logger = get_fabric_logger(__name__)
        

    def get_data(self, query: any, page_size = 10) -> List[Dict]:
        """
        Fetch journal events data using the provided query
        """
        results = self.search_service.elastic_service.search(
            "nebulastore", query, page_size)
        self.logger.info("result print %s", query)
        self.logger.info("results")
        self.logger.info(results)
        return results
