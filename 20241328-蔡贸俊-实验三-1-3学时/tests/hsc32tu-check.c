#include <stdio.h>
#include "sdf.h" /* Use the HSC32TU vendor header, not the teaching sdf.h. */

static SGD_RV show(const char *name, SGD_RV rc)
{
    printf("%s: 0x%08x\n", name, (unsigned)rc);
    return rc;
}

int main(void)
{
    SGD_HANDLE device = NULL, session = NULL;
    SGD_UCHAR sample[16] = {0};
    SGD_RV rc = show("SDF_OpenDevice", SDF_OpenDevice(&device));
    if (rc) return 1;
    rc = show("SDF_OpenSession", SDF_OpenSession(device, &session));
    if (!rc) {
        rc = show("SDF_GenerateRandom", SDF_GenerateRandom(session, sample, sizeof(sample)));
        if (!rc) printf("Requested %zu random bytes successfully (contents omitted).\n", sizeof(sample));
        SGD_RV close_rc = show("SDF_CloseSession", SDF_CloseSession(session));
        if (!rc) rc = close_rc;
    }
    SGD_RV close_rc = show("SDF_CloseDevice", SDF_CloseDevice(device));
    return rc || close_rc ? 1 : 0;
}
