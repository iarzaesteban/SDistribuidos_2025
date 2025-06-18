import threading
import time
import os

from fastapi import FastAPI
from app.routes import router as pool_router
from utils.logger import logger
from utils.state import State
from utils.helper import (push_tx_to_queue,
                          assign_next_tx_to_workers,
                          publish_results_to_coordinator,
                          fetch_transactions)

TASK_ASSIGN_INTERVAL = int(os.getenv("TASK_ASSIGN_INTERVAL", 60))

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


def periodic_result_publisher():
    while True:
        try:
            publish_results_to_coordinator()
        except Exception as e:
            logger.error(f"Error publicando resultados al coordinador: {e}")
        
        time.sleep(TASK_ASSIGN_INTERVAL)

@app.on_event("startup")
def startup_event():
    logger.info("Pool Service started")
    try:
        thread1 = threading.Thread(target=periodic_task_assignment, daemon=True)
        thread2 = threading.Thread(target=periodic_result_publisher, daemon=True)
        thread1.start()
        thread2.start()
        logger.info("Pool Service started sussefully")
    except Exception as e:
        logger.error(f"Error al correr el Pool de TXs: {e}")

    
@app.on_event("shutdown")
def shutdown_event():
    logger.info("Pool Service stopped")

app.include_router(pool_router)
