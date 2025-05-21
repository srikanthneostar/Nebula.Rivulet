from abc import ABC, abstractmethod
from messaging.entities.requests.RequestPayload import RequestPayload


class NebulaProducer(ABC):
    @abstractmethod
    def sendMessage(self, topic: str, message: RequestPayload):
        pass

    @abstractmethod
    def serializer(self, message):
        pass
