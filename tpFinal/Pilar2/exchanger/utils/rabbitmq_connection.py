import json
import pika
from utils.helper import connect_with_retry

class RabbitMQClient:
    def __init__(self, queue_name, is_consumer=False):
        self.queue_name = queue_name
        self.connection = connect_with_retry()
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        self.is_consumer = is_consumer
        if is_consumer:
            self.channel.basic_qos(prefetch_count=1)
        self._connect()

    def _connect(self):
        self.connection = connect_with_retry()
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        if self.is_consumer:
            self.channel.basic_qos(prefetch_count=1)

    def _ensure_connection(self):
        if self.connection is None or self.connection.is_closed:
            print("[WARN] Conexión cerrada, reconectando...")
            self._connect()
        elif self.channel is None or self.channel.is_closed:
            print("[WARN] Canal cerrado, reconectando...")
            self._connect()

    def publish(self, body, exchange=''):
        self._ensure_connection()
        if isinstance(body, dict):
            body = json.dumps(body)

        self.channel.basic_publish(
            exchange=exchange,
            routing_key=self.queue_name,
            body=body,
            # Para hacer persistente el mensaje
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def consume(self, callback):
        self._ensure_connection()
        if not self.is_consumer:
            raise Exception("Client is not configured as consumer")
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callback,
            auto_ack=False
        )
        print(f"[INFO] Waiting for messages on {self.queue_name}. To exit press CTRL+C")
        self.channel.start_consuming()

    def ack(self, delivery_tag):
        self._ensure_connection()
        self.channel.basic_ack(delivery_tag)

    def nack(self, delivery_tag, requeue=True):
        self._ensure_connection()
        self.channel.basic_nack(delivery_tag, requeue=requeue)

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        
            
