import json
import os
import time
import signal
import threading
from utils.logger import logger
from utils.rabbitmq_connection import RabbitMQClient
from utils.helper import (
    TransactionStatus,
    publish_monitoring_transaction,
    EARRING_QUEUE,
    IN_PROGRESS_QUEUE,
    REDIS_CLIENT,
    CHALLENGE
)

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 30))

# Flag para terminar de forma limpia
shutdown_event = threading.Event()

def wait_for_genesis_block(timeout=None):
    """
    Espera hasta que el bloque génesis esté presente en Redis o hasta agotar el timeout.
    """
    start_time = time.time()
    while True:
        last_block_hash = REDIS_CLIENT.get("last_block")

        if last_block_hash is not None:
            # No necesitamos decode, ya es str
            block_key = f"block:{last_block_hash}"
            result = REDIS_CLIENT.get(block_key)
            if result is not None:
                logger.info(f"Bloque génesis encontrado con clave: {block_key}")
                return json.loads(result)
            else:
                logger.info(f"El hash del último bloque existe pero no se encontró el bloque: {block_key}")
        else:
            logger.info("No se encontró 'last_block' en Redis.")

        if timeout and time.time() - start_time > timeout:
            raise TimeoutError("Timeout esperando el bloque génesis en Redis.")

        time.sleep(1)
        

def seconds_until_post_monitoring(genesis_config):
    """
    Calcula cuántos segundos faltan hasta el instante justo después de la ventana de monitoreo.
    """
    period = genesis_config['window_period_seconds']
    monitoring_end = genesis_config['monitoring_window_end']

    now = int(time.time())
    seconds_in_period = now % period

    target = monitoring_end + 1

    if seconds_in_period < target:
        wait_seconds = target - seconds_in_period
    else:
        wait_seconds = period - seconds_in_period + target

    return wait_seconds

def move_transactions():
    rabbit_earring = RabbitMQClient(queue_name=EARRING_QUEUE)
    rabbit_in_progress = RabbitMQClient(queue_name=IN_PROGRESS_QUEUE)

    logger.info("Conexiones a RabbitMQ establecidas")

    # Esperar bloque génesis
    genesis_block = wait_for_genesis_block(timeout=None)
    genesis_config = genesis_block.get("config", {})

    while not shutdown_event.is_set():
        try:
            # Calcular tiempo hasta post-monitoring window
            wait_time = seconds_until_post_monitoring(genesis_config)
            logger.info(f"Esperando {wait_time} segundos hasta post-monitoring window...")
            shutdown_event.wait(wait_time)

            logger.info("Post-monitoring window alcanzada. Moviendo transacciones...")

            moved = 0

            # Procesar transacciones pendientes en EARRING_QUEUE
            while True:
                method_frame, _, body = rabbit_earring.channel.basic_get(
                    queue=rabbit_earring.queue_name, auto_ack=False
                )
                if not method_frame:
                    break  # No hay más mensajes en la cola

                try:
                    tx = json.loads(body)
                    tx["status"] = TransactionStatus.en_proceso.value
                    tx["challenge"] = CHALLENGE

                    # Publicar en IN_PROGRESS_QUEUE
                    rabbit_in_progress.publish(tx)

                    # Publicar en Redis para monitoreo
                    publish_monitoring_transaction(tx)

                    # Confirmar procesamiento
                    rabbit_earring.ack(method_frame.delivery_tag)
                    moved += 1
                except Exception as e:
                    logger.error(f"No se pudo mover transacción: {e}")
                    rabbit_earring.nack(method_frame.delivery_tag, requeue=True)

            if moved:
                logger.info(f"Movidas {moved} transacciones a in_progress.")
            else:
                logger.info("No había transacciones para mover.")

        except Exception as ex:
            logger.critical(f"Fallo inesperado: {ex}. Reintentando en 10s...")
            shutdown_event.wait(10)

            # Reconectar RabbitMQ
            rabbit_earring = RabbitMQClient(queue_name=EARRING_QUEUE)
            rabbit_in_progress = RabbitMQClient(queue_name=IN_PROGRESS_QUEUE)

def handle_shutdown(signum, frame):
    logger.warning(f"Señal {signum} recibida. Cerrando servicio...")
    shutdown_event.set()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    worker_thread = threading.Thread(target=move_transactions)
    worker_thread.start()

    # Espera pasiva hasta que llegue una señal de salida
    while not shutdown_event.is_set():
        time.sleep(1)

    logger.info("Proceso finalizado correctamente.")
