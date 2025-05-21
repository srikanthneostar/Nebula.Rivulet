import pika


class NebulaRabbitMQCommon:
    def __init__(self, servers: str, userName: str, password: str, port: str, vhost: str):
        self.servers = servers
        self.userName = userName
        self.password = password
        self.port = port
        self.vhost = vhost

    def getChannel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        credentials = pika.PlainCredentials(self.userName, self.password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.servers,
                                                                       credentials=credentials,
                                                                       port=self.port, virtual_host=self.vhost))
        self.channel = connection.channel()
        self.channel.basic_qos(prefetch_count=10,global_qos=False)
        return self.channel

    def createExchange(self, exchangeName: str,
                       exchangeType: str = "topic") -> pika.adapters.blocking_connection.BlockingChannel:
        channel = self.getChannel()
        channel.exchange_declare(exchangeName, durable=True, exchange_type='topic')
        return channel

    def createQueue(self, queueName: str, routingKey: str,
                    exchangeName: str = None) -> pika.adapters.blocking_connection.BlockingChannel:
        exchangeName = exchangeName if exchangeName != None else self.exchangeName
        channel = self.channel
        print("Creating queue:"+queueName)
        channel.queue_declare(queue=queueName,durable=True)
        print("Creating RoutingKey:"+routingKey)
        channel.queue_bind(exchange=exchangeName,
                           queue=queueName, routing_key=routingKey)
        return channel
