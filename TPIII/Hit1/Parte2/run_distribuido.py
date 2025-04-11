import os
import cv2
import time
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

INPUT_IMAGE = "input/ejemplo.jpg"
FRAGMENTS_DIR = "fragments"
PROCESSED_DIR = "processed"
OUTPUT_IMAGE = "output/ejemplo_sobel_distribuido.jpg"

os.makedirs(FRAGMENTS_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs("output", exist_ok=True)

def dividir_imagen(path_imagen, n):
    imagen = cv2.imread(path_imagen, cv2.IMREAD_GRAYSCALE)
    if imagen is None:
        raise FileNotFoundError(f"No se pudo abrir la imagen: {path_imagen}")

    alto_total = imagen.shape[0]
    fragmentos = []

    for i in range(n):
        inicio = i * alto_total // n
        fin = (i + 1) * alto_total // n if i != n - 1 else alto_total
        fragmento = imagen[inicio:fin, :]
        path_fragmento = os.path.join(FRAGMENTS_DIR, f"parte_{i}.jpg")
        cv2.imwrite(path_fragmento, fragmento)
        fragmentos.append(path_fragmento)

    return fragmentos

def procesar_fragmento(path_fragmento):
    nombre = os.path.basename(path_fragmento)
    comando = [
        "docker", "run", "--rm",
        "-v", f"{os.path.abspath(FRAGMENTS_DIR)}:/app/input",
        "-v", f"{os.path.abspath(PROCESSED_DIR)}:/app/output",
        "sobel-filter",
        f"input/{nombre}", f"output/{nombre.replace('.jpg', '_sobel.jpg')}"
    ]
    subprocess.run(comando, check=True)

def unir_fragmentos_sobel(n, output_path):
    partes = []
    for i in range(n):
        path = os.path.join(PROCESSED_DIR, f"parte_{i}_sobel.jpg")
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"No se pudo abrir la imagen procesada: {path}")
        partes.append(img)

    resultado = cv2.vconcat(partes)
    cv2.imwrite(output_path, resultado)

def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Uso: python run_distribuido.py <cantidad_nodos>")
        sys.exit(1)

    NUM_NODES = int(sys.argv[1])

    inicio_total = time.perf_counter()

    print(f"📤 Dividiendo imagen en {NUM_NODES} partes...")
    fragmentos = dividir_imagen(INPUT_IMAGE, NUM_NODES)

    print(f"⚙️ Procesando fragmentos con {NUM_NODES} nodos Docker...")
    with ThreadPoolExecutor(max_workers=NUM_NODES) as executor:
        executor.map(procesar_fragmento, fragmentos)

    print("🔗 Uniendo fragmentos procesados...")
    unir_fragmentos_sobel(NUM_NODES, OUTPUT_IMAGE)

    fin_total = time.perf_counter()
    print(f"✅ Imagen final generada: {OUTPUT_IMAGE}")
    print(f"⏱️ Tiempo total: {fin_total - inicio_total:.2f} segundos")

if __name__ == "__main__":
    main()
