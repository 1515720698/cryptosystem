"""Run in openEuler; compile textbook implementations and compare all outputs.

For hardware tests, first run verify_ukey.py from Windows. This script reads
those actual saved outputs without requiring USB passthrough into WSL.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import platform
import shlex
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
os.environ['LC_ALL'] = 'C.UTF-8'
LOG, CHECKS = [], []


def flush():
    (ROOT / 'logs/crosscheck.log').write_text('\n'.join(LOG)+'\n', encoding='utf-8')


def run(args, expected=0, quiet=False):
    p = subprocess.run([str(x) for x in args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = p.stdout.decode('utf-8', errors='replace')
    LOG.extend(['$ '+shlex.join([str(x) for x in args]), text.rstrip(), f'[exit={p.returncode}]'])
    flush()
    if not quiet:
        print(LOG[-3], flush=True)
        print(text.rstrip(), flush=True)
    assert p.returncode == expected, (args, p.returncode, expected)
    return text


def check(name, condition, category):
    assert condition, name
    CHECKS.append({'name': name, 'category': category, 'passed': True})
    LOG.append('PASS '+name)
    print('PASS '+name, flush=True)
    flush()


def tlv(tag, body):
    n = len(body)
    b = n.to_bytes(max(1, (n.bit_length()+7)//8), 'big')
    length = bytes([n]) if n < 128 else bytes([0x80+len(b)])+b
    return bytes([tag])+length+body


def raw_to_der(raw):
    assert len(raw) > 96
    def integer(value):
        value = value.lstrip(b'\0') or b'\0'
        if value[0] & 128:
            value = b'\0'+value
        return tlv(2, value)
    return tlv(48, integer(raw[:32])+integer(raw[32:64])+tlv(4, raw[64:96])+tlv(4, raw[96:]))


def der_to_raw(data):
    def item(buf, offset):
        tag, n = buf[offset:offset+2]
        offset += 2
        if n & 128:
            size = n & 127
            n = int.from_bytes(buf[offset:offset+size], 'big')
            offset += size
        assert offset+n <= len(buf)
        return tag, buf[offset:offset+n], offset+n
    tag, body, end = item(data, 0)
    assert tag == 48 and end == len(data)
    offset, fields = 0, []
    for expected in (2, 2, 4, 4):
        tag, value, offset = item(body, offset)
        assert tag == expected
        fields.append(value)
    assert offset == len(body) and len(fields[2]) == 32
    x, y = [value.lstrip(b'\0') for value in fields[:2]]
    assert len(x) <= 32 and len(y) <= 32
    return x.rjust(32, b'\0')+y.rjust(32, b'\0')+fields[2]+fields[3]


def read(name):
    return (ROOT / name).read_bytes()


def main():
    for folder in ('build', 'logs', 'data'):
        (ROOT / folder).mkdir(exist_ok=True)
    run(['python3', 'tools/prepare_textbook_sources.py'])
    run(['uname', '-a'])
    run(['cat', '/etc/os-release'])
    run(['gcc', '--version'], quiet=True)
    run(['gmssl', 'version'])
    builds = [
        ['g++', '-std=c++17', '-O2', '-g', '-Wall', '-Wextra', '-I', 'src', '-I', 'src/textbook/sm3', 'src/textbook/sm3/sm3.cpp', 'src/sm3_driver.cpp', '-o', 'build/textbook_sm3'],
        ['g++', '-std=c++17', '-O2', '-g', '-Wall', '-Wextra', '-I', 'src', '-I', 'src/textbook/sm4', 'src/textbook/sm4/sm4.cpp', 'src/sm4_driver.cpp', '-o', 'build/textbook_sm4'],
        ['gcc', '-O2', '-g', '-std=c11', '-Wall', '-Wextra', '-fcommon', '-fno-strict-aliasing', '-I', 'src', '-I', 'src/miracl', '-I', 'src/textbook/sm2', 'src/textbook/sm2/SM2_ENC.c', 'src/textbook/sm2/kdf.c', 'src/sm2_driver.c', *[str(x.relative_to(ROOT)) for x in sorted((ROOT/'src/miracl').glob('mr*.c'))], '-lm', '-o', 'build/textbook_sm2'],
        ['gcc', '-O2', 'src/test_key.c', '-lgmssl', '-o', 'build/test_key'],
    ]
    build_log = []
    for args in builds:
        build_log.append(run(args, quiet=True))
    (ROOT/'logs/build_current.log').write_text('\n'.join(build_log), encoding='utf-8')
    run(['file', 'build/textbook_sm2', 'build/textbook_sm3', 'build/textbook_sm4'])
    selftest = run(['build/textbook_sm2'])
    check('Textbook SM2 official selftest return=0', 'selftest return=0' in selftest, 'software')
    run(['build/test_key'])
    key = '0123456789abcdeffedcba9876543210'
    for length in (0, 1, 3, 55, 56, 63, 64, 65, 127, 128, 1024):
        message = b'abc' if length == 3 else bytes((37*i+11)%256 for i in range(length))
        name = f'data/soft_msg_{length}.bin'
        (ROOT/name).write_bytes(message)
        out, gm = f'data/soft_sm3_{length}.bin', f'data/gmssl_sm3_{length}.bin'
        run(['build/textbook_sm3', name, out], quiet=True)
        run(['gmssl', 'sm3', '-in', name, '-bin', '-out', gm], quiet=True)
        check(f'SM3 textbook=GmSSL length={length}', read(out) == read(gm), 'software')
        if (ROOT/f'data/ukey_sm3_{length}.bin').is_file():
            check(f'SM3 UKey=textbook=GmSSL length={length}', read(f'data/ukey_msg_{length}.bin') == message and read(out) == read(f'data/ukey_sm3_{length}.bin'), 'hardware')
    for i in range(8):
        message = bytes.fromhex(key) if i == 0 else bytes((19*j+31*i)%256 for j in range(16))
        name = f'data/soft_sm4_plain_{i}.bin'
        (ROOT/name).write_bytes(message)
        out, gm, recovered = f'data/soft_sm4_cipher_{i}.bin', f'data/gmssl_sm4_cipher_{i}.bin', f'data/soft_sm4_recovered_{i}.bin'
        run(['build/textbook_sm4', 'enc', name, out], quiet=True)
        run(['gmssl', 'sm4_ecb', '-encrypt', '-key', key, '-in', name, '-out', gm], quiet=True)
        check(f'SM4 textbook=GmSSL case={i}', read(out) == read(gm), 'software')
        run(['build/textbook_sm4', 'dec', gm, recovered], quiet=True)
        check(f'SM4 GmSSL->textbook recover case={i}', read(recovered) == message, 'software')
        if i < 4:
            check(f'SM4 UKey=textbook=GmSSL case={i}', read(f'data/ukey_sm4_plain_{i}.bin') == message and read(out) == read(f'data/ukey_sm4_cipher_{i}.bin'), 'hardware')
        if i == 0:
            check('SM4 published standard ciphertext', read(out).hex() == '681edf34d206965e86b3e94f536e4246', 'software')
    # Unique failure destinations avoid stale plaintext from prior successes.
    for name in ('rejected_sm4.bin', 'rejected_c3.bin', 'rejected_short.bin'):
        (ROOT/'data'/name).unlink(missing_ok=True)
    run(['build/textbook_sm4', 'enc', 'data/soft_msg_3.bin', 'data/rejected_sm4.bin'], expected=2, quiet=True)
    check('SM4 invalid block rejected without output', not (ROOT/'data/rejected_sm4.bin').exists(), 'software')
    msg = '20241328 蔡贸俊'.encode('utf-8')
    (ROOT/'data/soft_sm2_message.bin').write_bytes(msg)
    for i in range(3):
        raw, der = f'data/soft_sm2_{i}.raw', f'data/soft_sm2_{i}.der'
        run(['build/textbook_sm2', 'enc', 'data/soft_sm2_message.bin', raw], quiet=True)
        (ROOT/der).write_bytes(raw_to_der(read(raw)))
        plain = f'data/gmssl_from_textbook_{i}.bin'
        run(['gmssl', 'sm2decrypt', '-key', 'data/test_private.pem', '-pass', 'lab2-test-only', '-in', der, '-out', plain], quiet=True)
        check(f'SM2 textbook encrypt->GmSSL decrypt trial={i}', read(plain) == msg, 'software')
        gmder, gmraw, out = f'data/gmssl_sm2_{i}.der', f'data/gmssl_sm2_{i}.raw', f'data/textbook_from_gmssl_{i}.bin'
        run(['gmssl', 'sm2encrypt', '-pubkey', 'data/test_public.pem', '-in', 'data/soft_sm2_message.bin', '-out', gmder], quiet=True)
        (ROOT/gmraw).write_bytes(der_to_raw(read(gmder)))
        run(['build/textbook_sm2', 'dec', gmraw, out], quiet=True)
        check(f'SM2 GmSSL encrypt->textbook decrypt trial={i}', read(out) == msg, 'software')
        ukraw = f'data/ukey_sm2_{i}.raw'
        ukder, uksoft, ukgm = f'data/ukey_sm2_{i}.der', f'data/textbook_from_ukey_{i}.bin', f'data/gmssl_from_ukey_{i}.bin'
        (ROOT/ukder).write_bytes(raw_to_der(read(ukraw)))
        run(['build/textbook_sm2', 'dec', ukraw, uksoft], quiet=True)
        run(['gmssl', 'sm2decrypt', '-key', 'data/test_private.pem', '-pass', 'lab2-test-only', '-in', ukder, '-out', ukgm], quiet=True)
        check(f'SM2 UKey encrypt->textbook decrypt trial={i}', read(uksoft) == read('data/ukey_sm2_message.bin') == msg, 'hardware')
        check(f'SM2 UKey encrypt->GmSSL decrypt trial={i}', read(ukgm) == msg, 'hardware')
    check('SM2 UKey encryption produced distinct ciphertexts', len({read(f'data/ukey_sm2_{i}.raw') for i in range(3)}) == 3, 'hardware')
    bad = bytearray(read('data/ukey_sm2_0.raw'))
    bad[64] ^= 1
    (ROOT/'data/bad_c3.raw').write_bytes(bad)
    failed = run(['build/textbook_sm2', 'dec', 'data/bad_c3.raw', 'data/rejected_c3.bin'], expected=1, quiet=True)
    check('SM2 C3 tamper rejected rc=6 without plaintext file', 'return=6' in failed and not (ROOT/'data/rejected_c3.bin').exists(), 'software')
    run(['build/textbook_sm2', 'dec', 'data/soft_msg_3.bin', 'data/rejected_short.bin'], expected=2, quiet=True)
    check('SM2 truncated ciphertext rejected without output', not (ROOT/'data/rejected_short.bin').exists(), 'software')
    # Undefined-shift fixes are checked under UBSan on boundary messages.
    for alg in ('sm3', 'sm4'):
        args = builds[0 if alg == 'sm3' else 1].copy()
        args[args.index('-O2')] = '-O1'
        args += ['-fsanitize=undefined', '-fno-sanitize-recover=undefined']
        args[args.index('-o')+1] = 'build/'+alg+'_ubsan'
        run(args, quiet=True)
        if alg == 'sm3':
            run(['build/sm3_ubsan', 'data/soft_msg_65.bin', 'data/ubsan_sm3.bin'], quiet=True)
        else:
            run(['build/sm4_ubsan', 'enc', 'data/soft_sm4_plain_0.bin', 'data/ubsan_sm4.bin'], quiet=True)
        check(f'{alg.upper()} representative input UBSan passed', True, 'software')
    totals = {kind: sum(x['category'] == kind for x in CHECKS) for kind in ('software', 'hardware')}
    result = {'time': datetime.datetime.now().astimezone().isoformat(), 'platform': platform.platform(),
              'passed': len(CHECKS), 'totals': totals, 'checks': CHECKS,
              'hardware_scope': 'SKF SM3 digest, SM4 ECB encrypt/decrypt, SM2 external public-key encryption (d=1 fixture); no token private key/PIN operation',
              'input_output_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'data').iterdir()) if p.is_file() and p.suffix != '.pem'}}
    (ROOT/'logs/crosscheck_results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'ALL {len(CHECKS)} CHECKS PASSED: {totals}', flush=True)
    LOG.append(f'ALL {len(CHECKS)} CHECKS PASSED: {totals}')
    flush()


if __name__ == '__main__':
    main()
