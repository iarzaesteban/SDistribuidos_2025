
# 🕵️ Brute-force MD5 en GPU con CUDA

Este programa toma una **cadena base** y un **prefijo hexadecimal** y arranca una búsqueda intensiva (brute-force) en la GPU para encontrar un número (nonce) que, al concatenarse con la cadena, produzca un hash MD5 que comience con ese prefijo.

---

## ✨ ¿Qué pasó cuando lo corrimos?

1. Arrancamos el ejecutable con:
   ```
   .\brute_md5.exe "MI_TEXTO_BASE" "0000"
   ```
2. El programa inicializó un **batch** de 1024 posibles nonces generados aleatoriamente.
3. Cada lote se envió a la GPU, donde el kernel `mcm_cuda_md5_hash_batch` calculó en paralelo los 1024 MD5.
4. De regreso en la CPU, el código revisó cada hash en formato hexadecimal para ver si empezaba con `"0000"`.
5. Al cabo de unas pocas iteraciones (dependiendo del prefijo y la suerte), encontró el **nonce 23312**:
   ```
   Nonce: 23312
   Hash:  0000af08541c9b05925ffb697d3049e5
   ```

Gracias a la capacidad paralela de la RTX 2060 Super, el programa prueba miles de combinaciones por segundo y logra romper el prefijo establecido en pocos segundos.

---

## 🚀 Cómo se ejecuta (narrado)

Cuando ejecutás:
```bat
.\brute_md5.exe "MI_TEXTO_BASE" "0000"
```
el sistema imprime en pantalla:
```
Buscando MD5(base+nonce) que empiece con "0000"...
[OK] Encontrado!
Nonce: 23312
Hash:  0000af08541c9b05925ffb697d3049e5
```
— así te muestra el número mágico (**nonce**) y su hash resultante

---