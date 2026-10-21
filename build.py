import sys
#!/usr/bin/env python3
"""Build the VENDAVAL website into docs/ (served by GitHub Pages).

Texts:  content/i18n/<lang>.json  (all strings are HTML; a language is live when its file exists)
Facts:  content/data.json         (shows, agenda, artists, downloads, photos)
Layout: src/page.html + includes, src/style.css, src/site.js
Static: static/ (fonts, ready-made webp images, PDFs) is copied as is.
New photos: put the original in source-images/ and use its slug in data.json.

Pages per language:  /<lang>/  ·  /<lang>/<show-slug>/  ·  /<lang>/workshops|agenda|artists|downloads/
Short links:         /dossier/<short>/<lang>/  ·  /rider/<short>/<lang>/  (without <lang>: browser language)
Run:  pip install jinja2 pillow && python3 build.py
"""
import json, datetime, pathlib, re, shutil, zipfile, io
from jinja2 import Environment, FileSystemLoader
from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).parent
SRC, OUT, CONTENT, STATIC, IMGSRC = ROOT/'src', ROOT/'docs', ROOT/'content', ROOT/'static', ROOT/'source-images'
data = json.loads((CONTENT/'data.json').read_text(encoding='utf-8'))
SITE_URL = 'https://' + data['site']['domain'] if data['site'].get('domain_live') else data['site']['preview_url']
langs = [l for l in data['languages'] if (CONTENT/'i18n'/f'{l}.json').exists()]
i18n = {l: json.loads((CONTENT/'i18n'/f'{l}.json').read_text(encoding='utf-8')) for l in langs}
today = datetime.date.today().isoformat()
version = datetime.datetime.now().strftime('%Y%m%d%H%M')

def slug(name): return re.sub(r'[^a-z0-9]+', '-', pathlib.Path(name).stem.lower()).strip('-')

# ---------- static files and images
def build_static():
    if OUT.exists():
        for p in OUT.iterdir():
            if p.name not in ('img', 'press'): (shutil.rmtree if p.is_dir() else pathlib.Path.unlink)(p)
    shutil.copytree(STATIC, OUT, dirs_exist_ok=True)
    (OUT/'assets').mkdir(exist_ok=True)
    for f in ('style.css', 'site.js', 'crew.js'): shutil.copy(SRC/f, OUT/'assets'/f)
    shutil.copytree(SRC/'crew-data', OUT/'assets'/'crew-data', dirs_exist_ok=True)
    # any new photo in source-images/ that has no web version yet
    for f in sorted(IMGSRC.iterdir()):
        s = slug(f.name)
        if f.suffix.lower() not in ('.jpg', '.jpeg', '.png') or (OUT/'img'/f'{s}-800.webp').exists(): continue
        im = ImageOps.exif_transpose(Image.open(f)).convert('RGB')
        for w in (800, 1600):
            c = im.copy(); c.thumbnail((w, w * 2)); c.save(OUT/'img'/f'{s}-{w}.webp', quality=80, method=6)

def original(s):
    name = data.get('originals', {}).get(s)
    if name:
        for f in IMGSRC.iterdir():
            if f.name == name: return f
    for f in IMGSRC.iterdir():
        if slug(f.name) == s: return f

# ---------- press photo ZIPs: web (1000 px) and print (long side >= 1500 px, 300 dpi)
press_zips = {}
def build_press():
    (OUT/'press').mkdir(exist_ok=True)
    for key, imgs in data['press'].items():
        z = {}
        for kind in ('web', 'print'):
            buf = io.BytesIO(); n = 0
            with zipfile.ZipFile(buf, 'w', zipfile.ZIP_STORED) as zf:
                for i, s in enumerate(imgs, 1):
                    if kind == 'web':
                        im = Image.open(OUT/'img'/f'{s}-1600.webp').convert('RGB'); im.thumbnail((1000, 1000))
                        b = io.BytesIO(); im.save(b, 'JPEG', quality=85, dpi=(72, 72))
                    else:
                        f = original(s)
                        if not f: continue
                        im = ImageOps.exif_transpose(Image.open(f)).convert('RGB')
                        if max(im.size) < 1500: continue
                        b = io.BytesIO(); im.save(b, 'JPEG', quality=92, dpi=(300, 300))
                    zf.writestr(f'VENDAVAL_{key}_{i:02d}_{s}.jpg', b.getvalue()); n += 1
            if n:
                p = OUT/'press'/f'VENDAVAL_{key}_photos_{kind}.zip'
                if not p.exists() or p.read_bytes() != buf.getvalue(): p.write_bytes(buf.getvalue())
                z[kind] = {'url': f'press/{p.name}', 'n': n, 'mb': f'{p.stat().st_size / 1e6:.1f}'}
        press_zips[key] = z

# ---------- helpers
ICONS = {p.stem: p.read_text().strip() for p in (SRC/'icons').glob('*.svg')}
def icon(name): return ICONS.get(name, '').replace('<svg ', '<svg class="icon" aria-hidden="true" focusable="false" ', 1)

MONTHS = {
 'ca': 'gen. febr. març abr. maig juny jul. ag. set. oct. nov. des.', 'es': 'ene feb mar abr may jun jul ago sep oct nov dic',
 'en': 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec', 'de': 'Jan. Feb. März Apr. Mai Juni Juli Aug. Sept. Okt. Nov. Dez.',
 'fr': 'janv. févr. mars avr. mai juin juil. août sept. oct. nov. déc.', 'it': 'gen feb mar apr mag giu lug ago set ott nov dic',
 'pt': 'jan fev mar abr mai jun jul ago set out nov dez', 'ja': ''}
def make_fmt(lang):
    M = MONTHS[lang].split()
    def d(x): return datetime.date.fromisoformat(x)
    def fmt_range(start, end, precision='day'):
        a, b = d(start), d(end)
        if lang == 'ja':
            if precision == 'month': return f'{a.year}年{a.month}月 – {b.year}年{b.month}月'
            if a == b: return f'{a.year}年{a.month}月{a.day}日'
            return f'{a.year}年{a.month}月{a.day}日–{b.month}月{b.day}日'
        if precision == 'month': return f'{M[a.month-1]} {a.year} – {M[b.month-1]} {b.year}'
        if a == b: return f'{a.day} {M[a.month-1]} {a.year}'
        if a.month == b.month: return f'{a.day}–{b.day} {M[a.month-1]} {a.year}'
        return f'{a.day} {M[a.month-1]} – {b.day} {M[b.month-1]} {b.year}'
    return fmt_range

def loc(v, lang):
    if isinstance(v, dict): return v.get(lang) or v.get('*') or v.get('en') or ''
    return v or ''

def avail(key, lang=None):
    files = data['downloads'][key]['files']
    return [(l, u) for l, u in files.items() if (OUT/u).exists()]

def make_dlfile(lang):
    def dlfile(key):
        fs = dict(avail(key))
        for l in (lang, 'en', 'es', 'ca'):
            if l in fs: return {'url': fs[l], 'lang': l}
        l = next(iter(fs)); return {'url': fs[l], 'lang': l}
    return dlfile

# ---------- short links for emails: /dossier/brass/de/ -> the PDF
def redirect(target, rel):
    return f'<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={rel}{target}"><link rel="canonical" href="https://{data["site"]["domain"]}/{target}"><a href="{rel}{target}">{target}</a>\n'
def build_links():
    lines = []
    for key, d in data['downloads'].items():
        kind = 'rider' if d['kind'] == 'rider' else 'dossier'
        fs = dict(avail(key))
        if not fs: continue
        base = OUT/kind/d['short']
        for l, u in fs.items():
            (base/l).mkdir(parents=True, exist_ok=True); (base/l/'index.html').write_text(redirect(u, '../../../'))
            lines.append(f'{SITE_URL}/{kind}/{d["short"]}/{l}')
        js = json.dumps(fs)
        (base/'index.html').write_text(f'<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><script>var f={js},n=(navigator.languages||[navigator.language||"en"]).map(function(x){{return x.slice(0,2)}}),k=n.find(function(x){{return f[x]}})||(f.en?"en":Object.keys(f)[0]);location.replace("../../"+f[k]);</script>\n')
        lines.append(f'{SITE_URL}/{kind}/{d["short"]}  (opens in the reader\'s language)')
    (ROOT/'LINKS.txt').write_text('\n'.join(lines) + '\n')

# ---------- pages
def render():
    env = Environment(loader=FileSystemLoader(SRC), autoescape=False, trim_blocks=True, lstrip_blocks=True)
    env.filters['loc'] = loc
    tpl = env.get_template('page.html')
    shows = data['shows']; slugs = {s['id']: s['slug'] for s in shows}
    agenda = data['agenda']
    up = sorted([e for e in agenda if e['end'] >= today], key=lambda e: e['start'])
    past = sorted([e for e in agenda if e['end'] < today], key=lambda e: (e['end'], e['start']), reverse=True)
    boxes = {b['id']: b for b in data['download_boxes']}
    urls = []
    for lang in langs:
        t = i18n[lang]
        groups = [dict(g, url_l=loc(g['url'], lang)) for g in data['workshop_groups']]
        base = dict(data, site_url=SITE_URL, t=t, lang=lang, langs=langs, i18n=i18n, today=today, version=version, icon=icon,
                    fmt_range=make_fmt(lang), slugs=slugs, agenda_up=up, agenda_past=past, boxes=boxes,
                    press_zips=press_zips, avail=avail, shows_by_id={x['id']: x for x in shows}, dlfile=make_dlfile(lang), workshop_groups=groups,
                    og_image='og/photo-' + data['hero_slides'][0]['image'] + '.jpg', page_title=None, page_desc=None)
        pages = [('', 'home', {})]
        for s in shows:
            st = t['show'][s['id']]
            pages.append((s['slug'] + '/', 'show', {'s': s, 'page_title': st['name'], 'page_desc': re.sub('<[^>]+>', '', st['text'][0])[:180], 'og_image': 'og/photo-' + s['cover'] + '.jpg'}))
        for k in ('workshops', 'agenda', 'artists', 'downloads', 'crew'):
            og = ('og/photo-' + data['workshop_groups'][0]['photo'] + '.jpg') if k == 'workshops' else f'og/{lang}-{k}.jpg'
            pages.append((k + '/', k, {'page_title': t['nav'][k], 'og_image': og}))
        for path, page, extra in pages:
            depth = path.count('/') + 1
            R = '../' * depth
            ctx = dict(base, page=page, path=path, R=R, H=R + lang + '/', **extra)
            out = OUT/lang/path/'index.html'; out.parent.mkdir(parents=True, exist_ok=True)
            html = tpl.render(**ctx)
            # links to another page always open at its top (#top), not at the old scroll position
            html = re.sub(r'href="((?:\.\./)+[a-z]{2}/(?:[a-z-]+/)?)"', r'href="\1#top"', html)
            out.write_text(html, encoding='utf-8')
            urls.append(f'{SITE_URL}/{lang}/{path}')
    # root: pick the visitor's language
    codes = json.dumps(langs)
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="ca"><meta charset="utf-8"><title>Cia. VENDAVAL</title>
<meta name="viewport" content="width=device-width, initial-scale=1"><link rel="icon" href="favicon.ico" sizes="any"><link rel="apple-touch-icon" href="img/apple-touch-icon.png">
<meta property="og:title" content="Cia. VENDAVAL"><meta property="og:image" content="{SITE_URL}/og/photo-{data['hero_slides'][0]['image']}.jpg">
<script>var L={codes},n=(navigator.languages||[navigator.language||"ca"]).map(function(x){{return x.slice(0,2).toLowerCase()}}),k=n.find(function(x){{return L.indexOf(x)>=0}})||"{data['site']['default_lang']}";location.replace(k+"/");</script>
<p>{' · '.join(f'<a href="{l}/">{i18n[l]["lang_name"]}</a>' for l in langs)}</p></html>
''')
    (OUT/'404.html').write_text(f'''<!doctype html><html><meta charset="utf-8"><title>VENDAVAL</title><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="/assets/style.css"><body><main class="sec"><div class="wrap"><h1>404</h1><p><a href="/">VENDAVAL.cat</a></p>
<p>{' · '.join(f'<a href="/{l}/">{i18n[l]["lang_name"]}</a>' for l in langs)}</p></div></main></body></html>
''')
    import tools.og as og
    og.make(OUT, force='--og' in sys.argv)
    # vendaval.cat only once its DNS points to GitHub (set site.domain_live = true in content/data.json)
    if data['site'].get('domain_live'): (OUT/'CNAME').write_text(data['site']['domain'] + '\n')
    elif (OUT/'CNAME').exists(): (OUT/'CNAME').unlink()
    (OUT/'.nojekyll').write_text('')
    (OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: https://{data["site"]["domain"]}/sitemap.xml\n')
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'<url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n' for u in urls) + '</urlset>\n')

def check():
    # every language needs the same keys as Catalan
    def keys(d, p=''):
        return {p + k for k in d} | {x for k, v in d.items() if isinstance(v, dict) for x in keys(v, p + k + '.')}
    ref = keys(i18n['ca'])
    for l in langs:
        miss = ref - keys(i18n[l])
        if miss: print(f'  ! {l}: missing {sorted(miss)[:8]}')
    for key, d in data['downloads'].items():
        for l, u in d['files'].items():
            if not (OUT/u).exists(): print(f'  ! missing PDF {u}')

if __name__ == '__main__':
    build_static(); build_press(); build_links(); render(); check()
    print(f'built {len(langs)} languages → docs/')
