import json
from typing import List, Dict, Any
from configuration.appConfigProvider import AppConfigProvider
from chat_history.chat_source import ChatMessageHistory
from langchain_community.chat_message_histories.redis import RedisChatMessageHistory

class RedisChatHistory(ChatMessageHistory):
    def __init__(self, s_id: str):
        appConfigProvider = AppConfigProvider()
        configs = appConfigProvider.get_config_by_category("REDIS")
        url = [config for config in configs if config.key == "redis.hosts"][0].value
        redis_ttl = [config for config in configs if config.key == "redis.ttl"][0].value
        self.redis_client = RedisChatMessageHistory(session_id=s_id, url=url,key_prefix="chat_history", ttl=redis_ttl)

    def add_message(self, role: str, message: str):
        if role == "user":
            self.redis_client.add_user_message(message)
        elif role == "assistant":
            self.redis_client.add_ai_message(message)
        else:
            raise ValueError(f"Invalid role: {role}.")

    def get_messages(self) -> List[Dict[str, Any]]:
        messages = self.redis_client.messages
        return [{"type": msg.type,
                "content" : msg.content} for msg in messages]

    def clear(self) -> None:
        self.redis_client.clear()