
from chat_history.chat_source import ChatMessageHistory
from enums.chat_enum import ChatHistoryType
from chat_history.elasticChatHistory import ElasticChatHistory
from chat_history.fileChatHistory import FileChatHistory
from chat_history.redisChatHistory import RedisChatHistory

class ChatHistoryFactory:
    @staticmethod
    def create_chat_history(history_type: ChatHistoryType, session_id: str) -> ChatMessageHistory:
        if history_type == ChatHistoryType.ELASTIC:
            return ElasticChatHistory(session_id)
        elif history_type == ChatHistoryType.FILE:
            return FileChatHistory(session_id) 
        elif history_type == ChatHistoryType.REDIS:
            return RedisChatHistory(session_id)
        else:
            raise ValueError(f"Invalid history type: {history_type}. Expected one of {list(ChatHistoryType)}")