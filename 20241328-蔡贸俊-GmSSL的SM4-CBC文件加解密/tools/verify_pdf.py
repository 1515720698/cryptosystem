from pathlib import Path
import hashlib
import fitz
from PIL import Image, ImageOps, ImageDraw

root = Path(__file__).resolve().parent.parent
pdf = root / (root.name + '.pdf')
doc = fitz.open(pdf)
text = '\n'.join(p.get_text() for p in doc)
assert '蔡贸俊' in text and '20241328' in text
assert 'rand_bytes' in text and 'diff sn.txt sn2.txt' in text
assert 'sm4_cbc_encrypt_finish' in text
assert (root / 'sn.txt').read_bytes() == (root / 'sn2.txt').read_bytes()
assert (root / 'sn.txt').read_bytes() == (root / 'logs/sn_cli.txt').read_bytes()
assert (root / 'key.bin').stat().st_size == (root / 'iv.bin').stat().st_size == 16
report = (root / (root.name + '.md')).read_text(encoding='utf-8')
assert (root / 'key.bin').read_bytes().hex() in report
assert (root / 'iv.bin').read_bytes().hex() in report
assert (root / 'src/sm4_file.c').read_text(encoding='utf-8').strip() in report
assert sum(len(page.get_images()) for page in doc) >= 2
supp = root / 'logs/screenshot-run'
assert (supp / 'sm4_file.c').read_bytes() == (root / 'src/sm4_file.c').read_bytes()
assert (supp / 'sn.txt').read_bytes() == (supp / 'sn2.txt').read_bytes() == (root / 'sn.txt').read_bytes()
rows = (len(doc) + 2) // 3
sheet = Image.new('RGB', (3 * 450, rows * 660), '#b8b8b8')
draw = ImageDraw.Draw(sheet)
stats = []
for i, page in enumerate(doc):
    pix = page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2))
    image = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    image.thumbnail((430, 620))
    x, y = (i % 3) * 450 + 10, (i // 3) * 660 + 25
    sheet.paste(image, (x, y))
    draw.text((x, y - 18), f'Page {i+1}', fill='black')
    blocks = page.get_text('blocks')
    assert all(b[0] >= 40 and b[2] <= page.rect.width - 35 for b in blocks)
    stats.append(f'Page {i+1}: {len(page.get_text())} extracted characters')
temp = Path(r'C:\Users\HUAWEI\AppData\Local\Temp\opencode')
assert temp.is_dir()
sheet.save(temp / 'gmssl_pdf_overview.png')
result = '\n'.join([
    'Submission verification: PASS',
    'C source matches report appendix: PASS',
    'sn.txt == sn2.txt == CLI plaintext: PASS',
    'key/IV sizes and report consistency: PASS',
    'Chinese text extraction and horizontal page bounds: PASS',
    f'PDF pages: {len(doc)}', *stats,
    'sn.txt SHA256: ' + hashlib.sha256((root / 'sn.txt').read_bytes()).hexdigest(),
]) + '\n'
(root / 'logs/submission-check.txt').write_text(result, encoding='utf-8')
print(result)
print('Preview: ' + str(temp / 'gmssl_pdf_overview.png'))
