
# 🔑 CUDA MD5 Hashing

Este proyecto implementa el cálculo del hash MD5 utilizando la capacidad de procesamiento paralelo de las GPUs NVIDIA mediante CUDA. La solución permite calcular eficientemente el hash MD5 para un texto proporcionado desde la línea de comandos.

---

## 🚀 ¿Qué hace este programa?

- **Entrada:** recibe una cadena de texto como parámetro desde la consola.
- **Salida:** devuelve el hash MD5 calculado utilizando GPU CUDA.

---

## 🛠️ ¿Cómo funciona?

La solución está basada en una librería especializada que implementa el algoritmo MD5 usando CUDA. El proceso es:

1. Recibir el texto a través de argumentos del programa.
2. Utilizar la GPU (CUDA kernels) para calcular eficientemente el hash MD5.
3. Retornar el resultado (hash MD5) como cadena hexadecimal en consola.

---

## 🗂️ Estructura del proyecto

```
📂 Hit4
│
├── main.cu (programa principal, maneja entrada y salida)
├── md5.cu (implementación CUDA del algoritmo MD5)
├── config.h (Type Definitions)
└── md5.cuh (cabecera con declaración del algoritmo MD5)

```

---

## ⚙️ ¿Cómo compilar?

Para compilar el proyecto necesite inicializar correctamente el entorno de compilación de Visual Studio 2019 en modo `x64`. Ejecute primero:

```bash
"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"
```

Luego compile con `nvcc` así:

```bash
nvcc -arch=sm_75 main.cu md5.cu -o md5_hasher.exe
```

- `sm_75` corresponde a la arquitectura compatible con GPUs RTX (en este caso, probado con RTX 2060 Super).

---

## ▶️ ¿Cómo ejecutarlo?

Una vez compilado, ejecutá así:

```bash
.\md5_hasher.exe "Texto a hashear"
```

Ejemplo de ejecución:

```bash
.\md5_hasher.exe "Hola Mundo CUDA"
```

Esto producirá una salida como:

```
MD5 Hash: 27a61cb914e5587df2a8c96e8ae0da40
```

---

## ⚠️ Problemas encontrados (y soluciones)

Durante el desarrollo surgieron algunos inconvenientes específicos:

- **Error al inicializar Visual Studio y CUDA:**  
  Fue necesario usar explícitamente el script de inicialización del entorno:
  ```bash
  "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"
  ```

- **Error `unresolved external symbol` (Linker):**  
  Solucionado agregando `extern "C"` en el header `md5.cuh` para garantizar compatibilidad con linkage:
  ```cpp
  extern "C" {
      void mcm_cuda_md5_hash_batch(BYTE* in, WORD inlen, BYTE* out, WORD n_batch);
  }
  ```

Esto aseguró compatibilidad correcta entre CUDA y el linker de Visual Studio.

---