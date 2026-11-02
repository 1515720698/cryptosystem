"""Direct Windows CryptoAPI verification via ctypes; no third-party packages."""
import ctypes as C
from ctypes import wintypes as W
import hashlib
import platform
from pathlib import Path

api = C.WinDLL('advapi32', use_last_error=True)
H = C.c_size_t
D = W.DWORD
P = C.POINTER
def bind(name, args):
    f = getattr(api, name)
    f.argtypes, f.restype = args, W.BOOL
    return f
acquire = bind('CryptAcquireContextW', [P(H), W.LPCWSTR, W.LPCWSTR, D, D])
create = bind('CryptCreateHash', [H, D, H, D, P(H)])
update = bind('CryptHashData', [H, C.c_void_p, D, D])
get = bind('CryptGetHashParam', [H, D, C.c_void_p, P(D), D])
destroy = bind('CryptDestroyHash', [H])
release = bind('CryptReleaseContext', [H, D])
lines = []
def log(text):
    print(text)
    lines.append(text)
def check(result):
    if not result:
        raise C.WinError(C.get_last_error())
provider = 'Microsoft Enhanced RSA and AES Cryptographic Provider'
log('OS: ' + platform.platform())
log('Python: ' + platform.python_version() + ', direct Advapi32.dll calls')
log('Command: python code/verify_cryptoapi.py')
log('Provider: ' + provider)
ctx = H()
check(acquire(C.byref(ctx), None, provider, 24, 0xF0000000))
try:
    for label, message in [('abc', b'abc'), ('LF', b'abc\n'), ('CRLF', b'abc\r\n')]:
        h = H()
        check(create(ctx, 0x800C, 0, 0, C.byref(h)))
        try:
            check(update(h, message, len(message), 0))
            if label == 'abc':
                small = C.create_string_buffer(1)
                n = D(1)
                ok = get(h, 2, small, C.byref(n), 0)
                error = C.get_last_error()
                log(f'Small buffer: ok={bool(ok)}, error={error}, required={n.value}')
                assert not ok and error == 234 and n.value == 32
            n = D(0)
            check(get(h, 2, None, C.byref(n), 0))
            buf = C.create_string_buffer(n.value)
            check(get(h, 2, buf, C.byref(n), 0))
            digest = buf.raw[:n.value].hex()
            assert digest == hashlib.sha256(message).hexdigest()
            log(f'{label}: bytes={len(message)}, SHA256={digest}, cross-check=PASS')
        finally:
            check(destroy(h))
finally:
    check(release(ctx, 0))
bad = H()
ok = acquire(C.byref(bad), None, provider, 1, 0xF0000000)
error = C.get_last_error() & 0xFFFFFFFF
if ok:
    release(bad, 0)
log(f'Mismatched provider type: ok={bool(ok)}, error=0x{error:08X}')
assert not ok and error == 0x8009001B
log('ALL CHECKS PASSED; hash handles and provider context released.')
out = Path(__file__).resolve().parents[1] / 'evidence'
out.mkdir(exist_ok=True)
(out / 'experiment-log.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
