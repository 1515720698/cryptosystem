#include <stdio.h>
#include <string.h>
#include "textbook/sm2/SM2_ENC.h"
#include "file_io.h"

int main(int argc, char **argv) {
    int result;
    if (argc == 1) {
        result = SM2_ENC_SelfTest();
        printf("SM2 textbook selftest return=%d\n", result);
        return result;
    }
    if (argc != 4) return 2;
    mip = mirsys(1000, 16);
    if (!mip) return 1;
    mip->IOBASE = 16;
    if (SM2_Init()) return 1;
    size_t length;
    unsigned char *data = load_file(argv[2], &length), output[2048];
    big d = mirvar(1); /* Public test fixture d=1. Never a user's private key. */
    if (!strcmp(argv[1], "dec")) {
        if (length <= 96 || length > 1120) { free(data); return 2; }
        result = SM2_Decrypt(d, data, (int)length, output);
        printf("SM2 textbook decrypt return=%d\n", result);
        if (!result) save_file(argv[3], output, length-96);
    } else if (!strcmp(argv[1], "enc")) {
        unsigned char nonce[32];
        epoint *pub = epoint_init();
        if (!length || length > 1024 || SM2_KeyGeneration(d, pub)) { free(data); return 2; }
        FILE *rng = fopen("/dev/urandom", "rb");
        if (!rng) return 1;
        do {
            if (fread(nonce, 1, 32, rng) != 32) return 1;
        } while (memcmp(nonce, SM2_n, 32) >= 0 || Test_Null(nonce, 32));
        fclose(rng);
        result = SM2_Encrypt(nonce, pub, data, (int)length, output);
        if (!result) save_file(argv[3], output, length+96);
        printf("SM2 textbook encrypt return=%d\n", result);
    } else { free(data); return 2; }
    free(data);
    return result ? 1 : 0;
}
