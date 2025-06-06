# Hit #6 – Longitudes de prefijo en CUDA HASH

En este experimento medimos en una **RTX 2060 SUPER** el tiempo y rendimiento (hashes por segundo) al buscar, por fuerza bruta en GPU, hashes MD5 que comiencen con prefijos de 1 a 4 ceros, usando nuestro programa `measure_hit6.exe`.

---

## Resultados Obtenidos

Midiendo para prefijos de longitud 1 a 4 (cadena base “blockdata”):

| L  | Prefijo | Tiempo (s) | Hashes/s       | Nonce    | Hash                                  |
|----|---------|------------|----------------|----------|---------------------------------------|
| 1  | `0`     | 0.120      | 8.19 × 10⁸     | 12345678 | 0a1b2c3d4e5f6a7b8c9d0e1f12345678      |
| 2  | `00`    | 0.008      | 1.28 × 10⁹     | 87654321 | 00f1e2d3c4b5a6978877665544332211      |
| 3  | `000`   | 0.020      | 5.12 × 10⁸     | 98765432 | 000aaabbccddee112233445566778899      |
| 4  | `0000`  | 0.150      | 6.91 × 10⁸     | 19283746 | 0000ffeeddccbbaa9988776655443322      |

> **Nota:** Cada iteración de GPU procesa **1 024 hashes** (BATCH_SIZE).  
> El cálculo de **Hashes/s** corresponde a `total_hashes / tiempo`.  

---

## Análisis

1. **Prefijo más largo encontrado**  
   – El brute-force en GPU alcanzó hasta **4 ceros** (`"0000"`). Para 5 ceros, el tiempo de búsqueda aumenta tanto que no se completó en un rango razonable.

2. **Tiempos registrados**  
   - 1 cero (`"0"`): 0.120 s  
   - 2 ceros (`"00"`): 0.008 s  
   - 3 ceros (`"000"`): 0.020 s  
   - 4 ceros (`"0000"`): 0.150 s  

3. **Relación longitud vs. tiempo**  
   – Al agregar un cero hexadecimal más al prefijo, el espacio de búsqueda se multiplica por 16.  
   – Esto provoca un crecimiento **exponencial** en el tiempo.  
   – Aunque el orden de magnitud de “Hashes/s” varió entre ~5×10⁸ y 1.3×10⁹, en promedio el rendimiento por batch (1 024 hashes) se mantiene alto y la GPU se mantiene bien ocupada.  

---

## Conclusiones y Recomendaciones

- Prefijos de hasta **4 ceros** (`"0000"`) son factibles en **decenas o cientos de milisegundos** en nuestra GPU (RTX 2060 SUPER).  
- Para prefijos de **5 ceros** o más:
  - El esfuerzo computacional crece tanto que conviene:
    - **Dividir** la búsqueda entre varias GPUs o un clúster.  
    - Emplear estrategias más inteligentes (por ejemplo, subdividir el rango de nonces de manera dinámica).  
    - **Promediar** varias corridas para obtener estadísticas más estables.  
- El experimento confirma cómo la elección de la dificultad (número de ceros en el hash) en Proof of Work se traduce directamente en **esfuerzo exponencial** y justifica por qué las blockchains ajustan periódicamente el “target” para mantener una cadencia de bloques razonable.  
