import json
import asyncio
import aiohttp
import hashlib
import time
import uvicorn
from fastapi import FastAPI, Request
from utils.logger import logger
from utils.helper import (generate_worker_key,
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

GENESIS_BLOCK = None
WORKER_PRIVATE_KEY = None
WORKER_PUBLIC_KEY_HEX = None

mining_task = None
CURRENT_TX_ID = None 
STOP_MINING = None

TOTAL_REWARD = 0.0  # Sumamos los premios del worker
WORKER_IP = get_container_ip() # Obtnemos la ip del container
REGISTER_URL = f"{COORDINATOR_URL}/register-worker"
PUBLISH_URL = f"{COORDINATOR_URL}/publish-results"
MINING_DURATION = 60 # Duracion del procesamiento de mineria, luego publicar (1 min)
WAIT_DURATION = 30
GENESIS_BLOCK_URL = f"{COORDINATOR_URL}/genesis-block"

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


async def fetch_genesis_block():
    global GENESIS_BLOCK
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(GENESIS_BLOCK_URL) as resp:
                if resp.status == 200:
                    GENESIS_BLOCK = await resp.json()
                    logger.info(f"[GENESIS] Bloque génesis recibido: {json.dumps(GENESIS_BLOCK, indent=2)}")
                else:
                    logger.error(f"[GENESIS] Fallo al obtener bloque génesis. Status: {resp.status}")
        except Exception as e:
            logger.error(f"[GENESIS] Error al obtener bloque génesis: {e}")


async def register():
    global WORKER_PUBLIC_KEY_HEX, GENESIS_BLOCK
    payload = {"ip": WORKER_IP, "type": WORKER_TYPE, "port": 8000, "pub_key": WORKER_PUBLIC_KEY_HEX}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(REGISTER_URL, json=payload) as resp:
                data = await resp.json()
                logger.info(f"[REGISTER] {data}")

                await fetch_genesis_block()
                    
        except Exception as e:
            logger.error(f"[ERROR] No se pudo registrar el worker: {e}")


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
            start_mine = time.time()
            hash = await tx.mine(prefix=tx.challenge, mock_result=MOCK_TASK_WORKER)
            end_mine = time.time()
            tx.mine_time = round(end_mine - start_mine, 4)
            previous_hash = hash
            mined.append(tx)
        except asyncio.CancelledError:
            logger.warning("[MINING] Minería cancelada!")
            break
    return mined


async def publish_results(transactions: list[Transaction]):
    global WORKER_PUBLIC_KEY_HEX
    for tx in transactions:
        tx.pub_key = WORKER_PUBLIC_KEY_HEX
    payload = {"transactions": [tx.dict() for tx in transactions]}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(PUBLISH_URL, json=payload) as resp:
                data = await resp.json()
                logger.info(f"[PUBLISH] {data}")
        except Exception as e:
            logger.error(f"[ERROR] No se pudo publicar resultados: {e}")


def get_current_window(genesis_config):
    period = genesis_config['window_period_seconds']
    monitoring_start = genesis_config['monitoring_window_start']
    monitoring_end = genesis_config['monitoring_window_end']
    publish_start = genesis_config['publish_window_start']
    publish_end = genesis_config['publish_window_end']

    now = int(time.time())
    seconds_in_period = now % period

    if monitoring_start <= seconds_in_period <= monitoring_end:
        return 'monitoring'
    elif publish_start <= seconds_in_period <= publish_end:
        return 'publishing'
    else:
        return 'waiting'

async def mining_cycle():
    global GENESIS_BLOCK
    global mining_task
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

                # Iniciar minado solo si hay transacciones
                if transactions:
                    logger.info("[WORKER] Iniciando minería en background.")
                    mining_task = asyncio.create_task(mine_transactions(transactions, fetched_previous_hash))

            elif current_window == 'publishing':
                logger.info("[WORKER] Ventana PUBLISHING activa: publicando resultados.")
                if fetched_previous_hash is None:
                    logger.error("[WORKER] No hay previous_hash para minar.")
                elif transactions:
                    if mining_task and not mining_task.done():
                        logger.info("[WORKER] Cancelando minería para publicar.")
                        mining_task.cancel()
                        try:
                            await mining_task
                        except asyncio.CancelledError:
                            logger.info("[WORKER] Minería cancelada para publicar.")

                    # Publicar lo minado hasta ahora:
                    await publish_results(transactions)
                    transactions = []

            last_window = current_window

        await asyncio.sleep(0.5)


def proof_of_work(tx: Transaction, nonce_start, nonce_end, difficulty, config):
    prefix = '0' * difficulty
    for nonce in range(nonce_start, nonce_end + 1):
        if STOP_MINING or tx.tx_id != CURRENT_TX_ID:
            logger.info(f"[WORKER] Minado cancelado para tx_id={tx.tx_id}")
            return None, None
        # Verificar si cambió la ventana a 'publishing'
        current_window = get_current_window(config)
        if current_window == 'publishing':
            logger.info(f"[WORKER] Detectada ventana PUBLISHING durante minado. Abortando minería para tx_id={tx.tx_id}.")
            return None, None

        tx.nonce = nonce
        new_hash = tx.compute_hash()
        if new_hash.startswith(prefix):
            tx.hash = new_hash
            return nonce, new_hash
    return None, None


@app.post("/mine-task")
async def mine_task(request: Request):
    global CURRENT_TX_ID, STOP_MINING, WORKER_PUBLIC_KEY_HEX
    data = await request.json()
    
    tx_id = data["tx_id"]
    hash_previo = data["hash_previo"]
    nonce_start = data["nonce_start"]
    nonce_end = data["nonce_end"]
    difficulty = data["difficulty"]
    tx = Transaction(**data['transaction'])

    if tx_id != CURRENT_TX_ID:
        logger.info(f"[WORKER] Nueva tarea recibida: {tx_id}. Cancelando la anterior: {CURRENT_TX_ID}")
        STOP_MINING = True
        await asyncio.sleep(0.1)
        STOP_MINING = False
        CURRENT_TX_ID = tx_id


    tx.worker_ip = WORKER_IP
    tx.pub_key = WORKER_PUBLIC_KEY_HEX
    tx.hash_previo = hash_previo
    config = GENESIS_BLOCK['config']
    logger.info(f"[WORKER] Minando tx_id={tx_id} desde nonce {nonce_start} hasta {nonce_end} con dificultad {difficulty}...")

    nonce, valid_hash = proof_of_work(tx, nonce_start, nonce_end, difficulty, config)
    
    if valid_hash:
        logger.info(f"[WORKER] Transacción {tx_id} resuelta con nonce {nonce}, hash {valid_hash}")
        # Enviar resultado al Pool
        async with aiohttp.ClientSession() as session:
            payload = {
                "worker_ip": get_container_ip(),
                "transaction": tx.dict(),
            }
            try:
                async with session.post(f"{POOL_URL}/mine-result", json=payload) as resp:
                    text = await resp.text()
                    logger.info(f"[WORKER] Resultado enviado al Pool: {resp.status} {text}")
            except Exception as e:
                logger.error(f"[WORKER] Error enviando resultado al Pool: {e}")
    else:
        logger.info(f"[WORKER] No se encontró solución para tx_id {tx_id} en rango asignado.")

    return {"status": "done"}


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
    global WORKER_PRIVATE_KEY, WORKER_PUBLIC_KEY_HEX
    WORKER_PRIVATE_KEY, WORKER_PUBLIC_KEY_HEX = await generate_worker_key()
    logger.info(f"[STARTUP] WORKER_PUBLIC_KEY_HEX: {WORKER_PUBLIC_KEY_HEX}")
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