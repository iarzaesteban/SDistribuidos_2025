import json

from fastapi import APIRouter, Request, HTTPException, Query
from utils.logger import logger
from utils.helper import (WorkerRegistration,
                          fetch_transactions,
                          calculate_difficulty,
                          prepare_tasks_for_workers,
                          dispatch_tasks_to_workers,
                          REDIS_CLIENT)
router = APIRouter()

@router.get("/")
def root():
    return {"message": f"El pool esta esperando solicitudes"}


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/register-worker")
def register_worker(worker: WorkerRegistration):
    """
    Registra un worker con su IP y tipo de procesamiento (CPU/GPU)
    """
    try:
        redis_key = f"worker:{worker.ip}"
        worker_data = {
            "type": worker.type, 
            "port": str(worker.port)}
        REDIS_CLIENT.hmset(redis_key, worker_data)

        return {"status": "registered", "IP": worker.ip, "port": worker.port}
    except Exception as e:
        logger.error(f"Error registrando worker: {e}")
        raise HTTPException(status_code=500, detail="Error registrando worker")


@router.get("/workers")
def list_registered_workers():
    """
    Devuelve todos los workers registrados con su IP y tipo.
    """
    try:
        worker_keys = REDIS_CLIENT.keys("worker:*")
        workers = []

        for key in worker_keys:
            ip = key.split(":")[1]
            worker_info = REDIS_CLIENT.hgetall(key)
            workers.append({"ip": ip, "info": worker_info})

        return {"status": "success", "workers": workers}
    
    except Exception as e:
        logger.error(f"Error listando workers: {e}")
        raise HTTPException(status_code=500, detail="Error listando workers")



@router.post("/assign-tasks")
def assign_tasks():
    """
    Calcula dificultad, prepara y envía tareas a workers.
    """
    try:
        last_hash, transactions = fetch_transactions()
        if not transactions:
            return {"message": "No hay transacciones para procesar."}

        difficulty = calculate_difficulty()
        tasks = prepare_tasks_for_workers(transactions, last_hash, difficulty)
        dispatch_tasks_to_workers(tasks)

        return {"status": "Tareas asignadas", "tasks": tasks}
    except Exception as e:
        logger.error(f"Error en assign-tasks: {e}")
        raise HTTPException(status_code=500, detail="Error al asignar tareas a los workers.")

