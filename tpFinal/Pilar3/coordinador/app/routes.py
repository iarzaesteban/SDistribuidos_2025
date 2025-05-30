import redis
import json
import hashlib
import time
import pika
import uuid
import os
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from utils.logger import logger
from datetime import datetime

router = APIRouter()

# Config Redis
redis_host = os.getenv("REDIS_HOST")
redis_port = int(os.getenv("REDIS_PORT"))
redis_password = os.getenv("REDIS_PASSWORD")

r = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True
)

# Config RabbitMQ
rabbitmq_user = os.getenv("RABBITMQ_USER")
rabbitmq_pass = os.getenv("RABBITMQ_PASS")
rabbitmq_host = os.getenv("RABBITMQ_HOST")
rabbitmq_port = int(os.getenv("RABBITMQ_PORT"))
rabbitmq_queue = os.getenv("RABBITMQ_QUEUE")

credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
params = pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue=rabbitmq_queue)

class Transaction(BaseModel):
    id: int
    amount: float
    description: str


@router.get("/")
def root():
    return {"mensaje": f"Hola bebeee"}

def generar_hash_dummy():
    return hashlib.sha256(str(datetime.now()).encode()).hexdigest()


@router.post("/nombre")
async def guardar_nombre(nombre: str):
    r.rpush("nombres", nombre)
    return {"mensaje": "Nombre guardado en Redis con éxito"}

@router.get("/nombres")
async def obtener_nombres():
    nombres = r.lrange("nombres", 0, -1)
    return {"nombres": nombres}


@router.post("/transaccion")
def encolar_transaccion(tx: Transaction):
    tx_json = json.dumps(tx.dict())
    channel.basic_publish(exchange='', routing_key='transacciones', body=tx_json)
    return {"mensaje": "Transacción encolada", "transaccion": tx_json}


@router.get("/transacciones")
def obtener_transacciones():
    mensajes = []
    for method_frame, properties, body in channel.consume('transacciones', inactivity_timeout=1, auto_ack=False):
        if body:
            mensajes.append(json.loads(body))
            channel.basic_nack(method_frame.delivery_tag, requeue=True)
        else:
            break
    return {"transacciones": mensajes}


@router.post("/transaccion/eliminar")
def eliminar_transaccion(id: int):
    # Simulamos extracción y recreación de la cola
    nuevos = []
    while True:
        method_frame, _, body = channel.basic_get(queue='transacciones', auto_ack=False)
        if body is None:
            break
        tx = json.loads(body)
        if tx['id'] != id:
            nuevos.append(body)
        channel.basic_ack(method_frame.delivery_tag)
    # Limpiar y reinsertar
    channel.queue_delete(queue='transacciones')
    channel.queue_declare(queue='transacciones')
    for item in nuevos:
        channel.basic_publish(exchange='', routing_key='transacciones', body=item)
    return {"mensaje": f"Transacción con ID {id} eliminada si existía"}