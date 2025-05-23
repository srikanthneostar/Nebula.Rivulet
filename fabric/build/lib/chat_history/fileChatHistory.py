import os
import json
from typing import List, Dict, Any
from chat_history.chat_source import ChatMessageHistory
from langchain_community.chat_message_histories.file import FileChatMessageHistory
from configuration.envConfig import EnvConfig

class FileChatHistory(ChatMessageHistory):

    def __init__(self, session_id: str, file_path=None):
        config = EnvConfig()
        rivulet_home = config.get_env_variable()
        if file_path is None:
            file_path = os.path.join(rivulet_home, "chat_history", f"{session_id}.json")
        self.file_path = file_path
        self.file_chat_history = FileChatMessageHistory(file_path=self.file_path)
        print(f"File path for chat history: {self.file_path}")

    def add_message(self, role: str, message: str):
        if role == "user":
            self.file_chat_history.add_user_message(message)
        elif role == "assistant":
            self.file_chat_history.add_ai_message(message)
        else:
            raise ValueError(f"Invalid role: {role}. Expected 'user' or 'assistant'.")

    def get_messages(self) -> List[Dict[str, Any]]:
        messages = self.file_chat_history.messages
        return [{"type": msg.type,
                "content" : msg.content} for msg in messages]

    def clear(self) -> None:
        self.file_chat_history.clear()