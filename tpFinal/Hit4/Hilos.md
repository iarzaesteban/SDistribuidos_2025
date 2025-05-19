# TESTEAR HILOS

Este documento explica cómo elegir y ajustar la configuración de hilos por bloque para kernels CUDA, específicamente en una RTX 2060 Super.

---

## 1. Hilos por bloque recomendados

Para una **RTX 2060 Super** (2 176 CUDA‑cores distribuidos en 34 SMs — 64 cores/SM), se recomienda usar **256** hilos por bloque:

* **Múltiplo de 32** (tamaño de warp) para evitar warps parciales.
* Valor típico en el rango **128–512**, que suele maximizar ocupación sin saturar recursos.

```cpp
// Definición en md5.cu (wrapper):
WORD thread = 256;  // hilos por bloque (blockDim.x)
```

---

## 2. Medir y afinar la ocupación

Para aprovechar al máximo los 2 176 cores de la 2060 Super, es ideal usar la API de ocupación de CUDA:

```cpp
#include <iostream>
#include <cuda_runtime.h>

int minGrid, optBlock;
cudaOccupancyMaxPotentialBlockSize(
    &minGrid,
    &optBlock,
    kernel_md5_hash,    // tu kernel
    0,                  // memoria compartida extra
    0                   // deja que calcule el block ideal
);
std::cout
  << "Bloques óptimos: " << minGrid
  << ", Hilos/bloque óptimos: " << optBlock << "\n";

// Luego lanzás el kernel:
kernel_md5_hash<<< minGrid, optBlock >>>(
    cuda_indata,
    inlen,
    cuda_outdata,
    n_batch
);
```

Con esto te aseguras de:

1. **Maximizar la ocupación** de los SMs.
2. **Aprovechar** todos los cores físicos.
3. **Evitar** cuellos de botella por registros o memoria compartida.

---

## 3. Ejemplo de lanzamiento de kernel en md5.cu

```cpp
// Número de hilos por bloque
WORD thread = 256;

// Número de bloques (redondeo hacia arriba)
WORD block = (n_batch + thread - 1) / thread;

// Lanzamiento del kernel
kernel_md5_hash<<< block, thread >>>(
    cuda_indata,
    inlen,
    cuda_outdata,
    n_batch
);
```

> **Nota:** Si cambias `thread` (p. ej. 128, 512, 1024), ajustá `block` para cubrir siempre `n_batch` elementos.

---

Con esta configuración de **256 hilos/bloque** y midiendo la ocupación, tu kernel estará bien preparado para exprimir el poder de tu RTX 2060 Super.

---

> **Nota:** Llamados permitidos entre tipos de variables.

| Punto de llamada       | Llamar `__host__` | Llamar `__device__` | Llamar `__global__` (kernel)                   |
| ---------------------- | ----------------- | ------------------- | ---------------------------------------------- |
| **Desde host (CPU)**   | ✅ Sí              | ❌ No                | ✅ Sí, pero **con** `<<<…>>>`                   |
| **Desde `__global__`** | ❌ No              | ✅ Sí                | ❌ No  (a menos que uses *dynamic parallelism*) |
| **Desde `__device__`** | ❌ No              | ✅ Sí                | ❌ No  (salvo *dynamic parallelism*)            |
