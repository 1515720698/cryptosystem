"""Run in Linux/WSL: python3 code/run_tls.py. Requires gcc and OpenSSL dev files."""
from pathlib import Path
import json
import os
import platform
import selectors
import shlex
import shutil
import socket
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
LOG = []


def run(args, cwd):
    LOG.append('$ ' + shlex.join(map(str, args)))
    p = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=40)
    LOG.append(p.stdout.rstrip() + '\nexit=' + str(p.returncode))
    if p.returncode:
        raise RuntimeError('Command failed: ' + str(args))
    return p.stdout


def main():
    for filename in ('experiment-log.txt', 'results.json'):
        old = EVIDENCE / filename
        previous = EVIDENCE / ('previous-' + filename)
        if old.exists() and not previous.exists():
            shutil.copyfile(old, previous)
    LOG.append('OS: ' + platform.platform())
    LOG.append('Python: ' + platform.python_version())
    results = []
    with tempfile.TemporaryDirectory(prefix='week8-tls-') as temp:
        wd = Path(temp)
        run(['openssl', 'version', '-a'], wd)
        run(['gcc', '--version'], wd)
        run(['gcc', '-std=c11', '-Wall', '-Wextra', '-Werror',
             str(ROOT / 'code/tls_demo.c'), '-o', str(wd / 'tls_demo'), '-lssl', '-lcrypto'], wd)
        for ca in ('ca', 'other-ca'):
            run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                 '-keyout', ca + '.key', '-out', ca + '.pem', '-days', '2',
                 '-subj', '/CN=Week8-' + ca,
                 '-addext', 'basicConstraints=critical,CA:TRUE',
                 '-addext', 'keyUsage=critical,keyCertSign,cRLSign'], wd)
        for role, usage in [('server', 'serverAuth'), ('client', 'clientAuth')]:
            run(['openssl', 'req', '-new', '-newkey', 'rsa:2048', '-nodes',
                 '-keyout', role + '.key', '-out', role + '.csr',
                 '-subj', '/CN=' + ('localhost' if role == 'server' else 'Week8-device')], wd)
            ext = ('basicConstraints=critical,CA:FALSE\n'
                   'keyUsage=critical,digitalSignature\n'
                   'extendedKeyUsage=' + usage + '\n'
                   'subjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid,issuer\n')
            if role == 'server':
                ext += 'subjectAltName=DNS:localhost\n'
            (wd / (role + '.ext')).write_text(ext)
            run(['openssl', 'x509', '-req', '-in', role + '.csr', '-CA', 'ca.pem',
                 '-CAkey', 'ca.key', '-CAcreateserial', '-out', role + '.pem',
                 '-days', '2', '-extfile', role + '.ext'], wd)
            shutil.copyfile(wd / (role + '.pem'), EVIDENCE / (role + '-cert.pem'))
        shutil.copyfile(wd / 'ca.pem', EVIDENCE / 'ca-cert.pem')
        cases = [
            ('trusted_server', 'ca.pem', 'localhost', False, False, True, None),
            ('untrusted_ca', 'other-ca.pem', 'localhost', False, False, False,
             'alert unknown ca'),
            ('hostname_mismatch', 'ca.pem', 'wrong.example', False, False, False,
             'hostname mismatch'),
            ('mtls_missing_client', 'ca.pem', 'localhost', True, False, False,
             'peer did not return a certificate'),
            ('mtls_valid_client', 'ca.pem', 'localhost', True, True, True, None),
        ]
        for name, ca, host, require, client_cert, success, reason in cases:
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = str(sock.getsockname()[1])
            server_args = ['./tls_demo', 'server', port, 'ca.pem', 'server.pem',
                           'server.key', str(int(require))]
            client_args = ['./tls_demo', 'client', port, ca, host]
            if client_cert:
                client_args += ['client.pem', 'client.key']
            LOG.append('\nCASE ' + name + '\n$ ' + shlex.join(server_args))
            server = subprocess.Popen(server_args, cwd=wd, text=True,
                                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            try:
                with selectors.DefaultSelector() as selector:
                    selector.register(server.stdout, selectors.EVENT_READ)
                    if not selector.select(timeout=10):
                        raise RuntimeError('Server readiness timeout')
                ready = server.stdout.readline()
                if not ready.startswith('READY'):
                    raise RuntimeError('Server not ready: ' + ready)
                client = subprocess.run(client_args, cwd=wd, text=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15)
                rest, _ = server.communicate(timeout=15)
            finally:
                if server.poll() is None:
                    server.kill()
                    server.communicate()
            combined = ready + rest + client.stdout
            accepted = client.returncode == 0 and server.returncode == 0
            passed = accepted == success
            if success:
                passed = passed and combined.count('EXCHANGE_OK') == 2
            else:
                passed = passed and client.returncode != 0 and server.returncode != 0
                passed = passed and reason in combined and 'EXCHANGE_OK' not in combined
            LOG.extend(['$ ' + shlex.join(client_args), 'CLIENT:\n' + client.stdout,
                    'SERVER:\n' + ready + rest,
                    f'client_exit={client.returncode} server_exit={server.returncode} PASS={passed}'])
            results.append(dict(case=name, expected_accept=success, passed=passed,
                                client_exit=client.returncode, server_exit=server.returncode,
                                client_output=client.stdout, server_output=ready + rest))
            print(name, 'PASS' if passed else 'FAIL')
        (EVIDENCE / 'results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
        assert all(x['passed'] for x in results), 'A case failed'
        LOG.append('\nALL 5 CASES PASSED. Temporary private keys and binary removed on exit.')


if __name__ == '__main__':
    try:
        main()
    finally:
        (EVIDENCE / 'experiment-log.txt').write_text('\n'.join(LOG), encoding='utf-8')
