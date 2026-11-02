"""Build an isolated teaching CA, exercise validation, retain public evidence."""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence'
OUT.mkdir(exist_ok=True)
parser = argparse.ArgumentParser()
parser.add_argument('--openssl', default=r'C:\Program Files\Git\usr\bin\openssl.exe')
args = parser.parse_args()
logs, results = [], []
def run(*items, expect=0):
    cmd = [args.openssl, *map(str, items)]
    result = subprocess.run(cmd, cwd=work, env=env, capture_output=True)
    text = (result.stdout + result.stderr).decode('utf-8', errors='replace')
    logs.append('$ openssl ' + ' '.join(map(str, items)) + '\n' + text + f'\n[exit={result.returncode}]\n')
    if (result.returncode == 0) != (expect == 0):
        raise RuntimeError(logs[-1])
    return text
def validate(label, options, good=True, token=None):
    text = run('verify', *options, expect=0 if good else 1)
    if token:
        assert token in text, text
    results.append({'case': label, 'expected_accept': good, 'pass': True})
    return text

with tempfile.TemporaryDirectory(prefix='week7-pki-') as tmp:
    work = Path(tmp)
    env = dict(os.environ, OPENSSL_CONF=str(work / 'empty.cnf'))
    (work / 'empty.cnf').write_text('', encoding='ascii')
    logs.append('OS: ' + platform.platform() + '\nUTC: ' + time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    run('version', '-a')
    for ca in ['root', 'intermediate']:
        (work / ca / 'newcerts').mkdir(parents=True)
        (work / ca / 'index.txt').write_text('', encoding='ascii')
        (work / ca / 'serial').write_text('1000\n', encoding='ascii')
        (work / ca / 'crlnumber').write_text('1000\n', encoding='ascii')
    config = '''[ca]
default_ca = CA_default
[CA_default]
dir = {ca}
database = $dir/index.txt
new_certs_dir = $dir/newcerts
certificate = $dir/cert.pem
private_key = $dir/key.pem
serial = $dir/serial
crlnumber = $dir/crlnumber
default_md = sha256
default_days = 365
default_crl_days = 7
policy = policy_any
unique_subject = no
copy_extensions = none
[policy_any]
commonName = supplied
[v3_root]
basicConstraints = critical,CA:true,pathlen:1
keyUsage = critical,keyCertSign,cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always
[v3_intermediate]
basicConstraints = critical,CA:true,pathlen:0
keyUsage = critical,keyCertSign,cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always
[v3_server]
basicConstraints = critical,CA:false
keyUsage = critical,digitalSignature,keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = DNS:lab.example.test
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always
'''
    for ca in ['root', 'intermediate']:
        (work / f'{ca}.cnf').write_text(config.format(ca=ca), encoding='ascii')
    for stem in ['root/key', 'intermediate/key', 'server']:
        run('genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:2048', '-out', stem + '.pem')
    run('req', '-new', '-x509', '-key', 'root/key.pem', '-out', 'root/cert.pem', '-days', '3650', '-sha256', '-subj', '/CN=Week7 Teaching Root CA', '-config', 'root.cnf', '-extensions', 'v3_root')
    run('req', '-new', '-key', 'intermediate/key.pem', '-out', 'intermediate.csr', '-subj', '/CN=Week7 Intermediate CA')
    run('ca', '-batch', '-config', 'root.cnf', '-extensions', 'v3_intermediate', '-days', '1825', '-in', 'intermediate.csr', '-out', 'intermediate/cert.pem', '-notext')
    run('req', '-new', '-key', 'server.pem', '-out', 'server.csr', '-subj', '/CN=lab.example.test')
    run('req', '-in', 'server.csr', '-verify', '-noout')
    run('ca', '-batch', '-config', 'intermediate.cnf', '-extensions', 'v3_server', '-in', 'server.csr', '-out', 'server-cert.pem', '-notext')
    base = ['-CAfile', 'root/cert.pem', '-no-CApath', '-no-CAstore', '-untrusted', 'intermediate/cert.pem']
    validate('complete chain', [*base, '-show_chain', '-purpose', 'sslserver', '-verify_hostname', 'lab.example.test', 'server-cert.pem'])
    validate('missing intermediate', ['-CAfile', 'root/cert.pem', '-no-CApath', '-no-CAstore', 'server-cert.pem'], False, 'unable to get local issuer certificate')
    validate('root not trusted', ['-no-CAfile', '-no-CApath', '-no-CAstore', '-untrusted', 'intermediate/cert.pem', 'server-cert.pem'], False, 'unable to get local issuer certificate')
    validate('wrong hostname', [*base, '-verify_hostname', 'wrong.example.test', 'server-cert.pem'], False, 'hostname mismatch')
    validate('wrong purpose', [*base, '-purpose', 'sslclient', 'server-cert.pem'], False, 'unsuitable certificate purpose')
    future = str(int(time.time()) + 366 * 86400)
    validate('expired at future validation time', [*base, '-attime', future, 'server-cert.pem'], False, 'certificate has expired')
    run('ca', '-config', 'intermediate.cnf', '-gencrl', '-out', 'before.crl.pem')
    validate('CRL before revocation', [*base, '-CRLfile', 'before.crl.pem', '-crl_check', 'server-cert.pem'])
    run('ca', '-config', 'intermediate.cnf', '-revoke', 'server-cert.pem', '-crl_reason', 'keyCompromise')
    run('ca', '-config', 'intermediate.cnf', '-gencrl', '-out', 'after.crl.pem')
    validate('revoked certificate', [*base, '-CRLfile', 'after.crl.pem', '-crl_check', 'server-cert.pem'], False, 'certificate revoked')
    validate('revocation not automatically enabled', [*base, 'server-cert.pem'])
    run('x509', '-in', 'server-cert.pem', '-outform', 'DER', '-out', 'server-cert.der')
    run('x509', '-inform', 'DER', '-in', 'server-cert.der', '-out', 'roundtrip.pem')
    a = run('x509', '-in', 'server-cert.pem', '-fingerprint', '-sha256', '-noout')
    b = run('x509', '-in', 'roundtrip.pem', '-fingerprint', '-sha256', '-noout')
    assert a == b
    results.append({'case': 'PEM DER fingerprint unchanged', 'pass': True})
    run('x509', '-in', 'server-cert.pem', '-noout', '-text')
    run('crl', '-in', 'after.crl.pem', '-noout', '-text')
    for src, dst in [('root/cert.pem', 'root-cert.pem'), ('intermediate/cert.pem', 'intermediate-cert.pem'), ('server-cert.pem', 'server-cert.pem'), ('server-cert.der', 'server-cert.der'), ('before.crl.pem', 'before.crl.pem'), ('after.crl.pem', 'after.crl.pem'), ('server.csr', 'server.csr'), ('intermediate/index.txt', 'intermediate-index.txt')]:
        shutil.copyfile(work / src, OUT / dst)
    for ca in ['root', 'intermediate']:
        shutil.copyfile(work / f'{ca}.cnf', ROOT / 'code' / f'{ca}.cnf')
    logs.append(f'ALL {len(results)} CHECKS PASSED. Temporary private keys removed when temporary directory exits.')
(OUT / 'experiment-log.txt').write_text('\n'.join(logs), encoding='utf-8')
(OUT / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print('\n'.join(f"PASS: {r['case']}" for r in results))
print(f'ALL {len(results)} CHECKS PASSED')
