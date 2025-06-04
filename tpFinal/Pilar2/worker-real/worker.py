import pika
import json
import os
import redis
import subprocess
import time

# ------------------------------ SECCIÓN AÑADIDA ------------------------------
import threading

# Redis config para heartbeat (ya tienes REDIS_HOST e incluso import Redis)
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
WORKER_ID  = os.getenv("WORKER_ID", "worker-real")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def send_heartbeat():
    """
    Cada 5 segundos escribe 'heartbeat:{WORKER_ID}' con TTL=10s en Redis.
    """
    while True:
        try:
            redis_client.setex(f"heartbeat:{WORKER_ID}", 10, "alive")
            print(f"[HEARTBEAT] {WORKER_ID} => alive")
        except Exception as e:
            print(f"[HEARTBEAT ERROR] {e}")
        time.sleep(5)

# Arrancamos el hilo daemon para heartbeat ANTES de la conexión a RabbitMQ
heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
heartbeat_thread.start()
# --------------------------- FIN SECCIÓN AÑADIDA ----------------------------

# RabbitMQ y Redis ya estaban así:
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
WORKER_ID = os.getenv("WORKER_ID", "worker-real")

# RabbitMQ auth
credentials = pika.PlainCredentials(
    os.getenv("RABBITMQ_USER", "admin"),
    os.getenv("RABBITMQ_PASS", "admin")
)
params = pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    port=int(os.getenv("RABBITMQ_PORT", 5672)),
    credentials=credentials
)

connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue="transactions")

def ejecutar_brute_range(data):
    # ... tu lógica existente de brute-force ...
    return resultado_o_None

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
