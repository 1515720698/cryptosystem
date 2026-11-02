"""从已读取的课件页面提取实验向量；不产生模拟抓包。"""
import re,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def page(n):
 t=(ROOT/'references'/f'slide-{n:02}.txt').read_text(encoding='utf8')
 return t.rsplit('\n61\n\n',1)[-1].split('幻灯片 ')[0]
def blocks(n):
 return [''.join(x.split()) for x in re.findall(r'(?m)^[0-9a-f]{16,}(?:\n[0-9a-f]{16,})*$',page(n))]
v={
 'prv_i':'2eb464dc25937be59938549f4cc6306cea1c2ecdcc491a4e3b4fc0bd29af1f99',
 'prv_r':'bb3d0ce3feaa521807031b86588d8d3ed35c888c266003780140e804491ad6d7',
 'ski_cipher_raw':'83e6ecef3fb62d7d4683132d920a298dd88efc8342256fb751987a5c37300cd3398674a09fc955c21d9218a5016994738d9eddb2939b133e8ed2273aa3a215d3cf1f2e14abe2de8c81fc9f2fbf028648570af88dcdaa98659a4c3eb1f9697510ac34d8306c55b50003a96045184deb81',
 'ski':'e6b74813213bfe4759c20225ade2678e',
 'skr':'93754381265febcf025a6c0d53abf6d3',
 'cookies':'a89a4662a4d1cad049a2eb29cf6d65db',
 'msgid':'cc2d2221',
 'ni_cipher':blocks(14)[0], 'idi_cipher':blocks(16)[0],
 'cert_enc_i':blocks(18)[0], 'signed_i':blocks(20)[0],
 'sig_i':blocks(21)[0], 'pub_sig_i':blocks(22)[0],
 'signed_r':blocks(25)[0], 'sig_r':blocks(26)[0], 'pub_sig_r':blocks(26)[1],
 'sa':blocks(41)[0],
 'hashi_cipher':'c60c2e7689fa1519256ec690bbfb7d6380a52de3d51ce8fb1ac5923a84ceac86b958be5fa74277fc91b3bfd3d1cbf7e0',
 'hashr_cipher':'dd55ad19832211a7909550c3472615c55feddb949b5ee01f9cfe6d9e228e3a1dd92048953a172891b194012f8db5f7b0',
 'qm1_cipher':blocks(52)[0], 'qm2_cipher':blocks(58)[0],
}
v['ni']=v['signed_i'][32:64]; v['nr']=v['signed_r'][32:64]
v['idi']=v['signed_i'][64:v['signed_i'].index(v['cert_enc_i'])]
v['idr']=v['signed_r'][64:v['signed_r'].index('05308201')]
for k,s in v.items():
 bytes.fromhex(s)
 print(k,len(s)//2,s[:68])
(ROOT/'data/vectors.json').write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf8')
(ROOT/'references/课件逐页摘录.txt').write_text('\n\n'.join(f'=== 第{n}页 ===\n{page(n)}' for n in range(10,60)),encoding='utf8')
