"""Supplementary SM2 execution in a real terminal; separate from initial data."""
from pathlib import Path
import os
import shlex
import subprocess
import sys

root = Path(__file__).resolve().parent.parent
work = root / 'logs/screenshot-run'
work.mkdir(exist_ok=True)
phase = sys.argv[1]
env = os.environ.copy()
env['SM2_PASS'] = Path('/root/.local/state/gmssl-sm2-20241328/password').read_text().strip()
key = '../../private/screenshot_private.pem'
if phase == '1':
    (work / 'sm2_file.c').write_bytes((root / 'src/sm2_file.c').read_bytes())
    (work / 'sn.txt').write_bytes((root / 'sn.txt').read_bytes())
    commands = [
        (['date', '-Iseconds'], 0),
        (['grep', 'PRETTY_NAME', '/etc/os-release'], 0),
        (['gmssl', 'version'], 0),
        (['gmssl', 'sm2keygen', '-pass', env['SM2_PASS'], '-out', key, '-pubout', 'sm2_public.pem'], 0),
        (['head', '-n', '1', key], 0),
        (['head', '-n', '1', 'sm2_public.pem'], 0),
        (['gcc', '-Wall', '-Wextra', '-O2', 'sm2_file.c', '-I/usr/local/include',
          '-L/usr/local/lib', '-Wl,-rpath,/usr/local/lib', '-lgmssl', '-o', 'sm2_file'], 0),
    ]
elif phase == '2':
    commands = [
        (['./sm2_file', 'encrypt', 'sm2_public.pem', 'sn.txt', 'sn.enc'], 0),
        (['./sm2_file', 'decrypt', key, 'sn.enc', 'sn2.txt'], 0),
        (['diff', 'sn.txt', 'sn2.txt'], 0),
        (['sha256sum', 'sn.txt', 'sn2.txt'], 0),
        (['tail', '-n', '3', 'sn.txt'], 0),
    ]
else:
    data = bytearray((work / 'sn.txt').read_bytes())
    data[7] = ord('9')
    (work / 'sn_tampered.txt').write_bytes(data)
    commands = [
        (['./sm2_file', 'sign', key, 'sn.txt', 'sn.sig'], 0),
        (['./sm2_file', 'verify', 'sm2_public.pem', 'sn.txt', 'sn.sig'], 0),
        (['gmssl', 'sm2verify', '-pubkey', 'sm2_public.pem', '-id', '1234567812345678', '-in', 'sn.txt', '-sig', 'sn.sig'], 0),
        (['./sm2_file', 'verify', 'sm2_public.pem', 'sn_tampered.txt', 'sn.sig'], 2),
    ]
with (work / f'phase{phase}.txt').open('w', encoding='utf-8') as f:
    def emit(text):
        print(text, flush=True)
        f.write(text + '\n')
        f.flush()
    emit(f'20241328 CAI MAOJUN | openEuler | SM2 supplementary run {phase}')
    emit('Working directory: logs/screenshot-run\n')
    for cmd, expected in commands:
        shown = ['$SM2_PASS' if x == env['SM2_PASS'] else x for x in cmd]
        emit('$ ' + shlex.join(shown).replace("'$SM2_PASS'", '"$SM2_PASS"'))
        p = subprocess.run(cmd, cwd=work, env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True)
        if p.stdout:
            emit(p.stdout.rstrip().replace(env['SM2_PASS'], '[REDACTED]'))
        emit(f'[exit code: {p.returncode}; expected: {expected}]\n')
        assert p.returncode == expected
    emit('=== ALL CHECKS PASSED ===')
(work / f'phase{phase}.done').write_text('PASS', encoding='utf-8')
