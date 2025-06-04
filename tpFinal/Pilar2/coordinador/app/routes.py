import time
import uuid
import json
import hashlib
from datetime import datetime
from fastapi import APIRouter

from utils.helper import REDIS_CLIENT, Transaction
from utils.logger import logger
from utils.rabbitmq_client import peek_monitoring_transactions, publish_new_transaction

router = APIRouter()

@router.get("/")
def root():
    return {"message": f"El coordinador esta esperando transacciones"}


@router.get("/status")
def status():
    logger.info("Status checked")

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
        "redis": redis_status
    }

@router.post("/new-task")
def new_task(tx: Transaction):
    logger.info(f"Recived transaction {tx}")
    message = f"Error, no se pudo procesar la transacción {tx}"
    if tx.verify():
        tx_id = str(uuid.uuid4())
        tx_dict = tx.to_dict()
        tx_dict["tx_id"] = tx_id
        publish_new_transaction(tx_dict)
        message = f"Transacción publicada correctamente. ID: {tx_id}"
    return {"message": message}


@router.get("/get-transactions")
def get_transactions():
    try:
        transactions = peek_monitoring_transactions(limit=100)
        return {"transactions": transactions, "count": len(transactions)}
    except Exception as e:
        logger.error(f"Error al obtener transacciones: {e}")
        return {"error": "No se pudieron recuperar las transacciones."}
    

@router.post("/publish.-results")
def publish_results(result_data: dict):
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
    ## TODO
    ## Aca se validaran los resultados del procesamiento de los workers
    ## Se encadena el/los nuevo/s bloque/s a la blockchain redis
    tx_id = result_data.get("tx_id")

    return {"message": f"Resultado para transacción {tx_id} recibido"}
