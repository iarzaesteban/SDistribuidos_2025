from fastapi import APIRouter, Request, HTTPException, Query
from utils.logger import logger
from utils.state import State
from utils.helper import (assign_next_tx_to_workers,
                          WorkerRegistration,
                          Transaction,
                          validar_hash,
                          REDIS_CLIENT,
                          get_keys)
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
            "port": str(worker.port),
            "pub_key": worker.pub_key}
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
    WORKER_PRIVATE_KEY, WORKER_PUBLIC_KEY_HEX = get_keys()
    data = await request.json()
    tx = Transaction(**data['transaction'])
    worker_ip = data["worker_ip"]
    valid = validar_hash(tx)

    tx_key = f"tx:{tx.tx_id}"

    # Validamos si la transacción sigue existiendo en Redis (no fue publicada)
    if not REDIS_CLIENT.exists(tx_key):
        logger.warning(f"[POOL] Resultado tardío recibido para transacción {tx.tx_id} que ya fue publicada o descartada.")
        return {"status": "rejected", "reason": "tx_not_found_or_already_published", "tx_id": tx.tx_id}
    
    if valid:
        if REDIS_CLIENT.hget(tx_key, "status") == "resuelta":
            logger.info(f"[POOL] Transacción {tx.tx_id} ya resuelta.")
            return {"status": "ignored", "reason": "already_resolved"}

        tx.pub_key = WORKER_PUBLIC_KEY_HEX
        REDIS_CLIENT.hset(tx_key, mapping={
            "status": "resuelta",
            "resolved_by": WORKER_PUBLIC_KEY_HEX, # ojo poner la pub_key del pool
            "transaction": tx.json()
        })

        logger.info(f"[POOL] Transacción {tx.tx_id} resuelta por {worker_ip} con nonce {tx.nonce}.")
        State.last_hash = tx.hash

        await assign_next_tx_to_workers()

        return {"status": "accepted", "tx_id": tx.tx_id}

    return {"status": "canceled", "reason": "invalid_challenge", "tx_id": tx.tx_id}
