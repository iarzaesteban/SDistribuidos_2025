import asyncio
import os
import hashlib
import socket
import requests
from pydantic import BaseModel
from typing import List, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from utils.logger import logger

COORDINATOR_URL = os.getenv("COORDINATOR_URL", "http://nct:8989")
POOL_URL = os.getenv("POOL_URL", "http://pool:9998")

RESOLUTION_INTERVAL = int(os.getenv("RESOLUTION_INTERVAL", 5 * 60))
MOCK_TASK_WORKER  = os.getenv("MOCK_TASK_WORKER", False)

# Configuración por entorno
WORKER_MODE = os.getenv("WORKER_MODE", "COORDINADOR")
WORKER_TYPE = os.getenv("WORKER_TYPE", "CPU")
MAX_WORKERS = os.cpu_count()

TARGET_SUFFIX = None

def get_container_ip():
    return socket.gethostbyname(socket.gethostname())

def get_sufix_for_pub_key():
    global TARGET_SUFFIX
    ip_split = get_container_ip().split(".")
    last_numbers = ip_split[1] + ip_split[2] + ip_split[3]
    TARGET_SUFFIX = last_numbers[1:]
    if len(last_numbers) > 4:
        TARGET_SUFFIX = last_numbers[1:] 
    logger.info(f"[KEYGEN] Sufijo buscado para clave pública: {TARGET_SUFFIX}")

class Transaction(BaseModel):
    worker_ip: Optional[str] = None
    pub_key: Optional[str] = None
    hash: Optional[str] = None
    hash_previo: Optional[str] = None
    nonce: Optional[int] = 0
    challenge: Optional[str] = None
    
    tx_id: str
    source: str
    target: str
    amount: float
    description: str
    timestamp: str
    sign: str
    

    def to_string(self, include_nonce=True):
        parts = [
            self.tx_id,
            self.source,
            self.target,
            str(self.amount),
            self.description,
            self.timestamp,
            self.sign,
        ]
        if self.hash_previo:
            parts.append(self.hash_previo)
        else:
            parts.append("GENESIS")
        if include_nonce:
            parts.append(str(self.nonce))
        return "|".join(parts)

    def compute_hash(self):
        return hashlib.sha1(self.to_string().encode()).hexdigest()

    async def mine(self, prefix: str = None, mock_result: bool = False):
        self.nonce = 0

        while True:
            hash_ = self.compute_hash()
            if hash_.startswith(prefix):
                self.hash = hash_
                logger.info(f"Transacción minada: {self.hash} con nonce {self.nonce}")
                return self.hash
            self.nonce += 1
            await asyncio.sleep(0)

def fetch_transactions() -> List[Transaction]:
    try:
        url = f"{COORDINATOR_URL}/monitoring-tasks"
        response = requests.get(url)
        data = response.json()
        previos_hash = data.get("last_hash", "")
        return previos_hash, [Transaction(**tx) for tx in data.get("transactions", [])]
    except Exception as e:
        logger.error(f"[ERROR] No se pudo consultar el coordinador: {e}")
        return []
    

def generate_key_pair():
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    public_hex = public_bytes.hex()

    if public_hex.startswith(TARGET_SUFFIX):
        priv_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        pub_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return priv_pem, pub_pem, public_hex

    return None

def worker(_):
    while True:
        res = generate_key_pair()
        if res:
            return res

async def generate_worker_key():
    get_sufix_for_pub_key()
    logger.info("[KEYGEN] Buscando clave pública válida usando múltiples procesos...")
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(worker, i) for i in range(MAX_WORKERS)]
        for future in as_completed(futures):
            priv_pem, pub_pem, public_hex = future.result()
            private_key_obj = serialization.load_pem_private_key(priv_pem, password=None)
            logger.info(f"[KEYGEN] Clave encontrada: {public_hex}")
            return private_key_obj, public_hex

