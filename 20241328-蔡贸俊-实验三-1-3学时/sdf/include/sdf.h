#ifndef __SDF_H
#define __SDF_H

//typedefine
typedef unsigned char BYTE;
typedef unsigned char CHAR;
typedef int LONG;
typedef unsigned int ULONG;
typedef unsigned int FLAGS;
typedef CHAR * LPSTR;
typedef void * HANDLE;

typedef struct DeviceInfo_st{
    CHAR IssuerName[40];
    CHAR DeviceName[16];
    CHAR DeviceSerial[16];
    ULONG DeviceVersion;
    ULONG StandardVersion;
    ULONG AsymAlgAbility[2];
    ULONG SymAlgAbility;
    ULONG HashAlgAbility;
    ULONG BufferSize;
}DEVICEINFO;


#define ECCref_MAX_BITS 512
#define ECCref_MAX_LEN ((ECCref_MAX_BITS + 7) / 8)

typedef struct ECCrefPublicKey_st
{
    ULONG bits;
    BYTE x[ECCref_MAX_LEN];
    BYTE y[ECCref_MAX_LEN];
} ECCrefPublicKey;

typedef struct ECCrefPrivateKey_st
{
    ULONG bits;
    BYTE K[ECCref_MAX_LEN];
} ECCrefPrivateKey;

//device  management  interface

// 打开密码设备。phDeviceHandle由函数初始化并填写内容。
// 参数:
//     phDeviceHandle[out] 返回的设备句柄
// 返回值:
//     0 成功
//     非0 失败，返回错误代码
LONG SDF_OpenDevice(HANDLE * phDeviceHandle);




// 关闭密码设备，并释放相关资源。
// 参数:
//     hDeviceHandle[in] 已打开的设备句柄
// 返回值:
//     0 成功
//     非0 失败，返回错误代码
LONG SDF_CloseDevice(HANDLE hDeviceHandle);

// 获取密码设备能力描述。
// 参数:
//     hSessionHandle[in] 与设备建立的会话句柄
//     pstDeviceInfo[out] 设备能力描述信息，内容及格式见设备信息定义
// 返回值:
//     0 成功
//     非0 失败，返回错误代码
LONG SDF_GetDeviceInfo(HANDLE hSessionHandle, DEVICEINFO *pstDeviceInfo);
#endif
