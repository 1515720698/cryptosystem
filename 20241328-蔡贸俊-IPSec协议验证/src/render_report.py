"""Markdown 转中文 PDF；需要 markdown、playwright 和本机 Edge。"""
from pathlib import Path
import re,sys,os,tempfile
import markdown
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]
md=R/'20241328-蔡贸俊-IPSec协议验证.md'
body=markdown.markdown(md.read_text(encoding='utf8'),extensions=['extra','sane_lists'])
body=re.sub(r'src="(images/[^"]+)"',lambda m:'src="'+(R/m[1]).as_uri()+'"',body)
css='''
@page { size:A4; }
body {font-family:'Microsoft YaHei','SimSun',sans-serif;color:#202a36;font-size:10.2pt;line-height:1.65;}
h1 {font-size:23pt;color:#163957;border-bottom:2px solid #2b6184;padding-bottom:9px;margin-top:0;}
h2 {font-size:15pt;color:#163957;border-bottom:1px solid #a9bdcc;margin-top:1.1em;padding-bottom:3px;}
h3 {font-size:11.5pt;color:#264862;margin-top:1.1em;}
h1,h2,h3 {break-after:avoid;}
pre {white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f6f8;border:1px solid #d9e2e8;border-radius:4px;padding:8px 10px;font-size:8.5pt;line-height:1.5;break-inside:avoid;}
code {font-family:Consolas,'Microsoft YaHei',monospace;font-size:.9em;overflow-wrap:anywhere;}
pre code {font-size:inherit;}
table {border-collapse:collapse;width:100%;font-size:9.1pt;line-height:1.55;margin:10px 0;break-inside:avoid;}
th,td {border:1px solid #b9cbd7;padding:5px 7px;overflow-wrap:anywhere;vertical-align:top;}
th {background:#eaf1f6;color:#163957;}
tr {break-inside:avoid;}
img {display:block;margin:auto;max-width:100%;max-height:132mm;object-fit:contain;}
p:has(img) {break-inside:avoid;break-after:avoid;margin:10px 0 3px;}
p:has(>em:only-child) {font-size:9pt;text-align:center;color:#526679;margin-top:3px;}
a {color:#245978;text-decoration:none;overflow-wrap:anywhere;}
'''
with tempfile.TemporaryDirectory(prefix='ipsec-render-',dir=r'C:\Users\z8319\AppData\Local\Temp\opencode') as tmp:
 html=Path(tmp)/'report.html';html.write_text('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>'+css+'</style></head><body>'+body+'</body></html>',encoding='utf8')
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=os.environ.get('EDGE_PATH',r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'),headless=True)
  page=browser.new_page();page.goto(html.as_uri());page.evaluate('document.fonts.ready');page.wait_for_timeout(1000)
  assert page.locator('img').evaluate_all('(imgs)=>imgs.every(i=>i.complete&&i.naturalWidth>0)')
  page.pdf(path=str(md.with_suffix('.pdf')),format='A4',print_background=True,margin={'top':'17mm','bottom':'18mm','left':'18mm','right':'18mm'},display_header_footer=True,header_template='<span></span>',footer_template='<div style="width:100%;font-size:8px;color:#708090;text-align:center;"><span>20241328 蔡贸俊 · IPSec协议验证</span>　｜　<span class="pageNumber"></span> / <span class="totalPages"></span></div>')
  browser.close()
print('PDF generated:',md.with_suffix('.pdf'))
