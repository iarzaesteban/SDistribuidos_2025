from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from utils.redis_client import redis_client
from utils.logger import logger
from utils.rabbitmq_client import publish_transaction, get_transactions, publish_task
from datetime import datetime
import json
import hashlib
from utils.redis_client import get_active_workers
import time
import uuid

router = APIRouter()

class Transaction(BaseModel):
    id: int
    amount: float
    description: str

@router.get("/")
def root():
    nombre = redis_client.get("nombre") or "desconocido"
    return {"mensaje": f"Hola {nombre}"}

def generar_hash_dummy():
    return hashlib.sha256(str(datetime.now()).encode()).hexdigest()

# @router.post("/mine")
# def publicar_tarea_pow():
#     tarea = {
#         "previous_hash": generar_hash_dummy(),
#         "transactions": [
#             {"from": "A", "to": "B", "amount": 10},
#             {"from": "C", "to": "D", "amount": 25}
#         ],
#         "difficulty": 4,
#         "range_start": 0,
#         "range_end": 1000000,
#         "timestamp": datetime.utcnow().isoformat()
#     }
#     publish_transaction(json.dumps(tarea))
#     return {"message": "Tarea publicada en la cola RabbitMQ", "tarea": tarea}

@router.get("/status")
def status():
    logger.info("🔍 Status checked")

    # Estado de los workers
    workers = get_active_workers()

    # Estado de Redis
    try:
        redis_status = "online" if redis_client.ping() else "offline"
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
    redis_client.rpush("transaction_pool", tx.json())  # 🔄 En vez de publicarlas directamente
    return {"message": "Transacción agregada al pool temporal"}

@router.get("/getTransactions")
def get_all_transactions():
    messages = get_transactions()
    return {"transacciones": messages}

@router.delete("/blockchain")
def eliminar_blockchain():
    claves = redis_client.keys("block:*")
    if not claves:
        return {"message": "No hay bloques para eliminar."}
    redis_client.delete(*claves)
    return {"message": f"Se eliminaron {len(claves)} bloques de Redis."}

@router.get("/blockchain")
def obtener_blockchain():
    count = int(redis_client.get("block_count") or 0)
    bloques = []

    for i in range(count):
        raw = redis_client.get(f"block:{i}")
        if raw:
            bloque = json.loads(raw)
            bloques.append(bloque)

    bloques_ordenados = sorted(bloques, key=lambda b: b["timestamp"])
    return {"cantidad": len(bloques_ordenados), "bloques": bloques_ordenados}


@router.get("/workers")
def list_workers():
    return {"active_workers": get_active_workers()}

@router.post("/mine")
def mine_block(base: str, prefix: str, total_range: int = 5000000, splits: int = 5):
    # Recuperar transacciones desde el pool
    raw_tx = redis_client.lrange("transaction_pool", 0, -1)
    if not raw_tx:
        raise HTTPException(status_code=400, detail="No hay transacciones en el pool")

    transactions = [json.loads(tx) for tx in raw_tx]
    redis_client.delete("transaction_pool")  # Limpiar el pool después de leer

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
            "previous_hash": redis_client.get("last_block_hash") or "0" * 64,
            "difficulty": len(prefix)
        }

        logger.info(f"📤 [Direct] Tarea publicada: job_id={job_id}, rango {start} a {end}")
        publish_task(task)

    return {"status": "published", "job_id": job_id, "tasks": splits}
