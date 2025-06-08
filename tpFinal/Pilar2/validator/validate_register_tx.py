import json
import os
import aiohttp
import time
import asyncio
import hashlib
import signal
import threading
from typing import List, Dict, Optional
from datetime import datetime
from utils.logger import logger
from utils.rabbitmq_connection import RabbitMQClient
from utils.helper import (
    TransactionStatus,
    Transaction,
    validar_hash,
    IN_PROGRESS_QUEUE,
    REDIS_CLIENT,
    MAX_COINS,
    MAX_MINING_TRYS,
    CHALLENGE
)

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 30))
BLOCKCHAIN_KEY = os.getenv("BLOCKCHAIN_KEY", "blockchain") 

# Flag para terminar de forma limpia
shutdown_event = threading.Event()

rabbit_in_progress = RabbitMQClient(queue_name=IN_PROGRESS_QUEUE)


def select_best_worker(txs_by_worker: Dict[str, List[Transaction]]) -> Optional[str]:
    best_worker = None
    best_count = 0
    best_first_timestamp = None

    for worker_ip, txs in txs_by_worker.items():
        # Filtrar solo transacciones procesadas (las que tienen un hash válido)
        processed_txs = [tx for tx in txs if tx.hash is not None]

        if not processed_txs:
            continue

        # Ordenamos las transacciones procesadas por timestamp
        processed_txs.sort(key=lambda tx: tx.timestamp)

        count = len(processed_txs)
        first_ts = datetime.fromisoformat(processed_txs[0].timestamp)

        if (
            count > best_count or
            (count == best_count and first_ts < best_first_timestamp)
        ):
            best_worker = worker_ip
            best_count = count
            best_first_timestamp = first_ts

    return best_worker


async def reward_worker(winner: str, amount: float):
    try:
        async with aiohttp.ClientSession() as session:
            reward_url = f"http://{winner}:8000/reward"
            response = await session.post(reward_url, json={"amount": amount})
            response_data = await response.json()
            logger.info(f"Recompensa enviada a {winner}: {response_data}")
    except Exception as e:
        logger.error(f"[ERROR] No se pudo enviar la recompensa al worker ganador: {e}")


def get_transaction_queue_by_id(tx_id):
    tx = rabbit_in_progress._get_message_by_txid(tx_id)
    if not tx:
        logger.warning(f"No se encontró tx_id {tx_id} en in_progress")
        return

    return json.loads(tx['body'])


async def handle_transaction(tx: Transaction, is_winner: bool):
    tx_id = tx.tx_id
    key = f"in_progress:{tx.worker_ip}"
    valid = validar_hash(tx)

    if not valid:
        logger.info("EL hash NO es válido")
        transaction = get_transaction_queue_by_id(tx_id)

        if transaction['tries'] >= MAX_MINING_TRYS and len(transaction['challenge']) == len(CHALLENGE):
            logger.info(f"La TX {transaction} tiene MAS de {MAX_MINING_TRYS} intentos, le bajamos la complejidad al desafio")
            # Bajar complejida, seguir sumando el tries y seguir
            transaction['challenge'] = CHALLENGE[:-1]
            transaction['tries'] = 0
            REDIS_CLIENT.hset("monitoring_transactions", transaction['tx_id'], json.dumps(transaction))
            rabbit_in_progress.publish(transaction)
        elif transaction['tries'] >= MAX_MINING_TRYS*2: # ya si se pasa que luego de bajar la complejida, descartarla
            logger.info(f"La TX {transaction} tiene MAS de {MAX_MINING_TRYS*2} intentos, la marcamos como borrada")
            transaction["status"] = TransactionStatus.borrada.value
            REDIS_CLIENT.rpush("dropped_txs", json.dumps(transaction))

            REDIS_CLIENT.hdel("monitoring_transactions", tx_id)
            rabbit_in_progress.delete_message_by_txid(tx_id)
        else:
            transaction['tries'] = transaction.get('tries', 0) + 1
            REDIS_CLIENT.hset("monitoring_transactions", transaction['tx_id'], json.dumps(transaction))
            rabbit_in_progress.publish(transaction)
        return
        
    logger.info("EL hash ES válido")
    if is_winner:
        # Tomo el último bloque de la blockchain
        last_block = REDIS_CLIENT.get("last_block") or "GENESIS"

        # Obtenemos un ID único e incremental para el bloque
        if not REDIS_CLIENT.exists("block_id_counter"):
            REDIS_CLIENT.set("block_id_counter", 0)
        block_id = REDIS_CLIENT.incr("block_id_counter")

        # Preparo el nuevo bloque
        block_data = {
            "block_id": block_id,
            "previous_hash": last_block,
            "nonce": tx.nonce,
            "transaction": tx.to_dict()
        }
        # Obtengo el hash del bloque para encadenar
        block_hash = hashlib.sha1(json.dumps(block_data).encode()).hexdigest()

        # Agregamos nuevo bloque
        REDIS_CLIENT.set(f"block:{block_hash}", json.dumps(block_data))
        REDIS_CLIENT.set("last_block", block_hash)

        # Borramos la transacción porque ya fue precesada
        REDIS_CLIENT.hdel("monitoring_transactions", tx_id)
        rabbit_in_progress.delete_message_by_txid(tx_id)
        REDIS_CLIENT.delete(key)
        
        logger.info(f"Tx {tx_id} validada y agregada al bloque {block_hash}")


async def process_transactions_and_reward(txs_by_worker: Dict[str, List[Transaction]]):
    # Buscamos el worker ganador
    winner = select_best_worker(txs_by_worker)
    logger.info(f"Worker ganador: {winner if winner else 'Ninguno'}")

    # Procesammos todas las transacciones
    for worker_ip, txs in txs_by_worker.items():
        is_winner = (worker_ip == winner)
        for tx in txs:
            await handle_transaction(tx, is_winner)

    # Si hay worker ganador, se le da la recompensa
    if winner:
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