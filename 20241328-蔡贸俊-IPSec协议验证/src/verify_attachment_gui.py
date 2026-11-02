"""真实操作附件 Fdog-Base 窗口，读取输出并保存原始窗口截图。"""
from pathlib import Path
import json,time,re,sys
from pywinauto import Desktop
ROOT=Path(__file__).resolve().parents[1]
V=json.loads((ROOT/'data/vectors.json').read_text(encoding='utf8'))
REF=json.loads((ROOT/'logs/openssl-results.json').read_text(encoding='utf8'))['results']
desktop=Desktop(backend='uia')
w=desktop.window(handle=next(x.handle for x in desktop.windows() if x.window_text().startswith('Fdog-')))
records=[]
def ctl(s):
 return next(c for c in w.descendants() if c.element_info.automation_id.endswith('.'+s))
def put(s,text):ctl(s).set_edit_text(text)
def press(s):ctl(s).invoke();time.sleep(.25)
def nav(name):w.child_window(title=name,control_type='Button').invoke();time.sleep(.3)
def radio(name):w.child_window(title=name,control_type='RadioButton').select()
def get(s):return ctl(s).window_text()
def capture(name):
 w.set_focus();time.sleep(.2);w.capture_as_image().save(ROOT/'images'/f'{name}.png')
def log(name,inputs,result,expect=None,screenshot=True):
 clean=re.sub(r'\s+','',result).lower()
 good=clean==expect.lower() if expect is not None else ('成功' in result or 'success' in result.lower())
 records.append({'name':name,'inputs':inputs,'output':result,'expected':expect,'pass':good})
 print(name,result[:140],'PASS' if good else 'FAIL',flush=True)
 if screenshot:capture(name)
def hash_(name,data,key=None):
 nav('杂凑计算');radio('Hex');radio('SM3-HMAC' if key is not None else 'SM3')
 put('SM3_input',data)
 if key is not None:put('z_key',key)
 press('z_js');out=get('z_result');log(name,{'data':data,'key':key},out,REF[name]);return re.sub(r'\s+','',out)
def dec(name,c,key,iv):
 nav('SM4加密解密');radio('Hex')
 ctl('sm4_mod').select('CBC')
 # Retain all decrypted bytes to examine protocol padding explicitly.
 print('padding options',ctl('sm4_pad').texts(),flush=True)
 ctl('sm4_pad').select('NO_PADDING')
 put('sm4_in',c);put('sm4_key',key);put('sm4_iv',iv);press('sm4_dec')
 out=get('sm4_out');log(name,{'cipher':c,'key':key,'iv':iv,'padding':ctl('sm4_pad').selected_text()},out,REF[name]);return out
def main():
 nav('SM2加密解密');radio('C1C3C2');put('sm2_ed',V['prv_i']);put('sm2_mc',V['ski_cipher_raw']);press('SM2_dec')
 log('ski_decrypted',{'private':V['prv_i'],'cipher':V['ski_cipher_raw']},get('sm2_result'),V['ski'])
 for side in ['i','r']:
  nav('SM2签名验签');radio('Hex');put('sm2sign_p','04'+V['pub_sig_'+side]);put('sm2sign_in',V['signed_'+side]);put('sm2sign_result',(ROOT/'data'/f'sig_{side}.der').read_bytes().hex())
  ctl('check_userid').toggle() if ctl('check_userid').get_toggle_state()==0 else None
  put('userid_in','31323334353637383132333435363738');press('sm2ver')
  log('signature_'+side,{'message':V['signed_'+side],'public':'04'+V['pub_sig_'+side],'signature_der':(ROOT/'data'/f'sig_{side}.der').read_bytes().hex(),'userid':'1234567812345678'},get('sm2ver_result'))
 dec('ni_decrypted',V['ni_cipher'],V['ski'],'00'*16)
 dec('idi_decrypted',V['idi_cipher'],V['ski'],V['ni_cipher'][-32:])
 h=hash_('nonce_hash',V['ni']+V['nr'])
 sk=hash_('skeyid',V['cookies'],h)
 kd=hash_('skeyid_d',V['cookies']+'00',sk)
 ka=hash_('skeyid_a',kd+V['cookies']+'01',sk)
 ke=hash_('skeyid_e_full',ka+V['cookies']+'02',sk)
 iv=hash_('main_iv_hash',V['ski']+V['skr'])[:32]
 dec('hashi_decrypted',V['hashi_cipher'],ke[:32],iv)
 dec('hashr_decrypted',V['hashr_cipher'],ke[:32],V['hashi_cipher'][-32:])
 hash_('hashi',V['cookies']+V['sa']+V['idi'],sk)
 hash_('hashr',V['cookies'][16:]+V['cookies'][:16]+V['sa']+V['idr'],sk)
 qiv=hash_('quick_iv_hash',V['hashr_cipher'][-32:]+V['msgid'])[:32]
 dec('qm1',V['qm1_cipher'],ke[:32],qiv)
 dec('qm2',V['qm2_cipher'],ke[:32],V['qm1_cipher'][-32:])
 q1=REF['qm1'];q2=REF['qm2'];ni2=REF['qm1_payloads'][2]['body']
 hash_('quick_hash1',V['msgid']+q1[72:296],ka)
 hash_('quick_hash2',V['msgid']+ni2+q2[72:296],ka)
if __name__=='__main__':
 try:main()
 finally:
  (ROOT/'logs/attachment-tool-results.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
  (ROOT/'logs/attachment-tool-verification.txt').write_text('\n\n'.join(x['name']+'\ninputs='+json.dumps(x['inputs'],ensure_ascii=False)+'\noutput='+x['output']+'\nPASS='+str(x['pass']) for x in records),encoding='utf8')
 if not all(x['pass'] for x in records):sys.exit(1)
