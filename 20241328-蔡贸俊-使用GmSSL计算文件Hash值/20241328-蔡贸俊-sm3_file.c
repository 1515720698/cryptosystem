/*
 * sm3_file.c —— 使用 GmSSL 计算文件 sn.txt 的 SM3 杂凑值
 *
 * 编译： gcc sm3_file.c -o sm3_file -lgmssl
 * 运行： ./sm3_file sn.txt
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <gmssl/sm3.h>

#define BUFSIZE 4096

static void print_hex(const uint8_t *buf, size_t len)
{
	size_t i;
	for (i = 0; i < len; i++) {
		printf("%02x", buf[i]);
	}
	printf("\n");
}

int main(int argc, char **argv)
{
	const char *path = (argc > 1) ? argv[1] : "sn.txt";
	FILE *fp;
	SM3_CTX ctx;
	uint8_t dgst[SM3_DIGEST_SIZE];
	uint8_t buf[BUFSIZE];
	size_t n;
	long total = 0;

	fp = fopen(path, "rb");
	if (!fp) {
		fprintf(stderr, "cannot open file: %s\n", path);
		return 1;
	}

	sm3_init(&ctx);
	while ((n = fread(buf, 1, sizeof(buf), fp)) > 0) {
		sm3_update(&ctx, buf, n);
		total += (long)n;
	}
	fclose(fp);
	sm3_finish(&ctx, dgst);

	printf("file   : %s\n", path);
	printf("bytes  : %ld\n", total);
	printf("SM3    : ");
	print_hex(dgst, SM3_DIGEST_SIZE);

	return 0;
}
