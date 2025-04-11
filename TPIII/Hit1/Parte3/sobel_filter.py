import cv2
import os
import sys
import random

def aplicar_filtro_sobel(path_imagen, path_salida=None):
    # Simulación de falla aleatoria para testing
    if "parte_1" in path_imagen and random.random() < 0.5:
        raise RuntimeError("💥 Simulación de caída del worker (parte_1)")

    imagen = cv2.imread(path_imagen, cv2.IMREAD_GRAYSCALE)
    if imagen is None:
        raise ValueError(f"No se pudo abrir la imagen: {path_imagen}")

    sobelx = cv2.Sobel(imagen, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(imagen, cv2.CV_64F, 0, 1, ksize=3)
    sobel_comb = cv2.magnitude(sobelx, sobely)
    resultado = cv2.convertScaleAbs(sobel_comb)

    if not path_salida:
        nombre_archivo = os.path.basename(path_imagen)
        nombre_salida = os.path.splitext(nombre_archivo)[0] + "_sobel.jpg"
        path_salida = os.path.join(os.path.dirname(path_imagen), nombre_salida)

    cv2.imwrite(path_salida, resultado)
    print(f"✅ Imagen filtrada guardada en: {path_salida}")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        aplicar_filtro_sobel(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 1:
        aplicar_filtro_sobel("/app/input/ejemplo.jpg")
    else:
        print("Uso: python sobel_filter.py [input_path output_path]")
        sys.exit(1)