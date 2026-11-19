#include "sdf_device.h"

#include <stdio.h>
#include <stdlib.h>

/* Teaching backend: at most one open device and one active session. */
static HANDLE device;
static HANDLE session;

LONG SDF_OpenDevice(HANDLE *out)
{
    if (!out) return SDR_OUTARGERR;
    if (device) return SDR_OPENDEVICE;
    device = malloc(1);
    if (!device) return SDR_OPENDEVICE;
    *out = device;
    return SDR_OK;
}

LONG SDF_CloseDevice(HANDLE handle)
{
    if (!device || handle != device || session) return SDR_INARGERR;
    free(device);
    device = NULL;
    return SDR_OK;
}

LONG SDF_OpenSession(HANDLE handle, HANDLE *out)
{
    if (!device || handle != device) return SDR_INARGERR;
    if (!out) return SDR_OUTARGERR;
    if (session) return SDR_OPENSESSION;
    session = malloc(1);
    if (!session) return SDR_OPENSESSION;
    *out = session;
    return SDR_OK;
}

LONG SDF_CloseSession(HANDLE handle)
{
    if (!session || handle != session) return SDR_INARGERR;
    free(session);
    session = NULL;
    return SDR_OK;
}

LONG SDF_GetDeviceInfo(HANDLE handle, DEVICEINFO *out)
{
    if (!session || handle != session) return SDR_INARGERR;
    if (!out) return SDR_OUTARGERR;
    const DEVICEINFO info = {
        .IssuerName = "Teaching software",
        .DeviceName = "LAB3-SDF",
        .DeviceSerial = "0000000000000000",
        .DeviceVersion = 1,
        .StandardVersion = 2,
        /* No crypto or file storage is implemented in this example. */
    };
    *out = info;
    return SDR_OK;
}

#ifndef LAB_SDF_NO_MAIN
int main(void)
{
    HANDLE dev = NULL;
    HANDLE sess = NULL;
    DEVICEINFO info = {0};
    LONG rc = SDF_OpenDevice(&dev);
    printf("SDF_OpenDevice: 0x%08x\n", (unsigned)rc);
    if (rc != SDR_OK) return 1;

    rc = SDF_OpenSession(dev, &sess);
    printf("SDF_OpenSession: 0x%08x\n", (unsigned)rc);
    if (rc == SDR_OK) {
        rc = SDF_GetDeviceInfo(sess, &info);
        printf("SDF_GetDeviceInfo: 0x%08x\n", (unsigned)rc);
        if (rc == SDR_OK) {
            printf("backend=software IssuerName=%.40s DeviceName=%.16s DeviceSerial=%.16s\n",
                   (const char *)info.IssuerName, (const char *)info.DeviceName,
                   (const char *)info.DeviceSerial);
            printf("DeviceVersion=%u StandardVersion=%u AsymAlgAbility=[%u,%u] "
                   "SymAlgAbility=%u HashAlgAbility=%u BufferSize=%u\n",
                   info.DeviceVersion, info.StandardVersion,
                   info.AsymAlgAbility[0], info.AsymAlgAbility[1],
                   info.SymAlgAbility, info.HashAlgAbility, info.BufferSize);
        }
        LONG close_rc = SDF_CloseSession(sess);
        printf("SDF_CloseSession: 0x%08x\n", (unsigned)close_rc);
        if (rc == SDR_OK) rc = close_rc;
    }
    LONG close_rc = SDF_CloseDevice(dev);
    printf("SDF_CloseDevice: 0x%08x\n", (unsigned)close_rc);
    return rc != SDR_OK || close_rc != SDR_OK;
}
#endif
