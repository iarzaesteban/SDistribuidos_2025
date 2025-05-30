
import json
from utils.helper import TASK_QUEUE, \
                        get_rabbit_connection, \
                        connect_with_retry

connection = connect_with_retry()
channel = connection.channel()
channel.queue_declare(queue=TASK_QUEUE)


def get_transactions():
    messages = []

    def callback(ch, method, properties, body):
        messages.append(body.decode())

    for method_frame, properties, body in channel.consume(TASK_QUEUE, inactivity_timeout=1):
        if method_frame is None:
            break
        messages.append(body.decode())
        channel.basic_ack(method_frame.delivery_tag)

    return messages


def publish_task(task_data):
    print(f"Publicando tarea: {task_data}")
    connection = get_rabbit_connection()
    channel = connection.channel()
    
    channel.queue_declare(queue=TASK_QUEUE)
    channel.basic_publish(
        exchange='',
        routing_key=TASK_QUEUE,
        body=json.dumps(task_data)
    )
    connection.close()