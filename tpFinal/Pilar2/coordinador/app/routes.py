from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from utils.redis_client import redis_client
from utils.logger import logger
from utils.rabbitmq_client import publish_transaction, get_transactions

router = APIRouter()

class Transaction(BaseModel):
    id: int
    amount: float
    description: str

@router.get("/")
def root():
    nombre = redis_client.get("nombre") or "desconocido"
    return {"mensaje": f"Hola {nombre}"}


@router.get("/status")
def status():
    logger.info("Status checked")
    return {"status": "ok"}


@router.post("/sendTransaction")
def send_transaction(tx: Transaction):
    publish_transaction(tx.json())
    return {"message": "Transacción enviada a RabbitMQ"}


@router.get("/getTransactions")
def get_all_transactions():
    messages = get_transactions()
    return {"transacciones": messages}