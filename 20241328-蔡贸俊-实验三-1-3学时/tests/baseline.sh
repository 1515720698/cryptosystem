#!/usr/bin/env bash
set -eu
export LC_ALL=C
ulimit -c 0
cd "$(dirname "$0")/.."
cat /etc/os-release
uname -m
uname -r
gcc --version | sed -n '1p'
make --version | sed -n '1p'
sha256sum -c vendor/SHA256SUMS
make -B build/skf-original build/sdf-original
file build/skf-original build/sdf-original
ldd build/skf-original
for d in /dev/bus/usb /sys/bus/usb/devices; do
    if [ ! -d "$d" ]; then printf 'Not visible: %s\n' "$d"; fi
done
run() {
    local rc=0
    printf '\n$ %s\n' "$*"
    "$@" || rc=$?
    printf 'exit=%s\n' "$rc"
}
run timeout 15s build/skf-original
if command -v gdb >/dev/null; then
    run timeout 15s gdb -nx -batch -ex 'set debuginfod enabled off' \
        -ex run -ex bt --args build/skf-original
fi
run build/sdf-original
