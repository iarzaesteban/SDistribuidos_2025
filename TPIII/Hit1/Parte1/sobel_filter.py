import cv2
import sys
import os


def aplicar_filtro_sobel(path_imagen):
    # Leer la imagen en escala de grises
    imagen = cv2.imread(path_imagen, cv2.IMREAD_GRAYSCALE)
    if imagen is None:
        raise ValueError(f"No se pudo abrir la imagen: {path_imagen}")

    # Aplicar el filtro de Sobel en X e Y
    sobelx = cv2.Sobel(imagen, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(imagen, cv2.CV_64F, 0, 1, ksize=3)

    # Calcular la magnitud del gradiente
    sobel_comb = cv2.magnitude(sobelx, sobely)

    # Normalizar la imagen resultante a 8 bits
    resultado = cv2.convertScaleAbs(sobel_comb)

    # Guardar la imagen con sufijo _sobel
    nombre_archivo = os.path.basename(path_imagen)
    nombre_salida = os.path.splitext(nombre_archivo)[0] + "_sobel.jpg"
    path_salida = os.path.join(os.path.dirname(path_imagen), nombre_salida)

    cv2.imwrite(path_salida, resultado)
    print(f"Imagen filtrada guardada en: {path_salida}")

if __name__ == "__main__":
    path_default = "/app/input/ejemplo.jpg"  # ruta fija
    aplicar_filtro_sobel(path_default)
