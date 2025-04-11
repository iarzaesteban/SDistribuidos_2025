# 🖼️ Filtro de Sobel con Docker

Este proyecto aplica el **filtro de Sobel** a una imagen usando un script en Python dentro de un contenedor Docker. El filtro de Sobel permite detectar bordes resaltando cambios bruscos de intensidad en imágenes en escala de grises.

---

## Pasos

### 1. Construí la imagen de Docker

```bash
docker build -t sobel-filter .
```

Esto crea una imagen llamada `sobel-filter` que contiene todo lo necesario para ejecutar el filtro.

---

### 2. Ejecutá el contenedor

Asegurate de tener una imagen llamada `ejemplo.jpg` dentro de la carpeta `input/`.

```bash
docker run --rm -v "${PWD}/input:/app/input" sobel-filter
```

Este comando:
- Monta la carpeta `input/` en el contenedor.
- Aplica el filtro a la imagen `ejemplo.jpg`.
- Guarda una nueva imagen `ejemplo_sobel.jpg` en la misma carpeta.

---

## 📝 Notas

- El script busca siempre una imagen llamada `ejemplo.jpg` dentro de la carpeta `input/`.
- La imagen debe estar en formato compatible con OpenCV (`.jpg`, `.png`, etc.).
- La imagen generada tiene el sufijo `_sobel`.

---

## 🧪 Ejemplo

Si en `input/` tenés:

```
ejemplo.jpg
```

Después de correr el comando, vas a tener:

```
ejemplo.jpg
ejemplo_sobel.jpg
```

---

## 🔧 Personalización

Si querés cambiar el nombre del archivo de entrada, podés modificar la variable `IMG_NAME` dentro del contenedor, o cambiar el script para tomarlo por argumento (ver documentación del script).


