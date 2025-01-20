from services.searchService import SearchService
from framework.data_source import DataSource

from typing import List, Dict, Any, Generic, TypeVar


class JournalEventsSource(DataSource):
    def __init__(self):
        self.search_service = SearchService()

    def get_data(self, query: any) -> List[Dict]:
        """
        Fetch journal events data using the provided query
        """
        results = self.search_service.elastic_service.search(
            "nebulastore", query, 1)
        return results
