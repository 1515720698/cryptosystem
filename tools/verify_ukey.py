"""Windows x64 GM3000 SKF public-operation tests. No PIN or persistent objects.

ABI follows the archived vendor skf/skfapi.h (pack=1, ULONG=uint32).
All keys in this test are public fixtures, not user token private keys.
"""
import ctypes as C
import datetime
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
SDK = ROOT / 'materials/GM3000_SDK_reference/longmaiskf0016-stu'
U32 = C.c_uint32
PTR = C.c_void_p
BYTE = C.c_ubyte


class BlockParam(C.Structure):
    _pack_ = 1
    _fields_ = [('iv', BYTE * 32), ('iv_len', U32), ('padding', U32), ('feedback', U32)]


class EccPublic(C.Structure):
    _pack_ = 1
    _fields_ = [('bits', U32), ('x', BYTE * 64), ('y', BYTE * 64)]


def main():
    assert sys.platform == 'win32' and C.sizeof(PTR) == 8
    dll = ROOT / 'materials/GM3000_runtime/mtoken_gm3000.dll'
    if not dll.is_file():
        dll = SDK / 'skf/windows/x64/mtoken_gm3000.dll'
    api = C.WinDLL(str(dll))
    signatures = {
        'SKF_EnumDev': [C.c_int, PTR, C.POINTER(U32)],
        'SKF_ConnectDev': [C.c_char_p, C.POINTER(PTR)],
        'SKF_DisConnectDev': [PTR], 'SKF_CloseHandle': [PTR],
        'SKF_DigestInit': [PTR, U32, PTR, PTR, U32, C.POINTER(PTR)],
        'SKF_Digest': [PTR, PTR, U32, PTR, C.POINTER(U32)],
        'SKF_SetSymmKey': [PTR, PTR, U32, C.POINTER(PTR)],
        'SKF_EncryptInit': [PTR, BlockParam],
        'SKF_DecryptInit': [PTR, BlockParam],
        'SKF_Encrypt': [PTR, PTR, U32, PTR, C.POINTER(U32)],
        'SKF_Decrypt': [PTR, PTR, U32, PTR, C.POINTER(U32)],
        'SKF_ExtECCEncrypt': [PTR, C.POINTER(EccPublic), PTR, U32, PTR],
    }
    for name, args in signatures.items():
        fn = getattr(api, name)
        fn.argtypes, fn.restype = args, U32
    calls, checks = [], []

    def call(name, *args):
        rv = int(getattr(api, name)(*args))
        calls.append({'function': name, 'rv': f'0x{rv:08x}'})
        print(f'{name}: 0x{rv:08x}', flush=True)
        if rv:
            raise RuntimeError(f'{name} failed: 0x{rv:08x}')

    def check(name, condition, **detail):
        assert condition, name
        checks.append({'name': name, 'passed': True, **detail})
        print('PASS ' + name, flush=True)

    dev, handles = PTR(), []
    result = {'started_at': datetime.datetime.now().astimezone().isoformat(),
              'dll': str(dll.relative_to(ROOT)), 'dll_sha256': hashlib.sha256(dll.read_bytes()).hexdigest(),
              'abi': 'Windows x64, stdcall, ULONG=32bit, struct pack=1',
              'pin_used': False, 'persistent_key_objects_created': False,
              'calls': calls, 'checks': checks}
    try:
        names, size = C.create_string_buffer(4096), U32(4096)
        call('SKF_EnumDev', 1, names, C.byref(size))
        devices = [x for x in names.raw[:size.value].split(b'\0') if x]
        if not devices:
            raise RuntimeError('No UKey present: insert initialized GM3000')
        result['device_count'] = len(devices)
        call('SKF_ConnectDev', devices[0], C.byref(dev))
        for length in (3, 1, 55, 56, 63, 64, 65, 1024):
            message = b'abc' if length == 3 else bytes((37*i+11) % 256 for i in range(length))
            h = PTR()
            call('SKF_DigestInit', dev, 1, None, None, 0, C.byref(h))
            handles.append(h)
            digest, out_len = C.create_string_buffer(32), U32(32)
            call('SKF_Digest', h, C.create_string_buffer(message), len(message), digest, C.byref(out_len))
            actual = digest.raw[:out_len.value]
            (ROOT / f'data/ukey_sm3_{length}.bin').write_bytes(actual)
            (ROOT / f'data/ukey_msg_{length}.bin').write_bytes(message)
            check(f'SM3 UKey vs independent hashlib length={length}', actual == hashlib.new('sm3', message).digest(), digest=actual.hex())
            call('SKF_CloseHandle', h)
            handles.pop()

        key = bytes.fromhex('0123456789abcdeffedcba9876543210')
        h = PTR()
        call('SKF_SetSymmKey', dev, C.create_string_buffer(key), 0x401, C.byref(h))
        handles.append(h)
        for i in range(4):
            message = key if i == 0 else bytes((19*j+31*i) % 256 for j in range(16))
            param = BlockParam()
            call('SKF_EncryptInit', h, param)
            out, size = C.create_string_buffer(64), U32(64)
            call('SKF_Encrypt', h, C.create_string_buffer(message), 16, out, C.byref(size))
            cipher = out.raw[:size.value]
            check(f'SM4 UKey ciphertext length case={i}', len(cipher) == 16)
            if i == 0:
                check('SM4 UKey standard vector', cipher.hex() == '681edf34d206965e86b3e94f536e4246', ciphertext=cipher.hex())
            (ROOT / f'data/ukey_sm4_plain_{i}.bin').write_bytes(message)
            (ROOT / f'data/ukey_sm4_cipher_{i}.bin').write_bytes(cipher)
            call('SKF_DecryptInit', h, param)
            size = U32(64)
            call('SKF_Decrypt', h, C.create_string_buffer(cipher), len(cipher), out, C.byref(size))
            check(f'SM4 UKey recover case={i}', out.raw[:size.value] == message)
        call('SKF_CloseHandle', h)
        handles.pop()

        # d=1, public key=G. SKF 512-bit coordinate slots hold 256-bit values
        # right-aligned. ECCCIPHERBLOB has 64+64+32+4 bytes before Cipher[].
        pub = EccPublic()
        pub.bits = 256
        gx = bytes.fromhex('32c4ae2c1f1981195f9904466a39c9948fe30bbff2660be1715a4589334c74c7')
        gy = bytes.fromhex('bc3736a2f4f6779c59bdcee36b692153d0a9877cc62a474002df32e52139f0a0')
        pub.x[:] = b'\0'*32 + gx
        pub.y[:] = b'\0'*32 + gy
        message = '20241328 蔡贸俊'.encode('utf-8')
        (ROOT / 'data/ukey_sm2_message.bin').write_bytes(message)
        for i in range(3):
            blob = C.create_string_buffer(164 + len(message))
            call('SKF_ExtECCEncrypt', dev, C.byref(pub), C.create_string_buffer(message), len(message), blob)
            raw = blob.raw
            length = struct.unpack_from('<I', raw, 160)[0]
            check(f'SM2 SKF blob length case={i}', length == len(message), cipher_length=length)
            cipher = raw[32:64] + raw[96:128] + raw[128:160] + raw[164:164+length]
            (ROOT / f'data/ukey_sm2_{i}.raw').write_bytes(cipher)
            (ROOT / f'data/ukey_sm2_{i}.skfblob').write_bytes(raw)
        result['status'] = 'hardware_operations_completed_crosscheck_required'
    except Exception as exc:
        result['status'], result['error'] = 'failed', str(exc)
        raise
    finally:
        for h in handles:
            call('SKF_CloseHandle', h)
        if dev.value:
            call('SKF_DisConnectDev', dev)
        result['finished_at'] = datetime.datetime.now().astimezone().isoformat()
        (ROOT / 'logs/ukey_results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        (ROOT / f'logs/ukey_run_{stamp}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
