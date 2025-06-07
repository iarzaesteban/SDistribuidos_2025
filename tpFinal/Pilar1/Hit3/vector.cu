#include <iostream>
#include <thrust/host_vector.h>
#include <thrust/device_vector.h>
#include <thrust/generate.h>
#include <thrust/sort.h>
#include <thrust/copy.h>
#include <thrust/random.h>
#include <cuda_runtime.h>

void checkCudaError(cudaError_t err, const char* msg) {
    if (err != cudaSuccess) {
        std::cerr << "Error CUDA en " << msg << ": " << cudaGetErrorString(err) << std::endl;
        exit(EXIT_FAILURE);
    }
}

int main() {
    thrust::default_random_engine rng(1337);
    thrust::uniform_int_distribution<int> dist;
    thrust::host_vector<int> h_vec(32 << 20);
    thrust::generate(h_vec.begin(), h_vec.end(), [&] { return dist(rng); });

    thrust::device_vector<int> d_vec;
    try {
        d_vec = h_vec;
    } catch (thrust::system_error &e) {
        std::cerr << "Error al copiar a dispositivo: " << e.what() << std::endl;
        return EXIT_FAILURE;
    }

    try {
        thrust::sort(d_vec.begin(), d_vec.end());
    } catch (thrust::system_error &e) {
        std::cerr << "Error al ordenar en dispositivo: " << e.what() << std::endl;
        return EXIT_FAILURE;
    }

    thrust::copy(d_vec.begin(), d_vec.end(), h_vec.begin());

    // Check CUDA errors
    checkCudaError(cudaDeviceSynchronize(), "sincronización final");

    std::cout << "Primeros 10 valores ordenados:" << std::endl;
    for (int i = 0; i < 10; ++i) {
        std::cout << h_vec[i] << " ";
    }
    std::cout << std::endl;

    return 0;
}
