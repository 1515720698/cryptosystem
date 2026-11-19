#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
make -B build/skf-state build/skf-state-mock
run() {
    local expected=$1 needle=$2 rc=0 output
    shift 2
    printf '\n$ %s\n' "$*"
    output=$("$@" 2>&1) || rc=$?
    printf '%s\nexit=%s\n' "$output" "$rc"
    test "$rc" -eq "$expected"
    [[ $output == *"$needle"* ]]
}
if [[ ! -r /dev/bus/usb && ! -r /sys/bus/usb/devices ]]; then
    run 3 'vendor API not called' build/skf-state
else
    printf 'USB bus visible; use build/skf-state for a manual hardware check.\n'
fi
run 0 'PRESENT (0x00000001)' build/skf-state-mock
run 0 'ABSENT (0x00000000)' build/skf-state-mock mock-absent
run 0 'UNKNOWN (0x00000002)' build/skf-state-mock mock-unknown
run 1 'failed: 0x0a000001' build/skf-state-mock invalid
run 2 'Usage:' build/skf-state-mock name extra
printf '\nSKF checks passed (hardware not asserted).\n'
