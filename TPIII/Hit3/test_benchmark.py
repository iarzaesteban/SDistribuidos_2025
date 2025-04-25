import os
import time
import requests
import concurrent.futures
import pandas as pd
from pathlib import Path

# Configuraciones
test_server_url = "http://34.44.27.113/upload"  # Cambiar si tu IP es otra
image_sizes_kb = [1024, 10240]  # 1MB, 10MB
concurrency_levels = [1, 5, 10]
test_image_dir = "test_images"
timeout_sec = 120

# Crear imágenes de prueba si no existen
os.makedirs(test_image_dir, exist_ok=True)
for size_kb in image_sizes_kb:
    path = Path(test_image_dir) / f"{size_kb}KB.jpg"
    if not path.exists():
        with open(path, "wb") as f:
            f.write(os.urandom(size_kb * 1024))

# Enviar una imagen y registrar tiempo
def send_image(image_path):
    with open(image_path, "rb") as img:
        start = time.perf_counter()
        try:
            res = requests.post(test_server_url, files={"image": img}, timeout=timeout_sec)
            elapsed = time.perf_counter() - start
            return {
                "status": res.status_code,
                "elapsed": elapsed,
                "size_kb": os.path.getsize(image_path) / 1024
            }
        except Exception as e:
            return {
                "status": "error",
                "elapsed": -1,
                "size_kb": os.path.getsize(image_path) / 1024,
                "error": str(e)
            }

# Ejecutar batería de pruebas
results = []
for size_kb in image_sizes_kb:
    image_path = Path(test_image_dir) / f"{size_kb}KB.jpg"
    for concurrency in concurrency_levels:
        print(f"🧪 Probando {size_kb}KB con concurrencia {concurrency}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(send_image, image_path) for _ in range(concurrency)]
            for f in concurrent.futures.as_completed(futures):
                result = f.result()
                result["concurrency"] = concurrency
                results.append(result)

# Guardar resultados
df = pd.DataFrame(results)
df.to_csv("benchmark_results.csv", index=False)
print("✅ Resultados guardados en benchmark_results.csv")
