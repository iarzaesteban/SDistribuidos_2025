import os
import pika
import redis
import json
import hashlib
import time
import base64
from typing import Optional
from enum import Enum
from datetime import datetime, timedelta
from pydantic import BaseModel, validator
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
EARRING_QUEUE = os.getenv("EARRING_QUEUE", "earrings") # Cola pendietes
IN_PROGRESS_QUEUE = os.getenv("IN_PROGRESS_QUEUE", "in_progress")  # Cola En Curso  
BLOCKCHAIN_KEY = os.getenv("BLOCKCHAIN_KEY", "blockchain") 

REDIS_CLIENT = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

class WorkerRegistration(BaseModel):
    ip: str
    type: str
    port: int
    
def get_last_block_hash():
    # Obtengo todas las keys de bloques
    block_keys = REDIS_CLIENT.keys("block:*")
    if not block_keys:
        return None  # No hay bloques en la blockchain

    blocks = []
    for key in block_keys:
        raw_data = REDIS_CLIENT.get(key)
        if raw_data:
            block = json.loads(raw_data)
            block["block_hash"] = key.decode().replace("block:", "") if isinstance(key, bytes) else key.replace("block:", "")
            blocks.append(block)

    # Ordenar por block_id
    blocks.sort(key=lambda b: int(b.get("block_id", 0)))

    # Tomar el último bloque
    last_block = blocks[-1]
    return last_block.get("block_hash")


def generate_genesis_block():
    block_data = {
        "block_id": 0,
        "transaction": {
            "block_name": "GENESIS"
        }
    }
    # Obtenemos el hash del bloque para encadenar
    block_hash = hashlib.sha1(json.dumps(block_data).encode()).hexdigest()

    # Verificamos si el bloque GENESIS ya existe en Redis
    if REDIS_CLIENT.exists(f"block:{block_hash}"):
        logger.info("El bloque GENESIS ya existe en la cadena.")
        return
    
    # Agregamos bloque GENESIS
    REDIS_CLIENT.set(f"block:{block_hash}", json.dumps(block_data))
    REDIS_CLIENT.set("last_block", block_hash)
    logger.info("Se encadenó el bloque GENESIS")


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
            "source": self.source,
            "target": self.target,
            "amount": self.amount,
            "description": self.description,
            "timestamp": self.timestamp,
            "sign": self.sign
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