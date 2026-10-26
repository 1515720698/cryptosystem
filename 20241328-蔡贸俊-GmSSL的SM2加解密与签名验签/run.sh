#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [[ -z "${SM2_PASS:-}" ]]; then
    read -r -s -p 'Password for the NEW classroom private key: ' SM2_PASS
    printf '\n'
fi
export SM2_PASS
mkdir -p private
chmod 700 private
umask 077
gmssl sm2keygen -pass "$SM2_PASS" -out private/sm2_private.pem -pubout sm2_public.pem
gcc -std=c11 -Wall -Wextra -O2 -I/usr/local/include src/sm2_file.c \
    -L/usr/local/lib -Wl,-rpath,/usr/local/lib -lgmssl -o sm2_file
./sm2_file encrypt sm2_public.pem sn.txt sn.enc
./sm2_file decrypt private/sm2_private.pem sn.enc sn2.txt
diff sn.txt sn2.txt
printf 'diff exit code = 0 (files identical)\n'
./sm2_file sign private/sm2_private.pem sn.txt sn.sig
./sm2_file verify sm2_public.pem sn.txt sn.sig
