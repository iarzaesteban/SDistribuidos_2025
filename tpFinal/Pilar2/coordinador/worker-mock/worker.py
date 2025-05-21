import pika
import json
import os
import redis
import random
import time
import hashlib

# Config
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
WORKER_ID = os.getenv("WORKER_ID", "worker-mock")

# Conexión a Redis
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# Credenciales RabbitMQ
credentials = pika.PlainCredentials(
    username=os.getenv("RABBITMQ_USER", "admin"),
    password=os.getenv("RABBITMQ_PASS", "admin")
)
parameters = pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    credentials=credentials
)

# Retry loop para RabbitMQ
max_retries = 10
for i in range(max_retries):
    try:
        connection = pika.BlockingConnection(parameters)
        break
    except pika.exceptions.AMQPConnectionError:
        print(f"[{i+1}/{max_retries}] RabbitMQ no disponible. Reintentando en 5 segundos...", flush=True)
        time.sleep(5)
else:
    raise RuntimeError("❌ No se pudo conectar a RabbitMQ luego de varios intentos.")

channel = connection.channel()
channel.queue_declare(queue='transactions')
channel.queue_declare(queue='results')

def cumple_dificultad(hash_str, prefix):
    return hash_str.startswith(prefix)

def mock_pow(tarea):
    print(f"🧪 [MOCK] Buscando nonce válido para tarea {tarea['job_id']}")
    for nonce in range(tarea["range_start"], tarea["range_end"]):
        base = tarea["base"]
        timestamp = tarea["timestamp"]
        raw = f"{base}{nonce}{timestamp}"
        hash_result = hashlib.sha256(raw.encode()).hexdigest()

        if cumple_dificultad(hash_result, tarea["prefix"]):
            print(f"✅ [MOCK] Nonce encontrado: {nonce} → {hash_result}")
            return {
                "task_id": tarea["job_id"],
                "nonce": nonce,
                "block_hash": hash_result,
                "original_task": tarea
            }

    print(f"❌ [MOCK] No se encontró nonce en rango {tarea['range_start']}–{tarea['range_end']}")
    return {
        "task_id": tarea["job_id"],
        "nonce": -1,
        "block_hash": "",
        "original_task": tarea
    }


def callback(ch, method, properties, body):
    tarea = json.loads(body)
    print("🔍 Tarea recibida:", tarea, flush=True)
    resultado = mock_pow(tarea)
    channel.basic_publish(
        exchange='',
        routing_key='results',
        body=json.dumps(resultado)
    )
    print(f"✅ [MOCK] Resultado enviado para tarea {tarea['job_id']}", flush=True)
    ch.basic_ack(delivery_tag=method.delivery_tag)

print("👷 [MOCK] Worker esperando tareas...", flush=True)
channel.basic_consume(queue='transactions', on_message_callback=callback)
channel.start_consuming()
