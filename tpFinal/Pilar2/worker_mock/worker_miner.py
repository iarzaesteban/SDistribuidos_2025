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
    WORKER_MODE,
    WORKER_TYPE,
    POOL_URL)

app = FastAPI()

TOTAL_REWARD = 0.0  # Sumamos los premios del worker
WORKER_IP = get_container_ip() # Obtnemos la ip del container
REGISTER_URL = f"{COORDINATOR_URL}/register-worker"
PUBLISH_URL = f"{COORDINATOR_URL}/publish-results"

MINING_DURATION = 60 # Duracion del procesamiento de mineria, luego publicar (1 min)
WAIT_DURATION = 30

# URL según modo
if WORKER_MODE == "COORDINADOR":
    REGISTER_URL = f"{COORDINATOR_URL}/register-worker"
    PUBLISH_URL = f"{COORDINATOR_URL}/publish-results"
elif WORKER_MODE == "POOL":
    REGISTER_URL = f"{POOL_URL}/register-worker"
    PUBLISH_URL = None 
else:
    raise ValueError("WORKER_MODE inválido: debe ser 'COORDINATOR' o 'POOL'.")


async def wait_for_service(url: str, timeout: int = 5):
    """
    Espera hasta que el servicio en 'url' responda con status 'ok'.
    """
    logger.info(f"[WAIT] Esperando que el servicio {url} esté disponible...")
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("status") == "ok":
                            logger.info(f"[WAIT] Servicio {url} disponible.")
                            return
            except Exception as e:
                logger.warning(f"[WAIT] Servicio {url} no disponible aún: {e}")
            logger.info(f"[WAIT] Reintentando en {timeout} segundos...")
            await asyncio.sleep(timeout)


async def register():
    payload = {"ip": WORKER_IP, "type": WORKER_TYPE, "port": 8000}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(REGISTER_URL, json=payload) as resp:
                data = await resp.json()
                logger.info(f"[REGISTER] {data}")
        except Exception as e:
            logger.error(f"[ERROR] No se pudo registrar el worker: {e}")


async def mine_transactions(transactions: list[Transaction], starting_previous_hash: str) -> list[Transaction]:
    logger.info(f"[MINING] Iniciando minería de {len(transactions)} transacciones por {MINING_DURATION} segundos...")
    start_time = time.time()
    mined = []
    previous_hash = starting_previous_hash

    for tx in transactions:
        if time.time() - start_time > MINING_DURATION:
            logger.warning(f"[MINING] Tiempo agotado.")
            break
        tx.worker_ip = WORKER_IP
        tx.hash_previo = previous_hash
        tx.mine(prefix=tx.challenge, mock_result=MOCK_TASK_WORKER)
        previous_hash = tx.hash
        mined.append(tx)
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
    await register()
    while True:
        logger.info("\n[CYCLE] Nuevo ciclo de minería iniciado")
        
        fetched_previous_hash, transactions = fetch_transactions()
        if not transactions:
            logger.warning("[CYCLE] No hay transacciones pendientes.")
            await asyncio.sleep(WAIT_DURATION)
            continue
        if fetched_previous_hash is None:
            logger.error("Error, no se envió el previos_hash")
            await asyncio.sleep(WAIT_DURATION)
            continue

        mined_transactions = await mine_transactions(transactions, fetched_previous_hash)

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
    health_url = ""

    if WORKER_MODE == "COORDINADOR":
        health_url = f"{COORDINATOR_URL}/health"
    elif WORKER_MODE == "POOL":
        health_url = f"{POOL_URL}/health"
    else:
        raise ValueError("WORKER_MODE inválido: debe ser 'COORDINATOR' o 'POOL'.")

    await wait_for_service(health_url)

    await register()

    if WORKER_MODE == "COORDINADOR":
        asyncio.create_task(mining_cycle())
    else:
        logger.info("[STARTUP] Worker en modo POOL listo para recibir tareas.")

if __name__ == "__main__":
    uvicorn.run("worker_miner:app", host="0.0.0.0", port=8000, reload=True)