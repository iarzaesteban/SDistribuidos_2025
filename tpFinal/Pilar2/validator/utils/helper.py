import os
import json
import pika
import redis
import time
import hashlib
import time
import base64
from pydantic import BaseModel, validator
from enum import Enum
from typing import Optional
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)
from cryptography.exceptions import InvalidSignature

from utils.logger import logger

#Config blockchain
MAX_MINING_TRYS = int(os.getenv("MAX_MINING_TRYS", 3))
MAX_COINS = int(os.getenv("MAX_COINS", 20_000_000))

# Config Redis
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Config RabbitMQ
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASS")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
CHALLENGE = os.getenv("CHALLENGE", "000")
EARRING_QUEUE = os.getenv("EARRING_QUEUE", "earrings") # Cola pendietes
IN_PROGRESS_QUEUE = os.getenv("IN_PROGRESS_QUEUE", "in_progress")  # Cola En Curso  

REDIS_CLIENT = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

class TransactionStatus(str, Enum):
    pendiente = "pendiente"
    en_proceso = "en_proceso"
    procesada = "procesada"
    borrada = "borrada"


class Transaction(BaseModel):
    tx_id: Optional[str] = None
    status: Optional[TransactionStatus] = None
    worker_ip: Optional[str] = None
    hash_previo: Optional[str] = None
    nonce: Optional[int] = 0
    tries: Optional[int] = 0
    hash: Optional[str] = None
    challenge: Optional[str] = None

    # De acá para abajo son los atributos para el hash
    source: str  # clave pública en base64
    target: str  # clave pública en base64
    amount: float
    description: str
    timestamp: str
    sign: str  # firma source en base64


    @validator("timestamp")
    def validate_timestamp_format(cls, value):
        try:
            # Validamos formato
            datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Formato de timestamp inválido")
        return value
        
    def verify(self) -> bool:
        """
        Verifica que la firma sea válida utilizando la clave pública del source.
        """
        try:
            # Decodificamos la clave pública
            pub_key_bytes = base64.b64decode(self.source)
            public_key = Ed25519PublicKey.from_public_bytes(pub_key_bytes)

            # Verificamos rango de timestamp
            timestamp_dt = datetime.fromisoformat(self.timestamp)
            now = datetime.utcnow()
            if timestamp_dt > now + timedelta(seconds=30):
                logger.warning("Timestamp en el futuro.")
                return False
            if now - timestamp_dt > timedelta(minutes=5):
                logger.warning("Timestamp muy viejo.")
                return False

            # Armamos mensaje con el mismo orden que el cliente
            message = f"{self.source}{self.target}{self.amount}{self.description}{self.timestamp}".encode()

            # Decodificamos la firma
            signature_bytes = base64.b64decode(self.sign)

            # Verificamos la firma
            public_key.verify(signature_bytes, message)
            logger.info("Verify succefully")
            return True
        except (InvalidSignature, ValueError):
            return False

        
    def to_dict(self):
        return {
            "tx_id": self.tx_id,
            "source": self.source,
            "target": self.target,
            "amount": self.amount,
            "description": self.description,
            "timestamp": self.timestamp,
            "sign": self.sign,
        }


def validar_hash(tx: Transaction) -> bool:
    tx_data = f"{tx.tx_id}|{tx.source}|{tx.target}|{tx.amount}|{tx.description}|{tx.timestamp}|{tx.sign}|{tx.hash_previo}|{tx.nonce}"
    return hashlib.sha1(tx_data.encode()).hexdigest().startswith(str(tx.challenge))


def get_rabbit_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    return pika.BlockingConnection(params)


def connect_with_retry(retries=10, delay=5):
    for i in range(retries):
        try:
            return get_rabbit_connection()
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection failed ({i + 1}/{retries}), retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Failed to connect to RabbitMQ after several retries")


def seconds_until_next_period(genesis_config):
    """
    Calcula cuántos segundos faltan hasta el próximo inicio de período (ejemplo: XX:00, XX:01, etc.).
    """
    period = genesis_config['window_period_seconds']
    now = int(time.time())
    seconds_in_period = now % period

    wait_seconds = period - seconds_in_period
    return wait_seconds

    
def wait_for_genesis_block(timeout=None):
    """
    Espera hasta que el bloque génesis esté presente en Redis o hasta agotar el timeout.
    """
    start_time = time.time()
    while True:
        last_block_hash = REDIS_CLIENT.get("last_block")

        if last_block_hash is not None:
            block_key = f"block:{last_block_hash}"
            result = REDIS_CLIENT.get(block_key)
            if result is not None:
                logger.info(f"Bloque génesis encontrado con clave: {block_key}")
                return json.loads(result)
            else:
                logger.info(f"El hash del último bloque existe pero no se encontró el bloque: {block_key}")
        else:
            logger.info("No se encontró 'last_block' en Redis.")

        if timeout and time.time() - start_time > timeout:
            raise TimeoutError("Timeout esperando el bloque génesis en Redis.")

        time.sleep(1)