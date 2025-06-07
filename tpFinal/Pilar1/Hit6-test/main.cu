// main_measure_all.cu
#include <iostream>
#include <string>
#include <cstring>
#include <cstdlib>
#include <ctime>
#include <chrono>
#include <cstdio>
#include <utility>
#include "md5.cuh"

#define BATCH_SIZE    1024
#define NONCE_DIGITS  10
#define MAX_INPUT     256

// Convierte 16 bytes MD5 a string hex de 32 caracteres
std::string to_hex(const unsigned char* d) {
    static const char* hex = "0123456789abcdef";
    std::string s; s.reserve(32);
    for(int i = 0; i < 16; ++i) {
        s.push_back(hex[(d[i] >> 4) & 0xF]);
        s.push_back(hex[d[i] & 0xF]);
    }
    return s;
}

// Bruteforce para un único prefijo:
// devuelve {nonce, hash_hex, total_hashes, tiempo(segundos)}
struct Result {
    uint32_t nonce;
    std::string hash;
    uint64_t total_hashes;
    double time_s;
};

Result find_for_prefix(const char* base, size_t base_len, const std::string& prefix) {
    // Buffers en host
    char*  h_in  = new char[BATCH_SIZE * MAX_INPUT]();
    BYTE*  h_out = new BYTE[BATCH_SIZE * 16]();
    bool found = false;
    uint32_t found_nonce = 0;
    std::string found_hash;
    uint64_t total_hashes = 0;

    // Iniciar medición de tiempo
    auto t0 = std::chrono::high_resolution_clock::now();

    while (!found) {
        // Generar batch de nonces aleatorios
        for (int i = 0; i < BATCH_SIZE; ++i) {
            uint32_t nonce = rand();
            sprintf(
                h_in + i * MAX_INPUT,
                "%s%0*u",
                base,
                NONCE_DIGITS,
                nonce
            );
        }
        // Calcular MD5 en GPU
        mcm_cuda_md5_hash_batch(
            (BYTE*)h_in,
            static_cast<WORD>(base_len + NONCE_DIGITS),
            h_out,
            static_cast<WORD>(BATCH_SIZE)
        );
        total_hashes += BATCH_SIZE;
        // Revisar resultados
        for (int i = 0; i < BATCH_SIZE; ++i) {
            BYTE* digest = h_out + i*16;
            std::string hex = to_hex(digest);
            if (hex.rfind(prefix, 0) == 0) {
                found = true;
                found_hash = hex;
                const char* s = h_in + i*MAX_INPUT + base_len;
                found_nonce = static_cast<uint32_t>(strtoul(s, nullptr, 10));
                break;
            }
        }
    }

    auto t1 = std::chrono::high_resolution_clock::now();
    double time_s = std::chrono::duration<double>(t1 - t0).count();

    delete[] h_in;
    delete[] h_out;
    return {found_nonce, found_hash, total_hashes, time_s};
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Uso: " << argv[0]
                  << " \"CADENA_BASE\" MAX_PREFIJO\n"
                  << "Ejemplo: measure_all.exe \"hola\" 4\n";
        return 1;
    }
    const char* base = argv[1];
    int max_len = std::atoi(argv[2]);
    size_t base_len = strlen(base);
    if (base_len + NONCE_DIGITS >= MAX_INPUT) {
        std::cerr << "Error: cadena base muy larga.\n";
        return 1;
    }
    srand((unsigned)time(NULL));

    std::cout << "Midiendo para prefijos de longitud 1 a " << max_len << "...\n";
    std::cout << "L  Prefijo  Tiempo(s)  Hashes/s         Nonce    Hash\n";
    std::cout << "---------------------------------------------------------------\n";

    for (int L = 1; L <= max_len; ++L) {
        std::string prefix(L, '0');
        Result r = find_for_prefix(base, base_len, prefix);
        double rate = r.total_hashes / r.time_s;
        printf("%-2d %-7s  %8.3f  %12llu  %8u  %s\n",
               L,
               prefix.c_str(),
               r.time_s,
               (unsigned long long)r.total_hashes / r.time_s,
               r.nonce,
               r.hash.c_str()
        );
    }
    return 0;
}
