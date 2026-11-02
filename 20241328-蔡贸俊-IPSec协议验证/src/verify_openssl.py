"""独立 OpenSSL 命令验证；Python 仅处理字节、ASN.1 和调用命令。"""
from pathlib import Path
import json,subprocess,os,shlex,sys
ROOT=Path(__file__).resolve().parents[1]
EXE=os.environ.get('OPENSSL_EXE',r'C:\Program Files\Git\usr\bin\openssl.exe')
D=ROOT/'data'; LOG=[]; results={}; checks=[]
V=json.loads((D/'vectors.json').read_text(encoding='utf8')); v={k:bytes.fromhex(s) for k,s in V.items()}
def run(args,stdin=None,ok=True):
 p=subprocess.run([EXE]+args,input=stdin,capture_output=True,cwd=ROOT)
 LOG.append('$ openssl '+subprocess.list2cmdline(args)+'\nexit='+str(p.returncode)+'\n'+p.stderr.decode('utf8','replace'))
 if p.stdout:
  try: out=p.stdout.decode('utf8'); assert all(ord(x)>=32 or x in '\n\r\t' for x in out)
  except: out='HEX: '+p.stdout.hex()
  LOG.append(out)
 if ok and p.returncode: raise RuntimeError(LOG[-1])
 return p
def save(name,b): (D/name).write_bytes(b);return 'data/'+name
def record(k,b):results[k]=b.hex() if isinstance(b,bytes) else b;return b
def check(k,a,b):
 good=a==b;checks.append({'name':k,'pass':good});print(k,'PASS' if good else 'FAIL',flush=True)
 if not good: print('ACTUAL',a.hex() if isinstance(a,bytes) else a,'EXPECTED',b.hex() if isinstance(b,bytes) else b)
def hash_(name,b,key=None):
 inp=save(name+'.bin',b)
 args=['dgst','-sm3']+(['-mac','HMAC','-macopt','hexkey:'+key.hex()] if key is not None else [])+['-binary',inp]
 out=run(args).stdout;save(name+'.sm3',out);return record(name,out)
def dec(name,c,key,iv):
 inp=save(name+'.enc',c);out=run(['enc','-d','-sm4-cbc','-K',key.hex(),'-iv',iv.hex(),'-nopad','-in',inp]).stdout
 save(name+'.plain',out);return record(name,out)
def tlv(tag,b):
 n=len(b);length=bytes([n]) if n<128 else bytes([128+(n.bit_length()+7)//8])+n.to_bytes((n.bit_length()+7)//8,'big')
 return bytes([tag])+length+b
def integer(b):
 b=b.lstrip(b'\0') or b'\0'
 return tlv(2,(b'\0' if b[0]&128 else b'')+b)
def seq(b):return tlv(48,b)
def signature(raw):return seq(integer(raw[:32])+integer(raw[32:]))
def public(raw):return seq(seq(bytes.fromhex('06072a8648ce3d020106082a811ccf5501822d'))+tlv(3,b'\0\x04'+raw))
def private(d):return seq(integer(b'\1')+tlv(4,d)+tlv(160,bytes.fromhex('06082a811ccf5501822d')))
def parse_payloads(b):
 out=[];kind=8;pos=0
 while kind:
  nxt,res=b[pos:pos+2];n=int.from_bytes(b[pos+2:pos+4],'big');assert n>=4 and pos+n<=len(b)
  out.append({'type':kind,'offset':pos,'length':n,'next':nxt,'body':b[pos+4:pos+n].hex()})
  pos+=n;kind=nxt
 assert not any(b[pos:]);return out
def main():
 record('openssl_version',run(['version']).stdout.decode().strip())
 for side in ['i','r']:
  key=save('enc_'+side+'.der',private(v['prv_'+side]))
  run(['pkey','-inform','DER','-in',key,'-out', 'data/enc_'+side+'.pem'])
  pub=run(['pkey','-in','data/enc_'+side+'.pem','-pubout','-outform','DER']).stdout
  record('pub_enc_'+side,pub[-65:]);check('private key '+side+' point size',len(pub[-65:]),65)
 c=v['ski_cipher_raw'];der=seq(integer(c[:32])+integer(c[32:64])+tlv(4,c[64:96])+tlv(4,c[96:]))
 cp=save('ski.der',der)
 ski=record('ski_decrypted',run(['pkeyutl','-decrypt','-inkey','data/enc_i.pem','-in',cp]).stdout)
 check('SM2 decrypt SKi',ski,v['ski'])
 ni=dec('ni_decrypted',v['ni_cipher'],ski,bytes(16));check('Ni plaintext',ni[:16],v['ni']);check('Ni padding',ni[16:],bytes(15)+b'\x0f')
 idi=dec('idi_decrypted',v['idi_cipher'],ski,v['ni_cipher'][-16:]);check('IDi plaintext',idi[:80],v['idi']);check('IDi padding',idi[80:],bytes(15)+b'\x0f')
 for side in ['i','r']:
  pub=save('sig_'+side+'_pub.der',public(v['pub_sig_'+side]));sig=save('sig_'+side+'.der',signature(v['sig_'+side]));msg=save('signed_'+side+'.bin',v['signed_'+side])
  args=['pkeyutl','-verify','-pubin','-keyform','DER','-inkey',pub,'-rawin','-digest','sm3','-pkeyopt','distid:1234567812345678','-in',msg,'-sigfile',sig]
  p=run(args,ok=False);record('verify_'+side,p.returncode==0);check('SM2 signature '+side,p.returncode,0)
  bad=bytearray(v['signed_'+side]);bad[0]^=1;badpath=save('signed_'+side+'_tampered.bin',bad)
  args[args.index(msg)]=badpath;p=run(args,ok=False);record('verify_'+side+'_tampered_rejected',p.returncode!=0);check('SM2 rejects tamper '+side,p.returncode!=0,True)
 h=hash_('nonce_hash',v['ni']+v['nr']);check('SM3 Ni||Nr',h.hex(),'83fddf2b5dc8bd853c343ee68f780cfaf2e37fdde3998da2c76a4b368816e972')
 sk=hash_('skeyid',v['cookies'],h)
 kd=hash_('skeyid_d',v['cookies']+b'\0',sk);check('SKEYID_d',kd.hex(),'d07385874bd72fa3ec6d42714e643a94de6644d24f2f50239892f8ef478293e7')
 ka=hash_('skeyid_a',kd+v['cookies']+b'\1',sk)
 ke=hash_('skeyid_e_full',ka+v['cookies']+b'\2',sk);check('SKEYID_e',ke.hex(),'f60661271d29c5093894dacdacf5378c13aeea3d52b2be0ce06ad87edbc9f7d1')
 iv=hash_('main_iv_hash',v['ski']+v['skr'])[:16]
 hi=hash_('hashi',v['cookies']+v['sa']+v['idi'],sk);hr=hash_('hashr',v['cookies'][8:]+v['cookies'][:8]+v['sa']+v['idr'],sk)
 pi=dec('hashi_decrypted',v['hashi_cipher'],ke[:16],iv);pr=dec('hashr_decrypted',v['hashr_cipher'],ke[:16],v['hashi_cipher'][-16:])
 # The encrypted HASH payload retains its 4-byte generic payload header.
 check('HASHi recompute vs decrypted',hi,pi[4:36]);check('HASHr recompute vs decrypted',hr,pr[4:36])
 check('HASHi course value',hi.hex(),'5855a82383911acace237a72d2c6427aa18d552fc4d80d13288104a7f9da2f3c')
 check('HASHr course value',hr.hex(),'4146700c999eb6b4ce92891881b8ec69c013bf83062b885372f2dfddfafe4ea6')
 qiv=hash_('quick_iv_hash',v['hashr_cipher'][-16:]+v['msgid'])[:16];check('Quick IV',qiv.hex(),'56e6dfc945499ae8aca47a6ca9cf2ada')
 q1=dec('qm1',v['qm1_cipher'],ke[:16],qiv);q2=dec('qm2',v['qm2_cipher'],ke[:16],v['qm1_cipher'][-16:])
 a,b=parse_payloads(q1),parse_payloads(q2);record('qm1_payloads',a);record('qm2_payloads',b)
 for name,payload in [('qm1',a),('qm2',b)]:check(name+' payload chain',[x['type'] for x in payload],[8,1,10,5,5])
 ni2=bytes.fromhex(a[2]['body']);nr2=bytes.fromhex(b[2]['body'])
 h1=hash_('quick_hash1',v['msgid']+q1[36:148],ka)
 h2=hash_('quick_hash2',v['msgid']+ni2+q2[36:148],ka)
 check('Quick HASH(1)',h1,q1[4:36]);check('Quick HASH(2)',h2,q2[4:36])
 for name,plain in [('qm1',q1),('qm2',q2)]:check(name+' padding zero',plain[148:],bytes(12))
 # 修改一字节，检查独立重算的 MAC 与原 MAC 不一致。
 altered=bytearray(q1[36:148]);altered[-1]^=1
 ht=hash_('quick_hash1_tampered',v['msgid']+altered,ka);check('Quick rejects altered content',ht!=h1,True)
 record('check_count',len(checks));record('pass_count',sum(c['pass'] for c in checks))
if __name__=='__main__':
 try:main()
 finally:
  (ROOT/'logs/openssl-verification.txt').write_text('\n'.join(LOG),encoding='utf8')
  (ROOT/'logs/openssl-results.json').write_text(json.dumps({'results':results,'checks':checks},ensure_ascii=False,indent=2),encoding='utf8')
 if not all(c['pass'] for c in checks):sys.exit(1)
