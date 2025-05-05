
# Hit #7 - HASH por fuerza bruta con CUDA (con limites)

Este programa busca un numero (nonce) dentro de un rango dado que, al concatenarse con una cadena base y calcular el hash MD5 en la GPU, produzca un hash que empiece con un prefijo especifico.

## Ejecucion y resultados

Se corrio el siguiente comando:

```
brute_range.exe "MI_TEXTO_BASE" "0000" 0 1000000
```

Salida obtenida:

```
[OK] Solucion encontrada
Nonce: 313108
Hash:  00002a3858a770c0799fbfc990085a11
Tiempo total: 146.101 segundos
```

- **Cadena base:** `MI_TEXTO_BASE`  
- **Prefijo MD5 buscado:** `0000`  
- **Rango de nonces:** [0, 1000000]  
- **Nonce encontrado:** 313108  
- **Hash resultante:** 00002a3858a770c0799fbfc990085a11  
- **Tiempo total de busqueda:** 146.101 segundos  

## Como compilar

1. Abrir Developer Command Prompt x64 de Visual Studio 2019:
   ```
   "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"
   ```
2. Compilar:
   ```
   nvcc -arch=sm_75 main.cu md5.cu -o brute_range.exe
   ```

## Como ejecutar

```
.\brute_range.exe "MI_TEXTO_BASE" "0000" 0 1000000
```

El programa recorre secuencialmente cada nonce dentro del rango y mide el tiempo total de busqueda.

