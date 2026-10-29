#include <cstdio>
#include "textbook/sm3/sm3.h"
#include "file_io.h"

int main(int argc, char **argv) {
    unsigned char digest[32];
    unsigned char message[] = "abc";
    if (argc == 3) {
        size_t length;
        unsigned char *data = load_file(argv[1], &length);
        sm3(data, (int)length, digest);
        save_file(argv[2], digest, 32);
        free(data);
    } else if (argc == 1) sm3(message, 3, digest);
    else return 2;
    std::printf("SM3 textbook digest: ");
    for (unsigned char byte : digest) std::printf("%02x", byte);
    std::printf("\n");
    return 0;
}
