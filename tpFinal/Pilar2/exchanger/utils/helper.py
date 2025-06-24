import os
import pika
from redis.sentinel import Sentinel
import redis
import time
import json
from enum import Enum
from utils.logger import logger

# Config Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis-sentinel-headless.pilar3-test.svc.cluster.local")
REDIS_PORT = int(os.getenv("REDIS_PORT", 26379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_MASTER_NAME = os.getenv("REDIS_MASTER_NAME", "mymaster")
REDIS_PRODUCTION = os.getenv("REDIS_PRODUCTION", "False").lower() in ("true", "1", "yes")

# Config RabbitMQ
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASS")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
EARRING_QUEUE = os.getenv("EARRING_QUEUE", "earrings") # Cola pendietes
IN_PROGRESS_QUEUE = os.getenv("IN_PROGRESS_QUEUE", "in_progress")  # Cola En Curso  

CHALLENGE = os.getenv("CHALLENGE", "000")

if REDIS_PRODUCTION:
    sentinel = Sentinel(
        [(REDIS_HOST, REDIS_PORT)],
        socket_timeout=0.5,
        sentinel_kwargs={"password": REDIS_PASSWORD},
    )

    REDIS_CLIENT = sentinel.master_for(
        service_name=REDIS_MASTER_NAME,
        socket_timeout=0.5,
        password=REDIS_PASSWORD,
        decode_responses=True,
    )   
else:
    REDIS_CLIENT = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

class TransactionStatus(str, Enum):
    pendiente = "pendiente"
    en_proceso = "en_proceso"
    procesada = "procesada"
    borrada = "borrada"

def publish_monitoring_transaction(task_data):
    if hasattr(task_data, "to_dict"):
        task_data = task_data.to_dict()
    
    # También lo guardamos en Redis para lectura múltiple sin consumir
    tx_id = task_data.get("tx_id")
    REDIS_CLIENT.hset("monitoring_transactions", tx_id, json.dumps(task_data))


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