
import os
import cv2
import time
import subprocess
import sys
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_IMAGE = "input/ejemplo.jpg"
FRAGMENTS_DIR = "fragments"
PROCESSED_DIR = "processed"
OUTPUT_IMAGE = "output/ejemplo_sobel_distribuido.jpg"

def limpiar_directorios():
    for folder in [FRAGMENTS_DIR, PROCESSED_DIR, "output"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)

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

def procesar_fragmento_con_reintentos(path_fragmento, max_reintentos=3):
    nombre = os.path.basename(path_fragmento)
    comando = [
        "docker", "run", "--rm",
        "-v", f"{os.path.abspath(FRAGMENTS_DIR)}:/app/input",
        "-v", f"{os.path.abspath(PROCESSED_DIR)}:/app/output",
        "sobel-filter",
        f"input/{nombre}", f"output/{nombre.replace('.jpg', '_sobel.jpg')}"
    ]

    for intento in range(1, max_reintentos + 1):
        try:
            print(f"🚀 Procesando {nombre} (intento {intento})")
            subprocess.run(comando, check=True)
            return
        except subprocess.CalledProcessError:
            print(f"❌ Falló el procesamiento de {nombre} (intento {intento})")
        except Exception as e:
            print(f"💥 Error inesperado en {nombre}: {e}")

    raise RuntimeError(f"🔥 No se pudo procesar {nombre} después de {max_reintentos} intentos")

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

    limpiar_directorios()

    inicio_total = time.perf_counter()

    print(f"📤 Dividiendo imagen en {NUM_NODES} partes...")
    fragmentos = dividir_imagen(INPUT_IMAGE, NUM_NODES)

    print(f"⚙️ Procesando fragmentos con {NUM_NODES} nodos Docker (con reintentos)...")
    errores = []

    with ThreadPoolExecutor(max_workers=NUM_NODES) as executor:
        future_map = {executor.submit(procesar_fragmento_con_reintentos, f): f for f in fragmentos}
        for future in as_completed(future_map):
            try:
                future.result()
            except Exception as e:
                errores.append(str(e))

    if errores:
        print("\n❌ Procesamiento incompleto. Errores:")
        for e in errores:
            print(f"   - {e}")
        print("⛔ Abortando unión de fragmentos.")
        sys.exit(1)

    print("🔗 Uniendo fragmentos procesados...")
    unir_fragmentos_sobel(NUM_NODES, OUTPUT_IMAGE)

    fin_total = time.perf_counter()
    print(f"✅ Imagen final generada: {OUTPUT_IMAGE}")
    print(f"⏱️ Tiempo total: {fin_total - inicio_total:.2f} segundos")

if __name__ == "__main__":
    main()
