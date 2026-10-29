#include <stdio.h>

// 计算累加和的自定义函数，用来练习函数相关调试
int calc_sum(int max_num) {
    int sum = 0;
    for (int i = 1; i <= max_num; i++) {
        sum += i;
    }
    return sum;
}

int main() {
    int limit = 10;
    int result = 0;
    result = calc_sum(limit);
    printf("1到%d的累加和是：%d\n", limit, result);
    return 0;
}
