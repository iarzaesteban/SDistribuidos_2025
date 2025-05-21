import pika
import time
import os
import json

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "transactions")
TASK_QUEUE = "transactions"

def connect_with_retry(retries=10, delay=5):
    for i in range(retries):
        try:
            params = pika.ConnectionParameters(
                host="rabbitmq", 
                port=5672,
                credentials=pika.PlainCredentials("admin", "admin")
            )
            return pika.BlockingConnection(params)
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection failed ({i + 1}/{retries}), retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Failed to connect to RabbitMQ after several retries")

connection = connect_with_retry()
channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_QUEUE)

def publish_transaction(message: str):
    channel.basic_publish(
        exchange='',
        routing_key=RABBITMQ_QUEUE,
        body=message
    )

def get_transactions():
    messages = []

    def callback(ch, method, properties, body):
        messages.append(body.decode())

    for method_frame, properties, body in channel.consume(RABBITMQ_QUEUE, inactivity_timeout=1):
        if method_frame is None:
            break
        messages.append(body.decode())
        channel.basic_ack(method_frame.delivery_tag)

    return messages

def publish_task(task_data):
    print(f"📤 Publicando tarea: {task_data}")
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=TASK_QUEUE)
    channel.basic_publish(
        exchange='',
        routing_key=TASK_QUEUE,
        body=json.dumps(task_data)
    )
    connection.close()