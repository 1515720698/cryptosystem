#ifndef LAB_SDF_DEVICE_H
#define LAB_SDF_DEVICE_H

#include "sdf.h"

#define SDR_OK          0
#define SDR_BASE        0x01000000
#define SDR_OPENDEVICE  (SDR_BASE + 0x05)
#define SDR_OPENSESSION (SDR_BASE + 0x06)
#define SDR_INARGERR    (SDR_BASE + 0x1D)
#define SDR_OUTARGERR   (SDR_BASE + 0x1E)

LONG SDF_OpenSession(HANDLE hDeviceHandle, HANDLE *phSessionHandle);
LONG SDF_CloseSession(HANDLE hSessionHandle);

#endif
