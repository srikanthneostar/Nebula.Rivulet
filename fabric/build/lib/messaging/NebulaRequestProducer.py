import datetime
import json
import uuid
from configuration.appConfigProvider import AppConfigProvider
from messaging.entities.enum.RequestStatus import RequestStatus
from messaging.entities.requests.ApplicationSystems import ApplicationSystems
from messaging.entities.requests.RequestPayload import RequestPayload
from messaging.entities.requests.SystemRequest import SystemRequest
from messaging.interfaces.producer.NebulaProducer import NebulaProducer
from messaging.kafka.producer.NebulaKafkaProducer import NebulaKafkaProducer
from messaging.mqtt.producer.NebulaMQTTProducer import NebulaMQTTProducer
from messaging.rabbitMQ.producer.NebulaRabbitMQProducer import NebulaRabbitMQProducer

# from redis.producer.NebulaRedisProducer import \
#     NebulaRedisProducer


class NebulaRequestProducer:
    def __init__(self):
        self.dataProvider = AppConfigProvider()
        self.producer: NebulaProducer = self.get_producer()

    def get_producer(self) -> NebulaProducer:
        config = self.dataProvider.get_config("COMMUNICATIONMODE")
        producer: any = None
        val = config.value.upper()
        if val == "KAFKA":
            producer = self.get_kafka_producer()
        elif val == "RABBITMQ":
            producer = self.get_rabbit_mq_producer()
        # elif val == "REDIS":
        #     producer = self.get_redis_producer()
        elif val == "MQTT":
            producer = self.get_mqtt_producer()
        return producer

    def get_mqtt_producer(self):
        return NebulaMQTTProducer()

    def get_kafka_producer(self):
        config = self.dataProvider.get_config("SERVERS")
        return NebulaKafkaProducer(config.value)

    def sendMessage(self, topic, message: RequestPayload):
        self.producer.sendMessage(topic=topic, message=message)

    def get_rabbit_mq_producer(self):
        configs = self.dataProvider.get_config_by_category("RABBITMQ")
        localhost = list(filter(lambda x: str(x.key).lower() == "host", configs))
        port = list(filter(lambda x: str(x.key).lower() == "port", configs))
        username = list(filter(lambda x: str(x.key).lower() == "username", configs))
        password = list(filter(lambda x: str(x.key).lower() == "password", configs))
        vnet = list(filter(lambda x: str(x.key).lower() == "virtualhost", configs))
        return NebulaRabbitMQProducer(
            localhost[0].value,
            port[0].value,
            username[0].value,
            password[0].value,
            "nebula.exchange",
            vnet[0].value,
        )

    # def get_redis_producer(self):
    #     config = self.dataProvider.get_key_category("REDISHOSTS", "Redis").value.split(
    #         ":"
    #     )
    #     return NebulaRedisProducer(config[0], config[1])

    def get_request_payload(self, requestType: str, requestJson: str) -> RequestPayload:
        requestPayload = RequestPayload()
        originSystem = ApplicationSystems()
        originSystem.id = 3
        system = ApplicationSystems()
        system.id = 1
        systemRequest = SystemRequest()
        systemRequest.id = 0
        systemRequest.objectid = 0
        systemRequest.entityid = -1
        systemRequest.entitytype = "TOPICTABLE"
        systemRequest.messageid = str(uuid.uuid4())
        systemRequest.isprocessed = False
        systemRequest.originalrequest = True
        systemRequest.forcebroadcast = True
        systemRequest.originsystem = originSystem
        systemRequest.system = system
        systemRequest.requeststatus = "Pending"
        systemRequest.requesttype = requestType
        systemRequest.requestjson = requestJson
        systemRequest.createondate = datetime.datetime.now()
        systemRequest.modifyondate = datetime.datetime.now()
        requestPayload.systemRequests = systemRequest

        return requestPayload
