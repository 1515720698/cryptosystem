#include <arpa/inet.h>
#include <errno.h>
#include <openssl/err.h>
#include <openssl/ssl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>

/* Local blocking-I/O teaching example. All connections use loopback only.
 * server PORT CA CERT KEY REQUIRE_CLIENT
 * client PORT CA HOST [CERT KEY]
 */
static int transfer(SSL *ssl, char *data, size_t length, int writing)
{
    size_t offset = 0;
    while (offset < length) {
        size_t done = 0;
        int ok = writing ? SSL_write_ex(ssl, data + offset, length - offset, &done)
                         : SSL_read_ex(ssl, data + offset, length - offset, &done);
        if (ok != 1) {
            fprintf(stderr, "TLS %s error=%d\n", writing ? "write" : "read",
                    SSL_get_error(ssl, ok));
            return 0;
        }
        if (done == 0) return 0;
        offset += done;
    }
    return 1;
}

int main(int argc, char **argv)
{
    int server, fd = -1, listener = -1, status = 1, ret;
    SSL_CTX *ctx = NULL;
    SSL *ssl = NULL;
    X509 *peer = NULL;
    struct sockaddr_in address = {0};
    struct timeval timeout = {5, 0};
    char message[6] = {0}, reply[5] = {0};
    if (argc < 2) return 2;
    server = strcmp(argv[1], "server") == 0;
    if ((server && argc != 7) || (!server && argc != 5 && argc != 7)) {
        fprintf(stderr, "server PORT CA CERT KEY REQUIRE_CLIENT | client PORT CA HOST [CERT KEY]\n");
        return 2;
    }
    signal(SIGPIPE, SIG_IGN);
    setvbuf(stdout, NULL, _IONBF, 0);
    ctx = SSL_CTX_new(server ? TLS_server_method() : TLS_client_method());
    if (!ctx || !SSL_CTX_set_min_proto_version(ctx, TLS1_2_VERSION)) goto end;
    if (!SSL_CTX_load_verify_locations(ctx, argv[3], NULL)) goto end;
    SSL_CTX_set_verify(ctx, server ? (atoi(argv[6]) ?
        SSL_VERIFY_PEER | SSL_VERIFY_FAIL_IF_NO_PEER_CERT : SSL_VERIFY_NONE)
        : SSL_VERIFY_PEER, NULL);
    if (server || argc == 7) {
        const char *cert = server ? argv[4] : argv[5];
        const char *key = server ? argv[5] : argv[6];
        if (SSL_CTX_use_certificate_chain_file(ctx, cert) != 1 ||
            SSL_CTX_use_PrivateKey_file(ctx, key, SSL_FILETYPE_PEM) != 1 ||
            SSL_CTX_check_private_key(ctx) != 1) goto end;
    }
    address.sin_family = AF_INET;
    address.sin_port = htons((unsigned short)atoi(argv[2]));
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) goto os_error;
    if (server) {
        int reuse = 1;
        listener = fd;
        fd = -1;
        if (setsockopt(listener, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) ||
            bind(listener, (struct sockaddr *)&address, sizeof(address)) ||
            listen(listener, 1)) goto os_error;
        puts("READY loopback");
        fd = accept(listener, NULL, NULL);
        if (fd < 0) goto os_error;
    }
    if (setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) ||
        setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout))) goto os_error;
    if (!server && connect(fd, (struct sockaddr *)&address, sizeof(address))) goto os_error;
    ssl = SSL_new(ctx);
    if (!ssl || SSL_set_fd(ssl, fd) != 1) goto end;
    if (!server && (SSL_set_tlsext_host_name(ssl, argv[4]) != 1 ||
                    SSL_set1_host(ssl, argv[4]) != 1)) goto end;
    ret = server ? SSL_accept(ssl) : SSL_connect(ssl);
    if (ret != 1) {
        int error = SSL_get_error(ssl, ret);
        long verify = SSL_get_verify_result(ssl);
        fprintf(stderr, "HANDSHAKE_FAIL ssl_error=%d verify=%ld (%s)\n",
                error, verify, X509_verify_cert_error_string(verify));
        goto end;
    }
    peer = SSL_get1_peer_certificate(ssl);
    printf("HANDSHAKE_OK version=%s cipher=%s peer_cert=%s\n",
           SSL_get_version(ssl), SSL_get_cipher_name(ssl), peer ? "present" : "absent");
    if (server) {
        if (!transfer(ssl, message, 5, 0) || memcmp(message, "HELLO", 5)) goto end;
        printf("RECEIVED %s\n", message);
        memcpy(reply, "PONG", 4);
        if (!transfer(ssl, reply, 4, 1)) goto end;
    } else {
        memcpy(message, "HELLO", 5);
        if (!transfer(ssl, message, 5, 1) || !transfer(ssl, reply, 4, 0) ||
            memcmp(reply, "PONG", 4)) goto end;
        printf("RECEIVED %s\n", reply);
    }
    /* Complete close_notify in both directions for the successful exchange. */
    ret = SSL_shutdown(ssl);
    if (ret == 0) ret = SSL_shutdown(ssl);
    if (ret != 1) {
        fprintf(stderr, "SHUTDOWN_FAIL error=%d\n", SSL_get_error(ssl, ret));
        goto end;
    }
    puts("EXCHANGE_OK");
    status = 0;
    goto end;
os_error:
    perror("socket operation");
end:
    if (status) ERR_print_errors_fp(stderr);
    X509_free(peer);
    SSL_free(ssl);
    SSL_CTX_free(ctx);
    if (fd >= 0) close(fd);
    if (listener >= 0) close(listener);
    return status;
}
