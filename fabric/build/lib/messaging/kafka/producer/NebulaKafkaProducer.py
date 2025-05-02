import json
from messaging.kafka.producer.NebulaKafkaProducer import KafkaProducer
from messaging.entities.requests.RequestPayload import RequestPayload
from messaging.interfaces.producer.NebulaProducer import NebulaProducer
from messaging.serializers.NebulaSerializer import NebulaSerializer


class NebulaKafkaProducer(NebulaProducer):
    def __init__(self, servers):
        self.servers = servers

    def serializer(self, message):
        return json.dumps(message, cls=NebulaSerializer).encode('utf-8')

    def sendMessage(self, topic: str, message: RequestPayload):
        producer = KafkaProducer(bootstrap_servers=[self.servers],
                                 value_serializer=self.serializer)
        producer.send(topic, message)
