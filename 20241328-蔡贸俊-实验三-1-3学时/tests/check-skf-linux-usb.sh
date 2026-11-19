#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
ulimit -c 0
uname -r
rpm -q kmod
udevadm settle --timeout=8 2>/dev/null || true
for i in {1..12}; do
    for dev in /sys/bus/usb/devices/*; do
        [[ -r $dev/idVendor && -r $dev/idProduct ]] || continue
        if [[ $(cat "$dev/idVendor"):$(cat "$dev/idProduct") == 055c:db08 ]]; then
            break 2
        fi
    done
    sleep 1
done
udevadm settle --timeout=8 2>/dev/null || true
found=0
for dev in /sys/bus/usb/devices/*; do
    [[ -r $dev/idVendor && -r $dev/idProduct ]] || continue
    vid=$(cat "$dev/idVendor")
    pid=$(cat "$dev/idProduct")
    [[ $vid:$pid == 055c:db08 ]] || continue
    found=1
    printf 'USB %s:%s path=%s\n' "$vid" "$pid" "${dev##*/}"
    for f in "$dev":*/bInterfaceClass; do
        [[ -r $f ]] || continue
        printf 'bInterfaceClass=%s\n' "$(cat "$f")"
        if [[ -L ${f%/*}/driver ]]; then readlink "${f%/*}/driver"; fi
    done
done
printf 'target_visible=%s\n' "$found"
if ((found)); then
    for i in {1..12}; do
        for f in /sys/class/scsi_generic/sg*/device/vendor; do
            [[ -r $f ]] || continue
            node=${f%/device/vendor}
            if [[ $(cat "$f") == Longmai* && -c /dev/${node##*/} ]]; then
                printf 'Longmai SCSI node: /dev/%s\n' "${node##*/}"
                break 2
            fi
        done
        sleep 1
    done
fi
lsblk -o NAME,TRAN,MODEL
ls -l /dev/sg* /dev/sr* 2>/dev/null || true
run() {
    local rc=0
    printf '\n$ %s\n' "$*"
    "$@" || rc=$?
    printf 'exit=%s\n' "$rc"
}
if ((found)); then
    run timeout 25s ./build/skf-original | sed -E 's/(SerialNumber *:).*/\1 [redacted]/'
fi
run timeout 20s ./build/skf-state | sed -E 's/SKF_GetDevState\([^)]*\)/SKF_GetDevState([redacted])/'
