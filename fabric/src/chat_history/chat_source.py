from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ChatMessageHistory(ABC):
    @abstractmethod
    def add_message(self, message: Dict[str, Any]) -> None:
        """Add a message to the chat history."""
        pass

    @abstractmethod
    def get_messages(self) -> List[Dict[str, Any]]:
        """Retrieve all messages from the chat history."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear the chat history."""
        pass