# TESTEAR HILOS

Este documento explica cómo elegir y ajustar la configuración de hilos por bloque para kernels CUDA, específicamente en una RTX 2060 Super.

---
## 1. Medir y afinar la ocupación

Para aprovechar al máximo los 2176 cores de la 2060 Super, es ideal usar la API de ocupación de CUDA:

```cpp
#include <iostream>
#include <cuda_runtime.h>

int minGrid, optBlock;
cudaOccupancyMaxPotentialBlockSize(
    &minGrid,
    &optBlock,
    kernel_md5_hash,    // kernel
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
