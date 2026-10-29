/* SCCTC algorithm exercise driver. Fixed keys/nonces are public test fixtures. */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include "SM3.h"
/* Reference headers define globals; include SM2 once in this translation unit. */
#include "SM2_ENC.c"
int SM4_SelfCheck(void);
void SM4_Encrypt(unsigned char *, unsigned char *, unsigned char *);
void SM4_Decrypt(unsigned char *, unsigned char *, unsigned char *);

static void save(const char *name, const void *data, size_t len) {
    FILE *f=fopen(name,"wb");
    if (!f || fwrite(data,1,len,f)!=len) {perror(name); exit(2);}
    fclose(f);
}
static unsigned char *readfile(const char *name, size_t *len) {
    FILE *f=fopen(name,"rb"); long n; unsigned char *p;
    if(!f) {perror(name); exit(2);}
    if(fseek(f,0,SEEK_END) || (n=ftell(f))<0 || n>1024*1024) exit(2);
    rewind(f); p=malloc((size_t)n+1); if(!p) exit(2);
    if(fread(p,1,(size_t)n,f)!=(size_t)n) exit(2);
    fclose(f); *len=(size_t)n; return p;
}
static void hex(const unsigned char *p,size_t n) {
    for(size_t i=0;i<n;i++) printf("%02x",p[i]);
    puts("");
}
static double now(void) {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t);
    return t.tv_sec+t.tv_nsec/1e9;
}
int main(int argc,char **argv) {
    unsigned char hash[32]; size_t len;
    if(argc==4 && !strcmp(argv[1],"sm3")) {
        unsigned char *p=readfile(argv[2],&len);
        SM3_256(p,(int)len,hash); save(argv[3],hash,32); hex(hash,32); free(p); return 0;
    }
    if(argc==5 && !strcmp(argv[1],"sm4")) {
        unsigned char key[16]={1,0x23,0x45,0x67,0x89,0xab,0xcd,0xef,0xfe,0xdc,0xba,0x98,0x76,0x54,0x32,0x10};
        unsigned char *p=readfile(argv[3],&len), out[16];
        if(len!=16) {fprintf(stderr,"SM4 needs exactly one 16-byte block\n"); free(p); return 2;}
        if(!strcmp(argv[2],"enc")) SM4_Encrypt(key,p,out);
        else if(!strcmp(argv[2],"dec")) SM4_Decrypt(key,p,out);
        else {free(p); return 2;}
        save(argv[4],out,16); hex(out,16); free(p); return 0;
    }
    mip=mirsys(10000,16); mip->IOBASE=16;
    if(argc==4 && !strcmp(argv[1],"sm2dec")) {
        unsigned char *p=readfile(argv[2],&len), out[1024];
        big d=mirvar(1);
        if(len<=96 || len>sizeof(out)+96) {free(p); return 2;}
        if(SM2_Init()!=0) return 1;
        int rc=SM2_Decrypt(d,p,(int)len,out);
        printf("SM2 decrypt return=%d\n",rc);
        if(!rc) save(argv[3],out,len-96);
        free(p); return rc?1:0;
    }
    if(argc!=2 || strcmp(argv[1],"selftest")) {
        fprintf(stderr,"Usage: lab2 selftest | sm3 in out | sm4 enc/dec in out | sm2dec raw out\n"); return 2;
    }
    int a=SM3_SelfTest(), b=SM4_SelfCheck(), c=SM2_ENC_SelfTest();
    printf("SM3 official selftest: %s\nSM4 official selftest: %s\nSM2 official selftest: %s (rc=%d)\n",
        a?"FAIL":"PASS",b?"FAIL":"PASS",c?"FAIL":"PASS",c);
    if(a||b||c) return 1;
    /* Use d=1, k=2 only for reproducible interoperability tests. */
    big d=mirvar(1); epoint *pub=epoint_init();
    unsigned char k[32]={0},msg[]="20241328 蔡贸俊",cipher[256],plain[256];
    k[31]=2;
    if(SM2_Init() || SM2_KeyGeneration(d,pub) || SM2_Encrypt(k,pub,msg,sizeof(msg)-1,cipher)) return 1;
    if(SM2_Decrypt(d,cipher,(int)(96+sizeof(msg)-1),plain) || memcmp(msg,plain,sizeof(msg)-1)) return 1;
    save("data/message.bin",msg,sizeof(msg)-1);
    save("data/sm2_official.raw",cipher,96+sizeof(msg)-1);
    printf("SM2 d=1 k=2 C1x||C1y||C3||C2: "); hex(cipher,96+sizeof(msg)-1);
    cipher[64]^=1;
    int rc=SM2_Decrypt(d,cipher,(int)(96+sizeof(msg)-1),plain);
    printf("SM2 tampered C3: %s (rc=%d, expected=6)\n",rc==6?"PASS":"FAIL",rc);
    if(rc!=6) return 1;
    unsigned char block[1024]={0}; double start=now();
    for(int i=0;i<10000;i++) SM3_256(block,sizeof(block),hash);
    printf("BENCH SM3 10000 x 1024 bytes: %.3f ms\n",(now()-start)*1000);
    start=now();
    for(int i=0;i<100000;i++) SM4_Encrypt(block,block,hash);
    printf("BENCH SM4 100000 x 16 bytes (includes key schedule): %.3f ms\n",(now()-start)*1000);
    start=now();
    for(int i=0;i<100;i++) if(SM2_Encrypt(k,pub,msg,sizeof(msg)-1,cipher)) return 1;
    printf("BENCH SM2 100 x %zu bytes (fixed k; includes allocation): %.3f ms\n",sizeof(msg)-1,(now()-start)*1000);
    return 0;
}
