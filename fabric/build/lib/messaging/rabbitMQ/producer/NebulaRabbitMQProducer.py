import json
from messaging.entities.requests.RequestPayload import RequestPayload
from messaging.interfaces.producer.NebulaProducer import NebulaProducer
from messaging.serializers.NebulaSerializer import NebulaSerializer
from messaging.rabbitMQ.utilities.NebulaRabbitMQCommon import NebulaRabbitMQCommon


class NebulaRabbitMQProducer(NebulaProducer):
    def __init__(self, servers: str, port: str, username: str, password: str, exchangename: str, vhost: str):
        self.exchangeName = exchangename
        self.rabbitMQCommon: NebulaRabbitMQCommon = NebulaRabbitMQCommon(
            servers=servers, userName=username, password=password, port=port, vhost=vhost)

    def serializer(self, message):
        return bytes(json.dumps(message, cls=NebulaSerializer), 'utf-8')

    def sendMessage(self, topic: str, message: RequestPayload):
        channel = self.rabbitMQCommon.createExchange(
            exchangeName=self.exchangeName)
        self.rabbitMQCommon.createQueue(queueName=topic, routingKey=topic.replace("nebula", "*") + "*",
                                        exchangeName=self.exchangeName)
        channel.basic_publish(exchange=self.exchangeName,
                                routing_key=topic.replace("nebula", "*") + "*", body=self.serializer(message))

        channel.close()
