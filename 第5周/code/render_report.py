"""Reuse the cryptosystem-report skill renderers, then verify the actual PDF.
Requires Markdown, Pillow, PyMuPDF and Edge. Set CRYPTO_REPORT_SKILL as needed.
"""
from pathlib import Path
import importlib
import json
import os
import re
import sys
import pymupdf
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SKILL = Path(os.environ.get('CRYPTO_REPORT_SKILL',
    str(Path.home()/'.config/opencode/skills/cryptosystem-report')))
sys.path.insert(0, str(SKILL))
name = '20241328蔡贸俊《密码系统设计》'
md = ROOT / f'{name}.md'
pdf = ROOT / f'{name}第5周.pdf'
image = ROOT / 'assets/week5-mindmap.png'
text = md.read_text(encoding='utf-8')
source = re.search(r'```mermaid\n(.*?)```', text, re.S).group(1).strip()
assert source == (ROOT/'assets/week5-mindmap.mmd').read_text(encoding='utf-8').strip()
mermaid = importlib.import_module('mermaid_render')
sys.argv = ['mermaid_render.py', str(md), str(image)]
mermaid.main()
renderer = importlib.import_module('md2pdf')
renderer.CSS += '''
h1, h2 {color:#173f66;} h3 {color:#225c84;}
h1 {border-color:#2b6a9a;} h2 {border-color:#b8cddd;}
table {width:100%;font-size:9.5pt;} th {background:#edf4fa;}
blockquote {background:#f2f6fa;border-left-color:#5d8bae;}
a {color:#205c89;text-decoration:none;}
p {orphans:3;widows:3;} h4 {break-after:avoid;}
pre code {font-size:8.5pt;line-height:1.5;}
'''
sys.argv = ['md2pdf.py', str(md), str(pdf)]
renderer.main()
doc = pymupdf.open(pdf)
evidence = ROOT/'evidence'
evidence.mkdir(exist_ok=True)
texts = []
thumbnails = []
checks = []
for index, page in enumerate(doc):
    page_text = page.get_text()
    texts.append(f'PAGE {index+1}\n{page_text}')
    assert len(page_text.strip()) > 25, f'Unexpected blank page {index+1}'
    pix = page.get_pixmap(matrix=pymupdf.Matrix(1.4,1.4))
    pix.save(str(evidence/f'pdf-page-{index+1}.png'))
    thumb = Image.open(evidence/f'pdf-page-{index+1}.png').convert('RGB')
    thumb.thumbnail((400,570))
    thumbnails.append(thumb)
    checks.append({'page':index+1,'characters':len(page_text),'images':len(page.get_images())})
full = '\n\n'.join(texts)
compact = re.sub(r'\s+','',full)
for required in ['第五周预习报告','一、AI 对学习内容的总结','二、对 AI 总结的反思与补充',
                 '三、学习思维导图','四、基于 AI 的学习','五、学习实践过程遇到的问题与解决方式',
                 '六、参考资料','作业提交说明','ALL 14 CHECKS PASSED']:
    assert re.sub(r'\s+','',required) in compact, required
assert any(c['images'] > 0 for c in checks), 'Missing mindmap image in PDF'
assert '第四周预习报告' not in full
(evidence/'pdf-text-check.txt').write_text(full,encoding='utf-8')
sheet = Image.new('RGB',(1260,620*((len(thumbnails)+2)//3)), '#dbe3eb')
draw = ImageDraw.Draw(sheet)
for i,thumb in enumerate(thumbnails):
    x=20+(i%3)*420; y=30+(i//3)*620
    sheet.paste(thumb,(x,y));draw.text((x,y-20),f'Page {i+1}',fill='black')
sheet.save(evidence/'pdf-contact-sheet.png')
(evidence/'pdf-check.json').write_text(json.dumps({'pages':len(doc),'checks':checks},indent=2),encoding='utf-8')
print(f'PDF checked: {len(doc)} pages, required sections and mindmap present.')
