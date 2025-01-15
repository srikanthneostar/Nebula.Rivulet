from elasticsearch import Elasticsearch
from typing import List, Dict, Union, Optional

class ElasticService:
    def __init__(self, hosts: Union[str, List[str]], **kwargs):
        self.client = Elasticsearch(hosts, **kwargs)

    def search(self, index: str, query: Dict, size: Optional[int] = 1000) -> List[Dict]:
        response = self.client.search(
            index=index,
            body=query,
            size=size
        )
        return [hit["_source"] for hit in response["hits"]["hits"]]

    def search_with_scroll(self, index: str, query: Dict, scroll: str = "5m", size: int = 1000) -> List[Dict]:
        results = []
        response = self.client.search(
            index=index,
            body=query,
            scroll=scroll,
            size=size
        )

        scroll_id = response["_scroll_id"]
        hits = response["hits"]["hits"]

        while hits:
            results.extend([hit["_source"] for hit in hits])
            response = self.client.scroll(
                scroll_id=scroll_id,
                scroll=scroll
            )
            hits = response["hits"]["hits"]

        self.client.clear_scroll(scroll_id=scroll_id)
        return results



# # Initialize the service
# es_service = ElasticService(['http://localhost:9200'])
#
# # Example search query
# query = {
#     "query": {
#         "bool": {
#             "must": [
#                 {"match": {"field": "value"}}
#             ]
#         }
#     }
# }
#
# # Get results
# results = es_service.search("your_index", query)
#
# # For large datasets, use scroll
# large_results = es_service.search_with_scroll("your_index", query)
