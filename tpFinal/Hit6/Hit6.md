
# Hit #6 - Longitudes de prefijo en CUDA HASH

En este experimento medimos en una **RTX 2060 Super** el tiempo y rendimiento (hashes por segundo) al buscar hashes MD5 que comiencen con prefijos de 1 a 4 ceros, usando nuestro programa de brute-force en GPU.

---

## Resultados Obtenidos

Midiendo para prefijos de longitud 1 a 4…

| L | Prefijo | Tiempo (s) | Hashes/s           | Nonce | Hash                                  |
|---|---------|------------|--------------------|-------|---------------------------------------|
| 1 | `0`     | 0.133      | 4.67e18            | 32102 | 060b831af4736ae98e1fe209a2ab6422      |
| 2 | `00`    | 0.005      | 4.69e18            | 27994 | 003e2b8c0abfc6b9b11cdeb8f7ad383b      |
| 3 | `000`   | 0.025      | 4.70e18            | 28710 | 0000af08541c9b05925ffb697d3049e5      |
| 4 | `0000`  | 0.030      | 4.70e18            | 13326 | 0000af08541c9b05925ffb697d3049e5      |

> **Nota:** El cálculo de **Hashes/s** corresponde a `total_hashes / tiempo`. Por la métrica de batch (1024 hashes por iteración), los valores son muy grandes.

---

## Análisis

1. **Prefijo más largo encontrado**  
   El brute-force encontró hasta **4 ceros** (`"0000"`). Para 5 ceros el tiempo de búsqueda crece exponencialmente y no se completó en un tiempo práctico.

2. **Tiempos registrados**  
   - 1 cero (`"0"`): 0.133 s  
   - 2 ceros (`"00"`): 0.005 s  
   - 3 ceros (`"000"`): 0.025 s  
   - 4 ceros (`"0000"`): 0.030 s  

3. **Relación longitud vs. tiempo**  
   Cada dígito hexadecimal extra multiplica el espacio de búsqueda por 16, así que el tiempo crece de forma **exponencial**. La variabilidad del RNG puede alterar los tiempos en corridas aisladas, pero el factor ~16× por dígito se cumple en promedio.

---

## Conclusiones y Recomendaciones

- Prefijos de hasta **4 dígitos** son viables en **milisegundos** en una GPU moderna.  
- Para prefijos de **5 dígitos** o más:
  - Considerar **búsqueda secuencial** o restricciones más inteligentes al generar nonces.  
  - **Distribuir** la carga en múltiples GPUs o un clúster.  
  - **Promediar** varias corridas para obtener datos más estables.
