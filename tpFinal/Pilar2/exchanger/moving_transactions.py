import json
import os
import time
import signal
import threading
from utils.logger import logger
from utils.rabbitmq_connection import RabbitMQClient
from utils.helper import (
    EARRING_QUEUE,
    IN_PROGRESS_QUEUE,
    MONITORING_IN_PROGRESS_QUEUE,
    publish_monitoring_transaction,
    REDIS_CLIENT,
)

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 30))
BLOCKCHAIN_KEY = os.getenv("BLOCKCHAIN_KEY", "blockchain") 

# Flag para terminar de forma limpia
shutdown_event = threading.Event()



def get_last_block_hash():
    try:
        last_block_json = REDIS_CLIENT.lindex(BLOCKCHAIN_KEY, -1)
        if not last_block_json:
            return "GENESIS"
        last_block = json.loads(last_block_json)
        return last_block.get("hash_actual", "GENESIS")
    except Exception as e:
        logger.error(f"No se pudo obtener el último bloque de la blockchain: {e}")
        return "GENESIS"


def move_transactions():
    rabbit_earring = RabbitMQClient(queue_name=EARRING_QUEUE)
    rabbit_in_progress = RabbitMQClient(queue_name=IN_PROGRESS_QUEUE)
    rabbit_monitoring = RabbitMQClient(queue_name=MONITORING_IN_PROGRESS_QUEUE)

    logger.info("Conexiones a RabbitMQ establecidas")

    while not shutdown_event.is_set():
        try:
            logger.info("Inicio de ciclo de escaneo de mensajes")
            moved = 0
            last_hash = get_last_block_hash()

            while not shutdown_event.is_set():
                method_frame, _, body = rabbit_earring.channel.basic_get(
                    queue=rabbit_earring.queue_name, auto_ack=False
                )
                if not method_frame:
                    break

                try:
                    tx = json.loads(body)
                    tx["hash_previo"] = last_hash
                    rabbit_in_progress.publish(tx)
                    rabbit_monitoring.publish(tx)
                    #Metemos las TXs en redis tambíen
                    publish_monitoring_transaction(tx)
                    # La quitamos de la cola de pendientes
                    rabbit_earring.ack(method_frame.delivery_tag)
                    moved += 1
                except Exception as e:
                    logger.error(f"No se pudo mover transacción: {e}")
                    rabbit_earring.nack(method_frame.delivery_tag, requeue=True)

            if moved:
                logger.info(f"Movidas {moved} transacciones a in_progress.")
            else:
                logger.info("No había transacciones para mover.")

            shutdown_event.wait(POLL_INTERVAL)

        except Exception as ex:
            logger.critical(f"Fallo inesperado: {ex}. Reintentando en 10s...")
            shutdown_event.wait(10)
            # Reconectar
            rabbit_earring = RabbitMQClient(queue_name=EARRING_QUEUE)
            rabbit_in_progress = RabbitMQClient(queue_name=IN_PROGRESS_QUEUE)
            rabbit_monitoring = RabbitMQClient(queue_name=MONITORING_IN_PROGRESS_QUEUE)


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
