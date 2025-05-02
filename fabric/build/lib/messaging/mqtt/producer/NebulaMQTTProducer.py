from messaging.interfaces.producer.NebulaProducer import NebulaProducer
from messaging.mqtt.utilities.MQTTUtilities import NebulaMQTTUtilities
import json
from messaging.serializers.NebulaSerializer import NebulaSerializer
from messaging.entities.requests.RequestPayload import RequestPayload


class NebulaMQTTProducer(NebulaProducer):
    def __init__(self):
        self.utils = NebulaMQTTUtilities()

    def serializer(self, message):
        return bytes(json.dumps(message, cls=NebulaSerializer), "utf-8")

    def sendMessage(self, topic: str, message: RequestPayload):
        client = self.utils.get_client()
        client.publish(topic, self.serializer(message))
