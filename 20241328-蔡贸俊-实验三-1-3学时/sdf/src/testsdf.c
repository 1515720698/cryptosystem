#include <stdio.h>
#include "sdf.h"


int main() {
    HANDLE deviceHandle;
    LONG openResult, closeResult;

    // 打开设备
    openResult = SDF_OpenDevice(&deviceHandle);
    if (openResult == 0) {
        printf("设备打开成功。\n");

    } else {
        printf("设备打开失败，错误代码: %ld\n", openResult);
    }

        // 关闭设备
        closeResult = SDF_CloseDevice(deviceHandle);
        if (closeResult == 0) {
            printf("设备关闭成功。\n");
        } else {
            printf("设备关闭失败，错误代码: %ld\n", closeResult);
        }
    return 0;
}

