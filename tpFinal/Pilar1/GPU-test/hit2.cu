#include <stdio.h>
#include <cuda_runtime.h>

// Kernel sencillo
__global__ void holaDesdeCUDA() {
    printf("Hola desde hilo %d del bloque %d\n", threadIdx.x, blockIdx.x);
}

int main() {
    // Mostrar información del dispositivo GPU
    cudaDeviceProp prop;
    int device;
    cudaGetDevice(&device);
    cudaGetDeviceProperties(&prop, device);

    printf("=== Información de la GPU ===\n");
    printf("Nombre: %s\n", prop.name);
    printf("Máximo número de hilos por bloque: %d\n", prop.maxThreadsPerBlock);
    printf("Cantidad máxima de bloques en cada dimensión: x=%d, y=%d, z=%d\n",
           prop.maxGridSize[0], prop.maxGridSize[1], prop.maxGridSize[2]);
    printf("Cantidad máxima de hilos por bloque en cada dimensión: x=%d, y=%d, z=%d\n",
           prop.maxThreadsDim[0], prop.maxThreadsDim[1], prop.maxThreadsDim[2]);
    printf("Memoria compartida por bloque: %zu bytes\n", prop.sharedMemPerBlock);
    printf("Número de multiprocesadores: %d\n", prop.multiProcessorCount);
    printf("=============================\n");

    // Lanzar el kernel con múltiples bloques e hilos
    holaDesdeCUDA<<<2, 4>>>();  // 2 bloques, 4 hilos por bloque

    // Sincronizar antes de salir
    cudaDeviceSynchronize();

    return 0;
}
