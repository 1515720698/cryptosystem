/* Serialize the public d=1 fixture for independent GmSSL commands only. */
#include <gmssl/sm2.h>
int main(void) {
    SM2_KEY key;
    sm2_z256_t d = {1,0,0,0};
    FILE *priv = fopen("data/test_private.pem", "w");
    FILE *pub = fopen("data/test_public.pem", "w");
    if (!priv || !pub || sm2_key_set_private_key(&key, d) != 1) return 1;
    if (sm2_private_key_info_encrypt_to_pem(&key, "lab2-test-only", priv) != 1 ||
        sm2_public_key_info_to_pem(&key, pub) != 1) return 1;
    fclose(priv);
    fclose(pub);
    return 0;
}
