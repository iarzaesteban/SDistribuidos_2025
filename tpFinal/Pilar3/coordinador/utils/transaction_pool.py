import threading
import time
import json
import hashlib
from datetime import datetime
from utils.redis_client import REDIS_CLIENT
from utils.rabbitmq_client import publish_task
from utils.logger import logger

def generar_hash_dummy():
    return hashlib.sha256(str(datetime.now()).encode()).hexdigest()

def procesar_pool_de_transacciones():
    while True:
        time.sleep(10)

        total = REDIS_CLIENT.llen("transaction_pool")
        if total == 0:
            continue

        transacciones_raw = REDIS_CLIENT.lrange("transaction_pool", 0, -1)
        REDIS_CLIENT.delete("transaction_pool")
        transacciones = [json.loads(t) for t in transacciones_raw]

        dificultad = 4
        rango_total = 1000000
        partes = 4  # Dividimos en 4 tareas
        salto = rango_total // partes
        timestamp_base = datetime.utcnow().timestamp()

        job_id = f"pool_{datetime.utcnow().timestamp():.6f}"

        for i in range(partes):
            tarea = {
                "job_id": job_id,
                "previous_hash": generar_hash_dummy(),
                "transactions": transacciones,
                "difficulty": dificultad,
                "range_start": i * salto,
                "range_end": (i + 1) * salto - 1,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Marcar que el trabajo completo aún no fue resuelto
            REDIS_CLIENT.set(f"solved:{job_id}", "0")

            publish_task(json.dumps(tarea))
            logger.info(f"Tarea publicada: job_id={job_id}, rango {tarea['range_start']} a {tarea['range_end']} con {len(transacciones)} transacciones.")



def start_transaction_pool_manager():
    t = threading.Thread(target=procesar_pool_de_transacciones, daemon=True)
    t.start()
