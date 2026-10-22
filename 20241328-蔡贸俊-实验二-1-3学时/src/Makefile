CC = gcc
CFLAGS = -O2 -g -std=c11 -Wall -Wextra -fno-strict-aliasing
MRSRC = $(wildcard miracl/mr*.c)
MROBJ = $(MRSRC:.c=.o)

all: lab2

miracl/%.o: miracl/%.c
	$(CC) -O2 -I miracl -c $< -o $@

miracl/miracl.a: $(MROBJ)
	ar rcs $@ $^

lab2: main.c SM2_ENC.c SM2_ENC.h kdf.h SM3.c SM3.h SM4.c SM4.h miracl/miracl.a
	$(CC) $(CFLAGS) -I miracl main.c SM3.c SM4.c miracl/miracl.a -lm -o $@

clean:
	rm -f lab2 lab2_san miracl/*.o miracl/miracl.a

.PHONY: all clean
