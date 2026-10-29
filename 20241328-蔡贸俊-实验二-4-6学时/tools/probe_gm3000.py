"""Read-only PKCS#11 token discovery for the GM3000 UKey.

This script does not open a session, request a PIN, create objects, or alter
the token. It only initializes the vendor PKCS#11 module long enough to list
token-present slots and their public token metadata.
"""

from __future__ import annotations

import ctypes
import json
import sys
from ctypes import POINTER, Structure, byref, c_ubyte, c_ulong, c_void_p
from pathlib import Path

CKR_OK = 0


class CK_TOKEN_INFO(Structure):
    _fields_ = [
        ("label", c_ubyte * 32),
        ("manufacturer_id", c_ubyte * 32),
        ("model", c_ubyte * 16),
        ("serial_number", c_ubyte * 16),
        ("flags", c_ulong),
        ("max_session_count", c_ulong),
        ("session_count", c_ulong),
        ("max_rw_session_count", c_ulong),
        ("rw_session_count", c_ulong),
        ("max_pin_len", c_ulong),
        ("min_pin_len", c_ulong),
        ("total_public_memory", c_ulong),
        ("free_public_memory", c_ulong),
        ("total_private_memory", c_ulong),
        ("free_private_memory", c_ulong),
        ("hardware_version_major", c_ubyte),
        ("hardware_version_minor", c_ubyte),
        ("firmware_version_major", c_ubyte),
        ("firmware_version_minor", c_ubyte),
        ("utc_time", c_ubyte * 16),
    ]


def text(value: object) -> str:
    return bytes(value).decode("ascii", "replace").rstrip(" \0")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: probe_gm3000.py <pkcs11-dll> <result-json>", file=sys.stderr)
        return 2
    dll_path = Path(sys.argv[1])
    output = Path(sys.argv[2])
    if not dll_path.is_file():
        print(f"PKCS#11 DLL not found: {dll_path}", file=sys.stderr)
        return 2

    # WinDLL preserves the vendor module's WINAPI calling convention.
    module = ctypes.WinDLL(str(dll_path))
    initialize = module.C_Initialize
    initialize.argtypes = [c_void_p]
    initialize.restype = c_ulong
    finalize = module.C_Finalize
    finalize.argtypes = [c_void_p]
    finalize.restype = c_ulong
    get_slot_list = module.C_GetSlotList
    get_slot_list.argtypes = [c_ubyte, POINTER(c_ulong), POINTER(c_ulong)]
    get_slot_list.restype = c_ulong
    get_token_info = module.C_GetTokenInfo
    get_token_info.argtypes = [c_ulong, POINTER(CK_TOKEN_INFO)]
    get_token_info.restype = c_ulong

    rv = initialize(None)
    if rv != CKR_OK:
        output.write_text(json.dumps({"initialize_rv": f"0x{rv:08x}"}, indent=2), encoding="utf-8")
        print(f"C_Initialize failed: 0x{rv:08x}", file=sys.stderr)
        return 1
    try:
        count = c_ulong()
        rv = get_slot_list(1, None, byref(count))
        if rv != CKR_OK:
            raise RuntimeError(f"C_GetSlotList(count) failed: 0x{rv:08x}")
        slots = (c_ulong * count.value)()
        rv = get_slot_list(1, slots, byref(count))
        if rv != CKR_OK:
            raise RuntimeError(f"C_GetSlotList(values) failed: 0x{rv:08x}")
        tokens = []
        for slot in slots:
            info = CK_TOKEN_INFO()
            rv = get_token_info(slot, byref(info))
            if rv != CKR_OK:
                tokens.append({"slot": int(slot), "token_info_rv": f"0x{rv:08x}"})
                continue
            tokens.append(
                {
                    "slot": int(slot),
                    "label": text(info.label),
                    "manufacturer": text(info.manufacturer_id),
                    "model": text(info.model),
                    "serial_number": text(info.serial_number),
                    "flags": f"0x{info.flags:08x}",
                    "hardware_version": f"{info.hardware_version_major}.{info.hardware_version_minor}",
                    "firmware_version": f"{info.firmware_version_major}.{info.firmware_version_minor}",
                }
            )
        result = {"module": str(dll_path), "token_present_slots": tokens}
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    finally:
        finalize(None)


if __name__ == "__main__":
    raise SystemExit(main())
