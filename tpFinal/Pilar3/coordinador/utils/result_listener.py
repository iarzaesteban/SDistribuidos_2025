import json
import threading
import hashlib

from utils.redis_client import REDIS_CLIENT
from utils.logger import logger
from utils.helper import RESULTS_QUEUE, \
                        get_rabbit_connection


def cumple_dificultad(hash_str, dificultad):
    """
        Verificamos si el hash comienza con cierta cantidad de ceros
    """
    return hash_str.startswith("0" * dificultad)


def validar_y_guardar_bloque(ch, method, properties, body):
    data = json.loads(body.decode())
    tarea = data["original_task"]
    nonce = data["nonce"]
    block_hash = data["block_hash"]
    job_id = data.get("task_id")

    # Evita duplicados: ¿ya se resolvió este job_id?
    if job_id:
        valor_actual = REDIS_CLIENT.get(f"solved:{job_id}")
        if valor_actual and valor_actual == "1":
            logger.warning(f"Resultado ignorado: ya se resolvió job_id={job_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

    raw_data = f"{tarea['previous_hash']}{tarea['transactions']}{nonce}{tarea['timestamp']}"
    logger.info(f"LA tarea es --->: {tarea}")
    logger.info(f"LA raw_data es: {raw_data}")
    recalculado = hashlib.sha256(raw_data.encode()).hexdigest()

    if recalculado != block_hash:
        logger.warning("Hash no coincide con el contenido del bloque.")
    elif not cumple_dificultad(block_hash, tarea["difficulty"]):
        logger.warning("Hash no cumple con la dificultad.")
    else:
        # Guardar bloque
        block_count = int(REDIS_CLIENT.get("block_count") or 0)
        REDIS_CLIENT.set(f"block:{block_count}", json.dumps({
            "previous_hash": tarea["previous_hash"],
            "nonce": nonce,
            "timestamp": tarea["timestamp"],
            "transactions": tarea["transactions"],
            "block_hash": block_hash
        }))
        REDIS_CLIENT.set("block_count", block_count + 1)
        REDIS_CLIENT.set("last_block_hash", block_hash)
        logger.info(f"Bloque #{block_count} guardado correctamente (completo).")

        # Marcamos que este job fue resuelto
        if job_id:
            REDIS_CLIENT.set(f"solved:{job_id}", "1")
            logger.info(f"Marcado como resuelto: solved:{job_id}")

    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_result_listener():
    def run():
        logger.info("Escuchando resultados en la cola 'results'...")

        connection = get_rabbit_connection()
        channel = connection.channel()
        channel.queue_declare(queue=RESULTS_QUEUE)
        channel.basic_consume(queue=RESULTS_QUEUE, on_message_callback=validar_y_guardar_bloque)
        channel.start_consuming()

    t = threading.Thread(target=run, daemon=True)
    t.start()



{'job_id': 'pool_1748648084.639175', 
 'previous_hash': 'a6476ad0dcc8137d7fc29396317d2562c1e6830a04f83fc4e9f4def8aa2c82ab', 
 'transactions': [{'id': 1, 'amount': 122000.55, 'description': 'Pago de servicioss'}], 
 'difficulty': 4, 
 'range_start': 750000, 
 'range_end': 999999, 
 'timestamp': '2025-05-30T23:34:44.644011'}
