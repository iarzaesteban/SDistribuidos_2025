// main_cpu.cpp
#include <windows.h>
#include <wincrypt.h>
#include <chrono>
#include <iostream>
#include <string>
#include <iomanip>
#include <sstream>
using namespace std;
using namespace std::chrono;

// MD5 con CryptoAPI
string md5_hex(const string& s) {
    HCRYPTPROV hProv = 0;
    HCRYPTHASH hHash = 0;
    BYTE  hash[16];
    DWORD hashLen = 16;

    if (!CryptAcquireContext(&hProv, nullptr, nullptr, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT))
        throw runtime_error("CryptAcquireContext failed");
    if (!CryptCreateHash(hProv, CALG_MD5, 0, 0, &hHash))
        throw runtime_error("CryptCreateHash failed");
    if (!CryptHashData(hHash, reinterpret_cast<BYTE const*>(s.data()), s.size(), 0))
        throw runtime_error("CryptHashData failed");
    if (!CryptGetHashParam(hHash, HP_HASHVAL, hash, &hashLen, 0))
        throw runtime_error("CryptGetHashParam failed");

    CryptDestroyHash(hHash);
    CryptReleaseContext(hProv, 0);

    ostringstream oss;
    for (DWORD i = 0; i < hashLen; ++i)
        oss << hex << setw(2) << setfill('0') << (int)hash[i];
    return oss.str();
}

int main(int argc, char* argv[]) {
    if (argc != 5) {
        cerr << "Uso: " << argv[0] << " base prefix start end\n";
        return 1;
    }
    string base = argv[1], pref = argv[2];
    unsigned long long start = stoull(argv[3]), end = stoull(argv[4]);
    bool found = false;
    string found_hash;
    unsigned long long found_nonce = 0;

    auto t0 = high_resolution_clock::now();
    for (auto nonce = start; nonce <= end; ++nonce) {
        string txt = base + to_string(nonce);
        string h = md5_hex(txt);
        if (h.rfind(pref, 0) == 0) {
            found = true;
            found_hash = h;
            found_nonce = nonce;
            break;
        }
    }
    auto t1 = high_resolution_clock::now();
    double secs = duration<double>(t1 - t0).count();

    if (found) {
        cout << "Hash: "  << found_hash  << "\n";
        cout << "Nonce: " << found_nonce << "\n";
    } else {
        cout << "No encontrado en rango\n";
    }
    cout << "Tiempo total: " << fixed << setprecision(3) << secs << " segundos\n";
    return 0;
}
