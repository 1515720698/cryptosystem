from pathlib import Path
from PIL import Image

images = Path(__file__).resolve().parent.parent / 'images'
for name, max_width in [('01-密钥生成与编译', 10000), ('02-加解密与diff验证', 2200), ('03-签名验签与篡改验证', 2200)]:
    image = Image.open(images / (name + '.png'))
    box = (0, 0, min(max_width, image.width), min(1350, image.height))
    image.crop(box).save(images / (name + '-展示.png'))
    print(name, image.size, box)
