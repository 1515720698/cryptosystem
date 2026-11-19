#include "sdf_device.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void check(const char *label, LONG actual, LONG expected)
{
    printf("%s: 0x%08x (expected 0x%08x)\n",
           label, (unsigned)actual, (unsigned)expected);
    assert(actual == expected);
}

int main(void)
{
    HANDLE dev = NULL, sess = NULL;
    DEVICEINFO info = {0};
    check("open device", SDF_OpenDevice(&dev), SDR_OK);
    assert(dev != NULL);
    check("open session", SDF_OpenSession(dev, &sess), SDR_OK);
    assert(sess != NULL && sess != dev);
    check("device handle is not a session", SDF_GetDeviceInfo(dev, &info), SDR_INARGERR);
    assert(info.DeviceName[0] == '\0');
    check("NULL output", SDF_GetDeviceInfo(sess, NULL), SDR_OUTARGERR);
    check("get device info", SDF_GetDeviceInfo(sess, &info), SDR_OK);
    assert(strcmp((const char *)info.DeviceName, "LAB3-SDF") == 0);
    assert(info.StandardVersion == 2);
    assert(info.AsymAlgAbility[0] == 0 && info.AsymAlgAbility[1] == 0);
    assert(info.SymAlgAbility == 0 && info.HashAlgAbility == 0 && info.BufferSize == 0);
    check("cannot close device before session", SDF_CloseDevice(dev), SDR_INARGERR);
    check("close session", SDF_CloseSession(sess), SDR_OK);
    sess = NULL;
    check("no active session", SDF_GetDeviceInfo(sess, &info), SDR_INARGERR);
    check("close device", SDF_CloseDevice(dev), SDR_OK);
    puts("SDF checks passed (software backend).");
    return 0;
}
