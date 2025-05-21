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
    job_id = data.get("task_id")

    # Evita duplicados: ¿ya se resolvió este job_id?
    if job_id and redis_client.exists(f"solved:{job_id}"):
        logger.warning(f"⚠️ Resultado ignorado: ya se resolvió job_id={job_id}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    raw_data = f"{tarea['previous_hash']}{tarea['transactions']}{nonce}{tarea['timestamp']}"
    recalculado = hashlib.sha256(raw_data.encode()).hexdigest()

    if recalculado != block_hash:
        logger.warning("❌ Hash no coincide con el contenido del bloque.")
    elif not cumple_dificultad(block_hash, tarea["difficulty"]):
        logger.warning("❌ Hash no cumple con la dificultad.")
    else:
        # ✅ Guardar bloque
        block_count = int(redis_client.get("block_count") or 0)
        redis_client.set(f"block:{block_count}", json.dumps({
            "previous_hash": tarea["previous_hash"],
            "nonce": nonce,
            "timestamp": tarea["timestamp"],
            "transactions": tarea["transactions"],
            "block_hash": block_hash
        }))
        redis_client.set("block_count", block_count + 1)
        redis_client.set("last_block_hash", block_hash)
        logger.info(f"✅ Bloque #{block_count} guardado correctamente (completo).")

        # Marcamos que este job fue resuelto
        if job_id:
            redis_client.set(f"solved:{job_id}", "1")
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
