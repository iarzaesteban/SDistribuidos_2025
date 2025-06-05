import time
import uuid
import json
import hashlib
import random
from fastapi import APIRouter, Request, HTTPException
from typing import List, Dict

from utils.logger import logger
from utils.rabbitmq_client import publish_new_transaction, RabbitMQClient
from utils.helper import (REDIS_CLIENT, 
                          Transaction, 
                          validar_hash, 
                          MAX_MINING_TRYS, 
                          MAX_COINS,
                          EARRING_QUEUE,
                          IN_PROGRESS_QUEUE,
                          MONITORING_IN_PROGRESS_QUEUE)

rabbit_earring = RabbitMQClient(queue_name=EARRING_QUEUE)
rabbit_in_progress = RabbitMQClient(queue_name=IN_PROGRESS_QUEUE)
rabbit_monitoring = RabbitMQClient(queue_name=MONITORING_IN_PROGRESS_QUEUE)
                                   
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

    
@router.post("/publish-results")
async def publish_results(request: Request):
    data = await request.json()
    txs_by_worker: Dict[str, List[Transaction]] = {}

    for tx_data in data.get("transactions", []):
        tx = Transaction(**tx_data)
        txs_by_worker.setdefault(tx.worker_id, []).append(tx)

    if not txs_by_worker:
        raise HTTPException(status_code=400, detail="No transactions received")

    # Determinamos al ganador
    max_count = max(len(txs) for txs in txs_by_worker.values())
    candidates = [wid for wid, txs in txs_by_worker.items() if len(txs) == max_count]
    winner = random.choice(candidates)
    logger.info(f"Worker ganador: {winner} con {max_count} transacciones")

    # Procesar transacciones
    for wid, txs in txs_by_worker.items():
        for tx in txs:
            key = f"in_progress:{tx.tx_id}"
            if not validar_hash(tx):
                tries = int(REDIS_CLIENT.hincrby(key, "mining_trys", 1))
                if tries >= MAX_MINING_TRYS:
                    REDIS_CLIENT.delete(key)
                    rabbit_in_progress.delete_message_by_txid(tx.tx_id)
                    rabbit_monitoring.delete_message_by_txid(tx.tx_id)
                else:
                    rabbit_in_progress.publish(tx.dict())
                    rabbit_monitoring.publish(tx.dict())
                continue

            # Hash válido: crear nuevo bloque
            last_block = REDIS_CLIENT.get("last_block")
            block_data = {
                "previous_hash": last_block or "GENESIS",
                "transaction": tx.dict()
            }
            block_hash = hashlib.sha1(json.dumps(block_data).encode()).hexdigest()
            REDIS_CLIENT.set(f"block:{block_hash}", json.dumps(block_data))
            REDIS_CLIENT.set("last_block", block_hash)

            # Limpiar datos
            REDIS_CLIENT.delete(key)
            rabbit_in_progress.delete_message_by_txid(tx.tx_id)
            rabbit_monitoring.delete_message_by_txid(tx.tx_id)

    # Premiar al ganador
    reward_amount = round(MAX_COINS * 0.001, 4)
    reward_tx = Transaction(
        source="SYSTEM",
        target=winner,
        amount=reward_amount,
        description="Mining reward",
        timestamp=str(request.headers.get("X-Timestamp", "")),
        sign="SYSTEM",
        nonce=0,
        hash_previo=REDIS_CLIENT.get("last_block") or "GENESIS",
        worker_id="SYSTEM",
        tx_id=f"reward_{winner}"
    )
    rabbit_earring.publish(reward_tx.dict())

    logger.info(f"Recompensa de {reward_amount} enviada a {winner}")
    return {"winner": winner, "reward": reward_amount}

