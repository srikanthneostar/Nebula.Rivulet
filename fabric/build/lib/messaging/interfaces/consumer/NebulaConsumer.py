
from abc import ABC, abstractmethod


class NebulaConsumer(ABC):
    @abstractmethod
    def consumeMessage(self, topic,messageCallBack):
        pass