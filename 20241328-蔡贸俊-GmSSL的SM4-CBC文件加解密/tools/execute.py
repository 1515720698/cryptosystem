"""Run on openEuler; preserve commands, real output and exit status."""
from pathlib import Path
import hashlib
import shlex
import subprocess

root = Path(__file__).resolve().parent.parent
logdir = root / 'logs'
logdir.mkdir(exist_ok=True)
original = Path('/root/hash_hw/sn.txt').read_bytes()
numbers = original.decode('ascii').splitlines()
assert len(numbers) == len(set(numbers)) == 29
assert all(len(n) == 8 and n.isdigit() for n in numbers)
assert numbers[-1] == '20241328'
(root / 'sn.txt').write_bytes(original)
(logdir / 'input-source.txt').write_text(
    'Source: /root/hash_hw/sn.txt (previous classroom exercise)\n'
    f'SHA256: {hashlib.sha256(original).hexdigest()}\n'
    'Copied unchanged; 29 unique eight-digit student IDs; last: 20241328.\n',
    encoding='utf-8')

commands = [
    ['date', '-Iseconds'], ['cat', '/etc/os-release'], ['uname', '-m'],
    ['gcc', '--version'], ['gmssl', 'version'],
    ['file', '/usr/local/lib/libgmssl.so'],
    ['python3', '-c', "from pathlib import Path; a=Path('sn.txt').read_text().splitlines(); assert len(a)==len(set(a))==29; assert all(len(x)==8 and x.isdigit() for x in a); assert a[-1]=='20241328'; print('ID validation: PASS; count=29; last='+a[-1])"],
    ['cat', 'sn.txt'],
    ['gcc', '-std=c11', '-Wall', '-Wextra', '-O2', '-I/usr/local/include',
     'src/sm4_file.c', '-L/usr/local/lib', '-Wl,-rpath,/usr/local/lib', '-lgmssl', '-o', 'sm4_file'],
    ['file', 'sm4_file'], ['./sm4_file'],
    ['wc', '-c', 'sn.txt', 'sn.enc', 'sn2.txt', 'key.bin', 'iv.bin'],
    ['diff', 'sn.txt', 'sn2.txt'], ['sha256sum', 'sn.txt', 'sn2.txt'],
]
with (logdir / 'practice.txt').open('w', encoding='utf-8', newline='\n') as log:
    for cmd in commands:
        heading = '$ ' + shlex.join(cmd) + '\n'
        result = subprocess.run(cmd, cwd=root, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True)
        record = heading + result.stdout + f'[exit code: {result.returncode}]\n\n'
        print(record, end='')
        log.write(record)
        log.flush()
        if result.returncode:
            raise SystemExit(result.returncode)

# Independent CLI decryption checks file format and library/CLI compatibility.
key = (root / 'key.bin').read_bytes().hex()
iv = (root / 'iv.bin').read_bytes().hex()
cross = ['gmssl', 'sm4_cbc', '-decrypt', '-key', key, '-iv', iv,
         '-pkcs7_padding', '-in', 'sn.enc', '-out', 'logs/sn_cli.txt']
with (logdir / 'cross-check.txt').open('w', encoding='utf-8') as log:
    for cmd in [cross, ['diff', 'sn.txt', 'logs/sn_cli.txt']]:
        r = subprocess.run(cmd, cwd=root, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True)
        record = '$ ' + shlex.join(cmd) + '\n' + r.stdout + f'[exit code: {r.returncode}]\n'
        print(record, end='')
        log.write(record)
        if r.returncode:
            raise SystemExit(r.returncode)
