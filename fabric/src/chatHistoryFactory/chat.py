
from chat_history.chat_source import ChatMessageHistory
from enums.chat_enum import ChatHistoryType
from chat_history.elasticChatHistory import ElasticChatHistory
from chat_history.fileChatHistory import FileChatHistory
from chat_history.redisChatHistory import RedisChatHistory

class ChatHistoryFactory:
    @staticmethod
    def create_chat_history(history_type: ChatHistoryType, session_id: str) -> ChatMessageHistory:
        match history_type:
            case ChatHistoryType.ELASTIC:
                return ElasticChatHistory(session_id)
            case ChatHistoryType.FILE:
                return FileChatHistory(session_id)
            case ChatHistoryType.REDIS:
                return RedisChatHistory(session_id)
            case _:
                return None