import requests
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np

# Ver como puedo hacer para usar entorno
COORDINADOR_URL = "http://localhost:8989/nct"

def fetch_blockchain():
    print(f"LA URL ES {COORDINADOR_URL}")
    response = requests.get(f"{COORDINADOR_URL}/blockchain")
    if response.status_code != 200:
        raise Exception(f"Error al obtener blockchain: {response.status_code}")
    return response.json().get("Blockchain", [])

def process_data(blockchain):
    data_by_difficulty = defaultdict(list)

    for block in blockchain:
        prefix = block.get("prefix", "")
        mine_time = block.get("mine_time", 0)
        
        # Considerar solo bloques minados válidamente (mine_time > 0)
        if mine_time and prefix is not None:
            difficulty = len(prefix)
            data_by_difficulty[difficulty].append(mine_time)

    return data_by_difficulty

def plot_data(data_by_difficulty):
    difficulties = sorted(data_by_difficulty.keys())
    avg_times = [np.mean(data_by_difficulty[d]) for d in difficulties]

    # Gráfico 1: Dificultad vs Tiempo promedio
    plt.figure(figsize=(10,6))
    plt.plot(difficulties, avg_times, marker='o', linestyle='-', color='b')
    plt.title('Dificultad (Prefijo) vs Tiempo Promedio de Minado')
    plt.xlabel('Dificultad (Longitud de Prefijo)')
    plt.ylabel('Tiempo Promedio de Minado (segundos)')
    plt.grid(True)
    plt.savefig(f'graphics/difficulty_vs_avg_time_{difficulties}_prefix.png')
    plt.show()

    # Gráfico 2: Boxplot de tiempos por dificultad
    plt.figure(figsize=(10,6))
    plt.boxplot([data_by_difficulty[d] for d in difficulties], tick_labels=difficulties)
    plt.title('Distribución de Tiempos de Minado por Dificultad')
    plt.xlabel('Dificultad (Longitud de Prefijo)')
    plt.ylabel('Tiempo de Minado (segundos)')
    plt.grid(True)
    plt.savefig(f'graphics/difficulty_boxplot_{difficulties}_prefix.png')
    plt.show()

if __name__ == "__main__":
    print("Recuperando blockchain del coordinador...")
    blockchain = fetch_blockchain()
    print(f"{len(blockchain)} bloques obtenidos.")
    
    data_by_difficulty = process_data(blockchain)
    
    for difficulty, times in data_by_difficulty.items():
        print(f"Dificultad {difficulty}: {len(times)} bloques, Tiempo Promedio = {np.mean(times):.4f} s")
    
    plot_data(data_by_difficulty)
