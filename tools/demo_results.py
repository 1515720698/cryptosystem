"""Display and recheck saved experimental evidence in a real console window."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
hardware = json.loads((root/'logs/ukey_results.json').read_text(encoding='utf-8'))
result = json.loads((root/'logs/crosscheck_results.json').read_text(encoding='utf-8'))
print('20241328 CAI MAOJUN - LAB 2 / HOURS 4-6 / GM3000 SKF')
print('Hardware run:', hardware['finished_at'])
print('Cross-check:', result['time'])
print('No PIN; external public key fixture d=1; no persistent token objects.')
assert all(call['rv'] == '0x00000000' for call in hardware['calls'])
print('SKF calls in saved hardware run: all returned 0')
print('')
for alg, files in [
    ('SM3(abc)', ['ukey_sm3_3.bin', 'soft_sm3_3.bin', 'gmssl_sm3_3.bin']),
    ('SM4 standard ciphertext', ['ukey_sm4_cipher_0.bin', 'soft_sm4_cipher_0.bin', 'gmssl_sm4_cipher_0.bin']),
    ('SM2 recovered plaintext', ['ukey_sm2_message.bin', 'textbook_from_ukey_0.bin', 'gmssl_from_ukey_0.bin']),
]:
    values = [(root/'data'/file).read_bytes() for file in files]
    assert values[0] == values[1] == values[2]
    print(alg + ': PASS (UKey / textbook / GmSSL)')
    print('  ' + values[0].hex())
    if alg.startswith('SM2'):
        print('  UTF-8: ' + values[0].decode('utf-8'))
print('')
for name, digest in result['input_output_sha256'].items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest() == digest, name
print('Saved input/output SHA-256 manifest: PASS')
print('ALL %d CHECKS PASSED: software=%d, hardware-crosschecks=%d' %
      (result['passed'], result['totals']['software'], result['totals']['hardware']))
print('Full commands / exit codes: logs/crosscheck.log')
