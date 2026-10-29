"""Package the tracked reproducible snapshot plus offline Git evidence.

Run after the final documentation commit and bundle export. The original
large textbook/SDK archives remain local; selected source/runtime is bundled.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = '20241328_蔡贸俊_实验二_4-6学时_提交材料.zip'


def main():
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode('utf-8').split('\0')
    names = sorted(set(filter(None, names)) | {'实验二_4-6学时_本地Git历史.bundle', 'logs/git_log_完整.txt'})
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT).strip(), 'Commit intended changes before packaging'
    assert all('test_private.pem' not in name and 'github_token' not in name for name in names)
    assert all((ROOT/name).is_file() for name in names)
    result = json.loads((ROOT/'logs/crosscheck_results.json').read_text(encoding='utf-8'))
    assert result['passed'] == 59 and result['totals'] == {'software':40, 'hardware':19}
    for name, expected in result['input_output_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected, name
    provenance = json.loads((ROOT/'logs/textbook_source_provenance.json').read_text(encoding='utf-8'))
    for record in provenance:
        assert hashlib.sha256((ROOT/record['source']).read_bytes()).hexdigest() == record['source_sha256']
        assert hashlib.sha256((ROOT/record['output']).read_bytes()).hexdigest() == record['output_sha256']
    manifest = {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names}
    (ROOT/'SHA256SUMS.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    temp = ROOT/'交付包生成中.zip'
    with zipfile.ZipFile(temp, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=8) as archive:
        for name in names+['SHA256SUMS.json']:
            archive.write(ROOT/name, name)
    with zipfile.ZipFile(temp) as archive:
        assert archive.testzip() is None
        for name, expected in manifest.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected, name
        assert '运行实验.ps1' in archive.namelist()
        assert not any(name.startswith(('build/', '.git/')) or name.endswith('/test_private.pem') for name in archive.namelist())
        count = len(archive.infolist())
    target = ROOT/NAME
    temp.replace(target)
    proof = {'zip':NAME, 'file_count':count, 'bytes':target.stat().st_size,
             'sha256':hashlib.sha256(target.read_bytes()).hexdigest(), 'zip_crc_pass':True,
             'all_member_sha256_pass':True, 'all_input_output_sha256_pass':True,
             'textbook_source_and_portable_copy_provenance_pass':True,
             'runtime_private_pem_excluded':True, 'full_duplicate_sdk_excluded':True,
             'git_status_clean':True, 'verified_checks':result['passed']}
    (ROOT/'logs/package_verification.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(proof, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
