from pathlib import Path
import os,subprocess,json
R=Path(__file__).resolve().parents[1]; os.chdir(R)
def run(args):
    print('$ '+' '.join(args),flush=True)
    p=subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    print(p.stdout.decode().rstrip(),flush=True)
print('LAB 2 - SCCTC SM2 / SM3 / SM4 on openEuler | 20241328',flush=True)
run(['gmssl','version'])
run(['src/lab2','sm3','data/msg_3.bin','data/demo_sm3.bin'])
run(['gmssl','sm3','-in','data/msg_3.bin'])
run(['gmssl','sm4_ecb','-decrypt','-key','0123456789abcdeffedcba9876543210','-in','data/sm4_standard.bin','-out','data/demo_sm4_plain.bin'])
print('SM4 GmSSL recovered:',(R/'data/demo_sm4_plain.bin').read_bytes().hex(),flush=True)
run(['gmssl','sm2decrypt','-key','data/test_private.pem','-pass','lab2-test-only','-in','data/sm2_official.der','-out','data/demo_sm2_plain.bin'])
print('SM2 plaintext matches:',(R/'data/demo_sm2_plain.bin').read_bytes()==(R/'data/message.bin').read_bytes(),flush=True)
run(['src/lab2','sm2dec','data/sm2_gmssl_0.raw','data/demo_sm2_c.bin'])
print('SM2 reverse direction matches:',(R/'data/demo_sm2_c.bin').read_bytes()==(R/'data/message.bin').read_bytes(),flush=True)
r=json.loads((R/'logs/results.json').read_text())
print('VERIFIED:',r['passed'],'checks passed. Full evidence: logs/verification.log',flush=True)
