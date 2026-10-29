"""Run under openEuler: python3 tools/verify_linux.py. Standard library only."""
from pathlib import Path
import os, subprocess, shlex, json, platform, datetime
R=Path(__file__).resolve().parents[1]
os.chdir(R)
os.environ['LC_ALL']='C.UTF-8'
log=[]; checks=[]
def run(args, expected=0):
    p=subprocess.run(args,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    text=p.stdout.decode('utf-8',errors='replace')
    log.extend(['$ '+shlex.join(args),text.rstrip(),f'[exit={p.returncode}]'])
    print(log[-3],flush=True)
    if text: print(text.rstrip(),flush=True)
    (R/'logs'/'verification.log').write_text('\n'.join(log)+'\n',encoding='utf-8')
    assert p.returncode==expected, (args,p.returncode,expected)
    return p.stdout
def check(name, yes):
    assert yes,name
    checks.append(name); log.append('PASS: '+name)
    print('PASS: '+name,flush=True)
def tlv(tag,b):
    n=len(b)
    size=bytes([n]) if n<128 else bytes([0x81,n])
    return bytes([tag])+size+b
def integer(b):
    b=b.lstrip(b'\0') or b'\0'
    if b[0]&128: b=b'\0'+b
    return tlv(2,b)
def raw_to_der(raw):
    return tlv(48,integer(raw[:32])+integer(raw[32:64])+tlv(4,raw[64:96])+tlv(4,raw[96:]))
def der_to_raw(data):
    def item(pos):
        tag=data[pos]; n=data[pos+1]; pos+=2
        if n&128:
            count=n&127; n=int.from_bytes(data[pos:pos+count],'big'); pos+=count
        return tag,data[pos:pos+n],pos+n
    tag,body,end=item(0)
    assert tag==48 and end==len(data)
    data=body; pos=0; fields=[]
    for expected in [2,2,4,4]:
        tag,b,pos=item(pos); assert tag==expected; fields.append(b)
    assert pos==len(body)
    return b''.join([fields[0].lstrip(b'\0').rjust(32,b'\0'),fields[1].lstrip(b'\0').rjust(32,b'\0'),*fields[2:]])

run(['uname','-a']); run(['cat','/etc/os-release']); run(['gcc','--version'])
run(['gmssl','version']); run(['openssl','version'])
build_output=run(['make','-C','src','-j4'])
(R/'logs/build.log').write_bytes(build_output)
run(['file','src/lab2'])
selftest=run(['src/lab2','selftest']).decode()
check('Official SM2/SM3/SM4 selftests and C3 tamper rejection',selftest.count('PASS')==4)
for n in [0,1,3,55,56,63,64,65,127,128,1024]:
    b=b'abc' if n==3 else bytes((i*37+11)%256 for i in range(n))
    (R/'data'/f'msg_{n}.bin').write_bytes(b)
    run(['src/lab2','sm3',f'data/msg_{n}.bin','data/sm3_c.bin'])
    run(['gmssl','sm3','-in',f'data/msg_{n}.bin','-bin','-out','data/sm3_gmssl.bin'])
    check(f'SM3 GmSSL comparison, length={n}',(R/'data/sm3_c.bin').read_bytes()==(R/'data/sm3_gmssl.bin').read_bytes())
key='0123456789abcdeffedcba9876543210'
for i in range(8):
    b=bytes.fromhex(key) if i==0 else bytes((j*19+i*31)%256 for j in range(16))
    (R/'data/sm4_plain.bin').write_bytes(b)
    run(['src/lab2','sm4','enc','data/sm4_plain.bin','data/sm4_c.bin'])
    run(['gmssl','sm4_ecb','-encrypt','-key',key,'-in','data/sm4_plain.bin','-out','data/sm4_gmssl.bin'])
    check(f'SM4 GmSSL encrypt block {i}',(R/'data/sm4_c.bin').read_bytes()==(R/'data/sm4_gmssl.bin').read_bytes())
    if i==0:
        check('SM4 standard ciphertext', (R/'data/sm4_c.bin').read_bytes().hex()=='681edf34d206965e86b3e94f536e4246')
        (R/'data/sm4_standard.bin').write_bytes((R/'data/sm4_c.bin').read_bytes())
    run(['src/lab2','sm4','dec','data/sm4_gmssl.bin','data/sm4_recovered.bin'])
    check(f'SM4 GmSSL -> C decrypt block {i}',(R/'data/sm4_recovered.bin').read_bytes()==b)
run(['src/lab2','sm4','enc','data/msg_3.bin','data/invalid.bin'],expected=2)
check('SM4 invalid length rejected',not (R/'data/invalid.bin').exists())
run(['gcc','-O2','src/test_key.c','-lgmssl','-o','src/test_key'])
run(['src/test_key'])
raw=(R/'data/sm2_official.raw').read_bytes()
(R/'data/sm2_official.der').write_bytes(raw_to_der(raw))
run(['gmssl','sm2decrypt','-key','data/test_private.pem','-pass','lab2-test-only','-in','data/sm2_official.der','-out','data/sm2_gmssl_plain.bin'])
check('SM2 C encrypt -> GmSSL decrypt',(R/'data/sm2_gmssl_plain.bin').read_bytes()==(R/'data/message.bin').read_bytes())
for i in range(3):
    run(['gmssl','sm2encrypt','-pubkey','data/test_public.pem','-in','data/message.bin','-out',f'data/sm2_gmssl_{i}.der'])
    raw=der_to_raw((R/f'data/sm2_gmssl_{i}.der').read_bytes())
    (R/f'data/sm2_gmssl_{i}.raw').write_bytes(raw)
    run(['src/lab2','sm2dec',f'data/sm2_gmssl_{i}.raw','data/sm2_c_plain.bin'])
    check(f'SM2 GmSSL encrypt -> C decrypt, random trial {i}',(R/'data/sm2_c_plain.bin').read_bytes()==(R/'data/message.bin').read_bytes())
bad=bytearray((R/'data/sm2_official.raw').read_bytes()); bad[64]^=1
(R/'data/sm2_bad.raw').write_bytes(bad)
run(['src/lab2','sm2dec','data/sm2_bad.raw','data/invalid_sm2.bin'],expected=1)
check('SM2 C3 failure produces no plaintext file',not (R/'data/invalid_sm2.bin').exists())
run(['src/lab2','sm2dec','data/msg_3.bin','data/invalid_sm2.bin'],expected=2)
check('SM2 truncated input rejected',True)
git_recorded=(R/'logs/repository_metadata.json').is_file()
summary={'time':datetime.datetime.now().astimezone().isoformat(),'platform':platform.platform(),'passed':len(checks),'checks':checks,'selftest_output':selftest,'scope':'Experiment 2, hours 1-3: SCCTC reference implementations', 'pending':[] if git_recorded else ['Course repository link and incremental git commits'], 'optional':['Rust implementation not attempted']}
(R/'logs/results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
log.append(f'ALL {len(checks)} CHECKS PASSED')
(R/'logs/verification.log').write_text('\n'.join(log)+'\n',encoding='utf-8')
print(log[-1])
