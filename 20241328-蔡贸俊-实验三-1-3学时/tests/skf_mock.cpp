#include "../skf/include/skfapi.h"

#include <cstring>

// Test-only doubles. Never linked into build/skf-state.
ULONG DEVAPI SKF_EnumDev(BOOL, LPSTR names, ULONG *size)
{
    static const char list[] = "mock-key\0";
    if (*size < sizeof(list)) {
        return SAR_FAIL;
    }
    std::memcpy(names, list, sizeof(list));
    *size = sizeof(list);
    return SAR_OK;
}

ULONG DEVAPI SKF_GetDevState(LPSTR name, ULONG *state)
{
    if (std::strcmp(name, "mock-key") == 0) {
        *state = DEV_PRESENT_STATE;
    } else if (std::strcmp(name, "mock-absent") == 0) {
        *state = DEV_ABSENT_STATE;
    } else if (std::strcmp(name, "mock-unknown") == 0) {
        *state = DEV_UNKNOW_STATE;
    } else {
        return SAR_FAIL;
    }
    return SAR_OK;
}
