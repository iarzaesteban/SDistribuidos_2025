
# Análisis de Rendimiento - Filtro Sobel Distribuido

## 🎯 Objetivo

Este informe analiza cómo varía el **tiempo promedio de respuesta** del sistema distribuido que aplica el filtro de Sobel sobre imágenes, evaluando tres factores principales:

- Tamaño de imagen (`size_kb`)
- Concurrencia (`concurrency`)
- Tiempo de respuesta (`elapsed`)

## 📈 Descripción del gráfico

- **Eje X:** Tamaño de la imagen en kilobytes (KB).
- **Eje Y:** Tiempo promedio de respuesta en segundos.
- **Color de líneas:** Nivel de concurrencia (cantidad de peticiones simultáneas).

![plot](benchmark_result_plot.png)


## 🔍 Resultados observados

### 1. Tendencia creciente esperada

- El tiempo de respuesta aumenta con el tamaño de la imagen.
- Esta relación se mantiene consistente en todos los niveles de concurrencia.

### 2. Impacto de la concurrencia

- A mayor concurrencia, los tiempos de respuesta son mayores, especialmente en imágenes grandes.
- Esto indica saturación del sistema cuando se combinan altos niveles de concurrencia con grandes volúmenes de datos.

### 3. Linealidad aparente

- El gráfico utiliza líneas para conectar los **promedios por grupo** (`size_kb`, `concurrency`).
- La variabilidad interna puede analizarse mejor con un gráfico de dispersión.

## ✅ Conclusión

El sistema se comporta eficientemente en escenarios de carga baja a moderada. Sin embargo, comienza a saturarse bajo escenarios de alta concurrencia y tamaños grandes de imagen. Esto refleja un comportamiento típico en sistemas distribuidos no balanceados dinámicamente.

## 📝 Recomendaciones

- Agregar monitoreo del uso de CPU/RAM por pod.
- Explorar técnicas de balanceo dinámico o cola de prioridad.
- Incluir métricas de ensamblado final en backend para analizar cuellos de botella posteriores al procesamiento individual.
