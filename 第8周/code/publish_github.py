"""Publish the week-8 report bundle through the GitHub REST API.

Reads its credential only from the already-running shell/process environment.
Never accepts a token argument and never stores, prints, or logs a token.
Requires requests and GITHUB_TOKEN or GH_TOKEN.
"""
from pathlib import Path
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

OWNER = '1515720698'
REPO = 'cryptosystem'
BRANCH = 'master'
API = 'https://api.github.com'
ROOT = Path(__file__).resolve().parents[1]
TITLE = '20241328蔡贸俊《密码系统设计》第 8 周'
REMOTE = '第8周'


def main():
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if not token:
        raise SystemExit('未找到 GITHUB_TOKEN 或 GH_TOKEN 环境变量；请在桌面 API 工具中设置并注入后重试。')
    auth_header = 'Bearer ' + token
    del token

    def api(method, path, **kwargs):
        payload = kwargs.get('json')
        headers = {'Authorization': auth_header,
                   'Accept': 'application/vnd.github+json',
                   'X-GitHub-Api-Version': '2022-11-28'}
        data = json.dumps(payload).encode('utf-8') if payload is not None else None
        if data is not None:
            headers['Content-Type'] = 'application/json'
        request = urllib.request.Request(API + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            try:
                detail = json.loads(exc.read().decode('utf-8')).get('message', 'request failed')
            except Exception:
                detail = 'request failed'
            raise RuntimeError(f'GitHub API {method} {path}: HTTP {exc.code}: {detail}') from None
        return json.loads(body.decode('utf-8')) if body else {}

    repo = api('GET', f'/repos/{OWNER}/{REPO}')
    if repo.get('default_branch'):
        branch = repo['default_branch']
    else:
        branch = BRANCH
    ref = api('GET', f'/repos/{OWNER}/{REPO}/git/ref/heads/{branch}')
    parent_sha = ref['object']['sha']
    parent_commit = api('GET', f'/repos/{OWNER}/{REPO}/git/commits/{parent_sha}')
    base_tree = parent_commit['tree']['sha']

    md_files = list(ROOT.glob('20241328*.md'))
    pdf_files = list(ROOT.glob('*.pdf'))
    if len(md_files) != 1 or len(pdf_files) != 1:
        raise RuntimeError('Expected exactly one report Markdown and one report PDF.')
    files = [md_files[0], pdf_files[0], ROOT / 'week8-mindmap.png', ROOT / 'README.md']
    files += sorted((ROOT / 'code').glob('*.c')) + sorted((ROOT / 'code').glob('*.py'))
    files += [ROOT / 'evidence' / 'experiment-log.txt', ROOT / 'evidence' / 'results.json']
    files += sorted(p for p in (ROOT / 'evidence').glob('*-cert.pem'))
    missing = [str(p) for p in files if not p.is_file()]
    if missing:
        raise RuntimeError('Required delivery files are missing: ' + ', '.join(missing))

    entries = []
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        remote_path = f'{REMOTE}/{relative}'
        data = path.read_bytes()
        blob = api('POST', f'/repos/{OWNER}/{REPO}/git/blobs',
                   json={'content': base64.b64encode(data).decode('ascii'), 'encoding': 'base64'})
        entries.append({'path': remote_path, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    tree = api('POST', f'/repos/{OWNER}/{REPO}/git/trees',
               json={'base_tree': base_tree, 'tree': entries})
    commit = api('POST', f'/repos/{OWNER}/{REPO}/git/commits',
                 json={'message': 'Add week 8 SSL-TLS preview report',
                       'tree': tree['sha'], 'parents': [parent_sha]})
    # Update the ref without force; a concurrent upstream change is reported
    # rather than overwritten.
    api('PATCH', f'/repos/{OWNER}/{REPO}/git/refs/heads/{branch}',
        json={'sha': commit['sha'], 'force': False})

    check = api('GET', f'/repos/{OWNER}/{REPO}/git/trees/{commit["sha"]}?recursive=1')
    expected = {e['path'] for e in entries}
    observed = {e['path'] for e in check.get('tree', [])}
    if not expected.issubset(observed):
        raise RuntimeError('Commit verification failed: some uploaded paths are missing.')
    print(f'Published {len(entries)} verified files in {OWNER}/{REPO}, branch {branch}.')
    print('Commit: ' + commit['html_url'])
    print('Folder: https://github.com/' + OWNER + '/' + REPO + '/tree/' + branch + '/' + urllib.parse.quote(REMOTE))
    for entry in entries:
        print('https://github.com/' + OWNER + '/' + REPO + '/blob/' + branch + '/' +
              '/'.join(urllib.parse.quote(x, safe='') for x in entry['path'].split('/')))


if __name__ == '__main__':
    main()
