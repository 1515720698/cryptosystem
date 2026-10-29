#pragma once

void SM4_KeySchedule(unsigned char MK[], unsigned int rk[]);//生成轮密钥
void SM4_Encrypt(unsigned char MK[], unsigned char PlainText[], unsigned char CipherText[]);
void SM4_Decrypt(unsigned char MK[], unsigned char CipherText[], unsigned char PlainText[]);
int SM4_SelfCheck();