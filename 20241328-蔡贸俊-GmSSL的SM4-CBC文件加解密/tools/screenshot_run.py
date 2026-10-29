"""Supplementary Linux run, displayed in a real Windows console for capture."""
from pathlib import Path
import subprocess
import shlex
import sys

root = Path(__file__).resolve().parent.parent
work = root / 'logs/screenshot-run'
work.mkdir(exist_ok=True)
phase = sys.argv[1]
if phase == '1':
    (work / 'sm4_file.c').write_bytes((root / 'src/sm4_file.c').read_bytes())
    (work / 'sn.txt').write_bytes((root / 'sn.txt').read_bytes())
    commands = [
        ['date', '-Iseconds'],
        ['grep', 'PRETTY_NAME', '/etc/os-release'],
        ['gmssl', 'version'],
        ['gcc', '-Wall', '-Wextra', '-O2', 'sm4_file.c', '-I/usr/local/include',
         '-L/usr/local/lib', '-Wl,-rpath,/usr/local/lib', '-lgmssl', '-o', 'sm4_file'],
        ['./sm4_file'],
        ['wc', '-c', 'sn.txt', 'sn.enc', 'sn2.txt', 'key.bin', 'iv.bin'],
    ]
else:
    commands = [
        ['date', '-Iseconds'],
        ['tail', '-n', '3', 'sn.txt'],
        ['diff', 'sn.txt', 'sn2.txt'],
        ['sha256sum', 'sn.txt', 'sn2.txt'],
        ['python3', '-c', "from pathlib import Path; a=Path('sn.txt').read_text().splitlines(); assert len(a)==len(set(a))==29; assert all(len(x)==8 and x.isdigit() for x in a); assert a[-1]=='20241328'; print('PASS: 29 unique 8-digit IDs; own ID is last.')"],
    ]
with (work / f'phase{phase}.txt').open('w', encoding='utf-8') as f:
    def emit(s):
        print(s, flush=True)
        f.write(s + '\n')
        f.flush()
    emit('20241328 CAI MAOJUN | openEuler | supplementary run')
    emit('Working directory: logs/screenshot-run\n')
    for cmd in commands:
        display = shlex.join(cmd) if cmd[0] != 'python3' else 'python3 [validate ID format, uniqueness and final line]'
        emit('$ ' + display)
        r = subprocess.run(cmd, cwd=work, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True)
        if r.stdout:
            emit(r.stdout.rstrip())
        emit(f'[exit code: {r.returncode}]\n')
        if r.returncode:
            raise SystemExit(r.returncode)
    emit('=== ALL CHECKS PASSED ===')
(work / f'phase{phase}.done').write_text('PASS', encoding='utf-8')
