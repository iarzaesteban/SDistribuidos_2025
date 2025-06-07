import asyncio
import time
import uuid
import json
import hashlib
import random
import aiohttp
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict

from utils.logger import logger
from utils.rabbitmq_client import publish_new_transaction, RabbitMQClient
from utils.helper import (REDIS_CLIENT, 
                          Transaction, 
                          validar_hash, 
                          MAX_MINING_TRYS, 
                          MAX_COINS,
                          EARRING_QUEUE,
                          IN_PROGRESS_QUEUE)

rabbit_earring = RabbitMQClient(queue_name=EARRING_QUEUE)
rabbit_in_progress = RabbitMQClient(queue_name=IN_PROGRESS_QUEUE)
                                   
router = APIRouter()

@router.get("/")
def root():
    return {"message": f"El coordinador esta esperando transacciones"}


@router.get("/health")
async def health():
    return {"status": "ok"}


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
        tx_dict["tries"] = 0
        publish_new_transaction(tx_dict)
        message = f"Transacción publicada correctamente. ID: {tx_id}"
    return {"message": message}


@router.get("/monitoring-tasks")
def get_monitoring_tasks():
    """
    Devuelve todas las transacciones monitoreadas sin desencolarlas.
    """
    try:
        tasks = REDIS_CLIENT.hgetall("monitoring_transactions")
        decoded_tasks = [json.loads(v) for v in tasks.values()]
        return {"transactions": decoded_tasks}
    except Exception as e:
        logger.error(f"Error al obtener transacciones de monitoreo: {str(e)}")
        return {"error": "No se pudieron obtener las transacciones"}


@router.post("/register-worker")
async def register_worker(request: Request):
    data = await request.json()
    worker_ip = data.get("worker_ip")

    if not worker_ip:
        raise HTTPException(status_code=400, detail="worker_ip es requerido")

    try:
        REDIS_CLIENT.sadd("registered_workers", worker_ip)
        logger.info(f"Worker registrado: {worker_ip}")
        return {"status": "ok", "worker_ip": worker_ip}
    except Exception as e:
        logger.error(f"Error al registrar worker: {e}")
        raise HTTPException(status_code=500, detail="No se pudo registrar el worker")
    

@router.get("/registered-workers")
async def get_registered_workers():
    try:
        workers = REDIS_CLIENT.smembers("registered_workers")
        return {"registered_workers": list(workers)}
    except Exception as e:
        logger.error(f"Error al obtener workers: {e}")
        raise HTTPException(status_code=500, detail="Error interno")
    
@router.get("/lb")
async def get_last_block():
    try:
        last_hash = REDIS_CLIENT.get("last_block")
        if last_hash:
            last_block = json.loads(REDIS_CLIENT.get(f"block:{last_hash}"))
            logger.info("Último bloque:", last_block)
        return {"Último bloque es ": last_block}
    except Exception as e:
        logger.error(f"Error al obtener el último bloque: {e}")
        raise HTTPException(status_code=500, detail="Error interno")
    

@router.get("/blockchain")
async def get_blockchain():
    try:
        block_keys = REDIS_CLIENT.keys("block:*")
        if block_keys:
            block_keys = [k for k in block_keys if k != "last_block"]
            blocks = {}
            for key in block_keys:
                raw_data = REDIS_CLIENT.get(key)
                blocks[key] = json.loads(raw_data)
            logger.info("Blockchain:", blocks)
        return {"Blockchain": blocks}
    except Exception as e:
        logger.error(f"Error al obtener el último bloque: {e}")
        raise HTTPException(status_code=500, detail="Error interno")



@router.post("/publish-results")
async def publish_results(request: Request):
    data = await request.json()
    transactions = data.get("transactions", [])
    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions received")
    
    for tx_data in transactions:
        REDIS_CLIENT.rpush("pending_transactions", json.dumps(tx_data))

    logger.info(f"Recibidas {len(transactions)} transacciones para procesar más tarde.")
    return {"status": "ok", "message": f"{len(transactions)} transacciones recibidas"}


@router.get("/workers-results")
async def get_workers_results(limit: int = 100):
    """
    Devuelve hasta `limit` transacciones pendientes almacenadas en Redis.
    """
    try:
        # Obtenemos los elementos de la lista enviadas por los workers
        raw_items = REDIS_CLIENT.lrange("pending_transactions", 0, limit - 1)

        transactions = []
        for item in raw_items:
            try:
                tx = json.loads(item)
                transactions.append(tx)
            except json.JSONDecodeError:
                logger.warning(f"Transacción inválida en Redis: {item}")
        
        return {
            "pending_transactions": transactions,
            "count": len(transactions)
        }

    except Exception as e:
        logger.exception("Error al obtener transacciones pendientes desde Redis")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

