import sys
import cv2
import os

def aplicar_sobel(path_entrada, path_salida):
    print(f"[WORKER] - Aplicando Sobel sobre {path_entrada}")
    imagen = cv2.imread(path_entrada, cv2.IMREAD_GRAYSCALE)
    if imagen is None:
        print(f"[WORKER] - No se pudo leer la imagen de entrada: {path_entrada}")
        return
    sobelx = cv2.Sobel(imagen, cv2.CV_64F, 1, 0, ksize=5)
    sobely = cv2.Sobel(imagen, cv2.CV_64F, 0, 1, ksize=5)
    resultado = cv2.magnitude(sobelx, sobely)
    cv2.imwrite(path_salida, resultado)
    print(f"[WORKER] - Resultado guardado en {path_salida}")
    os.remove(path_entrada)

if __name__ == '__main__':
    entrada = sys.argv[1]
    salida = sys.argv[2]
    aplicar_sobel(entrada, salida)
