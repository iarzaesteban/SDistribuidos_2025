// main.cu
#include <iostream>
#include <string>
#include <cstring>
#include <cstdlib>   // strtoul
#include <ctime>
#include <cstdio>    // sprintf
#include "md5.cuh"

#define BATCH_SIZE        1024      // candidatos por batch
#define NONCE_DIGITS      10        // dígitos fijos para el nonce
#define MAX_INPUT_LEN     256       // largo máximo (base + nonce)

std::string to_hex(const unsigned char* d) {
    static const char* hex = "0123456789abcdef";
    std::string s; s.reserve(32);
    for(int i = 0; i < 16; ++i) {
        s.push_back(hex[(d[i] >> 4) & 0xF]);
        s.push_back(hex[d[i] & 0xF]);
    }
    return s;
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Uso: " << argv[0]
                  << " \"CADENA_BASE\" \"PREFIJO_HEX\"\n"
                  << "Ejemplo: brute_md5.exe \"hola\" \"0000\"\n";
        return 1;
    }

    const char* base   = argv[1];
    const char* target = argv[2];
    size_t base_len    = strlen(base);
    if (base_len + NONCE_DIGITS >= MAX_INPUT_LEN) {
        std::cerr << "Error: cadena base muy larga.\n";
        return 1;
    }

    // buffers en host
    char*  h_in  = new char[BATCH_SIZE * MAX_INPUT_LEN]();
    BYTE*  h_out = new BYTE[BATCH_SIZE * 16]();

    srand((unsigned)time(NULL));
    bool found = false;
    uint32_t resultado_nonce = 0;
    std::string resultado_hash;

    std::cout << "Buscando MD5(base+nonce) que empiece con \"" << target << "\"...\n";
    while (!found) {
        // 1) Generar batch de NONCES y armar inputs
        for (int i = 0; i < BATCH_SIZE; ++i) {
            uint32_t nonce = rand();
            sprintf(
                h_in + i * MAX_INPUT_LEN,
                "%s%0*u",
                base,
                NONCE_DIGITS,
                nonce
            );
        }
        // 2) Ejecutar MD5 en GPU
        mcm_cuda_md5_hash_batch(
            (BYTE*)h_in,
            static_cast<WORD>(base_len + NONCE_DIGITS),
            h_out,
            static_cast<WORD>(BATCH_SIZE)
        );
        // 3) Revisar resultados
        for (int i = 0; i < BATCH_SIZE; ++i) {
            BYTE* digest = h_out + (i * 16);
            std::string hex = to_hex(digest);
            if (hex.rfind(target, 0) == 0) {
                found = true;
                resultado_hash  = hex;
                // parsear nonce con strtoul
                const char* s = h_in + i * MAX_INPUT_LEN + base_len;
                resultado_nonce = static_cast<uint32_t>(strtoul(s, nullptr, 10));
                break;
            }
        }
    }

    // 4) Mostrar resultado
    std::cout << "[OK] Encontrado!\n"
              << "Nonce: " << resultado_nonce << "\n"
              << "Hash:  " << resultado_hash << "\n";

    delete[] h_in;
    delete[] h_out;
    return 0;
}
