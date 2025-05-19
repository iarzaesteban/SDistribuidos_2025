from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from utils.redis_client import redis_client
from utils.logger import logger
from utils.rabbitmq_client import publish_transaction, get_transactions
from datetime import datetime
import json
import hashlib

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

@router.post("/mine")
def publicar_tarea_pow():
    tarea = {
        "previous_hash": generar_hash_dummy(),
        "transactions": [
            {"from": "A", "to": "B", "amount": 10},
            {"from": "C", "to": "D", "amount": 25}
        ],
        "difficulty": 4,
        "range_start": 0,
        "range_end": 1000000,
        "timestamp": datetime.utcnow().isoformat()
    }
    publish_transaction(json.dumps(tarea))
    return {"message": "Tarea publicada en la cola RabbitMQ", "tarea": tarea}

@router.get("/status")
def status():
    logger.info("Status checked")
    return {"status": "ok"}

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
    claves = redis_client.keys("block:*")
    bloques = []
    for clave in claves:
        datos = redis_client.hgetall(clave)
        if "transactions" in datos:
            datos["transactions"] = json.loads(datos["transactions"])
        bloques.append(datos)
    bloques_ordenados = sorted(bloques, key=lambda b: b["timestamp"])
    return {"cantidad": len(bloques_ordenados), "bloques": bloques_ordenados}
