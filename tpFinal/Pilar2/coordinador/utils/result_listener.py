import json
import threading
import hashlib
from utils.redis_client import redis_client
from utils.logger import logger
import pika
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin")
RESULT_QUEUE = "results"

def cumple_dificultad(hash_str, dificultad):
    return hash_str.startswith("0" * dificultad)

def validar_y_guardar_bloque(ch, method, properties, body):
    data = json.loads(body.decode())
    tarea = data["original_task"]
    nonce = data["nonce"]
    block_hash = data["block_hash"]

    raw_data = f"{tarea['previous_hash']}{tarea['transactions']}{nonce}{tarea['timestamp']}"
    recalculado = hashlib.sha256(raw_data.encode()).hexdigest()

    if recalculado != block_hash:
        logger.warning("❌ Hash no coincide con el contenido del bloque.")
    elif not cumple_dificultad(block_hash, tarea["difficulty"]):
        logger.warning("❌ Hash no cumple con la dificultad.")
    else:
        # Guardar bloque en Redis
        block_key = f"block:{block_hash}"
        redis_client.hmset(block_key, {
            "previous_hash": tarea["previous_hash"],
            "nonce": nonce,
            "timestamp": tarea["timestamp"],
            "transactions": json.dumps(tarea["transactions"]),
            "block_hash": block_hash
        })
        logger.info(f"✅ Bloque válido guardado en Redis: {block_key}")

        # Limpieza del job_id si existe
        job_id = data.get("job_id")
        if job_id:
            redis_client.delete(f"solved:{job_id}")
            logger.info(f"🧹 Eliminada clave de control: solved:{job_id}")

    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_result_listener():
    def run():
        logger.info("🧩 Escuchando resultados en la cola 'results'...")
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=RESULT_QUEUE)

        channel.basic_consume(queue=RESULT_QUEUE, on_message_callback=validar_y_guardar_bloque)
        channel.start_consuming()

    t = threading.Thread(target=run, daemon=True)
    t.start()
