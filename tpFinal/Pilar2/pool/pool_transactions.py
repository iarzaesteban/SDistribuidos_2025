import asyncio
import os
import aiohttp
import time
import math

from fastapi import FastAPI
from app.routes import router as pool_router
from utils.logger import logger
from utils.state import State
from utils.helper import (push_tx_to_queue,
                          generate_worker_key,
                          get_keys,
                          fetch_genesis_block,
                          generate_reward_tasks_for_workers,
                          get_current_window,
                          assign_next_tx_to_workers,
                          fetch_transactions,
                          publish_results,
                          Transaction,
                          REDIS_CLIENT,
                          COORDINATOR_URL)

TASK_ASSIGN_INTERVAL = int(os.getenv("TASK_ASSIGN_INTERVAL", 60))
GENESIS_BLOCK = None

app = FastAPI(title="Nodo Pool TX (POOL)")

app.include_router(pool_router)

async def mining_cycle():
    global GENESIS_BLOCK
    config = GENESIS_BLOCK['config']

    fetched_previous_hash = None
    transactions = []
    last_window = None

    while True:
        current_window = get_current_window(config)
        if current_window != last_window:
            logger.info(f"[POOL] Cambio de ventana detectado: {last_window} -> {current_window}")

            if current_window == 'monitoring':
                logger.info("[POOL] Ventana MONITORING activa: obteniendo transacciones.")
                fetched_previous_hash, transactions = fetch_transactions()
                if not transactions:
                    logger.warning("[POOL] No se encontraron transacciones.")
                else:
                    logger.info(f"[POOL] {len(transactions)} transacciones obtenidas.")
                    State.last_hash = fetched_previous_hash
                    for tx in transactions:
                        push_tx_to_queue(tx)
                    try:
                        await assign_next_tx_to_workers()
                    except Exception as e:
                        logger.error(f"[POOL] Error asignando tareas a workers: {e}")

            elif current_window == 'publishing':
                logger.info("[POOL] Ventana PUBLISHING activa: publicando resultados.")
                all_transactions = []

                keys_to_delete = REDIS_CLIENT.keys("tx:*")
                for key in keys_to_delete:
                    tx_data = REDIS_CLIENT.hgetall(key)
                    tx_json = tx_data.get("transaction")
                    if tx_json:
                        tx = Transaction.parse_raw(tx_json)
                        all_transactions.append(tx)

                if all_transactions:
                    await publish_results(all_transactions)
                else:
                    logger.info("[POOL] No hay transacciones para publicar.")

                if keys_to_delete:
                    REDIS_CLIENT.delete(*keys_to_delete)

                if REDIS_CLIENT.exists("tx_queue"):
                    REDIS_CLIENT.delete("tx_queue")

            last_window = current_window

        await asyncio.sleep(0.5)



async def sync_with_coordinator():
    global GENESIS_BLOCK
    period = GENESIS_BLOCK['config']['window_period_seconds']
    _, POOL_PUBLIC_KEY_HEX = get_keys()
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{COORDINATOR_URL}/get-last-chained-block") as resp:
                    data = await resp.json()
                    if "last-chained-block" in data:
                            last_block = data["last-chained-block"]
                            logger.info(f"[POOL] Último bloque encadenado recibido: {last_block}")

                            # Validación: block_hash presente y no vacío
                            block_hash = last_block.get("block_hash")
                            if not block_hash:
                                logger.warning("[POOL] El bloque recibido no contiene block_hash.")
                            else:
                                # Validar si el reward fue para este Pool
                                tx = last_block.get("transaction", {})
                                target = tx.get("target")
                                reward = tx.get("amount")

                                if target == POOL_PUBLIC_KEY_HEX:
                                    logger.info("[POOL] El reward de bloque fue asignado a este Pool. Generando tareas para distribuir recompensa.")
                                    await generate_reward_tasks_for_workers(reward)
                                else:
                                    logger.info("[POOL] El reward no fue asignado a este Pool.")
                    else:
                        logger.warning(f"[POOL] Estructura inesperada recibida: {data}")
        except Exception as e:
            logger.error(f"[POOL] Error sincronizando con Coordinador: {e}")

        now = time.time()
        next_minute = math.ceil(now / period) * period
        sleep_time = next_minute - now
        logger.info(f"[POOL] Próxima sincronización con Coordinador en {sleep_time:.2f} segundos.")

        await asyncio.sleep(sleep_time)


@app.on_event("startup")
async def startup_event():
    logger.info("Pool Service started")
    try:
        global GENESIS_BLOCK
        await generate_worker_key()

        # Reintenta hasta 10 veces (2s entre cada una) para obtener el bloque génesis
        for attempt in range(10):
            GENESIS_BLOCK = await fetch_genesis_block()
            if GENESIS_BLOCK and 'config' in GENESIS_BLOCK:
                break
            logger.warning(f"[POOL] Intento {attempt+1}/10: génesis no disponible. Reintentando en 2s...")
            await asyncio.sleep(2)

        if not GENESIS_BLOCK or 'config' not in GENESIS_BLOCK:
            logger.critical("[POOL] No se pudo obtener GENESIS_BLOCK con config. Abortando inicio.")
            return

        asyncio.create_task(mining_cycle())
        asyncio.create_task(sync_with_coordinator())

        logger.info("Pool Service started successfully")
    except Exception as e:
        logger.error(f"Error al correr el Pool de TXs: {e}")


    
@app.on_event("shutdown")
def shutdown_event():
    logger.info("Pool Service stopped")


