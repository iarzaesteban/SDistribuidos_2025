import os
import json
import pika
import subprocess
import logging
from typing import Optional, Dict, Any

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

# RabbitMQ config
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASS")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
TASK_QUEUE = os.getenv("TASK_QUEUE", "transactions")
RESULTS_QUEUE = os.getenv("RESULTS_QUEUE", "results")
BASE = int(os.getenv("BASE", "16"))
PREFIX = os.getenv("PREFIX", "0000")


# Worker config
WORKER_ID = os.getenv("WORKER_ID", "worker-real")


def get_rabbit_connection() -> pika.BlockingConnection:
    """Establece una conexión con RabbitMQ utilizando las credenciales de entorno."""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    return pika.BlockingConnection(params)


def ejecutar_brute_range(tarea: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Ejecuta el proceso externo `brute_range` para buscar un nonce válido.

    Args:
        tarea: Diccionario con la información de la tarea de minería.

    Returns:
        Diccionario con el resultado si se encuentra un nonce válido, o None en caso de error.
    """
    try:
        
        start = str(tarea["range_start"])
        end = str(tarea["range_end"])
        # Ejecuta bash brute_range
        result = subprocess.run(
            ["./brute_range", BASE, PREFIX, start, end],
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

    except subprocess.CalledProcessError as e:
        logger.error(f"[ERROR] Fallo al ejecutar brute_range: {e.stderr}")
    except Exception as e:
        logger.exception(f"[ERROR] Excepción general durante brute_range: {e}")
    return None


def manejar_tarea(ch, method, properties, body: bytes) -> None:
    """Procesa una tarea recibida desde la cola de RabbitMQ."""
    try:
        tarea = json.loads(body.decode())
        resultado = ejecutar_brute_range(tarea)
        if resultado:
            ch.basic_publish(
                exchange='',
                routing_key=RESULTS_QUEUE,
                body=json.dumps(resultado)
            )
            logger.info(f"[OK] Resultado enviado: nonce={resultado['nonce']} hash={resultado['block_hash']}")
        else:
            logger.warning("[SKIP] Tarea no completada correctamente.")
    except Exception as e:
        logger.exception(f"[ERROR] Error procesando mensaje: {e}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


def iniciar_worker() -> None:
    """Inicializa el worker, conecta a RabbitMQ y espera tareas."""
    connection = get_rabbit_connection()
    channel = connection.channel()

    channel.queue_declare(queue=TASK_QUEUE)
    channel.queue_declare(queue=RESULTS_QUEUE)

    logger.info(f"[{WORKER_ID}] Worker en espera de tareas...")
    channel.basic_consume(queue=TASK_QUEUE, on_message_callback=manejar_tarea)
    channel.start_consuming()


if __name__ == "__main__":
    try:
        iniciar_worker()
    except KeyboardInterrupt:
        logger.info("Worker detenido manualmente.")
    except Exception as e:
        logger.exception(f"[FATAL] El worker falló al iniciar: {e}")
 