# 🔁 Tolerancia a fallos en procesamiento distribuido - Filtro de Sobel

Este proyecto implementa una mejora al procesamiento distribuido del filtro de Sobel para detectar **fallos simulados** en los nodos (workers) y **reintentar automáticamente** hasta completar la tarea.

---

## ⚙️ ¿Cómo funciona?

El script `run_distribuido.py` divide una imagen en partes y lanza **un contenedor Docker por fragmento**. Si alguno de estos contenedores falla (por ejemplo, por un error simulado), el orquestador detecta la falla y vuelve a intentarlo.

- Cada fragmento tiene hasta **3 intentos** para ser procesado exitosamente.
- Si algún fragmento **falla todos los intentos**, la ejecución se detiene.
- Si todos los fragmentos se procesan correctamente, se genera una imagen final unificada.

---

## 🧪 Simulación de fallos

El script `sobel_filter.py` incluye una simulación intencional de caída de worker:

```python
if "parte_1" in path_imagen and random.random() < 0.5:
    raise RuntimeError("💥 Simulación de caída del worker (parte_1)")
```

Esto significa que **cada vez que se procese `parte_1.jpg` hay un 50% de probabilidad de que falle**.

---

## 🚀 Ejecución

### 1. Build de la imagen (si no lo hiciste ya):

```bash
docker build -t sobel-filter .
```

### 2. Correr el orquestador:

```bash
python run_distribuido.py 5
```

Este comando divide la imagen `input/ejemplo.jpg` en 5 partes, lanza 5 procesos Docker, reintenta si alguno falla y, si todo sale bien, genera:

```
output/ejemplo_sobel_distribuido.jpg
```

---

