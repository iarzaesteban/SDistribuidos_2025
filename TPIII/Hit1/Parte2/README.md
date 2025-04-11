# 🧩 Filtro de Sobel Distribuido con Docker

Este proyecto implementa una versión **distribuida** del filtro de Sobel, donde una imagen se divide en partes y se procesan en paralelo usando contenedores Docker.

---

## 🚀 Instrucciones de uso

### 1. Construí la imagen de Docker

Primero tenés que construir la imagen base `sobel-filter` que contiene el código para aplicar el filtro de Sobel a una imagen.

```bash
docker build -t sobel-filter .
```

---

### 2. Ejecutá el procesamiento distribuido

Usá el siguiente comando para ejecutar el script principal `run_distribuido.py`, pasando como argumento la cantidad de nodos (partes) que querés usar.

```bash
python run_distribuido.py 4
```

📌 Podés cambiar el `4` por la cantidad de nodos que quieras (por ejemplo: 2, 8, etc.).

---

## 🧠 ¿Qué hace este proceso?

1. Divide la imagen `input/ejemplo.jpg` en N fragmentos horizontales.
2. Ejecuta N contenedores Docker (uno por fragmento) que aplican el filtro de Sobel.
3. Une todos los fragmentos procesados en una sola imagen final.

---

## 📝 Notas

- La imagen procesada se guarda como `output/ejemplo_sobel_distribuido.jpg`.
- A mayor cantidad de nodos, mayor paralelismo (aunque depende también del tamaño de la imagen).
