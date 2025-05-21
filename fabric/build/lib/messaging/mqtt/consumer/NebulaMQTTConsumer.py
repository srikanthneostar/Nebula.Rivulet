
from messaging.interfaces.consumer.NebulaConsumer import NebulaConsumer
from messaging.mqtt.utilities.MQTTUtilities import NebulaMQTTUtilities


class NebulaMQTTConsumer(NebulaConsumer):
    def __init__(self):
        self.utils = NebulaMQTTUtilities()

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode('utf8')
        self.callBack(None, None, None, message)

    def consumeMessage(self, topic, messageCallBack):
        self.callBack = messageCallBack
        client = self.utils.get_client()
        client.subscribe(topic)
        client.on_message = self.on_message
        client.loop_forever()
