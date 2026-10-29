"""Create buildable openEuler copies from the supplied Windows textbook code.

The original Visual Studio projects remain unchanged under materials/. The
copies replace Windows' 32-bit unsigned long assumption with uint32_t and use
the attached MIRACL source in src/miracl instead of the textbook's Windows
mymiracl.lib binary.
"""

from pathlib import Path
import difflib
import hashlib
import json


ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "materials" / "教材代码" / "code"
if (ROOT / 'materials/textbook_selected/code').is_dir():
    BOOK = ROOT / 'materials/textbook_selected/code'
OUT = ROOT / "src" / "textbook"
RECORDS = []


def copy(source: Path, destination: Path, portable_u32: bool = False) -> None:
    raw = source.read_bytes()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('gb18030')
    text = text.replace('\r\n', '\n')
    original = text
    text = text.replace("#include <pch.h>\n", "").replace("#include \"pch.h\"\n", "")
    if portable_u32:
        text = "#include <stdint.h>\n" + text.replace("unsigned long", "uint32_t")
    if source.name == 'sm3.cpp':
        text = text.replace('#define ROTL(x,n) (SHL((x),n) | ((x) >> (32 - n)))',
                            '#define ROTL(x,n) ((uint32_t)((uint32_t)(x) << ((n)&31)) | ((uint32_t)(x) >> ((32-(n))&31)))')
    if source.name == 'sm4.cpp':
        # The source bytes are unsigned char but integer promotion is to int.
        # Cast every byte used for left shifts before the shift operation.
        import re
        text = re.sub(r'\((MK\[[^\]]+\]|PlainText\[[^\]]+\]|CipherText\[[^\]]+\]) <<', r'((unsigned int)\1 <<', text)
        text = re.sub(r'\(SM4_Sbox\[(.*?)\]\) <<', r'((unsigned int)SM4_Sbox[\1]) <<', text)
    if source.name == 'kdf.h':
        text = text.replace('(((x) << n) | ((x) >> (32 - n)))',
                            '(((uint32_t)(x) << ((n)&31)) | ((uint32_t)(x) >> ((32-(n))&31)))')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8", newline="\n")
    RECORDS.append({'source': str(source.relative_to(ROOT)), 'source_sha256': hashlib.sha256(raw).hexdigest(),
                    'output': str(destination.relative_to(ROOT)), 'output_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                    'diff': ''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True),
                                  fromfile=str(source.relative_to(ROOT)), tofile=str(destination.relative_to(ROOT))))})


def main() -> None:
    copy(BOOK / "ch03" / "3.6" / "test" / "test" / "sm4.cpp", OUT / "sm4" / "sm4.cpp")
    copy(BOOK / "ch03" / "3.6" / "test" / "test" / "sm4.h", OUT / "sm4" / "sm4.h")
    copy(BOOK / "ch04" / "4.2" / "test" / "test" / "sm3.cpp", OUT / "sm3" / "sm3.cpp", True)
    copy(BOOK / "ch04" / "4.2" / "test" / "test" / "sm3.h", OUT / "sm3" / "sm3.h", True)
    sm2 = BOOK / "ch14" / "14.2" / "test" / "test"
    for name in ("SM2_ENC.c", "SM2_ENC.h", "kdf.c", "kdf.h"):
        copy(sm2 / name, OUT / "sm2" / name, name.startswith("kdf"))
    (ROOT / 'logs/textbook_source_provenance.json').write_text(json.dumps(RECORDS, ensure_ascii=False, indent=2), encoding='utf-8')
    (ROOT / 'logs/textbook_portability.patch').write_text('\n'.join(x['diff'] for x in RECORDS), encoding='utf-8')


if __name__ == "__main__":
    main()
