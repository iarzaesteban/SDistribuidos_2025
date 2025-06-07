import json
import os
import aiohttp
import time
import asyncio
import hashlib
import signal
import random
import threading
from typing import List, Dict
from utils.logger import logger
from utils.rabbitmq_connection import RabbitMQClient
from utils.helper import (
    IN_PROGRESS_QUEUE,
    REDIS_CLIENT,
    validar_hash,
    Transaction,
    MAX_COINS,
    MAX_MINING_TRYS
)

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 30))
BLOCKCHAIN_KEY = os.getenv("BLOCKCHAIN_KEY", "blockchain") 

# Flag para terminar de forma limpia
shutdown_event = threading.Event()

rabbit_in_progress = RabbitMQClient(queue_name=IN_PROGRESS_QUEUE)


def select_best_worker(txs_by_worker: Dict[str, List[Transaction]]) -> str:
    sorted_workers = sorted(txs_by_worker.items(), key=lambda item: (-len(item[1]), item[1][0].timestamp))
    return sorted_workers[0][0] if sorted_workers else None


async def reward_worker(winner: str, amount: float):
    try:
        async with aiohttp.ClientSession() as session:
            reward_url = f"http://{winner}:8000/reward"
            response = await session.post(reward_url, json={"amount": amount})
            response_data = await response.json()
            logger.info(f"Recompensa enviada a {winner}: {response_data}")
    except Exception as e:
        logger.error(f"[ERROR] No se pudo enviar la recompensa al worker ganador: {e}")



async def handle_transaction(tx: Transaction, is_winner: bool):
    tx_id = tx.tx_id
    key = f"in_progress:{tx.worker_ip}"
    valid = validar_hash(tx)

    if not valid:
        logger.info("EL hash NOOO es válido")
        
        if tx.tries >= MAX_MINING_TRYS:
            REDIS_CLIENT.hdel("monitoring_transactions", tx_id)
            rabbit_in_progress.delete_message_by_txid(tx_id)
            logger.info("Tiene MAS de 3 intentos")
        else:
            logger.info("Tiene MENOS de 3 intentos")
            tx.tries = tx.tries + 1
            rabbit_in_progress.publish(tx.dict())
            REDIS_CLIENT.hset("monitoring_transactions", tx_id, json.dumps(tx.dict()))
        return
    logger.info("EL hash ES válido")
    if is_winner:
        # Tomo el último bloque de la blockchain
        last_block = REDIS_CLIENT.get("last_block") or "GENESIS"
        # Preparo el nuevo bloque
        block_data = {
            "previous_hash": last_block,
            "transaction": tx.to_dict()
        }
        # Obtengo el hash del bloque para encadenar
        block_hash = hashlib.sha1(json.dumps(block_data).encode()).hexdigest()
        logger.info(f"block_hash -----> {block_hash}")

        # Agregamos nuevo bloque
        REDIS_CLIENT.set(f"block:{block_hash}", json.dumps(block_data))
        REDIS_CLIENT.set("last_block", block_hash)

        # Borramos la transacción porque ya fue precesada
        REDIS_CLIENT.hdel("monitoring_transactions", tx_id)
        rabbit_in_progress.delete_message_by_txid(tx_id)
        REDIS_CLIENT.delete(key)
        
        logger.info(f"Tx {tx_id} validada y agregada al bloque {block_hash}")


async def process_transactions_and_reward(txs_by_worker: Dict[str, List[Transaction]]):
    winner = select_best_worker(txs_by_worker)
    logger.info(f"EL GANADOR ES {winner}")
    if not winner:
        logger.info("No hay workers disponibles para seleccionar como ganador.")
        return

    logger.info(f"Worker ganador: {winner}")

    for worker_ip, txs in txs_by_worker.items():
        is_winner = (worker_ip == winner)
        for tx in txs:
            await handle_transaction(tx, is_winner)

    await reward_worker(winner, round(MAX_COINS * 0.001, 4))


async def monitor_pending_transactions():
    while not shutdown_event.is_set():
        try:
            # Obtenemos todas las TXs de la lista enviadas por cada workers
            raw_txs = REDIS_CLIENT.lrange("pending_transactions", 0, -1)
            if not raw_txs:
                await asyncio.sleep(POLL_INTERVAL)
                continue

            REDIS_CLIENT.delete("pending_transactions")
            txs_by_worker: Dict[str, List[Transaction]] = {}

            for raw in raw_txs:
                try:
                    tx_data = json.loads(raw)
                    tx = Transaction(**tx_data)
                    txs_by_worker.setdefault(tx.worker_ip, []).append(tx)
                except Exception as ex:
                    logger.warning(f"Transacción mal formada: {ex}")

            await process_transactions_and_reward(txs_by_worker)

        except Exception as e:
            logger.error(f"[ERROR] Procesando transacciones pendientes: {e}")
        await asyncio.sleep(1)


def handle_shutdown(signum, frame):
    logger.warning(f"Señal {signum} recibida. Cerrando servicio...")
    shutdown_event.set()


def start_validator_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitor_pending_transactions())


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    validator_thread = threading.Thread(target=start_validator_loop)
    validator_thread.start()

    while not shutdown_event.is_set():
        time.sleep(1)

    logger.info("Proceso de validador finalizado correctamente.")