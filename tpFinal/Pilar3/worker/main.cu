// main.cu - Hit #7 con medición de tiempo
#include <iostream>
#include <string>
#include <cstring>
#include <cstdlib>
#include <cstdio>
#include <chrono>
#include "md5.cuh"

#define NONCE_DIGITS 10
#define MAX_INPUT    256

static std::string to_hex(const unsigned char* d) {
    static const char* hex = "0123456789abcdef";
    std::string s; s.reserve(32);
    for (int i = 0; i < 16; ++i) {
        s.push_back(hex[(d[i] >> 4) & 0xF]);
        s.push_back(hex[d[i] & 0xF]);
    }
    return s;
}

int main(int argc, char* argv[]) {
    if (argc != 5) {
        std::cout << "Uso: " << argv[0]
                  << " BASE PREFIJO RANGO_INI RANGO_FIN\n"
                  << "Ejemplo: brute_range.exe hola 0000 0 1000000\n";
        return 1;
    }

    const char* base      = argv[1];
    std::string prefix    = argv[2];
    uint32_t start        = static_cast<uint32_t>(std::stoul(argv[3]));
    uint32_t end          = static_cast<uint32_t>(std::stoul(argv[4]));
    size_t base_len       = std::strlen(base);

    if (start > end) {
        std::cout << "[ERROR] rango invalido\n";
        return 1;
    }
    if (base_len + NONCE_DIGITS >= MAX_INPUT) {
        std::cout << "[ERROR] base demasiado larga\n";
        return 1;
    }

    char input[MAX_INPUT];
    unsigned char output[16];
    bool found = false;
    uint32_t sol_nonce = 0;
    std::string sol_hash;

    // Inicio medicion
    auto t0 = std::chrono::high_resolution_clock::now();

    for (uint32_t n = start; n <= end; ++n) {
        int len = std::sprintf(input, "%s%0*u", base, NONCE_DIGITS, n);
        mcm_cuda_md5_hash_batch(
            reinterpret_cast<BYTE*>(input),
            static_cast<WORD>(len),
            output,
            1
        );
        std::string h = to_hex(output);
        if (h.rfind(prefix, 0) == 0) {
            found = true;
            sol_nonce = n;
            sol_hash  = h;
            break;
        }
    }

    // Fin medicion
    auto t1 = std::chrono::high_resolution_clock::now();
    double secs = std::chrono::duration<double>(t1 - t0).count();

    if (found) {
        std::cout << "[OK] Solucion encontrada\n"
                  << "Nonce: " << sol_nonce << "\n"
                  << "Hash:  " << sol_hash << "\n";
    } else {
        std::cout << "[ERROR] no se encontro en rango ["
                  << start << "," << end << "]\n";
    }

    std::cout << "Tiempo total: " << secs << " segundos\n";
    return 0;
}
