from configuration.appConfigProvider import AppConfigProvider
from messaging.interfaces.consumer.NebulaConsumer import NebulaConsumer
from messaging.kafka.consumer.NebulaKafkaConsumer import \
    NebulaKafkaConsumer
from messaging.mqtt.consumer.NebulaMQTTConsumer import \
    NebulaMQTTConsumer
from messaging.rabbitMQ.consumer.NebulaRabbitMQConsumer import \
    NebulaRabbitMQConsumer
# from redis.consumer.NebulaRedisConsumer import \
#     NebulaRedisConsumer


class NebulaRequestConsumer:
    def __init__(self):
        self.dataProvider = AppConfigProvider()
        self.consumer: NebulaConsumer = self.get_consumer()

    def get_consumer(self) -> NebulaConsumer:
        config = self.dataProvider.get_config("COMMUNICATIONMODE")
        consumer: any = None
        val = config.value.upper()
        if val == "KAFKA":
            consumer = self.get_kafka_consumer()
        elif val == "RABBITMQ":
            consumer = self.get_rabbit_mq_consumer()
        # elif val == "REDIS":
        #     consumer = self.get_redis_consumer()
        elif val == "MQTT":
            consumer = self.get_MQTT_consumer()
        return consumer

    def get_MQTT_consumer(self):
        return NebulaMQTTConsumer()

    def get_kafka_consumer(self):
        config = self.dataProvider.get_config("SERVERS")
        return NebulaKafkaConsumer(config.value)

    def get_rabbit_mq_consumer(self):
        configs = self.dataProvider.get_config_by_category("RABBITMQ")
        localhost = list(filter(lambda x: str(x.key).lower() == "host", configs))
        port = list(filter(lambda x: str(x.key).lower() == "port", configs))
        username = list(filter(lambda x: str(x.key).lower() == "username", configs))
        password = list(filter(lambda x: str(x.key).lower() == "password", configs))
        vnet = list(filter(lambda x: x.key == "VirtualHost", configs))
        return NebulaRabbitMQConsumer(localhost[0].value, port[0].value, username[0].value, password[0].value,
                                      "nebula.exchange", vnet[0].value)

    # def get_redis_consumer(self):
    #     config = self.dataProvider.get_key_category("REDISHOSTS", "Redis").value.split(":")
    #     return NebulaRedisConsumer(config[0], config[1])
