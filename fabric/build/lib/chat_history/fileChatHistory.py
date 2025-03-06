import os
import json
from typing import List, Dict, Any
from chat_history.chat_source import ChatMessageHistory
from langchain_community.chat_message_histories.file import FileChatMessageHistory

class FileChatHistory(ChatMessageHistory):
    def __init__(self):
        nebula_home = os.getenv("NEBULA_HOME")
        path = os.path.join(nebula_home, "chat_history")
        self.file_path = FileChatMessageHistory(path, encoding='utf-8')

    def add_message(self, message: Dict[str, Any]) -> None:
        self.file_path.add_message(message)

    def get_messages(self) -> List[Dict[str, Any]]:
        messages = self.file_path.messages
        messages = []
        with open(self.file_path, 'r') as file:
            for line in file:
                messages.append(json.loads(line.strip()))
        return messages

    def clear(self) -> None:
        self.file_path.clear()