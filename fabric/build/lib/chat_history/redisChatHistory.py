import json
from typing import List, Dict, Any
from configuration.appConfigProvider import AppConfigProvider
from chat_source import ChatMessageHistory
from langchain_community.chat_message_histories.redis import RedisChatMessageHistory

class RedisChatHistory(ChatMessageHistory):
    def __init__(self, s_id: str):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("REDIS")
        url = [config for config in configs if config.key == "redis.hosts"][0].value
        self.redis_client = RedisChatMessageHistory(session_id=s_id, url=url)

    def add_message(self, message: Dict[str, Any]) -> None:
        self.redis_client.add_message(message)

    def get_messages(self) -> List[Dict[str, Any]]:
        messages = self.redis_client.messages
        return [json.loads(message) for message in messages]

    def clear(self) -> None:
        self.redis_client.clear()