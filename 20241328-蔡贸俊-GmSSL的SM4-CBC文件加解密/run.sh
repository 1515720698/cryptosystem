#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
gcc -std=c11 -Wall -Wextra -O2 -I/usr/local/include \
    src/sm4_file.c -L/usr/local/lib -Wl,-rpath,/usr/local/lib \
    -lgmssl -o sm4_file
./sm4_file
diff sn.txt sn2.txt
printf 'diff exit code = 0 (files identical)\n'
