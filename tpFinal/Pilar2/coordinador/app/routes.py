import time
import uuid
import json
from fastapi import APIRouter, Request, HTTPException, Query
from typing import List, Dict
from utils.helper import REDIS_CLIENT as redis_client

from utils.logger import logger
from utils.rabbitmq_client import publish_new_transaction, RabbitMQClient
from utils.helper import (Transaction,
                          TransactionStatus,
                          WorkerRegistration,
                          REDIS_CLIENT,
                          EARRING_QUEUE,
                          ROUND_PERIOD,
                          get_last_block_hash,
                          IN_PROGRESS_QUEUE)

rabbit_earring = RabbitMQClient(queue_name=EARRING_QUEUE)
                                 
router = APIRouter()


def is_monitoring_window():
    current_second = int(time.time()) % 60
    return 5 <= current_second <= 15

def is_publish_window():
    current_second = int(time.time()) % 60
    return 50 <= current_second <= 59

@router.get("/")
def root():
    return {"message": f"El coordinador esta esperando transacciones"}


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/status")
def status():
    logger.info("Status checked")

    # Estado de Redis
    try:
        redis_status = "online" if REDIS_CLIENT.ping() else "offline"
    except Exception as e:
        redis_status = f"error: {str(e)}"

    # Timestamp actual
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    return {
        "status": "ok",
        "timestamp": now,
        "redis": redis_status
    }

@router.post("/new-task")
def new_task(tx: Transaction):
    logger.info(f"Recived transaction {tx}")
    message = f"Error, no se pudo procesar la transacción {tx}"
    if tx.verify():
        tx_id = str(uuid.uuid4())
        tx_dict = tx.to_dict()
        tx_dict["tx_id"] = tx_id
        tx_dict["tries"] = 0
        tx_dict["status"] = TransactionStatus.pendiente.value
        publish_new_transaction(tx_dict)
        message = f"Transacción publicada correctamente. ID: {tx_id}"
    return {"message": message, "tx": tx_id}


@router.get("/get-block/{block_hash}")
async def get_block(block_hash: str):
    logger.info(f"Buscando bloque con hash {block_hash}")
    
    redis_key = f"block:{block_hash}"
    raw_block = REDIS_CLIENT.get(redis_key)
    
    if raw_block:
        try:
            block = json.loads(raw_block)
            return {"status": "Encontrado", "block": block}
        except Exception as e:
            logger.error(f"Error al parsear el bloque: {e}")
            raise HTTPException(status_code=500, detail="Error al procesar el bloque desde Redis")
    
    raise HTTPException(status_code=404, detail="Bloque no encontrado")


@router.get("/get-earrings-transactions")
async def get_earrings_transactions():
    try:
        rabbit_client = RabbitMQClient(queue_name=EARRING_QUEUE)
        messages = rabbit_client.get_all_messages()
        rabbit_client.close()
        return {"count": len(messages), "transactions": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener transacciones de earring: {str(e)}")
   

@router.get("/get-transaction/{tx_id}")
async def get_transaction(tx_id: str):
    logger.info(f"Vamos a buscar la Tx {tx_id}")
    # Buscamos la TX en monitoring_transactions
    tx_data = REDIS_CLIENT.hget("monitoring_transactions", tx_id)
    if tx_data:
        return {"status": "En proceso", "tx": json.loads(tx_data)}

    # Buscamos la TX  en dropped_txs
    dropped_list = REDIS_CLIENT.lrange("dropped_txs", 0, -1)
    for raw_tx in dropped_list:
        try:
            tx = json.loads(raw_tx)
            if tx.get("tx_id") == tx_id:
                return {"status": "Borrada", "tx": tx}
        except Exception:
            continue
    
    # Buscamos la TX  en la cola rabbit earring
    rabbit_client_earring = RabbitMQClient(queue_name=EARRING_QUEUE)
    found = rabbit_client_earring._get_message_by_txid(tx_id)
    if found:
        return {"status": "Pendiente", "tx": json.loads(found["body"])}

    # Buscamos la TX  en los bloques de la blockchain
    block_keys = REDIS_CLIENT.keys("block:*")
    for key in block_keys:
        raw_block = REDIS_CLIENT.get(key)
        if raw_block:
            try:
                block = json.loads(raw_block)
                tx = block.get("transaction")
                if tx and tx.get("tx_id") == tx_id:
                    block_hash = key.decode().replace("block:", "") if isinstance(key, bytes) else key.replace("block:", "")
                    return {
                        "status": "Procesda",
                        "tx": tx,
                        "block_id": block.get("block_id"),
                        "block_hash": block_hash,
                        "nonce":block.get("nonce"),
                    }
            except Exception:
                continue

    raise HTTPException(status_code=404, detail="Transacción no encontrada")
    

@router.get("/monitoring-tasks")
def get_monitoring_tasks():
    """
        Devuelve todas las transacciones monitoreadas sin desencolarlas.
    """
    if not is_monitoring_window():
        raise HTTPException(status_code=403, detail="Ventana cerrada para obtener transacciones")
    
    try:
        tasks = REDIS_CLIENT.hgetall("monitoring_transactions")
        last_hash = get_last_block_hash()
        decoded_tasks = [json.loads(v) for v in tasks.values()]
        return {"last_hash": last_hash,"transactions": decoded_tasks}
    except Exception as e:
        logger.error(f"Error al obtener transacciones de monitoreo: {str(e)}")
        return {"error": "No se pudieron obtener las transacciones"}
    

@router.get("/get-in-progress-txs")
def get_in_progress_tx():
    """
        Devuelve todas las transacciones monitoreadas sin desencolarlas.
    """  
    try:
        tasks = REDIS_CLIENT.hgetall("monitoring_transactions")
        last_hash = get_last_block_hash()
        decoded_tasks = [json.loads(v) for v in tasks.values()]
        return {"last_hash": last_hash,"transactions": decoded_tasks}
    except Exception as e:
        logger.error(f"Error al obtener transacciones de monitoreo: {str(e)}")
        return {"error": "No se pudieron obtener las transacciones"}


@router.post("/register-worker")
async def register_worker(worker: WorkerRegistration):
    if not worker.ip:
        raise HTTPException(status_code=400, detail="worker_ip es requerido")
    
    try:
        redis_key = f"worker_registered:{worker.ip}"
        worker_data = {
            "type": worker.type, 
            "port": str(worker.port),
            "pub_key": worker.pub_key}
        REDIS_CLIENT.hmset(redis_key, worker_data)
        logger.info(f"Worker registrado: {worker.ip}")
        return {"status": "ok", "worker_ip": worker.ip, "port": worker.port}
    except Exception as e:
        logger.error(f"Error al registrar worker: {e}")
        raise HTTPException(status_code=500, detail="No se pudo registrar el worker")
    

@router.get("/registered-workers")
async def get_registered_workers():
    try:
        worker_keys = REDIS_CLIENT.keys("worker_registered:*")
        workers = []

        for key in worker_keys:
            ip = key.split(":")[1]
            worker_info = REDIS_CLIENT.hgetall(key)
            workers.append({"ip": ip, "info": worker_info})

        return {"status": "success", "workers": workers}
    except Exception as e:
        logger.error(f"Error al obtener workers: {e}")
        raise HTTPException(status_code=500, detail="Error interno")


@router.get("/genesis-block")
def get_genesis_block():
    """
    Devuelve el bloque génesis completo desde Redis.
    """
    try:
        genesis_block_hash = REDIS_CLIENT.get("genesis_block")
        if not genesis_block_hash:
            raise HTTPException(status_code=404, detail="Bloque génesis no encontrado")

        genesis_block = REDIS_CLIENT.get(f"block:{genesis_block_hash}")
        if not genesis_block:
            raise HTTPException(status_code=404, detail="Datos del bloque génesis no encontrados")

        return json.loads(genesis_block)
    except Exception as e:
        logger.error(f"Error al obtener el bloque génesis: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno al obtener el bloque génesis")


@router.post("/publish-results")
async def publish_results(request: Request):
    if not is_publish_window():
        raise HTTPException(status_code=403, detail="Ventana cerrada para publicar resultados")

    data = await request.json()
    transactions = data.get("transactions", [])
    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions received")
    
    for tx_data in transactions:
        REDIS_CLIENT.rpush("pending_transactions", json.dumps(tx_data))
    logger.info(f"Recibidas {len(transactions)} transacciones para procesar más tarde.")
    return {"status": "ok", "message": f"{len(transactions)} transacciones recibidas"}


@router.get("/workers-results")
async def get_workers_results(limit: int = 100):
    """
    Devuelve hasta `limit` transacciones pendientes almacenadas en Redis.
    """
    try:
        # Obtenemos los elementos de la lista enviadas por los workers
        raw_items = REDIS_CLIENT.lrange("pending_transactions", 0, limit - 1)

        transactions = []
        for item in raw_items:
            try:
                tx = json.loads(item)
                transactions.append(tx)
            except json.JSONDecodeError:
                logger.warning(f"Transacción inválida en Redis: {item}")
        
        return {
            "pending_transactions": transactions,
            "count": len(transactions)
        }

    except Exception as e:
        logger.exception("Error al obtener transacciones pendientes desde Redis")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/blockchain")
async def get_blockchain(
    id: int = Query(None),
    start: int = Query(None),
    end: int = Query(None),
):
    """
        Como pegarle a este endpoint
        curl http://localhost:8989/blockchain   ---> obtenemos todos los bloques
        curl http://localhost:8989/blockchain?id=2   ---> obtenemos el bloque con ese id 
        curl http://localhost:8989/blockchain?start=2&end=4   ---> obtenemos aquellos bloques con id entre 2 y 4 (use postman, con curl no funcó)
    """
    try:
        block_keys = REDIS_CLIENT.keys("block:*")
        if not block_keys:
            return {"Blockchain": []}
        
        blocks = []
        for key in block_keys:
            raw_data = REDIS_CLIENT.get(key)
            if raw_data:
                block = json.loads(raw_data)
                # Agregamos también el hash del bloque
                block["block_hash"] = key.decode().replace("block:", "") if isinstance(key, bytes) else key.replace("block:", "")
                blocks.append(block)

        # Ordenamos por block_id (convertido a int por si acaso viene como string)
        blocks.sort(key=lambda b: int(b.get("block_id", 0)))

        # Filtros según los parámetros
        if id is not None:
            filtered = [b for b in blocks if int(b.get("block_id", -1)) == id]
        elif start is not None and end is not None:
            if start > end:
                logger.warning(f"Parámetros inválidos: start={start} > end={end}")
                raise HTTPException(status_code=400, detail="Parámetro 'start' no puede ser mayor que 'end'")
            filtered = [b for b in blocks if start <= int(b.get("block_id", 0)) <= end]
        else:
            filtered = blocks
            logger.info("Retornando todos los bloques sin filtro.")

        return {"Blockchain": filtered}
    except Exception as e:
        logger.error(f"Error al obtener la blockchain: {e}")
        raise HTTPException(status_code=500, detail="Error interno")
    

@router.get("/heartbeats", response_model=List[Dict[str, int]])
def get_heartbeats():
    """
    Devuelve una lista de workers activos y su TTL restante en segundos.
    Cada clave en Redis tiene el formato 'heartbeat:{worker_id}' con un EXPIRE.
    """
    try:
        # En producción es mejor usar SCAN que KEYS para no bloquear Redis
        keys = list(redis_client.scan_iter("heartbeat:*"))
        heartbeats = []
        for key in keys:
            # key es un byte-string o str: 'heartbeat:worker123'
            worker_id = key.split(":", 1)[1]
            ttl = redis_client.ttl(key)  # segundos restantes
            if ttl and ttl > 0:
                heartbeats.append({"worker_id": worker_id, "ttl": ttl})
        return heartbeats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer heartbeats: {e}")


@router.get("/get-last-chained-block")
async def get_last_chained_block():
    try:
        last_hash = REDIS_CLIENT.get("last_block")
        if last_hash:
            last_block = json.loads(REDIS_CLIENT.get(f"block:{last_hash}"))
            logger.info("Último bloque:", last_block)
        return {"last-chained-block": last_block}
    except Exception as e:
        logger.error(f"Error al obtener el último bloque: {e}")
        raise HTTPException(status_code=500, detail="Error interno")
    