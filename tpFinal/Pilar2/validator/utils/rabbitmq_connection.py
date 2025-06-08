import json
import pika
from utils.helper import connect_with_retry, IN_PROGRESS_QUEUE
from utils.logger import logger


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
            logger.warning("Conexión cerrada, reconectando...")
            self._connect()
        elif self.channel is None or self.channel.is_closed:
            logger.warning("Canal cerrado, reconectando...")
            self._connect()

    def publish(self, body, exchange=''):
        self._ensure_connection()

        if isinstance(body, dict):
            body = json.dumps(body)
            
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=self.queue_name,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2)
        )


    def _get_message_by_txid(self, tx_id):
        """
        Busca y devuelve (sin borrar) un mensaje con el tx_id desde in_progress.
        """
        self._ensure_connection()
        temp_queue = f"{IN_PROGRESS_QUEUE}_temp"
        self.channel.queue_declare(queue=temp_queue, durable=True)

        found_message = None
        requeued = 0

        while True:
            method_frame, header_frame, body = self.channel.basic_get(queue=IN_PROGRESS_QUEUE, auto_ack=False)
            if method_frame is None:
                break

            tx = json.loads(body)
            if tx.get("tx_id") == tx_id and found_message is None:
                found_message = {
                    "body": body,
                    "delivery_tag": method_frame.delivery_tag,
                }
                self.channel.basic_ack(method_frame.delivery_tag)
            else:
                # Reencolar en temp
                self.channel.basic_publish(
                    exchange='',
                    routing_key=temp_queue,
                    body=body,
                    properties=header_frame
                )
                self.channel.basic_ack(method_frame.delivery_tag)
                requeued += 1

        # Restauramos los mensajes no usados
        while True:
            method_frame, header_frame, body = self.channel.basic_get(queue=temp_queue, auto_ack=False)
            if method_frame is None:
                break
            self.channel.basic_publish(
                exchange='',
                routing_key=IN_PROGRESS_QUEUE,
                body=body,
                properties=header_frame
            )
            self.channel.basic_ack(method_frame.delivery_tag)

        self.channel.queue_delete(queue=temp_queue)
        return found_message

    def delete_message_by_txid(self, tx_id):
        """
        Elimina el mensaje de la cola in_progress que tenga ese tx_id.
        """
        self._ensure_connection()
        deleted = False
        temp_queue = f"{IN_PROGRESS_QUEUE}_temp"
        self.channel.queue_declare(queue=temp_queue, durable=True)

        while True:
            method_frame, header_frame, body = self.channel.basic_get(queue=IN_PROGRESS_QUEUE, auto_ack=False)
            if method_frame is None:
                break

            tx = json.loads(body)
            if tx.get("tx_id") == tx_id and not deleted:
                logger.info(f"Borrando mensaje con tx_id {tx_id}")
                self.channel.basic_ack(method_frame.delivery_tag)
                deleted = True
            else:
                self.channel.basic_publish(
                    exchange='',
                    routing_key=temp_queue,
                    body=body,
                    properties=header_frame
                )
                self.channel.basic_ack(method_frame.delivery_tag)

        # Reenviamos todos los mensajes al in_progress
        while True:
            method_frame, header_frame, body = self.channel.basic_get(queue=temp_queue, auto_ack=False)
            if method_frame is None:
                break
            self.channel.basic_publish(
                exchange='',
                routing_key=IN_PROGRESS_QUEUE,
                body=body,
                properties=header_frame
            )
            self.channel.basic_ack(method_frame.delivery_tag)

        self.channel.queue_delete(queue=temp_queue)
        return  
    


    def ack(self, delivery_tag):
        self._ensure_connection()
        self.channel.basic_ack(delivery_tag)

    def nack(self, delivery_tag, requeue=True):
        self._ensure_connection()
        self.channel.basic_nack(delivery_tag, requeue=requeue)

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        
            
