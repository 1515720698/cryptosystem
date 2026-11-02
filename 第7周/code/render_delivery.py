"""Render report with installed cryptosystem-report skill; verify every page."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.executable).parent / 'Lib/site-packages'))
sys.path.insert(0, str(Path.home() / '.config/opencode/skills/cryptosystem-report'))
import mermaid_render
import md2pdf
import fitz
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
md = ROOT / '20241328蔡贸俊《密码系统设计》.md'
png = ROOT / 'assets/week7-mindmap.png'
png.parent.mkdir(exist_ok=True)
(png.parent / 'week7-mindmap.mmd').write_text(mermaid_render.extract_mermaid(md) + '\n', encoding='utf-8')
sys.argv = ['mermaid_render', str(md), str(png)]
mermaid_render.main()
# Keep section headings with subsequent content, including quoted notes.
md2pdf.CSS += '\nh2 + blockquote { break-after: avoid; }\n'
pdf = ROOT / '20241328蔡贸俊《密码系统设计》第7周.pdf'
sys.argv = ['md2pdf', str(md), str(pdf)]
md2pdf.main()
doc = fitz.open(pdf)
tiles, texts = [], []
for i, page in enumerate(doc):
    text = page.get_text()
    assert len(text.strip()) > 40, f'Blank or nearly blank page {i+1}'
    texts.append(text)
    path = ROOT / f'evidence/pdf-page-{i+1}.png'
    page.get_pixmap(matrix=fitz.Matrix(1, 1)).save(path)
    tile = Image.open(path).convert('RGB')
    tile.thumbnail((298, 421))
    tiles.append(ImageOps.expand(tile, border=8, fill='#cccccc'))
sheet = Image.new('RGB', (942, ((len(tiles)+2)//3)*455), 'white')
for i, tile in enumerate(tiles):
    sheet.paste(tile, ((i%3)*314, (i//3)*455))
sheet.save(ROOT / 'evidence/pdf-contact-sheet.png')
text = '\n'.join(texts)
for token in ['第七周', '20241328', '蔡贸俊', '参考资料', 'X509_verify_cert', 'certificate revoked']:
    assert token in text, token
assert '第六周预习报告' not in text
assert sum(len(p.get_images()) for p in doc) >= 1
(ROOT / 'evidence/pdf-text-check.txt').write_text(text, encoding='utf-8')
print('PDF CHECK PASS:', len(doc), 'pages; Chinese, sections, image and key terms verified')
