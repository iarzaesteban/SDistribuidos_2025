#include <stdio.h>

__global__ void helloFromGPU() {
    printf("¡Hola desde el GPU!\n");
}

int main() {
    printf("Hola desde el CPU\n");

    // Llamada al kernel con 1 bloque y 1 hilo
    helloFromGPU<<<1, 1>>>();

    // Esperar a que el GPU termine antes de salir
    cudaDeviceSynchronize();

    return 0;
}
