import json
from utils.rabbitmq_connection import RabbitMQClient
from utils.helper import EARRING_QUEUE

rabbit_client = RabbitMQClient(queue_name=EARRING_QUEUE)

def get_transactions():
    messages = []

    def callback(ch, method, properties, body):
        messages.append(body.decode())
        ch.basic_ack(method.delivery_tag)

    # Consume con timeout para evitar bloqueo infinito
    for method_frame, properties, body in rabbit_client.channel.consume(EARRING_QUEUE, inactivity_timeout=1):
        if method_frame is None:
            break
        messages.append(body.decode())
        rabbit_client.channel.basic_ack(method_frame.delivery_tag)

    return messages


def publish_task(task_data):
    print(f"Publicando tarea: {task_data}")
    rabbit_client.publish(task_data)
