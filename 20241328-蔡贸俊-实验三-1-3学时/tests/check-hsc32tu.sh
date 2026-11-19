#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
sdk=$(realpath "${1:?usage: bash tests/check-hsc32tu.sh EXTRACTED_SDK_DIR}")
lib="$sdk/so/Linux_x86_64"
mkdir -p build
gcc -std=c11 -Wall -Wextra -Werror -I"$sdk/include" tests/hsc32tu-check.c \
    -L"$lib" -Wl,-rpath,"$lib" -lhsctu_guomi_vpn -o build/hsc32tu-check
ldd build/hsc32tu-check | grep libhsctu
nm -D --defined-only "$lib/libhsctu_guomi_vpn.so" |
    grep -E ' SDF_(OpenDevice|OpenSession|GenerateRandom|GetDeviceInfo|GetDeviceSN|CloseSession|CloseDevice)$'
for i in {1..12}; do
    for d in /sys/bus/usb/devices/*; do
        [[ -r $d/idVendor && -r $d/idProduct ]] || continue
        if [[ $(cat "$d/idVendor"):$(cat "$d/idProduct") == 096e:082e &&
              -r $d/busnum && -r $d/devnum ]]; then
            printf -v node '/dev/bus/usb/%03d/%03d' "$(cat "$d/busnum")" "$(cat "$d/devnum")"
            if [[ -c $node ]]; then
                printf 'HSC32TU USB 096e:082e node=%s\n' "$node"
                rc=0
                timeout 20s ./build/hsc32tu-check || rc=$?
                printf 'Probe exit=%s\n' "$rc"
                exit "$rc"
            fi
        fi
    done
    sleep 1
done
echo 'HSC32TU USB node did not appear.'
exit 3
