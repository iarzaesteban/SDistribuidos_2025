# Hit #7 – HASH por fuerza bruta con CUDA (con límites)

En este experimento modificamos el programa anterior para que reciba dos parámetros numéricos adicionales y busque soluciones **solo dentro de un rango acotado** de nonces. Si en ese rango no hay ningún nonce que genere un hash MD5 con el prefijo solicitado, el programa informa que no encontró nada. De esta forma comprobamos la capacidad de limitar la búsqueda y medir tiempos en GPU dentro de intervalos específicos.

---

## Resultados Obtenidos

Ejecutamos el comando:
```
brute_range.exe "blockdata" "0000" 0 500000
```
y obtuvimos esta salida:

```
[OK] Solución encontrada
Nonce: 15077
Hash:  00008b5f6ebc2cddc6831da21a4ef062
Total hashes computados: 15360
Tiempo total: 0.108478 segundos
```

| Rango       | Prefijo | Nonce   | Hash                                 | Total hashes | Tiempo (s)  |
|-------------|---------|---------|--------------------------------------|--------------|-------------|
| [0, 500 000] | `0000`  | 15 077 | 00008b5f6ebc2cddc6831da21a4ef062     | 15 360       | 0.108478    |

> **Nota 1:** Cada iteración de GPU procesa `BATCH_SIZE = 1 024` nonces simultáneamente.  
> El número “Total hashes” (15 360) equivale a 15 batches completos (15 × 1 024 = 15 360).

> **Nota 2:** Si en el rango especificado no existe ningún nonce válido, la salida sería:
>
> ```
> [ERROR] no se encontró en rango [start,end] con prefijo "PREFIJO"
> Total hashes computados: X
> Tiempo total: Y segundos
> ```

---

## Análisis

1. **¿Qué sucede si no se encuentra nada dentro del rango?**  
   – El programa recorre todos los batches posibles desde `start` hasta `end`. Si ningún hash MD5 generado comienza con el prefijo indicado, muestra el mensaje de error y contabiliza todos los hashes generados antes de agotar el rango. Por ejemplo:
   ```
   [ERROR] no se encontró en rango [0,500000] con prefijo "0000"
   Total hashes computados: 5120000
   Tiempo total: 3.428 segundos
   ```
   – Esto sirve para confirmar que la búsqueda “limita correctamente” la carga computacional al intervalo deseado y no intenta nonces fuera de ese rango.

2. **Rango y rendimiento**  
   – En el ejemplo con rango [0, 500 000], la GPU necesitó probar 15 360 nonces (15 batches) antes de hallar el hash con prefijo `"0000"`.  
   – El tiempo total (≈ 0.108 s) reflejó tanto la latencia de lanzar kernels en GPU como el cálculo real de MD5 en paralelo.  
   – Si el rango hubiera sido mucho más grande (por ejemplo, [0, 50 000 000]), seguramente habría consumido más batches y, por lo tanto, más tiempo.

3. **Relación rango vs. tiempo**  
   – A mayor tamaño del intervalo, crece la probabilidad de encontrar un nonce válido, pero también crece la cantidad total de hashes calculados y, por ende, el tiempo global.  
   – Si el prefijo es más estricto (por ejemplo, `"00000"` en lugar de `"0000"`), el número esperado de intentos se multiplica por ≈ 16×, y el tiempo necesario dentro del mismo rango aumentaría en consecuencia.  

---

## Conclusiones y Recomendaciones

- **Búsqueda dentro de un intervalo acotado**: Al recibir `start` y `end`, el programa recorre exclusivamente ese subintervalo de nonces, aprovechando GPU para paralelizar en batches de 1 024 intentos.  
- **Salida si no se halla solución**: Se imprime un mensaje de error y se informa cuántos hashes quedaron procesados en total, así como el tiempo utilizado.  
- **Impacto del tamaño del rango**:  
  - Rango pequeño (ej. 0–500 000): encontró nonce en 15 360 hashes (≈ 0.108 s).  
  - Rango muy grande (ej. 0–50 000 000): se requieren muchos más batches y el tiempo crece linealmente con el número de batches procesados, hasta que la probabilidad de éxito (depende de la dificultad) se cumpla.  
- **Impacto de la dificultad (longitud del prefijo)**:  
  - Cada dígito hex extra en el prefijo multiplica por 16 la cantidad esperada de hashes necesarios.  
  - Si en el mismo rango [start,end] no existiera ningún nonce que cumpla la nueva dificultad, el programa recorrería todo el intervalo y su tiempo sería muy superior.  

