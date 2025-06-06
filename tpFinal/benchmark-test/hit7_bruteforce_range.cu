// hit7_bruteforce_range.cu
// Hit #7 – HASH por fuerza bruta con CUDA (con límites)
//
// Busca un nonce en [start, end] tal que MD5(base || nonce) empiece con un prefijo dado,
// procesando lotes (batches) de nonces en paralelo en GPU para acelerar la búsqueda.
// Usa la implementación CUDA de MD5 que tienes en md5.cu/md5.cuh.
//
// Archivos necesarios aquí (en la misma carpeta):
//    • config.h
//    • md5.cuh
//    • md5.cu
//
// Compilar (desde la carpeta Hit7-new):
//    nvcc hit7_bruteforce_range.cu md5.cu -o brute_range.exe
//
// Ejecutar:
//    brute_range.exe "BASE" "PREFIJO" start end
// Ejemplo:
//    brute_range.exe "blockdata" "0000" 0 50000000
//
// ———————————————————————————————————————————————————————————————————————————

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <chrono>
#include <iostream>

#include "config.h"   // define MAX_INPUT, BYTE, WORD, etc.
#include "md5.cuh"    // declara mcm_cuda_md5_hash_batch()

#define NONCE_DIGITS 10   // Reservamos 10 dígitos para convertir nonce a decimal
#define MAX_INPUT    256  // Máximo largo (base + nonce) – config.h debe cubrir esto
#define BATCH_SIZE   1024 // Cantidad de nonces que lanzamos a la GPU en cada iteración

struct ResultRange {
    uint32_t nonce;          // Nonce hallado (o 0xFFFFFFFF si no se halló nada)
    std::string hash_hex;    // Hash MD5 en hex (32 chars), si se encontró
    uint64_t total_hashes;   // Total de hashes MD5 calculados
    double   time_s;         // Tiempo total de búsqueda (en segundos)
};

// ----------------------------------------------------------------
// to_hex()
//   Convierte 16 bytes del digest MD5 a string hexadecimal (32 caracteres).
// ----------------------------------------------------------------
static std::string to_hex(const BYTE* digest) {
    const char hex_digits[] = "0123456789abcdef";
    char buf[33];
    for (int i = 0; i < 16; ++i) {
        buf[2 * i]     = hex_digits[(digest[i] >> 4) & 0xF];
        buf[2 * i + 1] = hex_digits[digest[i] & 0xF];
    }
    buf[32] = '\0';
    return std::string(buf);
}

// ----------------------------------------------------------------
// find_in_range()
//   • base:     puntero a la cadena base (por ej. "blockdata")
//   • base_len: longitud de esa cadena
//   • prefix:   prefijo MD5 a buscar (por ej. "0000")
//   • start:    límite inferior (inclusive) del rango de nonces
//   • end:      límite superior (inclusive) del rango de nonces
//
// La función recorre secuencialmente el rango [start…end], en bloques de BATCH_SIZE nonces.
// Para cada bloque (batch), empaqueta base||nonce_i en CPU, copia a GPU y llama a
//   mcm_cuda_md5_hash_batch(…)
//, que calcula MD5 de cada entrada en paralelo. Tan pronto encuentra un hash que comienza
// con el prefijo indicado, guarda ese nonce y detiene la búsqueda. Retorna un struct con:
//    • nonce hallado (o 0xFFFFFFFF si no lo encontró)
//    • hash MD5 en hex
//    • total de hashes computados
//    • tiempo en segundos
// ----------------------------------------------------------------
static ResultRange find_in_range(
    const char* base,
    size_t      base_len,
    const std::string& prefix,
    uint32_t    start,
    uint32_t    end
) {
    // Reservamos dos buffers en host:
    //   • h_in  para almacenar BATCH_SIZE cadenas “base||nonce” (cada una ocupa MAX_INPUT bytes)
    //   • h_out para recibir BATCH_SIZE hashes MD5 (16 bytes cada uno)
    char* h_in  = new char[BATCH_SIZE * MAX_INPUT]();
    BYTE* h_out = new BYTE[BATCH_SIZE * 16]();

    bool    found = false;
    uint32_t found_nonce = 0;
    std::string found_hash;
    uint64_t total_hashes = 0;

    // Iniciamos el cronómetro en CPU (solo para medir tiempo total)
    auto t0 = std::chrono::high_resolution_clock::now();

    uint32_t current = start;
    while (current <= end && !found) {
        // Determinamos cuántos nonces faltan por procesar en este batch
        uint32_t batch_count = (end - current + 1) < BATCH_SIZE
                             ? (end - current + 1)
                             : BATCH_SIZE;

        // Empaquetamos las cadenas “base||nonce” en el buffer h_in
        for (uint32_t i = 0; i < batch_count; ++i) {
            uint32_t nonce = current + i;
            sprintf(
                h_in + i * MAX_INPUT,
                "%s%0*u",
                base,
                NONCE_DIGITS,
                nonce
            );
        }

        // Llamamos a CUDA para calcular MD5 de todo el batch (batch_count entradas):
        //  • Cada entrada tiene longitud `base_len + NONCE_DIGITS`
        //  • El resultado (16 bytes por entrada) queda en h_out
        mcm_cuda_md5_hash_batch(
            reinterpret_cast<BYTE*> (h_in),
            static_cast<WORD>(base_len + NONCE_DIGITS),
            h_out,
            static_cast<WORD>(batch_count)
        );

        total_hashes += batch_count;

        // Recorremos los hashes devueltos en h_out, buscando coincidencia con el prefijo
        for (uint32_t i = 0; i < batch_count; ++i) {
            BYTE* digest = h_out + i * 16;
            std::string hexstr = to_hex(digest);
            if (hexstr.rfind(prefix, 0) == 0) {
                found = true;
                found_hash = hexstr;
                found_nonce = current + i;
                break;
            }
        }

        current += batch_count;
    }

    // Paramos el cronómetro
    auto t1 = std::chrono::high_resolution_clock::now();
    double time_s = std::chrono::duration<double>(t1 - t0).count();

    delete[] h_in;
    delete[] h_out;
    return { found_nonce, found_hash, total_hashes, time_s };
}

int main(int argc, char* argv[]) {
    if (argc != 5) {
        std::printf("Uso: %s \"BASE\" \"PREFIX\" start end\n", argv[0]);
        std::printf("Ejemplo: %s \"blockdata\" \"0000\" 0 50000000\n", argv[0]);
        return 1;
    }

    const char* base       = argv[1];
    const char* prefix_str = argv[2];
    uint32_t start = static_cast<uint32_t>(std::strtoul(argv[3], nullptr, 10));
    uint32_t end   = static_cast<uint32_t>(std::strtoul(argv[4], nullptr, 10));
    size_t   base_len = std::strlen(base);
    size_t   pref_len = std::strlen(prefix_str);

    if ((int)(base_len + NONCE_DIGITS) >= MAX_INPUT) {
        std::fprintf(stderr, "Error: base_len + NONCE_DIGITS excede MAX_INPUT (%d)\n", MAX_INPUT);
        return 1;
    }
    std::string prefix(prefix_str);

    // Llamamos a la función que hace la búsqueda en rango
    ResultRange r = find_in_range(base, base_len, prefix, start, end);

    // Mostramos resultados
    if (!r.hash_hex.empty()) {
        std::cout << "[OK] Solución encontrada\n"
                  << "Nonce: " << r.nonce << "\n"
                  << "Hash:  " << r.hash_hex << "\n";
    } else {
        std::cout << "[ERROR] no se encontró en rango ["
                  << start << "," << end << "] con prefijo \"" << prefix << "\"\n";
    }
    std::cout << "Total hashes computados: " << r.total_hashes << "\n";
    std::cout << "Tiempo total: " << r.time_s << " segundos\n";
    return 0;
}
