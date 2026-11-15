from pathlib import Path
import json
import math
import re
import fitz
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
evidence = root / 'evidence'
pdf = next(root.glob('*.pdf'))
md = next(root.glob('20241328*.md')).read_text(encoding='utf-8')
results = json.loads((evidence / 'results.json').read_text(encoding='utf-8'))
assert len(results) == 5 and all(row['passed'] for row in results)
assert len(re.findall(r'^## [一二三四五六]、', md, re.M)) == 6
for image in re.findall(r'!\[.*?\]\((.*?)\)', md):
    assert (root / image).is_file(), image
doc = fitz.open(pdf)
text = '\n'.join(page.get_text() for page in doc)
for phrase in ['20241328', '蔡贸俊', '第八周', 'SSL_set1_host', 'hostname mismatch',
               '不能，他不能证明自己的身份，无法合规完成签名']:
    assert phrase in text, phrase
assert '\ufffd' not in text
assert any(page.get_images() for page in doc), 'Missing mindmap image'
notes = [f'PDF pages: {len(doc)}', 'Six sections, identity, quotes, images and 5 cases: PASS']
sheet = Image.new('RGB', (450 * 3, 665 * math.ceil(len(doc) / 3)), '#cccccc')
draw = ImageDraw.Draw(sheet)
for index, page in enumerate(doc):
    pix = page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4), alpha=False)
    pix.save(evidence / f'pdf-page-{index + 1:02d}.png')
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    im.thumbnail((430, 620))
    x, y = (index % 3) * 450 + 10, (index // 3) * 665 + 30
    sheet.paste(im, (x, y))
    draw.text((x, y - 22), f'PAGE {index + 1}', fill='black')
    count = len(page.get_text().strip())
    assert count > 30, f'Unexpected blank page {index + 1}'
    outside = [b for b in page.get_text('blocks') if b[0] < 0 or b[1] < 0 or
               b[2] > page.rect.width + 1 or b[3] > page.rect.height + 1]
    assert not outside, f'Text exceeds page {index + 1}'
    notes.append(f'Page {index + 1}: text_chars={count}, images={len(page.get_images())}, bounds=PASS')
sheet.save(evidence / 'pdf-contact-sheet.png')
(evidence / 'pdf-text.txt').write_text(text, encoding='utf-8')
(evidence / 'delivery-check.txt').write_text('\n'.join(notes), encoding='utf-8')
print('\n'.join(notes))
