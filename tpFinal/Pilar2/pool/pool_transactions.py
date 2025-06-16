import threading
import time
import os

from fastapi import FastAPI
from app.routes import router as pool_router
from utils.logger import logger
from utils.helper import (fetch_transactions,
                          calculate_difficulty,
                          prepare_tasks_for_workers,
                          dispatch_tasks_to_workers)

TASK_ASSIGN_INTERVAL = int(os.getenv("TASK_ASSIGN_INTERVAL", 60))

app = FastAPI(title="Nodo Pool TX (POOL)")

app.include_router(pool_router, prefix="/pool")

def periodic_task_assignment():
    logger.info("[POOL] Comenzando ciclo de asignación de tareas...")
    while True:
        try:
            last_hash, transactions = fetch_transactions()
            if not transactions:
                logger.info("[POOL] No hay transacciones pendientes.")
            else:
                difficulty = calculate_difficulty()
                tasks = prepare_tasks_for_workers(transactions, last_hash, difficulty)
                dispatch_tasks_to_workers(tasks)
                logger.info("[POOL] Tareas enviadas a workers.")
        except Exception as e:
            logger.error(f"Error en el ciclo de asignación de tareas: {e}")
        time.sleep(TASK_ASSIGN_INTERVAL)


@app.on_event("startup")
def startup_event():
    logger.info("Pool Service started")
    try:
        thread = threading.Thread(target=periodic_task_assignment, daemon=True)
        thread.start()
        logger.info("Pool Service started sussefully")
    except Exception as e:
        logger.error(f"Error al correr el Pool de TXs: {e}")

    
@app.on_event("shutdown")
def shutdown_event():
    logger.info("Pool Service stopped")

app.include_router(pool_router)
