import json
import hashlib
import time
import uuid
import pika
import os
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from utils.logger import logger
from utils.helper import get_rabbit_connection, get_redis_connection
from datetime import datetime

router = APIRouter()
rabbitmq_queue = os.getenv("RABBITMQ_QUEUE", "transacciones")

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
    redis_conn = get_redis_connection()
    redis_conn.rpush("nombres", nombre)
    return {"mensaje": "Nombre guardado en Redis con éxito"}

@router.get("/nombres")
async def obtener_nombres():
    redis_conn = get_redis_connection()
    nombres = redis_conn.lrange("nombres", 0, -1)
    return {"nombres": nombres}


@router.post("/transaccion")
def encolar_transaccion(tx: Transaction):
    try:
        connection = get_rabbit_connection()
        channel = connection.channel()

        channel.queue_declare(queue=rabbitmq_queue, durable=True)

        tx_json = json.dumps(tx.dict())
        channel.basic_publish(
            exchange='',
            routing_key=rabbitmq_queue,
            body=tx_json,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        channel.close()
        connection.close()

        return {"mensaje": "Transacción encolada", "transaccion": tx_json}
    except Exception as e:
        logger.error(f"Error encolar transacción: {e}")
        raise HTTPException(status_code=500, detail=f"Error al encolar transacción")


@router.get("/transacciones")
def obtener_transacciones():
    mensajes = []
    try:
        connection = get_rabbit_connection()
        channel = connection.channel()
        channel.queue_declare(queue=rabbitmq_queue, durable=True)

        while True:
            method_frame, _, body = channel.basic_get(queue=rabbitmq_queue, auto_ack=False)
            if method_frame is None:
                break
            mensajes.append(json.loads(body))
            # Requeue el mensaje (no lo consumimos realmente)
            channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)

        channel.close()
        connection.close()

        return {"transacciones": mensajes}
    except Exception as e:
        logger.error(f"Error al obtener transacciones: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener transacciones")


@router.post("/transaccion/eliminar")
def eliminar_transaccion(id: int):
    nuevos = []
    try:
        connection = get_rabbit_connection()
        channel = connection.channel()
        channel.queue_declare(queue=rabbitmq_queue, durable=True)

        while True:
            method_frame, _, body = channel.basic_get(queue=rabbitmq_queue, auto_ack=False)
            if body is None:
                break
            tx = json.loads(body)
            if tx["id"] != id:
                nuevos.append(body)
            channel.basic_ack(method_frame.delivery_tag)

        # Limpiar la cola
        channel.queue_delete(queue=rabbitmq_queue)
        channel.queue_declare(queue=rabbitmq_queue, durable=True)

        for item in nuevos:
            channel.basic_publish(
                exchange='',
                routing_key=rabbitmq_queue,
                body=item,
                properties=pika.BasicProperties(delivery_mode=2)
            )

        channel.close()
        connection.close()

        return {"mensaje": f"Transacción con ID {id} eliminada si existía"}
    except Exception as e:
        logger.error(f"Error al eliminar transacción: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar transacción")