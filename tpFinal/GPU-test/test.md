```
=== Información de la GPU ===
Nombre: NVIDIA GeForce RTX 2060 SUPER
Máximo número de hilos por bloque: 1024
Cantidad máxima de bloques en cada dimensión: x=2147483647, y=65535, z=65535
Cantidad máxima de hilos por bloque en cada dimensión: x=1024, y=1024, z=64
Memoria compartida por bloque: 49152 bytes
Número de multiprocesadores: 34
=============================
Hola desde hilo 0 del bloque 0
Hola desde hilo 1 del bloque 0
Hola desde hilo 2 del bloque 0
Hola desde hilo 3 del bloque 0
Hola desde hilo 0 del bloque 1
Hola desde hilo 1 del bloque 1
Hola desde hilo 2 del bloque 1
Hola desde hilo 3 del bloque 1
```

> **Nota:** Llamados permitidos entre tipos de variables.

| Punto de llamada       | Llamar `__host__` | Llamar `__device__` | Llamar `__global__` (kernel)                   |
| ---------------------- | ----------------- | ------------------- | ---------------------------------------------- |
| **Desde host (CPU)**   | ✅ Sí              | ❌ No                | ✅ Sí, pero **con** `<<<…>>>`                   |
| **Desde `__global__`** | ❌ No              | ✅ Sí                | ❌ No  (a menos que uses *dynamic parallelism*) |
| **Desde `__device__`** | ❌ No              | ✅ Sí                | ❌ No  (salvo *dynamic parallelism*)            |
