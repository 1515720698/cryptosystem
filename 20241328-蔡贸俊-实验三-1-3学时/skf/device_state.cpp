#include "include/skfapi.h"

#include <cstdio>
#include <cstring>
#include <unistd.h>

int main(int argc, char **argv)
{
    if (argc > 2 || (argc == 2 && argv[1][0] == '\0')) {
        std::fprintf(stderr, "Usage: %s [device-name]\n", argv[0]);
        return 2;
    }
#ifdef LAB_SKF_MOCK
    std::puts("backend=MOCK (no hardware)");
#else
    std::puts("backend=Longmai SKF SDK");
    // The course SDK crashes in USB discovery on this WSL setup with no USB bus.
    if (access("/dev/bus/usb", R_OK | X_OK) != 0 &&
        access("/sys/bus/usb/devices", R_OK | X_OK) != 0) {
        std::fprintf(stderr, "USB bus not visible; vendor API not called.\n");
        return 3;
    }
#endif
    char names[4096] = {};
    char *name = argc == 2 ? argv[1] : names;
    if (argc == 1) {
        ULONG size = sizeof(names);
        const ULONG rc = SKF_EnumDev(1, names, &size);
        if (rc != SAR_OK) {
            std::fprintf(stderr, "SKF_EnumDev failed: 0x%08x\n", rc);
            return 1;
        }
        if (names[0] == '\0') {
            std::puts("No present SKF device; provide a known name to query it.");
            return 3;
        }
        if (size > sizeof(names) || std::memchr(names, '\0', size) == nullptr) {
            std::fprintf(stderr, "SKF_EnumDev returned an invalid name list.\n");
            return 1;
        }
    }
    ULONG state = DEV_UNKNOW_STATE;
    const ULONG rc = SKF_GetDevState(name, &state);
    if (rc != SAR_OK) {
        std::fprintf(stderr, "SKF_GetDevState(%s) failed: 0x%08x\n", name, rc);
        return 1;
    }
    const char *label = "UNRECOGNIZED";
    switch (state) {
    case DEV_PRESENT_STATE: label = "PRESENT"; break;
    case DEV_ABSENT_STATE: label = "ABSENT"; break;
    case DEV_UNKNOW_STATE: label = "UNKNOWN"; break;
    }
    std::printf("SKF_GetDevState(%s): %s (0x%08x)\n", name, label, state);
    return 0;
}
