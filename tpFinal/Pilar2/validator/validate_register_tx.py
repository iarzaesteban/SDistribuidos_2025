import json
import os
import time
import asyncio
import signal
import threading
from typing import List, Dict
from utils.logger import logger
from utils.rabbitmq_connection import RabbitMQClient
from utils.helper import (wait_for_genesis_block,
                          select_best_worker,
                          reward_worker,
                          seconds_until_next_period,
                          create_reward_block,
                          TransactionStatus,
                          Transaction,
                          validar_hash,
                          IN_PROGRESS_QUEUE,
                          REDIS_CLIENT,
                          MAX_COINS,
                          MAX_MINING_TRYS,
                          CHALLENGE)

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 30))
BLOCKCHAIN_KEY = os.getenv("BLOCKCHAIN_KEY", "blockchain") 

# Flag para terminar de forma limpia
shutdown_event = threading.Event()

rabbit_in_progress = RabbitMQClient(queue_name=IN_PROGRESS_QUEUE)

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
        # Obtenemos un ID único e incremental para el bloque
        if not REDIS_CLIENT.exists("block_id_counter"):
            REDIS_CLIENT.set("block_id_counter", 0)
        block_id = REDIS_CLIENT.incr("block_id_counter")
        # Preparamos el nuevo bloque
        block_data = {
            "block_id": block_id,
            "previous_hash": tx.hash_previo,
            "nonce": tx.nonce,
            "miner": tx.worker_ip, # o poner el la pub del source
            "prefix": tx.challenge,
            "transaction": tx.to_dict()
        }

        # Agregamos nuevo bloque
        REDIS_CLIENT.set(f"block:{tx.hash}", json.dumps(block_data))
        REDIS_CLIENT.set("last_block", tx.hash)

        # Borramos la transacción porque ya fue precesada
        REDIS_CLIENT.hdel("monitoring_transactions", tx_id)
        rabbit_in_progress.delete_message_by_txid(tx_id)
        REDIS_CLIENT.delete(key)
        
        logger.info(f"Tx {tx_id} validada y agregada al bloque {tx.hash}")


async def process_transactions_and_reward(txs_by_worker: Dict[str, List[Transaction]]):
    winner = select_best_worker(txs_by_worker)
    logger.info(f"Worker ganador: {winner if winner else 'Ninguno'}")

    for worker_ip, txs in txs_by_worker.items():
        is_winner = (worker_ip == winner)
        for tx in txs:
            await handle_transaction(tx, is_winner)

    if winner:
        reward_amount = round(MAX_COINS * 0.001, 4)
        reward_block = create_reward_block(winner, reward_amount)
        await reward_worker(winner, round(MAX_COINS * 0.001, 4))
        
        if reward_block:
            REDIS_CLIENT.set(f"block:{reward_block['block_hash']}", json.dumps(reward_block))
            REDIS_CLIENT.set("last_block", reward_block['block_hash'])
            REDIS_CLIENT.incr("block_id_counter")  # opcional si usas contador también

            logger.info(f"[REWARD] Bloque de recompensa agregado para {winner} con {reward_amount} coins.")


async def monitor_pending_transactions(genesis_config):
    while not shutdown_event.is_set():
        try:
            wait_time = seconds_until_next_period(genesis_config)
            logger.info(f"Esperando {wait_time} segundos hasta el próximo inicio de período...")
            await asyncio.sleep(wait_time)

            logger.info("Inicio de período alcanzado. Validando transacciones...")

            raw_txs = REDIS_CLIENT.lrange("pending_transactions", 0, -1)
            if not raw_txs:
                logger.info("No hay transacciones pendientes.")
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
    genesis_block = wait_for_genesis_block(timeout=None)
    genesis_config = genesis_block.get("config", {})

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitor_pending_transactions(genesis_config))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    validator_thread = threading.Thread(target=start_validator_loop)
    validator_thread.start()

    while not shutdown_event.is_set():
        time.sleep(1)

    logger.info("Proceso de validador finalizado correctamente.")