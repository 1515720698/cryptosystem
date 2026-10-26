"""Crop only unused window area; preserve original captures alongside."""
from pathlib import Path
from PIL import Image

images = Path(__file__).resolve().parent.parent / 'images'
for name, box in [
    ('01-编译与加解密', (0, 0, 2000, 1300)),
    ('02-diff正确性验证', (0, 0, 1600, 1050)),
]:
    image = Image.open(images / (name + '.png'))
    image.crop(box).save(images / (name + '-裁剪.png'))
    print(name, image.size, '->', box)
