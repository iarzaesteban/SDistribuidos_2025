import threading
import time
import asyncio
import os

from fastapi import FastAPI
from app.routes import router as pool_router
from utils.logger import logger
from utils.state import State
from utils.helper import (push_tx_to_queue,
                          generate_worker_key,
                          fetch_genesis_block,
                          get_current_window,
                          assign_next_tx_to_workers,
                          publish_results_to_coordinator,
                          fetch_transactions)

TASK_ASSIGN_INTERVAL = int(os.getenv("TASK_ASSIGN_INTERVAL", 60))
GENESIS_BLOCK = None
app = FastAPI(title="Nodo Pool TX (POOL)")

app.include_router(pool_router, prefix="/pool")

def periodic_task_assignment():
    logger.info("[POOL] Comenzando ciclo de asignación de tareas...")

    while True:
        try:
            State.accepting_results = False
            logger.info("[POOL] Ventana ABIERTA.")

            previous_hash, transactions = fetch_transactions()
            logger.info(f"el hash previo es {previous_hash}")
            State.last_hash = previous_hash
            for tx in transactions:
                push_tx_to_queue(tx)
                logger.info(f"[POOL] Transacción {tx.tx_id} agregada a la cola Redis.")

            State.accepting_results = True
            logger.info("[POOL] Ventana CERRADA.")
            assign_next_tx_to_workers()

        except Exception as e:
            logger.error(f"Error en el ciclo de asignación de tareas: {e}")
        
        time.sleep(TASK_ASSIGN_INTERVAL)



async def mining_cycle():
    global GENESIS_BLOCK
    config = GENESIS_BLOCK['config']

    fetched_previous_hash = None
    transactions = []
    already_fetched = False
    already_published = False
    last_window = None
    while True:
        current_window = get_current_window(config)

        if current_window != last_window:
            already_fetched = False
            already_published = False
            last_window = current_window

        if current_window == 'monitoring' and not already_fetched:
            logger.info(f"[POOL] Ventana MONITOREO activa: solicitando transacciones.")
            fetched_previous_hash, transactions = fetch_transactions()
            if not transactions:
                logger.warning(f"[POOL] No se encontraron transacciones.")
            else:
                logger.info(f"[POOL] {len(transactions)} transacciones obtenidas.")
            already_fetched = True

        elif current_window == 'publishing' and transactions and not already_published:
            logger.info(f"[POOL] Ventana PUBLICACIÓN activa: publicando resultados.")
            if fetched_previous_hash is None:
                logger.error(f"[POOL] No hay previous_hash para minar.")
            else:
                # mined_transactions = await mine_transactions(transactions, fetched_previous_hash)
                # await publish_results(mined_transactions)
                transactions = []
            already_published = True
        await asyncio.sleep(0.5)


def periodic_result_publisher():
    while True:
        try:
            publish_results_to_coordinator()
        except Exception as e:
            logger.error(f"Error publicando resultados al coordinador: {e}")
        
        time.sleep(TASK_ASSIGN_INTERVAL)

@app.on_event("startup")
async def startup_event():
    logger.info("Pool Service started")
    try:

        # Generamos par de claves por si es eel pool el ganador generar tareas para minar
        global WORKER_PRIVATE_KEY, WORKER_PUBLIC_KEY_HEX, GENESIS_BLOCK
        WORKER_PRIVATE_KEY, WORKER_PUBLIC_KEY_HEX = await generate_worker_key()
        logger.info(f"[STARTUP] WORKER_PUBLIC_KEY_HEX: {WORKER_PUBLIC_KEY_HEX}")
        GENESIS_BLOCK = await fetch_genesis_block()
        asyncio.create_task(mining_cycle())

        # thread1 = threading.Thread(target=periodic_task_assignment, daemon=True)
        # thread2 = threading.Thread(target=periodic_result_publisher, daemon=True)
        # thread1.start()
        # thread2.start()
        logger.info("Pool Service started sussefully")
    except Exception as e:
        logger.error(f"Error al correr el Pool de TXs: {e}")

    
@app.on_event("shutdown")
def shutdown_event():
    logger.info("Pool Service stopped")

app.include_router(pool_router)
