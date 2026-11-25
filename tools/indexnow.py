"""Tell Bing (and Yandex, Seznam, Naver…) which pages changed, via IndexNow (no account, no Google).
Usage: python tools/indexnow.py <old-commit> | all   — sends the URLs whose docs/<lang>/…/index.html changed since then.
The key file static/8587380bd31edcc34795ba994f6e7399.txt is published at https://vendaval.cat/8587380bd31edcc34795ba994f6e7399.txt and proves the site is ours."""
import sys, subprocess, json, urllib.request, pathlib, re
KEY = '8587380bd31edcc34795ba994f6e7399'
ROOT = pathlib.Path(__file__).resolve().parent.parent
data = json.loads((ROOT / 'content/data.json').read_text(encoding='utf-8'))
HOST = data['site']['domain']
before = sys.argv[1] if len(sys.argv) > 1 else 'HEAD~1'
if before == 'all':   # first time / by hand: every page in the sitemap
    sm = (ROOT / 'docs/sitemap.xml').read_text(encoding='utf-8')
    files = [ 'docs/' + u.split(HOST + '/', 1)[1] + 'index.html' for u in re.findall(r'<loc>([^<]+)</loc>', sm)]
else: files = subprocess.run(['git', 'diff', '--name-only', before, 'HEAD', '--', 'docs'], capture_output=True, text=True, cwd=ROOT).stdout.split()
urls = sorted({f'https://{HOST}/' + re.sub(r'index\.html$', '', f[len('docs/'):]) for f in files
               if re.match(r'docs/([a-z]{2}/([a-z-]+/)?|chimera-opera/)index\.html$', f) and not f.startswith('docs/pt/')})
if not urls: print('IndexNow: no page changed'); sys.exit(0)
body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY}.txt', 'urlList': urls[:10000]}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
try:
    with urllib.request.urlopen(req, timeout=30) as r: print(f'IndexNow: {len(urls)} URLs sent, HTTP {r.status}')
except Exception as e: print(f'IndexNow: not sent ({e})')   # never fail the build for this
