/* Teaching example: RSA-PSS / SHA-256 / MGF1-SHA256 / 32-byte salt.
 * sign private.pem message.bin signature.bin
 * verify public.pem message.bin signature.bin
 * Exit: 0=success, 1=invalid signature, 2=operation/input error.
 */
#include <stdio.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/rsa.h>
#include <openssl/err.h>

static void print_errors(void)
{
    unsigned long code;
    char text[256];
    while ((code = ERR_get_error()) != 0) {
        ERR_error_string_n(code, text, sizeof text);
        fprintf(stderr, "%s\n", text);
    }
}

int main(int argc, char **argv)
{
    int signing, result = 2, verified, size;
    BIO *keybio = NULL;
    EVP_PKEY *key = NULL;
    EVP_MD_CTX *mdctx = NULL;
    EVP_PKEY_CTX *pctx = NULL; /* Borrowed from mdctx, not freed separately. */
    FILE *message = NULL, *sigfile = NULL;
    unsigned char chunk[7], *signature = NULL;
    size_t count, siglen = 0, total = 0;

    if (argc != 5 || (strcmp(argv[1], "sign") && strcmp(argv[1], "verify"))) {
        fprintf(stderr, "Usage: %s sign|verify key.pem message.bin signature.bin\n", argv[0]);
        return 2;
    }
    signing = strcmp(argv[1], "sign") == 0;
    keybio = BIO_new_file(argv[2], "rb");
    if (!keybio) goto cleanup;
    key = signing ? PEM_read_bio_PrivateKey(keybio, NULL, NULL, NULL)
                  : PEM_read_bio_PUBKEY(keybio, NULL, NULL, NULL);
    if (!key || !EVP_PKEY_is_a(key, "RSA")) goto cleanup;
    mdctx = EVP_MD_CTX_new();
    if (!mdctx) goto cleanup;
    if (signing) {
        if (EVP_DigestSignInit(mdctx, &pctx, EVP_sha256(), NULL, key) != 1) goto cleanup;
    } else {
        if (EVP_DigestVerifyInit(mdctx, &pctx, EVP_sha256(), NULL, key) != 1) goto cleanup;
    }
    if (EVP_PKEY_CTX_set_rsa_padding(pctx, RSA_PKCS1_PSS_PADDING) <= 0 ||
        EVP_PKEY_CTX_set_rsa_mgf1_md(pctx, EVP_sha256()) <= 0 ||
        EVP_PKEY_CTX_set_rsa_pss_saltlen(pctx, 32) <= 0) goto cleanup;
    message = fopen(argv[3], "rb");
    if (!message) goto cleanup;
    while ((count = fread(chunk, 1, sizeof chunk, message)) != 0) {
        int ok = signing ? EVP_DigestSignUpdate(mdctx, chunk, count)
                         : EVP_DigestVerifyUpdate(mdctx, chunk, count);
        if (ok != 1) goto cleanup;
        total += count;
    }
    if (ferror(message)) goto cleanup;
    if (signing) {
        if (EVP_DigestSignFinal(mdctx, NULL, &siglen) != 1) goto cleanup;
        signature = OPENSSL_malloc(siglen);
        if (!signature || EVP_DigestSignFinal(mdctx, signature, &siglen) != 1) goto cleanup;
        sigfile = fopen(argv[4], "wb");
        if (!sigfile || fwrite(signature, 1, siglen, sigfile) != siglen) goto cleanup;
        if (fclose(sigfile) != 0) { sigfile = NULL; goto cleanup; }
        sigfile = NULL;
        printf("SIGN OK: message=%zu bytes, signature=%zu bytes\n", total, siglen);
        result = 0;
    } else {
        size = EVP_PKEY_get_size(key);
        if (size <= 0) goto cleanup;
        signature = OPENSSL_malloc((size_t)size + 1);
        sigfile = fopen(argv[4], "rb");
        if (!signature || !sigfile) goto cleanup;
        siglen = fread(signature, 1, (size_t)size + 1, sigfile);
        if (ferror(sigfile)) goto cleanup;
        if (siglen != (size_t)size) {
            puts("VERIFY INVALID: incorrect RSA signature length");
            result = 1;
            goto cleanup;
        }
        verified = EVP_DigestVerifyFinal(mdctx, signature, siglen);
        if (verified == 1) { puts("VERIFY OK"); result = 0; }
        else if (verified == 0) { puts("VERIFY INVALID"); result = 1; }
        else { puts("VERIFY ERROR"); result = 2; }
    }
cleanup:
    if (result == 2) { fprintf(stderr, "Operation failed\n"); print_errors(); }
    if (message) fclose(message);
    if (sigfile) fclose(sigfile);
    OPENSSL_free(signature);
    EVP_MD_CTX_free(mdctx);
    EVP_PKEY_free(key);
    BIO_free(keybio);
    return result;
}
