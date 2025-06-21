import json
import asyncio
import aiohttp
import time
import subprocess
import uvicorn
from fastapi import FastAPI, Request

from utils.logger import logger
from utils.helper import (
    generate_worker_key,
    get_container_ip,
    fetch_transactions,
    Transaction,
    COORDINATOR_URL,
    WORKER_MODE,
    WORKER_TYPE,
    POOL_URL
)

app = FastAPI()

GENESIS_BLOCK = None
WORKER_PRIVATE_KEY = None
WORKER_PUBLIC_KEY_HEX = None
mining_task = None
CURRENT_TX_ID = None
STOP_MINING = False
TOTAL_REWARD = 0.0
WORKER_IP = get_container_ip()
REGISTER_URL = f"{COORDINATOR_URL}/register-worker" if WORKER_MODE == "COORDINADOR" else f"{POOL_URL}/register-worker"
PUBLISH_URL = f"{COORDINATOR_URL}/publish-results" if WORKER_MODE == "COORDINADOR" else None
GENESIS_BLOCK_URL = f"{COORDINATOR_URL}/genesis-block" if WORKER_MODE == "COORDINADOR" else f"{POOL_URL}/genesis-block"

def get_current_window(config):
    now = int(time.time())
    sec = now % config['window_period_seconds']
    if config['monitoring_window_start'] <= sec <= config['monitoring_window_end']:
        return 'monitoring'
    elif config['publish_window_start'] <= sec <= config['publish_window_end']:
        return 'publishing'
    return 'waiting'

def mine_cuda(prev_hash, tx: Transaction, start, end):
    blockdata = f"{prev_hash}{tx.source}{tx.target}{tx.amount}{tx.description}{tx.timestamp}"
    cmd = ["./brute_range", blockdata, tx.challenge, str(start), str(end)]
    logger.info(f"[CUDA] Ejecutando: {' '.join(cmd)}")

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        logger.error(f"[CUDA] Error: {proc.stderr}")
        return None, None

    nonce, new_hash = None, None
    for line in proc.stdout.splitlines():
        if line.startswith("Nonce:"):
            nonce = int(line.split(":", 1)[1].strip())
        elif line.startswith("Hash:"):
            new_hash = line.split(":", 1)[1].strip()
    return nonce, new_hash

async def mine_transactions(transactions: list[Transaction], starting_previous_hash: str) -> list[Transaction]:
    logger.info(f"[MINING] Iniciando minería de {len(transactions)} transacciones...")
    global WORKER_PUBLIC_KEY_HEX
    mined = []
    previous_hash = starting_previous_hash

    for tx in transactions:
        try:
            tx.worker_ip = WORKER_IP
            tx.pub_key = WORKER_PUBLIC_KEY_HEX
            tx.hash_previo = previous_hash
            nonce, hash_result = mine_cuda(previous_hash, tx, 0, 500000)
            if nonce is not None:
                tx.nonce = nonce
                tx.hash = hash_result
                previous_hash = hash_result
                mined.append(tx)
        except asyncio.CancelledError:
            logger.warning("[MINING] Minería cancelada!")
            break
    return mined

async def publish_results(transactions: list[Transaction]):
    payload = {"transactions": [tx.dict() for tx in transactions]}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(PUBLISH_URL, json=payload) as resp:
                data = await resp.json()
                logger.info(f"[PUBLISH] {data}")
        except Exception as e:
            logger.error(f"[ERROR] No se pudo publicar resultados: {e}")

async def mining_cycle():
    global GENESIS_BLOCK
    config = GENESIS_BLOCK['config']
    fetched_previous_hash = None
    transactions = []
    last_window = None

    while True:
        current_window = get_current_window(config)
        if current_window != last_window:
            logger.info(f"[WORKER] Cambio de ventana detectado: {last_window} -> {current_window}")

            if current_window == 'monitoring':
                logger.info("[WORKER] Ventana MONITORING activa: obteniendo transacciones.")
                fetched_previous_hash, transactions = fetch_transactions()
                if not transactions:
                    logger.warning("[WORKER] No se encontraron transacciones.")
                else:
                    logger.info(f"[WORKER] {len(transactions)} transacciones obtenidas.")

            elif current_window == 'publishing':
                logger.info("[WORKER] Ventana PUBLISHING activa: minando y publicando resultados.")
                if fetched_previous_hash is None:
                    logger.error("[WORKER] No hay previous_hash para minar.")
                elif transactions:
                    mined_txs = await mine_transactions(transactions, fetched_previous_hash)
                    if mined_txs:
                        await publish_results(mined_txs)
                    transactions = []

            last_window = current_window

        await asyncio.sleep(0.5)

@app.post("/reward")
async def receive_reward(request: Request):
    global TOTAL_REWARD
    data = await request.json()
    amount = data.get("amount", 0.0)
    TOTAL_REWARD += amount
    return {"status": "ok", "message": f"Recompensa de {amount} recibida", "total_reward": TOTAL_REWARD}

@app.get("/reward")
def get_total_reward():
    return {"total_reward": TOTAL_REWARD}

@app.get("/health")
def health():
    return {"status": "ok"}

async def wait_for_service(url):
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("status") == "ok":
                            return
            except:
                pass
            await asyncio.sleep(5)

async def fetch_genesis_block():
    global GENESIS_BLOCK
    async with aiohttp.ClientSession() as session:
        async with session.get(GENESIS_BLOCK_URL) as resp:
            GENESIS_BLOCK = await resp.json()

async def register():
    global WORKER_PRIVATE_KEY, WORKER_PUBLIC_KEY_HEX
    WORKER_PRIVATE_KEY, WORKER_PUBLIC_KEY_HEX = await generate_worker_key()
    logger.info(f"[STARTUP] WORKER_PUBLIC_KEY_HEX: {WORKER_PUBLIC_KEY_HEX}")
    await fetch_genesis_block()
    payload = {"ip": WORKER_IP, "type": WORKER_TYPE, "port": 8000, "pub_key": WORKER_PUBLIC_KEY_HEX}
    async with aiohttp.ClientSession() as session:
        async with session.post(REGISTER_URL, json=payload) as resp:
            await resp.text()

@app.on_event("startup")
async def startup():
    url = f"{COORDINATOR_URL}/health" if WORKER_MODE == "COORDINADOR" else f"{POOL_URL}/health"
    await wait_for_service(url)
    await register()
    if WORKER_MODE == "COORDINADOR":
        asyncio.create_task(mining_cycle())

if __name__ == "__main__":
    uvicorn.run("worker:app", host="0.0.0.0", port=8000)
