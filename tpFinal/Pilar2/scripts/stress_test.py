import argparse
import requests
import time
import csv
from nacl import signing
from base64 import b64encode
import random
from datetime import datetime, timedelta
import statistics

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
    ts = (datetime.utcnow() + timedelta(seconds=1)).isoformat() + "+00:00"
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

def run_stress_test(keys_amount, tasks_amount):
    key_pairs = generate_key_pairs(keys_amount)
    tasks = []

    for _ in range(tasks_amount):
        src, tgt = random.sample(key_pairs, 2)
        tasks.append(create_task(src, tgt[1]))

    durations = []
    errors = 0
    start_total = time.time()

    for task in tasks:
        start = time.time()
        try:
            response = requests.post(f"{COORDINADOR_URL}/new-task", json=task)
            end = time.time()
            durations.append(end - start)

            if response.status_code != 200:
                errors += 1
        except Exception as e:
            print(f"Error al enviar tarea: {e}")
            errors += 1
            durations.append(0)

    end_total = time.time()

    total_time = end_total - start_total
    avg_time = sum(durations) / len(durations)
    stddev_time = statistics.stdev(durations) if len(durations) > 1 else 0
    tps = tasks_amount / total_time
    error_percentage = (errors / tasks_amount) * 100

    print(f"\n{tasks_amount} tareas enviadas.")
    print(f"Duración total: {total_time:.2f} segundos")
    print(f"TPS promedio: {tps:.2f}")
    print(f"Latencia promedio: {avg_time:.4f} segundos")
    print(f"Desviación estándar de latencia: {stddev_time:.4f}")
    print(f"Errores: {errors} ({error_percentage:.2f}%)")

    return {
        "tasks_amount": tasks_amount,
        "total_time_seconds": total_time,
        "tps_avg": tps,
        "latency_avg": avg_time,
        "latency_stddev": stddev_time,
        "errors_count": errors,
        "error_percentage": error_percentage
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stress Test Blockchain Coordinator")
    parser.add_argument("--keys", type=int, required=True, help="Cantidad de pares de claves")
    parser.add_argument("--tasks", type=int, required=True, help="Cantidad de tareas a crear")
    parser.add_argument("--output", type=str, default="stress_test_results.csv", help="Archivo CSV de salida")
    args = parser.parse_args()

    result = run_stress_test(args.keys, args.tasks)

    # Escribir o agregar al CSV
    header = ["tasks_amount", "total_time_seconds", "tps_avg", "latency_avg", "latency_stddev", "errors_count", "error_percentage"]

    try:
        with open(args.output, "x", newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
    except FileExistsError:
        pass  # Si existe, no hace falta volver a escribir header

    with open(args.output, "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writerow(result)

    print(f"\nResultados guardados en {args.output}")
