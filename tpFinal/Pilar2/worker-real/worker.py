import pika
import json
import os
import redis
import subprocess
import time

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
WORKER_ID = os.getenv("WORKER_ID", "worker-real")

# RabbitMQ auth
credentials = pika.PlainCredentials(
    os.getenv("RABBITMQ_USER", "admin"),
    os.getenv("RABBITMQ_PASS", "admin")
)
params = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue='transactions')
channel.queue_declare(queue='results')

redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def ejecutar_brute_range(tarea):
    base = tarea["base"]
    prefix = tarea["prefix"]
    start = str(tarea["range_start"])
    end = str(tarea["range_end"])

    try:
        result = subprocess.run(
            ["./brute_range", base, prefix, start, end],
            capture_output=True,
            text=True,
            check=True
        )
        salida = result.stdout.splitlines()
        nonce = next(int(l.split(":")[1].strip()) for l in salida if "Nonce:" in l)
        hash_val = next(l.split(":")[1].strip() for l in salida if "Hash:" in l)

        return {
            "task_id": tarea["job_id"],
            "nonce": nonce,
            "block_hash": hash_val,
            "original_task": tarea
        }

    except Exception as e:
        print(f"[ERROR] Ejecutando brute_range: {e}")
        return None

def callback(ch, method, properties, body):
    tarea = json.loads(body.decode())
    resultado = ejecutar_brute_range(tarea)
    if resultado:
        channel.basic_publish(
            exchange='',
            routing_key='results',
            body=json.dumps(resultado)
        )
        print(f"[OK] Resultado enviado: {resultado['nonce']} {resultado['block_hash']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

print("🚀 [REAL] Worker GPU esperando tareas...")
channel.basic_consume(queue='transactions', on_message_callback=callback)
channel.start_consuming()
