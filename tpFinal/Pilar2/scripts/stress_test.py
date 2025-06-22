import argparse
import requests
import time
from nacl import signing
from base64 import b64encode
import random
from datetime import datetime

# Ver como puedo hacer para usar entorno
COORDINADOR_URL = "http://localhost:8989/nct"
DESCRIPTION = "Transacción desde StressTask Python"

def generate_key_pairs(n):
    pairs = []
    for _ in range(n):
        priv = signing.SigningKey.generate()
        pub = priv.verify_key
        pairs.append((priv, pub.encode().hex()))
    return pairs

def create_task(source_pair, target_pubkey):
    amount = round(random.uniform(1, 100), 1)
    ts = datetime.utcnow().isoformat() + "+00:00"
    message = f"{source_pair[1]}{target_pubkey}{amount}{DESCRIPTION}{ts}"
    message_bytes = message.encode('utf-8')
    signature = source_pair[0].sign(message_bytes).signature
    signature_b64 = b64encode(signature).decode('utf-8')

    return {
        "source": source_pair[1],
        "target": target_pubkey,
        "amount": amount,
        "description": DESCRIPTION,
        "timestamp": ts,
        "sign": signature_b64
    }

def main(keys_amount, tasks_amount):
    key_pairs = generate_key_pairs(keys_amount)
    tasks = []

    for _ in range(tasks_amount):
        src, tgt = random.sample(key_pairs, 2)
        tasks.append(create_task(src, tgt[1]))

    durations = []

    for task in tasks:
        start = time.time()
        response = requests.post(f"{COORDINADOR_URL}/new-task", json=task)
        end = time.time()
        durations.append(end - start)
        print(f"Status {response.status_code}, Time: {end - start:.4f}s")

    avg_time = sum(durations) / len(durations)
    print(f"\n{len(tasks)} tareas enviadas.")
    print(f"Tiempo promedio por tarea: {avg_time:.4f} segundos")

if __name__ == "__main__":
    print("Iniciando el script")
    parser = argparse.ArgumentParser(description="Stress Test Blockchain Coordinator")
    parser.add_argument("--keys", type=int, required=True, help="Cantidad de pares de claves")
    parser.add_argument("--tasks", type=int, required=True, help="Cantidad de tareas a crear")
    args = parser.parse_args()

    main(args.keys, args.tasks)
