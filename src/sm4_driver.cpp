#include <cstdio>
#include <cstring>
#include "textbook/sm4/sm4.h"
#include "file_io.h"

static void dump(const unsigned char *value, int length) {
    for (int i = 0; i < length; ++i) std::printf("%02x", value[i]);
    std::printf("\n");
}

int main(int argc, char **argv) {
    unsigned char key[16] = {0x01,0x23,0x45,0x67,0x89,0xab,0xcd,0xef,0xfe,0xdc,0xba,0x98,0x76,0x54,0x32,0x10};
    unsigned char plain[16];
    unsigned char cipher[16];
    unsigned char recovered[16];
    if (argc == 4) {
        size_t length;
        unsigned char *data = load_file(argv[2], &length);
        if (length != 16) { free(data); return 2; }
        if (!std::strcmp(argv[1], "enc")) SM4_Encrypt(key, data, cipher);
        else if (!std::strcmp(argv[1], "dec")) SM4_Decrypt(key, data, cipher);
        else { free(data); return 2; }
        save_file(argv[3], cipher, 16);
        dump(cipher, 16);
        free(data);
        return 0;
    }
    if (argc != 1) return 2;
    std::memcpy(plain, key, sizeof(plain));
    SM4_Encrypt(key, plain, cipher);
    SM4_Decrypt(key, cipher, recovered);
    std::printf("SM4 textbook ciphertext: ");
    dump(cipher, sizeof(cipher));
    return std::memcmp(plain, recovered, sizeof(plain)) == 0 ? 0 : 1;
}
