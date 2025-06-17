import os
import redis
import json
import requests
import hashlib
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
accepting_results = True
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


def validar_hash(tx: Transaction) -> bool:
    tx_data = f"{tx.tx_id}|{tx.source}|{tx.target}|{tx.amount}|{tx.description}|{tx.timestamp}|{tx.sign}|{tx.hash_previo}|{tx.nonce}"
    return hashlib.sha1(tx_data.encode()).hexdigest().startswith(str(tx.challenge))


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
    

def handle_worker_result(result):
    global last_hash
    tx = Transaction(**result['transaction'])
    last_hash = tx.hash  # Actualizar con el hash resuelto
    logger.info(f"[POOL] Nuevo last_hash confirmado: {last_hash}")




def prepare_task_for_workers(tx: Transaction, last_hash: str, difficulty: int):
    worker_keys = [key for key in REDIS_CLIENT.keys("worker:*") if not key.endswith(":resolved_count")]

    workers = []
    for key in worker_keys:
        ip = key.replace("worker:", "")
        worker_info = REDIS_CLIENT.hgetall(key)

        workers.append({
            "ip": ip,
            "port": worker_info.get("port", "8000"),
            "type": worker_info.get("type", "CPU")
        })

    nonce_range_per_worker = TOTAL_NONCE_RANGE // len(workers)
    tasks = []

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

    return tasks


def calculate_difficulty():
    try:
        # Buscamos todos los workers registrados
        # worker_keys = REDIS_CLIENT.keys("worker:*")
        worker_keys = [key for key in REDIS_CLIENT.keys("worker:*") if not key.endswith(":resolved_count")]

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
        # worker_keys = REDIS_CLIENT.keys("worker:*")
        worker_keys = [key for key in REDIS_CLIENT.keys("worker:*") if not key.endswith(":resolved_count")]

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
            tx_key = f"tx:{tx.tx_id}"
            if not REDIS_CLIENT.exists(tx_key):
                REDIS_CLIENT.hset(tx_key, mapping={"status": "pendiente", "resolved_by": "", "transaction": tx.json()})
                logger.info(f"[POOL] Transacción {tx.tx_id} almacenada en Redis con estado 'pendiente'.")

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


def publish_results_to_coordinator():
    logger.info("[POOL] Publicando resultados al Coordinador...")
    transactions = []
    tx_keys = REDIS_CLIENT.keys("tx:*")

    for tx_key in tx_keys:
        tx_data = REDIS_CLIENT.hgetall(tx_key)
        
        transaction_json = tx_data.get("transaction", None)
        resolved_by = tx_data.get("resolved_by", None)

        if transaction_json:
            tx = Transaction.parse_raw(transaction_json)
            tx_dict = tx.dict()
            tx_dict['worker_ip'] = resolved_by
            transactions.append(tx_dict)

    if transactions:
        try:
            response = requests.post(f"{COORDINATOR_URL}/publish-results", json={"transactions": transactions})
            logger.info(f"[POOL] Resultados publicados: {response.text}")
        except Exception as e:
            logger.error(f"Error publicando resultados: {e}")
    else:
        logger.info("[POOL] No hay transacciones.")