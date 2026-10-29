#pragma once
#include <stdio.h>
#include <stdlib.h>

static unsigned char *load_file(const char *name, size_t *length) {
    FILE *fp = fopen(name, "rb");
    long size;
    unsigned char *data;
    if (!fp) { perror(name); exit(2); }
    if (fseek(fp, 0, SEEK_END) || (size = ftell(fp)) < 0 || size > 1048576) exit(2);
    rewind(fp);
    data = (unsigned char *)malloc((size_t)size + 1);
    if (!data || fread(data, 1, (size_t)size, fp) != (size_t)size) exit(2);
    fclose(fp);
    *length = (size_t)size;
    return data;
}

static void save_file(const char *name, const unsigned char *data, size_t length) {
    FILE *fp = fopen(name, "wb");
    if (!fp || fwrite(data, 1, length, fp) != length) { perror(name); exit(2); }
    if (fclose(fp)) exit(2);
}
