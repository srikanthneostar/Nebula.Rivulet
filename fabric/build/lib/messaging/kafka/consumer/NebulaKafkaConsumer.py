from messaging.interfaces.consumer.NebulaConsumer import NebulaConsumer
from kafka import KafkaConsumer


class NebulaKafkaConsumer(NebulaConsumer):
    def __init__(self, servers):
        self.servers = servers

    def consumeMessage(self, topic, messageCallBack):
        consumer = KafkaConsumer(
            topic, bootstrap_servers=self.servers, auto_offset_reset='earliest')
        for message in consumer:
            messageCallBack(None, None, None, message)
