#include "SM4.h"
void SM4_KeySchedule(unsigned char MK[],unsigned int rk[])
{
    unsigned int tmp,buf,K[36];
    int i;
    for(i=0;i<4;i++)
     {
              K[i]=SM4_FK[i]^( (((unsigned int)MK[4*i])<<24) | (((unsigned int)MK[4*i+1])<<16)
                              |(((unsigned int)MK[4*i+2])<<8) | (((unsigned int)MK[4*i+3])) );
     }
    for(i=0;i<32;i++)
     {
        tmp =K[i+1]^K[i+2]^K[i+3]^ SM4_CK[i];
        //nonlinear operation
        buf= (((unsigned int)SM4_Sbox[(tmp >> 24) & 0xFF])) << 24
             |(((unsigned int)SM4_Sbox[(tmp >> 16) & 0xFF])) << 16
             |(((unsigned int)SM4_Sbox[(tmp >> 8)  & 0xFF])) << 8
             |(((unsigned int)SM4_Sbox[tmp & 0xFF]));
         //linear operation
         K[i+4]=K[i]^((buf)^(SM4_Rotl32((buf),13))^(SM4_Rotl32((buf),23)));
         rk[i]=K[i+4];
     }
}
void SM4_Encrypt(unsigned char MK[],unsigned char PlainText[],unsigned char CipherText[])
{
    unsigned int rk[32],X[36],tmp,buf;
    int i,j;
    SM4_KeySchedule(MK,rk);
    for(j=0;j<4;j++)
     {
           X[j]=(((unsigned int)PlainText[j*4])<<24) |(((unsigned int)PlainText[j*4+1])<<16)
               |(((unsigned int)PlainText[j*4+2])<<8)|(((unsigned int)PlainText[j*4+3]));
     }
     for(i=0;i<32;i++)
      {
                tmp = X[i+1]^X[i+2]^X[i+3]^rk[i];
                //nonlinear operation
                 buf=  ( ((unsigned int)SM4_Sbox[(tmp >> 24) & 0xFF])) << 24
                       |(((unsigned int)SM4_Sbox[(tmp >> 16) & 0xFF])) << 16
                       |(((unsigned int)SM4_Sbox[(tmp >> 8)  & 0xFF])) << 8
                       |(((unsigned int)SM4_Sbox[tmp & 0xFF]));
                //linear operation
                X[i+4]=X[i]^(buf^SM4_Rotl32((buf),2)^ SM4_Rotl32((buf),10)
                           ^ SM4_Rotl32((buf),18)^ SM4_Rotl32((buf),24));
         }
    for(j=0;j<4;j++)
     {
              CipherText[4*j]=(X[35-j]>> 24)& 0xFF;
              CipherText[4*j+1]=(X[35-j]>> 16)& 0xFF;
              CipherText[4*j+2]=(X[35-j]>> 8)& 0xFF;
              CipherText[4*j+3]=(X[35-j])& 0xFF;
     }
}
void SM4_Decrypt(unsigned char MK[],unsigned char CipherText[],unsigned char PlainText[])
{
    unsigned int rk[32],X[36],tmp,buf;
    int i,j;
    SM4_KeySchedule(MK,rk);
    for(j=0;j<4;j++)
     {
            X[j]=(((unsigned int)CipherText[j*4])<<24) |(((unsigned int)CipherText[j*4+1])<<16)|
                 (((unsigned int)CipherText[j*4+2])<<8)|(((unsigned int)CipherText[j*4+3]));
     }
    for(i=0;i<32;i++)
        {
            tmp = X[i+1]^X[i+2]^X[i+3]^rk[31-i];
            //nonlinear operation
            buf= (((unsigned int)SM4_Sbox[(tmp >> 24) & 0xFF])) << 24
                |(((unsigned int)SM4_Sbox[(tmp >> 16) & 0xFF])) << 16
                |(((unsigned int)SM4_Sbox[(tmp >> 8)  & 0xFF])) << 8
                |(((unsigned int)SM4_Sbox[tmp & 0xFF]));
            //linear operation
            X[i+4]=X[i]^(buf^SM4_Rotl32((buf),2)^ SM4_Rotl32((buf),10)
                       ^ SM4_Rotl32((buf),18)^ SM4_Rotl32((buf),24));
      }
    for(j=0;j<4;j++)
     {
              PlainText[4*j]=(X[35-j]>> 24)& 0xFF;
              PlainText[4*j+1]=(X[35-j]>>16)& 0xFF;
              PlainText[4*j+2]=(X[35-j]>> 8)& 0xFF;
              PlainText[4*j+3]=(X[35-j])& 0xFF;
     }
}
int SM4_SelfCheck()
{
    int i;
    //Standard data
    unsigned char key[16]  =
{0x01,0x23,0x45,0x67,0x89,0xab,0xcd,0xef,0xfe,0xdc,0xba,0x98,0x76,0x54,0x32,0x10};
    unsigned char plain[16]=
{0x01,0x23,0x45,0x67,0x89,0xab,0xcd,0xef,0xfe,0xdc,0xba,0x98,0x76,0x54,0x32,0x10};
    unsigned char
cipher[16]={0x68,0x1e,0xdf,0x34,0xd2,0x06,0x96,0x5e,0x86,0xb3,0xe9,0x4f,0x53,0x6e,0x42,0x46}
;
    unsigned char En_output[16];
    unsigned char De_output[16];
    SM4_Encrypt(key,plain,En_output);
    SM4_Decrypt(key,cipher,De_output);
    for(i=0;i<16;i++)
    {
        if ( (En_output[i]!=cipher[i]) | (De_output[i]!=plain[i]) )
           {
 //             printf("Self-check error");
                return 1;
           }
    }
//  printf("Self-check success");
    return 0;
}
