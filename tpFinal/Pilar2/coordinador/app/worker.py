import json
import time
import hashlib
import pika
import random
import os
import redis

# Config
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin")
TASK_QUEUE = "transactions"
RESULT_QUEUE = "results"

import redis

# Redis Config desde .env
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)


# Conexión
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
params = pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    port=RABBITMQ_PORT,
    credentials=credentials,
    heartbeat=600,  # 10 minutos
    blocked_connection_timeout=300  # opcional
)
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue=TASK_QUEUE)
channel.queue_declare(queue=RESULT_QUEUE)

def cumple_dificultad(hash_str, dificultad):
    return hash_str.startswith("0" * dificultad)

def simular_mineria_pow(tarea):
    job_id = tarea.get("job_id", "default")
    print(f"⚙️  Worker comenzando job {job_id}...")

    for _ in range(100000):
        if redis_client.get(f"solved:{job_id}") == "1":
            print(f"🛑 Trabajo {job_id} ya fue resuelto. Abortando.")
            return None

        nonce = random.randint(tarea["range_start"], tarea["range_end"])
        data = f"{tarea['previous_hash']}{tarea['transactions']}{nonce}{tarea['timestamp']}"
        hash_val = hashlib.sha256(data.encode()).hexdigest()
        if cumple_dificultad(hash_val, tarea["difficulty"]):
            redis_client.set(f"solved:{job_id}", "1")  # Marcar como resuelta
            return {
                "task_id": job_id,
                "nonce": nonce,
                "block_hash": hash_val,
                "original_task": tarea
            }

    return None

def callback(ch, method, properties, body):
    tarea = json.loads(body.decode())
    resultado = simular_mineria_pow(tarea)
    if resultado:
        channel.basic_publish(
            exchange='',
            routing_key=RESULT_QUEUE,
            body=json.dumps(resultado)
        )
        print(f"✅ Solución enviada: nonce {resultado['nonce']}, hash {resultado['block_hash']}")
    else:
        print("❌ No se encontró solución en el intento simulado.")
    ch.basic_ack(delivery_tag=method.delivery_tag)

print("👷 Worker esperando tareas de minería...")
channel.basic_consume(queue=TASK_QUEUE, on_message_callback=callback)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("👋 Worker detenido.")
