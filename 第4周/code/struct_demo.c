#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    unsigned char version;
    uint32_t length;
} PacketHeader;

typedef struct {
    unsigned char c1[65];
    unsigned char c3[32];
    unsigned char *c2;
    size_t c2_len;
} SM2CiphertextView;

static void wrong_change(PacketHeader h) { h.length = 99; (void)h; }
static void correct_change(PacketHeader *h) { h->length = 99; }

int main(void)
{
    PacketHeader h = {1, 5};
    unsigned char wire[5];
    unsigned char binary[] = {0x41, 0x00, 0x42, 0x00};
    printf("header: sizeof=%zu, fields=%zu, length_offset=%zu\n",
           sizeof h, sizeof h.version + sizeof h.length,
           offsetof(PacketHeader, length));
    wrong_change(h);
    printf("after pass-by-value: length=%u\n", (unsigned)h.length);
    correct_change(&h);
    printf("after pass-by-pointer: length=%u\n", (unsigned)h.length);
    wire[0] = h.version;
    wire[1] = (unsigned char)(h.length >> 24);
    wire[2] = (unsigned char)(h.length >> 16);
    wire[3] = (unsigned char)(h.length >> 8);
    wire[4] = (unsigned char)h.length;
    printf("serialized:");
    for (size_t i = 0; i < sizeof wire; ++i) printf(" %02X", wire[i]);
    printf("\nbinary: strlen=%zu, actual_bytes=%zu\n",
           strlen((const char *)binary), sizeof binary);
    return h.length == 99 && wire[4] == 99 ? 0 : 1;
}
