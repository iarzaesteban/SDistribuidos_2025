import os
import hashlib
import socket
import requests
from pydantic import BaseModel
from typing import List, Optional
from utils.logger import logger

COORDINATOR_URL = os.getenv("COORDINATOR_URL", "http://nct:8989")
RESOLUTION_INTERVAL = int(os.getenv("RESOLUTION_INTERVAL", 5 * 60))
MOCK_TASK_WORKER  = os.getenv("MOCK_TASK_WORKER", False)

def get_container_ip():
    return socket.gethostbyname(socket.gethostname())

class Transaction(BaseModel):
    worker_ip: Optional[str] = None
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

    def mine(self, prefix: str = None, mock_result: bool = False):
        self.nonce = 0
        if mock_result and self.description != "pepe":
            self.hash = None
            self.nonce = -1
            return self.hash
        else:
            while True:
                hash_ = self.compute_hash()
                if hash_.startswith(prefix):
                    self.hash = hash_
                    logger.info(f"Transacción minada: {self.hash} con nonce {self.nonce}")
                    return self.hash
                self.nonce += 1

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