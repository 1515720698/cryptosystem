"""Update verification date, render Markdown PDF, preview, and package delivery."""
from pathlib import Path
import json,re,subprocess,sys,zipfile,hashlib
import pymupdf
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
B='20241328_蔡贸俊_实验二_1-3学时_实践记录'
sys.stdout.reconfigure(encoding='utf-8')
result=json.loads((R/'logs/results.json').read_text(encoding='utf-8'))
assert result['passed']==36
date=result['time'].split('T')[0]
y,m,d=date.split('-')
md=(R/(B+'.md')).read_text(encoding='utf-8')
md=re.sub(r'实际验证日期：[^\n]+',f'实际验证日期：{y}年{int(m)}月{int(d)}日',md)
assert '4—6学时任务' not in md
assert 'UKey' not in md
assert '待运行结果更新' not in md
(R/(B+'.md')).write_text(md,encoding='utf-8')
shot=Image.open(R/'images/实际终端验证截图.png')
if shot.size==(1700,850):shot.crop((0,0,1700,550)).save(R/'images/实际终端验证截图.png')
renderer=Path.home()/'.config/opencode/skills/cryptosystem-report/md2pdf.py'
subprocess.run([sys.executable,str(renderer),str(R/(B+'.md')),str(R/(B+'.pdf'))],check=True)
pdf=pymupdf.open(R/(B+'.pdf'))
text='\n'.join(p.get_text() for p in pdf)
assert all(len(p.get_text().strip())>40 for p in pdf)
assert '蔡贸俊' in text and '36' in text
assert '\ufffd' not in text
(R/'logs/实践记录PDF文字.txt').write_text(text,encoding='utf-8')
ims=[]
for p in pdf:
    pix=p.get_pixmap(matrix=pymupdf.Matrix(0.7,0.7))
    im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((400,570));ims.append(im)
sheet=Image.new('RGB',(400*4,600*((len(ims)+3)//4)),'#ddd')
draw=ImageDraw.Draw(sheet)
for i,im in enumerate(ims):
    x=i%4*400;y=i//4*600
    draw.text((x+5,y+3),f'Page {i+1}',fill='black');sheet.paste(im,(x,y+20))
sheet.save(R/'images/PDF分页核验.png')
verifier=Path.home()/'.config/opencode/skills/course-lab-delivery/scripts/verify_submission.py'
subprocess.run([sys.executable,str(verifier),str(R),'--require',B+'.md','--require',B+'.pdf','--require','src/main.c','--require','src/SM2_ENC.c','--require','src/SM3.c','--require','src/SM4.c','--require','logs/results.json','--require','logs/build.log','--markdown',B+'.md','--markdown','README_提交清单.md','--json',str(R/'logs/文件与链接核验.json')],check=True)
git_recorded=(R/'logs/repository_metadata.json').is_file()
report={'scope':'实验二1—3学时','algorithm_assertions':result['passed'],'verification_time':result['time'],'pdf_pages':len(pdf),'blank_pdf_pages':0,'pending':[] if git_recorded else ['课程仓库链接及功能递增Git记录'],'optional_not_attempted':['Rust']}
(R/'logs/交付状态.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
archive=R/'20241328_蔡贸俊_实验二_1-3学时_提交材料.zip'
def include(p):
    return p.is_file() and p.suffix not in ['.o','.a','.zip'] and p.name not in ['PDF分页核验.png','SHA256SUMS.json','test_private.pem','lab2','test_key'] and '__pycache__' not in p.parts and '.git' not in p.parts
files=sorted(p for p in R.rglob('*') if include(p))
manifest={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(R/'SHA256SUMS.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
files.append(R/'SHA256SUMS.json')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,R.name+'/'+p.relative_to(R).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(files)
    for p in files:
        if p.name=='SHA256SUMS.json':continue
        assert hashlib.sha256(z.read(R.name+'/'+p.relative_to(R).as_posix())).hexdigest()==manifest[p.relative_to(R).as_posix()]
print(json.dumps(report,ensure_ascii=False,indent=2))
print('ZIP:',len(files),'files,',round(archive.stat().st_size/1024/1024,2),'MiB; CRC and SHA-256 match')
