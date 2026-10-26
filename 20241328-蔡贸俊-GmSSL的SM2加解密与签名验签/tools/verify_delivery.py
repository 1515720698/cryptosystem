from pathlib import Path
import hashlib
import json
import fitz
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent.parent
result = json.loads((root / 'logs/results.json').read_text(encoding='utf-8'))
report = (root / (root.name + '.md')).read_text(encoding='utf-8')
plain = (root / 'sn.txt').read_bytes()
assert plain == (root / 'sn2.txt').read_bytes() == (root / 'logs/sn_cli.txt').read_bytes()
assert len(plain) == result['input_bytes'] == 261
assert len(plain.splitlines()) == len(set(plain.splitlines())) == 29
assert plain.splitlines()[-1] == b'20241328'
assert hashlib.sha256(plain).hexdigest() == result['sha256_plain']
assert (root / 'sn.enc').stat().st_size == result['cipher_bytes']
assert (root / 'sn.sig').stat().st_size == result['signature_bytes']
assert all(result[k] is True for k in ['roundtrip', 'cli_decryption',
    'cli_verifies_c_signature', 'c_verifies_cli_signature',
    'tampered_message_rejected', 'truncated_ciphertext_rejected'])
assert 'AI 生成说明' in report and '255 + 6' in report
doc = fitz.open(root / (root.name + '.pdf'))
text = '\n'.join(p.get_text() for p in doc)
assert all(x in text for x in ['蔡贸俊', '20241328', 'sm2keygen', 'verify: PASS', 'verify: REJECT', 'AI 生成说明'])
rows = (len(doc) + 2) // 3
sheet = Image.new('RGB', (1350, rows * 660), '#b8b8b8')
draw = ImageDraw.Draw(sheet)
lines = ['Delivery verification: PASS', 'Actual Linux checks and report data consistency: PASS',
         'Chinese text and AI generation note in PDF: PASS', f'PDF pages: {len(doc)}']
for i, page in enumerate(doc):
    for block in page.get_text('blocks'):
        assert block[0] >= 35 and block[2] <= page.rect.width - 30, (i+1, block[:4])
    pix = page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2))
    image = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    image.thumbnail((430, 620))
    x, y = (i % 3)*450 + 10, (i // 3)*660 + 25
    sheet.paste(image, (x, y))
    draw.text((x, y - 18), f'Page {i+1}', fill='black')
    lines.append(f'Page {i+1}: {len(page.get_text())} extracted characters')
temp = Path(r'C:\Users\HUAWEI\AppData\Local\Temp\opencode')
assert temp.is_dir()
sheet.save(temp / 'sm2_pdf_overview.png')
(root / 'logs/submission-check.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('\n'.join(lines))
print('Preview:', temp / 'sm2_pdf_overview.png')
