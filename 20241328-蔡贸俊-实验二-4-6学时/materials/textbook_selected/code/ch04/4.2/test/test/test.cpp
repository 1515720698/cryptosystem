// test.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include "pch.h"
#include <string.h>
#include <stdio.h>
#include "sm3.h"

int main(int argc, char *argv[])
{
	unsigned char *input = (unsigned char*)"abc";
	int ilen = 3;
	unsigned char output[32];
	int i;
	sm3_context ctx;

	printf("Message: ");
	printf("%s\n", input);

	sm3(input, ilen, output);
	printf("Hash:   ");
	for (i = 0; i < 32; i++)
	{
		printf("%02x", output[i]);
		if (((i + 1) % 4) == 0) printf(" ");
	}
	printf("\n");

	printf("Message: ");
	for (i = 0; i < 16; i++)
		printf("abcd");
	printf("\n");

	sm3_starts(&ctx);
	for (i = 0; i < 16; i++)
		sm3_update(&ctx, (unsigned char*)"abcd", 4);
	sm3_finish(&ctx, output);
	memset(&ctx, 0, sizeof(sm3_context));

	printf("Hash:   ");
	for (i = 0; i < 32; i++)
	{
		printf("%02x", output[i]);
		if (((i + 1) % 4) == 0) printf(" ");
	}
	printf("\n");
	//getch();	
}
