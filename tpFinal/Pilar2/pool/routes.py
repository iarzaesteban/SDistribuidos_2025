from fastapi import APIRouter, Request, HTTPException, Query
from utils.logger import logger
from utils.helper import (accepting_results,
                          WorkerRegistration,
                          Transaction,
                          validar_hash,
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


@router.post("/mine-result")
async def mine_result(request: Request):
    if not accepting_results:
        logger.info("[POOL] Ventana cerrada: Resultado rechazado.")
        return {"status": "rejected", "reason": "window_closed"}
    
    data = await request.json()
    tx = Transaction(**data['transaction'])
    worker_ip = data["worker_ip"]
    valid = validar_hash(tx)
    
    if valid:
        tx_key = f"tx:{tx.tx_id}"

        # Verificar si la transacción ya fue resuelta
        if REDIS_CLIENT.hget(tx_key, "status") == "resuelta":
            logger.info(f"[POOL] Resultado ignorado: transacción {tx.tx_id} ya resuelta.")
            return {"status": "ignored", "reason": "already_resolved"}

        # Marcar la transacción como resuelta y guardar el worker que la resolvió
        REDIS_CLIENT.hset(tx_key, mapping={
            "status": "resuelta",
            "resolved_by": worker_ip,
            "transaction": tx.json()
        })
        logger.info(f"[POOL] Transacción {tx.tx_id} resuelta por {worker_ip} con nonce {tx.nonce}.")

        # Aumentar contador de transacciones resueltas por worker
        REDIS_CLIENT.incr(f"worker:{worker_ip}:resolved_count")

        return {"status": "accepted", "tx_id": tx.tx_id}
    return {"status": "canceled", "reason": "invalid_challenge", "tx_id": tx.tx_id}