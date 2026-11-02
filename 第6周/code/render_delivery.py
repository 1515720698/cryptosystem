"""Reuse installed skill renderers and save PDF verification evidence."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SITE = Path(sys.executable).parent / 'Lib' / 'site-packages'
sys.path.insert(0, str(SITE))
SKILL = Path.home() / '.config/opencode/skills/cryptosystem-report'
sys.path.insert(0, str(SKILL))
import mermaid_render
import md2pdf
md = ROOT / '20241328蔡贸俊《密码系统设计》.md'
png = ROOT / 'assets/week6-mindmap.png'
png.parent.mkdir(exist_ok=True)
mermaid = mermaid_render.extract_mermaid(md)
(png.parent / 'week6-mindmap.mmd').write_text(mermaid + '\n', encoding='utf-8')
sys.argv = ['mermaid_render', str(md), str(png)]
mermaid_render.main()
pdf = ROOT / '20241328蔡贸俊《密码系统设计》第6周.pdf'
sys.argv = ['md2pdf', str(md), str(pdf)]
md2pdf.main()
import fitz
from PIL import Image, ImageOps, ImageDraw
doc = fitz.open(pdf)
tiles = []
texts = []
for i, page in enumerate(doc):
    text = page.get_text()
    texts.append(text)
    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
    path = ROOT / f'evidence/pdf-page-{i+1}.png'
    pix.save(path)
    tile = Image.open(path).convert('RGB')
    tile.thumbnail((298, 421))
    tile = ImageOps.expand(tile, border=8, fill='#cccccc')
    tiles.append(tile)
sheet = Image.new('RGB', (3*314, ((len(tiles)+2)//3)*455), 'white')
for i, tile in enumerate(tiles):
    sheet.paste(tile, ((i%3)*314, (i//3)*455))
sheet.save(ROOT / 'evidence/pdf-contact-sheet.png')
alltext = '\n'.join(texts)
for token in ['第六周', '20241328', '蔡贸俊', '参考资料', '0x8009001B']:
    assert token in alltext, token
assert sum(len(p.get_images()) for p in doc) >= 1
(ROOT / 'evidence/pdf-text-check.txt').write_text(alltext, encoding='utf-8')
print('PDF CHECK PASS:', len(doc), 'pages; image present; Chinese and required tokens present')
