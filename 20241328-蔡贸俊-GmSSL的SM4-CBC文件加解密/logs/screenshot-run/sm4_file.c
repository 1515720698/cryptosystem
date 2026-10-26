#include <stdio.h>
#include <stdint.h>
#include <gmssl/rand.h>
#include <gmssl/sm4.h>

/* Each operation gets a fresh context, so decryption uses the original IV. */
static int crypt_file(const char *input, const char *output,
    const uint8_t key[16], const uint8_t iv[16], int encrypt)
{
    FILE *in = NULL, *out = NULL;
    SM4_CBC_CTX ctx;
    uint8_t ibuf[4096], obuf[4096 + 32];
    size_t n, outlen, total_in = 0, total_out = 0;
    int ret = -1;

    in = fopen(input, "rb");
    if (!in) { perror(input); goto end; }
    out = fopen(output, "wb");
    if (!out) { perror(output); goto end; }
    if ((encrypt ? sm4_cbc_encrypt_init(&ctx, key, iv)
                 : sm4_cbc_decrypt_init(&ctx, key, iv)) != 1)
        goto end;

    while ((n = fread(ibuf, 1, sizeof(ibuf), in)) > 0) {
        if ((encrypt ? sm4_cbc_encrypt_update(&ctx, ibuf, n, obuf, &outlen)
                     : sm4_cbc_decrypt_update(&ctx, ibuf, n, obuf, &outlen)) != 1)
            goto end;
        if (fwrite(obuf, 1, outlen, out) != outlen) goto end;
        total_in += n;
        total_out += outlen;
    }
    if (ferror(in)) goto end;
    /* finish adds PKCS#7 padding on encryption and removes it on decryption. */
    if ((encrypt ? sm4_cbc_encrypt_finish(&ctx, obuf, &outlen)
                 : sm4_cbc_decrypt_finish(&ctx, obuf, &outlen)) != 1)
        goto end;
    if (fwrite(obuf, 1, outlen, out) != outlen) goto end;
    total_out += outlen;
    if (fclose(out) != 0) { out = NULL; goto end; }
    out = NULL;
    printf("%s: %s (%zu bytes) -> %s (%zu bytes)\n",
        encrypt ? "encrypt" : "decrypt", input, total_in, output, total_out);
    ret = 1;
end:
    if (in) fclose(in);
    if (out) fclose(out);
    if (ret != 1) fprintf(stderr, "File operation failed: %s\n", output);
    return ret;
}

static int save_bytes(const char *path, const uint8_t data[16])
{
    FILE *fp = fopen(path, "wb");
    int ok;
    if (!fp) { perror(path); return -1; }
    ok = fwrite(data, 1, 16, fp) == 16;
    if (fclose(fp) != 0) ok = 0;
    return ok ? 1 : -1;
}

static void print_hex(const char *name, const uint8_t data[16])
{
    size_t i;
    printf("%s = ", name);
    for (i = 0; i < 16; ++i) printf("%02x", data[i]);
    putchar('\n');
}

int main(void)
{
    uint8_t key[16], iv[16];
    /* GmSSL's random API is called twice, once for each 128-bit value. */
    if (rand_bytes(key, sizeof(key)) != 1 ||
        rand_bytes(iv, sizeof(iv)) != 1) {
        fprintf(stderr, "GmSSL rand_bytes failed\n");
        return 1;
    }
    print_hex("key", key);
    print_hex("iv", iv);
    if (save_bytes("key.bin", key) != 1 || save_bytes("iv.bin", iv) != 1)
        return 1;
    if (crypt_file("sn.txt", "sn.enc", key, iv, 1) != 1) return 1;
    if (crypt_file("sn.enc", "sn2.txt", key, iv, 0) != 1) return 1;
    return 0;
}
