"""Capture the actual Linux experiment and independent CLI checks."""
from pathlib import Path
import hashlib
import json
import os
import secrets
import shlex
import subprocess

root = Path(__file__).resolve().parent.parent
logs = root / 'logs'
logs.mkdir(exist_ok=True)
private = root / 'private'
private.mkdir(mode=0o700, exist_ok=True)
original = Path('/root/hash_hw/sn.txt').read_bytes()
ids = original.decode('ascii').splitlines()
assert len(ids) == len(set(ids)) == 29
assert all(len(n) == 8 and n.isdigit() for n in ids) and ids[-1] == '20241328'
(root / 'sn.txt').write_bytes(original)
env = os.environ.copy()
env['SM2_PASS'] = secrets.token_urlsafe(24)
password = env['SM2_PASS']
# Retain the local password outside the submission directory, never in logs.
state = Path('/root/.local/state/gmssl-sm2-20241328')
state.mkdir(mode=0o700, parents=True, exist_ok=True)
(state / 'password').write_text(password, encoding='utf-8')
(state / 'password').chmod(0o600)

def run(cmd, log, expected=0):
    shown = ['$SM2_PASS' if x == password else x for x in cmd]
    text = '$ ' + shlex.join(shown).replace("'$SM2_PASS'", '"$SM2_PASS"') + '\n'
    p = subprocess.run(cmd, cwd=root, env=env, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True)
    text += p.stdout.replace(password, '[REDACTED]')
    text += f'[exit code: {p.returncode}; expected: {expected}]\n\n'
    print(text, end='')
    log.write(text)
    log.flush()
    assert p.returncode == expected, cmd[0]

with (logs / 'practice.txt').open('w', encoding='utf-8') as f:
    f.write('SM2_PASS is provided through the execution environment; its value is not logged.\n\n')
    for cmd in [['date', '-Iseconds'], ['cat', '/etc/os-release'], ['uname', '-m'],
                ['gcc', '--version'], ['gmssl', 'version'], ['cat', 'sn.txt'],
                ['gmssl', 'sm2keygen', '-pass', password, '-out', 'private/sm2_private.pem', '-pubout', 'sm2_public.pem'],
                ['head', '-n', '1', 'private/sm2_private.pem'], ['cat', 'sm2_public.pem'],
                ['gcc', '-std=c11', '-Wall', '-Wextra', '-O2', '-I/usr/local/include',
                 'src/sm2_file.c', '-L/usr/local/lib', '-Wl,-rpath,/usr/local/lib', '-lgmssl', '-o', 'sm2_file'],
                ['file', 'sm2_file'],
                ['./sm2_file', 'encrypt', 'sm2_public.pem', 'sn.txt', 'sn.enc'],
                ['./sm2_file', 'decrypt', 'private/sm2_private.pem', 'sn.enc', 'sn2.txt'],
                ['diff', 'sn.txt', 'sn2.txt'],
                ['./sm2_file', 'sign', 'private/sm2_private.pem', 'sn.txt', 'sn.sig'],
                ['./sm2_file', 'verify', 'sm2_public.pem', 'sn.txt', 'sn.sig'],
                ['wc', '-c', 'sn.txt', 'sn.enc', 'sn2.txt', 'sn.sig'],
                ['sha256sum', 'sn.txt', 'sn2.txt']]:
        run(cmd, f)

tampered = bytearray(original)
tampered[7] = ord('9') if tampered[7] != ord('9') else ord('8')
(logs / 'sn_tampered.txt').write_bytes(tampered)
with (logs / 'negative-check.txt').open('w', encoding='utf-8') as f:
    run(['./sm2_file', 'verify', 'sm2_public.pem', 'logs/sn_tampered.txt', 'sn.sig'], f, 2)
    (logs / 'truncated.enc').write_bytes((root / 'sn.enc').read_bytes()[:-1])
    run(['./sm2_file', 'decrypt', 'private/sm2_private.pem', 'logs/truncated.enc', 'logs/should_not_exist.txt'], f, 1)
    assert not (logs / 'should_not_exist.txt').exists()

blob = (root / 'sn.enc').read_bytes()
assert blob[:4] == b'SM2F'
pos, records = 4, []
while pos < len(blob):
    size = int.from_bytes(blob[pos:pos+2], 'big')
    der = blob[pos+2:pos+2+size]
    assert len(der) == size
    records.append(der)
    pos += 2 + size
assert pos == len(blob) and len(records) == 2
with (logs / 'cross-check.txt').open('w', encoding='utf-8') as f:
    for i, der in enumerate(records, 1):
        (logs / f'block{i}.der').write_bytes(der)
        run(['gmssl', 'sm2decrypt', '-key', 'private/sm2_private.pem', '-pass', password,
             '-in', f'logs/block{i}.der', '-out', f'logs/block{i}.plain'], f)
    cli_plain = b''.join((logs / f'block{i}.plain').read_bytes() for i in range(1, 3))
    (logs / 'sn_cli.txt').write_bytes(cli_plain)
    run(['diff', 'sn.txt', 'logs/sn_cli.txt'], f)
    run(['gmssl', 'sm2verify', '-pubkey', 'sm2_public.pem', '-id', '1234567812345678',
         '-in', 'sn.txt', '-sig', 'sn.sig'], f)
    run(['gmssl', 'sm2sign', '-key', 'private/sm2_private.pem', '-pass', password,
         '-id', '1234567812345678', '-in', 'sn.txt', '-out', 'logs/cli.sig'], f)
    run(['./sm2_file', 'verify', 'sm2_public.pem', 'sn.txt', 'logs/cli.sig'], f)

result = {'input_bytes': len(original), 'id_count': len(ids), 'last_id': ids[-1],
          'cipher_bytes': len(blob), 'blocks_plain_bytes': [255, 6],
          'blocks_der_bytes': [len(r) for r in records],
          'signature_bytes': (root / 'sn.sig').stat().st_size,
          'sha256_plain': hashlib.sha256(original).hexdigest(),
          'roundtrip': (root / 'sn2.txt').read_bytes() == original,
          'cli_decryption': cli_plain == original,
          'cli_verifies_c_signature': True, 'c_verifies_cli_signature': True,
          'tampered_message_rejected': True, 'truncated_ciphertext_rejected': True,
          'source_input': '/root/hash_hw/sn.txt'}
assert result['roundtrip'] and result['cli_decryption']
(logs / 'results.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
