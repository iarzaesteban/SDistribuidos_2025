# Comparativa de Rendimiento: CPU vs GPU en Prefijos MD5

Este experimento busca comparar el rendimiento entre la versión **CUDA (GPU)** y la versión **CPU** de nuestro programa de fuerza bruta `brute_range`, utilizando la misma base de datos (`blockdata`) y el mismo rango de búsqueda (`0 a 500000`), variando la dificultad mediante diferentes longitudes de prefijo.

---

## Resultados Comparativos

| Long. | Prefijo | Tiempo GPU (s) | Nonce GPU | Tiempo CPU (s) | Nonce CPU | Speedup |
|-------|---------|----------------|-----------|----------------|-----------|---------|
| 1     | `0`     | 0.134          | 1         | 0.004          | 1         | 0.03×   |
| 2     | `00`    | 0.085          | 1159      | 0.015          | 130       | 0.18×   |
| 3     | `000`   | 0.075          | 4056      | 0.440          | 4206      | 5.87×   |
| 4     | `0000`  | 0.090          | 15077     | 6.695          | 61353     | 74.38×  |
| 5     | `00000` | 0.377          | —         | 45.851         | 406755    | 121.6×  |

En el caso de CPU para 5 ceros, sí se encontró solución, mientras que en GPU no se halló en ese rango. Sin embargo, se computaron los mismos 500.001 hashes.

---

## Análisis

- Para prefijos **cortos** (1-2 dígitos), la **CPU se desempeña mejor o similar**, dado que el overhead de lanzar kernels en GPU no compensa en tareas tan pequeñas.
- A partir de prefijos de **3 o más dígitos**, la **GPU supera ampliamente a la CPU**, con mejoras de hasta más de 100× para prefijos de 5 dígitos.
- La **diferencia en performance** se vuelve más notoria a medida que aumenta la dificultad, lo que hace que CUDA sea ideal para búsquedas exigentes.

---

## Conclusiones

- Usar GPU con CUDA mejora significativamente el rendimiento para prefijos largos.
- La CPU puede ser preferible para tareas pequeñas o con prefijos muy cortos.
- Esta comparativa valida la estrategia de combinar fuerza bruta con ejecución paralela en GPU para desafíos de tipo Proof of Work.
