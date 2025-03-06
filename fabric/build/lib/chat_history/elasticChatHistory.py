from typing import List, Dict, Any
from chat_history.chat_source import ChatMessageHistory
from configuration.appConfigProvider import AppConfigProvider
from langchain_community.chat_message_histories.elasticsearch import ElasticsearchChatMessageHistory

class ElasticChatHistory(ChatMessageHistory):
    def __init__(self, index: str, s_id: str):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("ELASTIC")
        url = [config for config in configs if config.key == "elastic.hosts"][0].value
        self.es_client = ElasticsearchChatMessageHistory(es_url=url, index="chat_history",session_id=s_id)

    def add_message(self, message: Dict[str, Any]) -> None:
        self.es_client.add_message(message)

    def get_messages(self) -> List[Dict[str, Any]]:
        response = self.es_client.messages
        return [hit['_source'] for hit in response['hits']['hits']]

    def clear(self) -> None:
        self.es_client.clear()