import os
import hashlib
import requests
from pydantic import BaseModel
from typing import List, Optional

COORDINATOR_URL = os.getenv("COORDINATOR_URL", "http://nct:8989")
PREFIX = os.getenv("PREFIX", "0000")
RESOLUTION_INTERVAL = int(os.getenv("RESOLUTION_INTERVAL", 5 * 60))

class Transaction(BaseModel):
    source: str
    target: str
    amount: float
    description: str
    timestamp: str
    sign: str
    hash_previo: Optional[str] = None
    nonce: int = 0

    def to_string(self, include_nonce=True):
        parts = [
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

    def mine(self, prefix: str = PREFIX):
        self.nonce = 0
        while True:
            hash_ = self.compute_hash()
            if hash_.startswith(prefix):
                print(f"Transacción minada: {hash_} con nonce {self.nonce}")
                return hash_
            self.nonce += 1

def fetch_transactions() -> List[Transaction]:
    try:
        url = f"{COORDINATOR_URL}/monitoring-tasks"
        response = requests.get(url)
        data = response.json()
        return [Transaction(**tx) for tx in data.get("transactions", [])]
    except Exception as e:
        print(f"[ERROR] No se pudo consultar el coordinador: {e}")
        return []