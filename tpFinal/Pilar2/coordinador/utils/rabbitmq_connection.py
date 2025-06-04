import json
from utils.helper import connect_with_retry

class RabbitMQClient:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.connection = connect_with_retry()
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)

    def publish(self, body, exchange=''):
        if isinstance(body, dict):
            body = json.dumps(body)
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=self.queue_name,
            body=body
        )

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
