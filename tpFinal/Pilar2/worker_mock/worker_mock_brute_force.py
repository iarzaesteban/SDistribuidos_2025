import requests
import time
from typing import List
from .helper import Transaction, COORDINATOR_URL, fetch_transactions, RESOLUTION_INTERVAL

def publish_results(resolved_txs: List[Transaction]):
    try:
        url = f"{COORDINATOR_URL}/publish-results"
        txs_data = [tx.dict() for tx in resolved_txs]
        response = requests.post(url, json={"transactions": txs_data})
        print(f"[INFO] Resultados enviados al coordinador. Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] No se pudo enviar resultados: {e}")

def simulate_worker():
    resolved_transactions = []
    last_publish_time = time.time()

    while True:
        print("Buscando nuevas transacciones...")
        transactions = fetch_transactions()
        tx_index = 0

        while tx_index < len(transactions):
            current_time = time.time()
            elapsed_time = current_time - last_publish_time

            if elapsed_time >= RESOLUTION_INTERVAL:
                # Ya pasó el intervalo, publicamos lo que se haya minado
                if resolved_transactions:
                    print(f"[TIMEOUT] Publicando {len(resolved_transactions)} transacciones resueltas...")
                    publish_results(resolved_transactions)
                    resolved_transactions = []
                last_publish_time = current_time
                break  # salimos del procesamiento y seguimos al siguiente ciclo

            tx = transactions[tx_index]
            try:
                tx.mine()
                resolved_transactions.append(tx)
            except Exception as e:
                print(f"[ERROR] Falló la minería de una transacción: {e}")
            tx_index += 1

        # Publicamos por tiempo si no hay más transacciones
        if time.time() - last_publish_time >= RESOLUTION_INTERVAL:
            if resolved_transactions:
                print(f"[INFO] Publicando transacciones resueltas por timeout sin nuevas transacciones...")
                publish_results(resolved_transactions)
                resolved_transactions = []
            last_publish_time = time.time()

        time.sleep(10)

if __name__ == "__main__":
    print("Worker de minería inicializado", flush=True)
    simulate_worker()
