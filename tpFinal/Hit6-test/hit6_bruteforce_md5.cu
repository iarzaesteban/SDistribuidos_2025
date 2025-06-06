// ----------------------------------------------------
// hit6_bruteforce_md5.cu
//
// Hit #6 – Longitudes de prefijo en CUDA HASH
//
// Lee estos archivos (md5.cuh, md5.cu y config.h) que ya tienes en la carpeta.
// Mide para cada prefijo de longitud L (por ejemplo, "0", "00", "000", ...) 
// cuánto tarda la GPU en hallar, por fuerza bruta, un nonce que cumpla con ese prefijo.
// ----------------------------------------------------

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <chrono>
#include <iostream>

#include "config.h"
#include "md5.cuh"

// Número de nonces que procesamos en cada "batch" paralelo en GPU
#define BATCH_SIZE    1024      
// Cantidad fija de dígitos decimales que reservamos para el nonce al concatenar
#define NONCE_DIGITS  10        
// Tamaño máximo (bytes) de la concatenación [texto_base || nonce]
// (config.h debe definir MAX_INPUT >= base_len + NONCE_DIGITS)
#ifndef MAX_INPUT
  #define MAX_INPUT 256
#endif

struct Result {
    uint32_t nonce;        // Nonce encontrado
    std::string hash_hex;  // Hash MD5 en hexadecimal (32 chars)
    uint64_t total_hashes; // Cantidad total de hashes computados
    double   time_s;       // Tiempo que tardó (en segundos)
};

// Convierte 16 bytes de digest MD5 a string hexadecimal (32 chars)
static std::string to_hex(const BYTE* digest) {
    const char hex_digits[] = "0123456789abcdef";
    char buf[33];
    for (int i = 0; i < 16; i++) {
        buf[2 * i]     = hex_digits[ (digest[i] >> 4) & 0xF ];
        buf[2 * i + 1] = hex_digits[ digest[i] & 0xF ];
    }
    buf[32] = '\0';
    return std::string(buf);
}

// ----------------------------------------------------
// find_for_prefix()
//   • Recibe:
//       - base: puntero a la cadena base (por ej. "blockdata")
//       - base_len: longitud de esa cadena
//       - prefix: prefijo MD5 a buscar (por ej. "0000")
//   • Devuelve un Result con:
//       - nonce encontrado (o 0xFFFFFFFF si no lo encontró en el rango dado)
//       - el hash MD5 en hex que cumplió el prefijo
//       - total_hashes (cantidad total de MD5 calculados)
//       - tiempo en segundos que tardó
// ----------------------------------------------------
static Result find_for_prefix(const char* base, size_t base_len, const std::string& prefix) {
    // Buffer en host para “batch” de entradas: 
    // cada entrada ocupa MAX_INPUT bytes, y hay BATCH_SIZE entradas por batch.
    char*     h_in  = new char[BATCH_SIZE * MAX_INPUT]();
    BYTE*     h_out = new BYTE[BATCH_SIZE * 16]();  // Cada MD5 es 16 bytes

    bool    found = false;
    uint32_t found_nonce = 0;
    std::string found_hash;
    uint64_t total_hashes = 0;

    // Medir tiempo CPU al comenzar la búsqueda
    auto t0 = std::chrono::high_resolution_clock::now();

    // Mientras no encontremos el prefijo, generamos batches aleatorios
    while (!found) {
        // Generar BATCH_SIZE valores de nonce aleatorios y empacarlos en h_in
        for (int i = 0; i < BATCH_SIZE; ++i) {
            uint32_t nonce = rand();  // número aleatorio de 0 a RAND_MAX
            // Escribimos en h_in + i*MAX_INPUT la cadena: base + nonce con padding 
            sprintf(
                h_in + i * MAX_INPUT,
                "%s%0*u",
                base,
                NONCE_DIGITS,
                nonce
            );
        }

        // Llamamos a la función CUDA que calcula MD5 para todo el batch en paralelo:
        //  • h_in  tiene BATCH_SIZE cadenas (cada MAX_INPUT bytes)
        //  • h_out tendrá BATCH_SIZE resultados MD5 (cada uno 16 bytes)
        mcm_cuda_md5_hash_batch(
            reinterpret_cast<BYTE*>(h_in),
            static_cast<WORD>(base_len + NONCE_DIGITS), 
            h_out,
            static_cast<WORD>(BATCH_SIZE)
        );

        total_hashes += BATCH_SIZE;

        // Revisamos en el host cada hash MD5 calculado para ver si coincide con el prefijo
        for (int i = 0; i < BATCH_SIZE; ++i) {
            BYTE* digest = h_out + i * 16;
            std::string hexstr = to_hex(digest);
            if (hexstr.rfind(prefix, 0) == 0) {
                // Coincidencia al comienzo
                found = true;
                found_hash = hexstr;
                // Recuperamos el nonce a partir de la cadena en h_in + i*MAX_INPUT + base_len
                const char* p = h_in + i * MAX_INPUT + base_len;
                found_nonce = static_cast<uint32_t>(strtoul(p, nullptr, 10));
                break;
            }
        }
    }

    // Medir tiempo CPU al terminar
    auto t1 = std::chrono::high_resolution_clock::now();
    double time_s = std::chrono::duration<double>(t1 - t0).count();

    delete[] h_in;
    delete[] h_out;
    return { found_nonce, found_hash, total_hashes, time_s };
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::printf("Uso: %s \"CADENA_BASE\" MAX_PREFIJO\n", argv[0]);
        std::printf("Ejemplo: %s \"blockdata\" 4\n", argv[0]);
        return 1;
    }

    const char* base = argv[1];
    int max_len = std::atoi(argv[2]);
    size_t base_len = std::strlen(base);

    if ((int)(base_len + NONCE_DIGITS) >= MAX_INPUT) {
        std::fprintf(stderr, "Error: la cadena base más '%d' dígitos excede MAX_INPUT (%d)\n",
                     NONCE_DIGITS, MAX_INPUT);
        return 1;
    }

    std::printf("Midiendo para prefijos de longitud 1 a %d...\n", max_len);
    std::printf("L  Prefijo  Tiempo(s)   Hashes/s       Nonce      Hash\n");
    std::printf("-------------------------------------------------------------\n");

    for (int L = 1; L <= max_len; ++L) {
        std::string prefix(L, '0');  // "0", "00", "000", ...
        Result r = find_for_prefix(base, base_len, prefix);
        double rate = (r.time_s > 0.0) ? (r.total_hashes / r.time_s) : 0.0;
        std::printf(
            "%-2d %-7s  %8.3f   %12.0f   %8u   %s\n",
            L,
            prefix.c_str(),
            r.time_s,
            rate,
            r.nonce,
            r.hash_hex.c_str()
        );
    }
    return 0;
}
