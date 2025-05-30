import os
import pika
import redis
import time
from pydantic import BaseModel
# Config Redis
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Config RabbitMQ
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASS")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
TASK_QUEUE = os.getenv("TASK_QUEUE", "transactions")
RESULTS_QUEUE = os.getenv("RESULTS_QUEUE", "results")

REDIS_CLIENT = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

class Transaction(BaseModel):
    id: int
    amount: float
    description: str

def get_rabbit_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    return pika.BlockingConnection(params)


def connect_with_retry(retries=10, delay=5):
    for i in range(retries):
        try:
            return get_rabbit_connection()
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection failed ({i + 1}/{retries}), retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Failed to connect to RabbitMQ after several retries")