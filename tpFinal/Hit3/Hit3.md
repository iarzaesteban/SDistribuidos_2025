
# Informe sobre NVIDIA/cccl (CUDA Core Compute Libraries)

El repositorio **NVIDIA/cccl** en GitHub es básicamente una caja de herramientas para desarrolladores que laburan con CUDA en C++. Es decir, es un conjunto de librerías que te facilita escribir código eficiente y seguro para correr en GPUs de NVIDIA.

Lo interesante es que este repo junta tres librerías que antes vivían por separado:

✅ **Thrust** → Es como el “STL paralelo” de CUDA. Tiene algoritmos paralelos de alto nivel que te permiten laburar en GPU o CPU sin romperte mucho la cabeza.

✅ **CUB** → Es más bajo nivel, pensado para sacarle el jugo a CUDA al máximo. Tiene algoritmos tipo reducción, escaneo, etc., para kernels personalizados.

✅ **libcudacxx** → Es la implementación de la Standard Library de C++ adaptada a CUDA. Trae cosas como atomics, control de caché, sincronización, etc., para el código que corre en GPU.

El objetivo de juntar todo en este repo es simplificarle la vida a los devs: tiene todo lo esencial para CUDA C++ en un solo lugar, con una versión unificada, menos problemas de compatibilidad y más facilidad para mantenerse al día.

## ¿Cuándo se actualizó por última vez?

El repo está muy activo todo el tiempo, tiene más de **11.000 commits**, **188 branches** y **35 tags** . Eso habla de una comunidad activa y un equipo de desarrollo detrás que no para.

## Otros detalles

- Es **header-only** → no tenés que andar compilando librerías aparte, solo incluir los headers y listo.
- Es compatible con **CMake** y tiene paquetes para **Conda**, así que integrarlo a proyectos existentes es bastante sencillo.
- Lo podés usar con CUDA Toolkit, pero si querés lo más nuevo, podés tirar directamente del repo en GitHub.
- Tiene ejemplos de uso, como una reducción paralela usando Thrust, CUB y libcudacxx, para que puedas comparar qué onda cada uno.

# Informe sobre Thrust (The C++ Parallel Algorithms Library)

**Thrust** es una librería C++ de algoritmos paralelos que jugó un rol clave en la llegada de algoritmos paralelos al estándar de C++. Básicamente, te permite escribir código paralelo para GPUs y CPUs de forma sencilla y portable, usando interfaces de alto nivel al estilo STL (Standard Template Library).

Con Thrust, podés aprovechar la potencia de CUDA, TBB (Threading Building Blocks) y OpenMP sin tener que lidiar con los detalles bajos como manejo de memoria y sincronización. Esto mejora la productividad del programador, porque te podés concentrar en el algoritmo en vez de pelearte con la infraestructura.

## Características principales

- Interfaces similares a STL con plantillas (templated) para algoritmos paralelos.
- Funciona sobre GPUs (CUDA) y CPUs multicore (TBB, OpenMP).
- Viene incluido en el CUDA Toolkit y en el NVIDIA HPC SDK, así que si ya tenés alguno de esos, no necesitás instalar nada extra.
- Es open source, disponible en GitHub.

## Rendimiento

Thrust permite aceleraciones considerables frente a CPU multicore: por ejemplo, el algoritmo `thrust::sort` puede ser entre 5x y 100x más rápido que el STL o TBB.

## Estado actual

Desde marzo de 2024, Thrust forma parte de CUDA Core Compute Libraries (CCCL), así que toda la gestión de versiones, issues y mejoras ahora pasa por ese repositorio unificado.

# Informe de Ejecución - Thrust Example (CUDA)

## Consigna

Compile y ejecute el primer ejemplo que se le presenta en  
https://docs.nvidia.com/cuda/thrust/index.html#vectors

## Resumen del proceso

El objetivo era compilar y ejecutar este código de ejemplo usando `nvcc`:

```cpp
#include <thrust/host_vector.h>
#include <thrust/device_vector.h>
#include <thrust/generate.h>
#include <thrust/sort.h>
#include <thrust/copy.h>
#include <thrust/random.h>

int main() {
    thrust::default_random_engine rng(1337);
    thrust::uniform_int_distribution<int> dist;
    thrust::host_vector<int> h_vec(32 << 20);
    thrust::generate(h_vec.begin(), h_vec.end(), [&] { return dist(rng); });

    thrust::device_vector<int> d_vec = h_vec;
    thrust::sort(d_vec.begin(), d_vec.end());
    thrust::copy(d_vec.begin(), d_vec.end(), h_vec.begin());
}
```

---

## ¿Qué es Thrust y para qué sirve?

El programa de ejemplo no es un simple `printf("Hola GPU")` como en el clásico "Hola Mundo",  
sino que utiliza **Thrust**, una biblioteca de plantillas C++ incluida en CUDA Toolkit.

### ✅ ¿Qué es Thrust?

Thrust es una biblioteca de algoritmos paralelos en C++ que proporciona:
- Vectores en CPU (`thrust::host_vector`) y GPU (`thrust::device_vector`),
- Algoritmos paralelos como `sort`, `reduce`, `transform`, `generate`,
- Una interfaz de alto nivel similar a la STL de C++,
- Optimización automática en CUDA para GPUs.

### ✅ ¿Por qué lo necesitaste para este ejemplo?

Este programa usa:
- `thrust::host_vector` → para almacenar datos en el host (CPU),
- `thrust::device_vector` → para operar en el dispositivo (GPU),
- `thrust::generate`, `thrust::sort`, `thrust::copy` → para generar, ordenar y copiar datos.

A diferencia de un kernel `__global__` simple como en “Hola Mundo”,  
este ejemplo requiere:
- Tener **Thrust disponible** (viene con CUDA Toolkit),
- Que el compilador entienda las plantillas C++ usadas en Thrust,
- Que la GPU soporte las arquitecturas CUDA necesarias.

### ✅ ¿Qué es lo nuevo respecto a Hola Mundo?

- Usa librerías C++ avanzadas (`<thrust/*>`),
- Necesita un compilador C++ que soporte plantillas modernas,
- Hace operaciones reales en GPU (no solo imprime texto),
- Depende de compatibilidad entre Toolkit, GPU y compilador.

## Problemas encontrados y soluciones

### ✅ Instalación de CUDA Toolkit

- Tenía instalado **CUDA 11.8 Toolkit** → incluye Thrust, no se requiere instalación adicional.
- Sin embargo, **no es suficiente solo CUDA Toolkit**:  
  Se necesita un compilador compatible (Visual Studio + cl.exe) en Windows.

---

### ⚠ Problema 1: `nvcc fatal : Cannot find compiler 'cl.exe' in PATH`

- Falta agregar Visual Studio C++ Build Tools al PATH.
- Solución:
    - Usar **Visual Studio Developer Command Prompt 2019**.
    - O pasar `--compiler-bindir` explícito:
      ```bash
      nvcc vector.cu -o vector.exe --compiler-bindir "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.29.30133\bin\Hostx64\x64"
      ```

---

### ⚠ Problema 2: `unsupported Microsoft Visual Studio version`

- CUDA 11.8 no soporta Visual Studio 2022.
- Solución:
    - Instalar **Visual Studio 2019 Community Edition**.
    - Usar el Developer Command Prompt de 2019.

---

### ⚠ Problema 3: `cudaErrorNoKernelImageForDevice`

- El ejecutable compilaba, pero al correr daba:
  ```
  Error al ordenar en dispositivo: radix_sort: failed on 1st step: cudaErrorNoKernelImageForDevice
  ```
- Causa:
    - Mi GPU **GeForce 940MX** tiene arquitectura `sm_50` (Maxwell),  
      no compatible por defecto con binarios de CUDA 11.8.
- Solución:
    - Compilar agregando el flag:
      ```bash
      nvcc vector.cu -o vector.exe --compiler-bindir "..." -arch=sm_50
      ```
    - Alternativa: instalar **CUDA Toolkit 11.4 o 10.2**.

---

## Conclusión

- **¿Necesité instalar algo adicional?**  
  ➥ Sí:
  - Visual Studio 2019 (compatible con CUDA 11.8)
  - Compilar con `-arch=sm_50` para soportar mi GPU (940MX).

- **¿Thrust viene con CUDA?**  
  ➥ Sí, viene incluido. Pero dependencias externas (compilador, arquitectura GPU) pueden romper la compilación/ejecución.

---

## Resumen de consideraciones

- Verificar con `nvidia-smi` la arquitectura y versión CUDA.
- Revisar compatibilidad entre CUDA Toolkit, Visual Studio y GPU.
- Probar con versiones anteriores de CUDA si aparecen errores de ejecución.

---

# 💥 Sobre Thrust y por qué se necesita

**Thrust** es una biblioteca de C++ para CUDA que funciona como una especie de “STL paralelo”, es decir, trae contenedores (como `host_vector`, `device_vector`) y algoritmos (como `sort`, `reduce`, `transform`) ya preparados para correr en la GPU, sin que tengamos que escribir kernels CUDA manualmente.

Cuando programás **CUDA “a pelo”**, vos te encargás de todo:
- Escribís tus kernels (`__global__` o `__device__`)
- Organizás los bloques e hilos
- Hacés manualmente las copias de memoria entre host y device (`cudaMemcpy`)
- Manejás el layout de memoria y optimizás acceso
- Controlás sincronizaciones y errores

Con **Thrust** eso cambia:
- Usás containers como `device_vector` o `host_vector` en lugar de manejar punteros y `cudaMalloc`.
- Llamás a algoritmos de alto nivel (`thrust::sort`, `thrust::reduce`, `thrust::transform`) que ya hacen todo el trabajo paralelo internamente.
- Ahorrás mucho código repetitivo.

### ✅ ¿Qué es lo nuevo que se necesita para correr este programa?
Necesitás tener disponible Thrust, que viene incluído en el CUDA Toolkit a partir de CUDA 4.0 (en mi caso CUDA 11.8 ya lo trae).  
No hay que instalar nada adicional, pero sí compilar con `nvcc` y asegurarte de que la GPU soporte los kernels que usa Thrust (a nosotros nos tiro `cudaErrorNoKernelImageForDevice` porque la GPU no es compatible).

### 🔑 Resumen de diferencia clave
- **CUDA “a pelo” →** Máximo control, máxima responsabilidad.
- **Thrust →** Menos código, más abstracto, menos optimizable a mano, ideal para prototipos o problemas conocidos (sorting, scan, reduce, etc).
