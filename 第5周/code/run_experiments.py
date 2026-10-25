"""Run reproducible CLI/C RSA signature tests. Python standard library only.

Set OPENSSL_BIN, CC, OPENSSL_HOME, TEMP_WORK_ROOT as needed.
OPENSSL_HOME on Windows points to the SDK folder containing include/ and bin/.
"""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
OPENSSL = os.environ.get('OPENSSL_BIN', 'openssl')
CC = os.environ.get('CC', 'gcc')
SDK = os.environ.get('OPENSSL_HOME')
WORK_ROOT = Path(os.environ.get('TEMP_WORK_ROOT', str(ROOT / 'evidence')))
if not WORK_ROOT.is_dir():
    raise SystemExit('TEMP_WORK_ROOT must already exist')
log = ['第五周实际运行记录：AI 助手执行，故障均为主动构造的复现验证。',
       f'Platform: {platform.platform()}', '']
checks = []

def run(args, expected=0):
    log.append('$ ' + subprocess.list2cmdline([str(a) for a in args]))
    p = subprocess.run([str(a) for a in args], cwd=work, capture_output=True)
    for data in (p.stdout, p.stderr):
        if data:
            log.append(data.decode('utf-8', errors='replace').rstrip())
    log.append(f'[exit={p.returncode}]\n')
    if p.returncode != expected:
        raise RuntimeError(f'Unexpected exit: {p.returncode}, expected {expected}')
    return p.stdout

def check(label, condition):
    checks.append({'test': label, 'passed': bool(condition)})
    log.append(('PASS: ' if condition else 'FAIL: ') + label)
    if not condition:
        raise AssertionError(label)

PSS = ['-sigopt', 'rsa_padding_mode:pss', '-sigopt', 'rsa_pss_saltlen:32',
       '-sigopt', 'rsa_mgf1_md:sha256']

try:
    with tempfile.TemporaryDirectory(prefix='week5-', dir=WORK_ROOT) as td:
        work = Path(td)
        run([OPENSSL, 'version'])
        message = b'Week5 digital signature\n20241328 Cai Maojun\n'
        (work / 'message.txt').write_bytes(message)
        (work / 'crlf.txt').write_bytes(message.replace(b'\n', b'\r\n'))
        (work / 'tampered.txt').write_bytes(message.replace(b'Week5', b'Week6'))
        for key in ['private.pem', 'other-private.pem']:
            run([OPENSSL, 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:2048', '-out', key])
        for src, dst in [('private.pem','public.pem'), ('other-private.pem','other-public.pem')]:
            run([OPENSSL, 'pkey', '-in', src, '-pubout', '-out', dst])
        def sign(out, source='message.txt', opts=PSS):
            run([OPENSSL, 'dgst', '-sha256', '-sign', 'private.pem', *opts, '-out', out, source])
        def verify(sig='pss1.bin', source='message.txt', key='public.pem', opts=PSS, expected=0):
            run([OPENSSL, 'dgst', '-sha256', '-verify', key, *opts, '-signature', sig, source], expected)
        sign('pss1.bin'); sign('pss2.bin')
        verify(); verify('pss2.bin')
        check('Two randomized PSS signatures differ and both verify',
              (work/'pss1.bin').read_bytes() != (work/'pss2.bin').read_bytes())
        check('RSA-2048 signature is 256 bytes', (work/'pss1.bin').stat().st_size == 256)
        for filename in ['tampered.txt', 'crlf.txt']:
            verify(source=filename, expected=1)
            check(f'Reject changed bytes: {filename}', True)
        verify(key='other-public.pem', expected=1)
        check('Reject unrelated public key', True)
        corrupted = bytearray((work/'pss1.bin').read_bytes()); corrupted[10] ^= 1
        (work/'bad-signature.bin').write_bytes(corrupted)
        verify('bad-signature.bin', expected=1)
        check('Reject modified signature', True)
        verify(opts=['-sigopt','rsa_padding_mode:pkcs1'], expected=1)
        check('Reject PSS signature under PKCS1-v1_5 verification', True)
        verify(opts=['-sigopt','rsa_padding_mode:pss','-sigopt','rsa_pss_saltlen:20',
                     '-sigopt','rsa_mgf1_md:sha256'], expected=1)
        check('Reject mismatched salt length', True)
        verify()
        check('Restore correct PSS parameters: verification succeeds', True)
        run([OPENSSL, 'dgst', '-sha256', '-binary', '-out','digest.bin','message.txt'])
        sign('double-hash.bin', 'digest.bin')
        verify('double-hash.bin', expected=1)
        verify('double-hash.bin', source='digest.bin')
        check('Signing a precomputed digest through dgst hashes it again', True)
        for n in [1,2]: sign(f'v15-{n}.bin', opts=['-sigopt','rsa_padding_mode:pkcs1'])
        verify('v15-1.bin', opts=['-sigopt','rsa_padding_mode:pkcs1'])
        check('PKCS1-v1_5 signatures are deterministic for identical inputs',
              (work/'v15-1.bin').read_bytes() == (work/'v15-2.bin').read_bytes())
        run([CC, '--version'])
        shutil.copyfile(ROOT/'code/rsa_pss.c', work/'rsa_pss.c')
        exe = work / ('rsa_pss.exe' if os.name == 'nt' else 'rsa_pss')
        build = [CC, '-std=c11', '-Wall', '-Wextra', '-Werror', 'rsa_pss.c', '-o', exe]
        if os.name == 'nt' and SDK:
            build += ['-I', str(Path(SDK)/'include'), str(Path(SDK)/'bin/libcrypto-3-x64.dll')]
        else:
            build += ['-lcrypto']
        run(build)
        run([exe, 'sign', 'private.pem','message.txt','c-signature.bin'])
        verify('c-signature.bin')
        check('C EVP signature verifies in OpenSSL CLI', True)
        run([exe, 'verify','public.pem','message.txt','pss1.bin'])
        check('CLI signature verifies in C EVP (7-byte update chunks)', True)
        run([exe, 'verify','public.pem','tampered.txt','pss1.bin'], 1)
        check('C EVP rejects tampered message', True)
        # Keep only public verification fixtures; private keys leave with temp dir.
        for filename in ['message.txt','crlf.txt','tampered.txt','public.pem','pss1.bin','c-signature.bin']:
            shutil.copyfile(work/filename, EVIDENCE/filename)
        metadata = {'message_bytes': len(message), 'crlf_bytes': (work/'crlf.txt').stat().st_size,
                    'signature_bytes': 256, 'message_sha256': hashlib.sha256(message).hexdigest(),
                    'checks': checks}
        (EVIDENCE/'results.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2),encoding='utf-8')
        log.append(f'ALL {len(checks)} CHECKS PASSED')
finally:
    (EVIDENCE/'experiment-log.txt').write_text('\n'.join(log)+'\n', encoding='utf-8')
    print('\n'.join(log))
