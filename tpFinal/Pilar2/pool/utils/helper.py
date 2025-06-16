import os
import redis
import json
import hashlib
import socket
import requests
from pydantic import BaseModel
from typing import List, Optional
from utils.logger import logger

#Config blockchain
MAX_MINING_TRYS = int(os.getenv("MAX_MINING_TRYS", 3))
MAX_COINS = int(os.getenv("MAX_COINS", 20_000_000))

# Config Redis
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
COORDINATOR_URL = os.getenv("COORDINATOR_URL", "http://nct:8989")
TOTAL_NONCE_RANGE = int(os.getenv("TOTAL_NONCE_RANGE", 4_000_000))
BASE_DIFFICULTY = int(os.getenv("BASE_DIFFICULTY", 4))


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
    

def calculate_difficulty():
    try:
        # Buscamos todos los workers registrados
        worker_keys = REDIS_CLIENT.keys("worker:*")
        num_cpu = 0
        num_gpu = 0

        for key in worker_keys:
            worker_info = REDIS_CLIENT.hgetall(key)
            if worker_info.get("type") == "CPU":
                num_cpu += 1
            elif worker_info.get("type") == "GPU":
                num_gpu += 1

        difficulty = BASE_DIFFICULTY + int(num_cpu * 0.5) + int(num_gpu * 0.2)

        logger.info(f"[POOL] Calculada dificultad dinámica: {difficulty} (CPU: {num_cpu}, GPU: {num_gpu})")
        return difficulty

    except Exception as e:
        logger.error(f"Error calculando dificultad: {e}")
        return BASE_DIFFICULTY


def prepare_tasks_for_workers(transactions: List[Transaction], last_hash: str, difficulty: int):
    try:
        worker_keys = REDIS_CLIENT.keys("worker:*")
        workers = []

        for key in worker_keys:
            ip = key.replace("worker:", "")
            worker_info = REDIS_CLIENT.hgetall(key)

            workers.append({
                "ip": ip,
                "port": worker_info.get("port", "8000"),
                "type": worker_info.get("type", "CPU")
            })

        if not workers:
            logger.warning("[POOL] No hay workers registrados.")
            return []

        # Parámetros de Nonce
        nonce_range_per_worker = TOTAL_NONCE_RANGE // len(workers)

        tasks = []

        for tx in transactions:
            nonce_start = 0

            for worker in workers:
                nonce_end = nonce_start + nonce_range_per_worker - 1

                task = {
                    "worker_ip": worker["ip"],
                    "worker_port": worker["port"],
                    "tx_id": tx.tx_id,
                    "transaction": tx.dict(),
                    "hash_previo": last_hash,
                    "nonce_start": nonce_start,
                    "nonce_end": nonce_end,
                    "difficulty": difficulty
                }

                tasks.append(task)
                nonce_start = nonce_end + 1

        logger.info(f"[POOL] Preparadas {len(tasks)} tareas para workers.")
        return tasks

    except Exception as e:
        logger.error(f"Error preparando tareas: {e}")
        return []


def dispatch_tasks_to_workers(tasks: List[dict]):
    for task in tasks:
        try:
            worker_ip = task["worker_ip"]
            worker_port = task["worker_port"] 
            url = f"http://{worker_ip}:{worker_port}/mine-task"
            response = requests.post(url, json=task)
            logger.info(f"Tarea {task} por enviar a {worker_ip}")
            if response.status_code == 200:
                logger.info(f"[POOL] Tarea enviada exitosamente al worker {worker_ip}:{worker_port}")
            else:
                logger.warning(f"[POOL] Worker {worker_ip}:{worker_port} respondió con código {response.status_code}")

        except Exception as e:
            logger.error(f"Error enviando tarea al worker {worker_ip}: {e}")