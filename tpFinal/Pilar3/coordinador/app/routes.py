import time
import uuid
import json
import hashlib
from datetime import datetime

from fastapi import APIRouter, HTTPException

from utils.helper import REDIS_CLIENT, Transaction
from utils.logger import logger
from utils.rabbitmq_client import get_transactions, publish_task
from utils.redis_client import get_active_workers

router = APIRouter()

@router.get("/")
def root():
    nombre = REDIS_CLIENT.get("nombre") or "desconocido"
    return {"mensaje": f"Hola {nombre}"}


def generar_hash_dummy():
    return hashlib.sha256(str(datetime.now()).encode()).hexdigest()


@router.get("/status")
def status():
    logger.info("Status checked")

    # Estado de los workers
    workers = get_active_workers()

    # Estado de Redis
    try:
        redis_status = "online" if REDIS_CLIENT.ping() else "offline"
    except Exception as e:
        redis_status = f"error: {str(e)}"

    # Timestamp actual
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    return {
        "status": "ok",
        "timestamp": now,
        "redis": redis_status,
        "workers_active": workers,
        "workers_count": len(workers)
    }

@router.post("/sendTransaction")
def send_transaction(tx: Transaction):
    REDIS_CLIENT.rpush("transaction_pool", tx.json())
    return {"message": "Transacción agregada al pool temporal"}


@router.get("/getTransactions")
def get_all_transactions():
    messages = get_transactions()
    return {"transacciones": messages}

@router.delete("/blockchain")
def eliminar_blockchain():
    """
        Elimina todos los bloques almacenados en Redis que tienen claves que comienzan con 'block:'.

        Busca las claves correspondientes a bloques en Redis (por ejemplo, 'block:1', 'block:2', etc.),
        y si existen, las elimina. Devuelve un mensaje indicando cuántos bloques fueron eliminados
        o si no había bloques para eliminar.
    """
    claves = REDIS_CLIENT.keys("block:*")
    if not claves:
        return {"message": "No hay bloques para eliminar."}
    REDIS_CLIENT.delete(*claves)
    return {"message": f"Se eliminaron {len(claves)} bloques de Redis."}


@router.get("/blockchain")
def obtener_blockchain():
    """
        Recupera y devuelve todos los bloques almacenados en Redis, ordenados por su timestamp.

        Obtiene la cantidad total de bloques desde la clave 'block_count', luego itera por cada índice
        para recuperar los bloques individuales almacenados con claves 'block:0', 'block:1', etc.
        Si se encuentran bloques, se parsean desde JSON, se agregan a una lista, y se ordenan por su
        campo 'timestamp'. Finalmente, se devuelve la cantidad total y la lista ordenada de bloques.

        Returns:
            dict: Un diccionario con dos claves:
                - "cantidad": número total de bloques recuperados.
                - "bloques": lista de bloques ordenados por timestamp.
    """
    count = int(REDIS_CLIENT.get("block_count") or 0)
    bloques = []

    for i in range(count):
        raw = REDIS_CLIENT.get(f"block:{i}")
        if raw:
            bloque = json.loads(raw)
            bloques.append(bloque)

    bloques_ordenados = sorted(bloques, key=lambda b: b["timestamp"])
    return {"cantidad": len(bloques_ordenados), "bloques": bloques_ordenados}


# Devuelve los workers activos
@router.get("/workers")
def list_workers():
    return {"active_workers": get_active_workers()}


@router.post("/mine")
def mine_block(base: str, prefix: str, total_range: int = 5000000, splits: int = 5):
    """
        Publica tareas de minado en una cola RabbitMQ dividiendo el trabajo en subtareas.

        Este endpoint recupera todas las transacciones del pool almacenado en Redis, 
        las elimina del pool y genera un conjunto de tareas de minado que se dividen 
        en rangos definidos por los parámetros `total_range` y `splits`. 
        Cada tarea se publica como un mensaje en una cola de RabbitMQ.

        Args:
            base (str): Texto base sobre el cual se minará el bloque.
            prefix (str): Prefijo que debe tener el hash resultante del bloque.
            total_range (int, optional): Rango total de números a explorar durante el minado. 
                                        Por defecto es 5,000,000.
            splits (int, optional): Número de divisiones (tareas) en que se separará el rango total. 
                                    Por defecto es 5.

        Returns:
            dict: Un diccionario con el estado de la publicación, el ID del trabajo (`job_id`) 
                y la cantidad de tareas generadas.
        
        Raises:
            HTTPException: Si no hay transacciones disponibles en el pool para incluir en el bloque.
    """
    raw_tx = REDIS_CLIENT.lrange("transaction_pool", 0, -1)
    if not raw_tx:
        raise HTTPException(status_code=400, detail="No hay transacciones en el pool")

    transactions = [json.loads(tx) for tx in raw_tx]
    REDIS_CLIENT.delete("transaction_pool")  # Limpiar el pool después de leer

    job_id = str(uuid.uuid4())
    step = total_range // splits

    for i in range(splits):
        start = i * step
        end = (i + 1) * step if i < splits - 1 else total_range

        task = {
            "job_id": job_id,
            "base": base,
            "prefix": prefix,
            "range_start": start,
            "range_end": end,
            "transactions": transactions
        }

        publish_task(task)

    return {"status": "published", "job_id": job_id, "tasks": splits}


@router.post("/mine_direct")
def mine_direct(base: str, prefix: str, total_range: int = 5000000, splits: int = 5):
    """
        Publica tareas de minado directo en la cola de RabbitMQ sin depender del pool de transacciones.

        Este endpoint genera tareas de minado dividiendo un rango numérico en partes iguales
        (según el parámetro `splits`) y publica cada tarea directamente en la cola RabbitMQ.
        A diferencia de `/mine`, utiliza transacciones ficticias y un bloque simulado, 
        permitiendo pruebas de minado sin datos reales.

        Args:
            base (str): Texto base sobre el cual se realizará el proceso de minado.
            prefix (str): Prefijo requerido que debe tener el hash resultante del bloque.
            total_range (int, optional): Rango total de números a explorar. Por defecto es 5,000,000.
            splits (int, optional): Cantidad de tareas en que se dividirá el rango. Por defecto es 5.

        Returns:
            dict: Un diccionario con el estado de la publicación, el `job_id` generado 
                y la cantidad de tareas creadas.
    """
    job_id = str(uuid.uuid4())
    step = total_range // splits

    for i in range(splits):
        start = i * step
        end = (i + 1) * step if i < splits - 1 else total_range

        task = {
            "job_id": job_id,
            "base": base,
            "prefix": prefix,
            "range_start": start,
            "range_end": end,
            "timestamp": "no_timestamp",  # para compatibilidad
            "transactions": [{"from": "mock", "to": "demo", "amount": 0}],
            "previous_hash": REDIS_CLIENT.get("last_block_hash") or "0" * 64,
            "difficulty": len(prefix)
        }

        logger.info(f"[Direct] Tarea publicada: job_id={job_id}, rango {start} a {end}")
        publish_task(task)

    return {"status": "published", "job_id": job_id, "tasks": splits}
