"""Read-only physical-device check using the course SDK's Windows x64 DLL."""
import ctypes as C
import sys
from pathlib import Path

dll = C.WinDLL(str(Path(sys.argv[1]).resolve()))
uint = C.c_uint32
enum = dll.SKF_EnumDev
enum.argtypes = [C.c_int, C.c_char_p, C.POINTER(uint)]
enum.restype = uint
state = dll.SKF_GetDevState
state.argtypes = [C.c_char_p, C.POINTER(uint)]
state.restype = uint

buf = C.create_string_buffer(4096)
length = uint(len(buf))
rc = enum(1, buf, C.byref(length))
print(f"SKF_EnumDev: ret=0x{rc:08x}, size={length.value}")
if rc or length.value > len(buf):
    sys.exit(1)
names = [name for name in buf.raw[:length.value].split(b"\0") if name]
print(f"Present device names returned: {len(names)} (names omitted)")
if not names:
    sys.exit(3)
ok = True
for i, name in enumerate(names, 1):
    value = uint(2)
    rc = state(name, C.byref(value))
    print(f"SKF_GetDevState(device #{i}): ret=0x{rc:08x}, state=0x{value.value:08x}")
    ok = ok and rc == 0 and value.value == 1
sys.exit(0 if ok else 1)
