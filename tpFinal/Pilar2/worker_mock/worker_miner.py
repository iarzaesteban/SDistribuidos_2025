import asyncio
import aiohttp
import time
import uvicorn
from fastapi import FastAPI, Request
from utils.logger import logger
from utils.helper import (
    get_container_ip,
    fetch_transactions,
    Transaction,
    COORDINATOR_URL,
    RESOLUTION_INTERVAL,
    MOCK_TASK_WORKER,
    PREFIX
)

app = FastAPI()

TOTAL_REWARD = 0.0
WORKER_IP = get_container_ip()
REGISTER_URL = f"{COORDINATOR_URL}/register-worker"
PUBLISH_URL = f"{COORDINATOR_URL}/publish-results"

MINING_DURATION = 60
WAIT_DURATION = 30

async def register():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(REGISTER_URL, json={"worker_ip": WORKER_IP}) as resp:
                data = await resp.json()
                logger.info(f"[REGISTER] {data}")
        except Exception as e:
            logger.error(f"[ERROR] No se pudo registrar el worker: {e}")


async def mine_transactions(transactions: list[Transaction]) -> list[Transaction]:
    logger.info(f"[MINING] Iniciando minería de {len(transactions)} transacciones por {MINING_DURATION} segundos...")
    start_time = time.time()
    mined = []
    for tx in transactions:
        if time.time() - start_time > MINING_DURATION:
            logger.warning(f"[MINING] Tiempo agotado.")
            break
        tx.worker_ip = WORKER_IP
        tx.mine(prefix=PREFIX, mock_result=MOCK_TASK_WORKER)
        mined.append(tx)
    return mined


async def publish_results(transactions: list[Transaction]):
    payload = {"transactions": [tx.dict() for tx in transactions]}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(PUBLISH_URL, json=payload) as resp:
                data = await resp.json()
                print(f"[PUBLISH] {data}")
        except Exception as e:
            logger.error(f"[ERROR] No se pudo publicar resultados: {e}")


async def mining_cycle():
    await register()
    while True:
        logger.info("\n[CYCLE] Nuevo ciclo de minería iniciado")
        
        transactions = fetch_transactions()
        if not transactions:
            logger.warning("[CYCLE] No hay transacciones pendientes.")
        
        mined_transactions = await mine_transactions(transactions)

        await publish_results(mined_transactions)

        logger.info(f"[WAIT] Esperando {WAIT_DURATION} segundos para próxima ronda...\n")
        await asyncio.sleep(WAIT_DURATION)


@app.post("/reward")
async def receive_reward(request: Request):
    global TOTAL_REWARD
    data = await request.json()
    amount = data.get("amount", 0.0)
    TOTAL_REWARD += amount
    logger.info(f"[INFO] Recompensa recibida: {amount}, total acumulado: {TOTAL_REWARD}")
    return {"status": "ok", "message": f"Recompensa de {amount} recibida", "total_reward": TOTAL_REWARD}


@app.get("/reward")
def get_total_reward():
    return {"total_reward": TOTAL_REWARD}


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(mining_cycle())