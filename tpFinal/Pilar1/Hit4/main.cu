#include <iostream>
#include <cstring>
#include "md5.cuh"

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Uso: " << argv[0] << " \"texto_a_hashear\"" << std::endl;
        return 1;
    }

    const char* input_str = argv[1];
    size_t length = strlen(input_str);

    // El resultado del hash MD5 siempre tiene 16 bytes
    unsigned char hash_output[16];

    // La función espera punteros tipo BYTE (unsigned char*)
    mcm_cuda_md5_hash_batch(
        (BYTE*)input_str,         // entrada
        (WORD)length,             // largo del string
        hash_output,              // salida
        1                         // cantidad de elementos en batch (solo 1 en tu caso)
    );

    // Mostrar resultado en formato hexadecimal
    std::cout << "MD5 Hash: ";
    for (int i = 0; i < 16; ++i) {
        printf("%02x", hash_output[i]);
    }
    std::cout << std::endl;

    return 0;
}
