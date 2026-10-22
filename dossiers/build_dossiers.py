#!/usr/bin/env python3
"""Dossier PDFs from Markdown, in the VENDAVAL dossier design.

    python3 dossiers/build_dossiers.py imaginary-friend [ca es ...]

Each dossier folder has <lang>.md and dossier.json (output name, photos).
Markdown shape: "# Name — tagline", a bold key-figures line ("A · B · C"), intro paragraphs,
then "## Section" blocks. "## Trailer"/"## Contact" (in any language: the last two sections)
are merged into the contact box. Output goes to static/pdf/ (and so to the website).
"""
import sys, json, re, base64, pathlib, asyncio, io
import markdown
from PIL import Image, ImageOps
from playwright.async_api import async_playwright

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
IMGSRC = ROOT / 'source-images'
OUT = ROOT / 'static' / 'pdf'
HEADER = 'data:image/png;base64,' + base64.b64encode((HERE / 'assets' / 'header.png').read_bytes()).decode()
LABEL = {'ca': 'Dossier', 'es': 'Dossier', 'en': 'Dossier', 'de': 'Dossier', 'fr': 'Dossier', 'it': 'Dossier', 'pt': 'Dossier', 'ja': '作品資料'}

def photo(name, max_px=1400):
    f = IMGSRC / name
    im = ImageOps.exif_transpose(Image.open(f)).convert('RGB'); im.thumbnail((max_px, max_px))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=84)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode(), im.width / im.height

def row(names, height_mm, width_mm=178, gap=3):
    ps = [photo(n) for n in names]
    h = min(height_mm, (width_mm - gap * (len(ps) - 1)) / sum(r for _, r in ps))
    cells = ''.join(f'<img src="{src}" style="width:{r * h:.1f}mm;height:{h:.1f}mm">' for src, r in ps)
    return f'<div class="photos">{cells}</div>'

CSS = '''
@page{size:A4;margin:32mm 16mm 18mm}
*{box-sizing:border-box}
body{margin:0;font:10.5pt/1.5 Inter,"Noto Sans CJK JP",sans-serif;color:#222}
html[lang=ja] body{font-family:"Noto Sans CJK JP",Inter,sans-serif;line-height:1.7}
h1{font:800 30pt/1.05 Inter,"Noto Sans CJK JP",sans-serif;color:#1ab3bf;text-transform:uppercase;margin:0}
.tag{font-size:14pt;color:#555;margin:4px 0 2px}
.who{font-size:10pt;color:#8f4a96;font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin:0 0 12px}
.cover{display:block;max-width:100%;max-height:120mm;width:auto;height:auto;margin:0 auto 12px;border-radius:6px}
.figs{display:flex;background:#8f4a96;color:#fff;border-radius:6px;margin:0 0 14px}
.figs div{flex:1;padding:10px 12px;border-left:1px solid rgba(255,255,255,.35);font-weight:700;font-size:10pt;text-align:center}
.figs div:first-child{border-left:0}
.figs b{display:block;font-size:17pt;line-height:1.1}
.intro p:first-child{font-size:12pt;font-style:italic;color:#8f4a96}
h2{font:700 15pt/1.2 Inter,"Noto Sans CJK JP",sans-serif;color:#8f4a96;border-bottom:1.5px solid #8f4a96;padding-bottom:4px;margin:10mm 0 3mm;break-after:avoid}
section{break-inside:avoid}
section.long{break-inside:auto}
p{margin:0 0 2.2mm}
ul,ol{margin:0 0 2mm;padding-left:5mm}
li{margin:0 0 1.2mm}
a{color:#0f8a94}
.photos{display:flex;gap:3mm;justify-content:center;margin:6mm 0 0;break-inside:avoid}
.photos img{display:block;border-radius:4px}
.contact{margin-top:7mm;background:#f5ebdd;border-left:5px solid #1ab3bf;border-radius:6px;padding:5mm 6mm;break-inside:avoid}
.contact h2{border:0;margin:0 0 2mm;padding:0}
.contact p{margin:0 0 1mm}
.tcw{break-inside:avoid;margin-top:7mm}.tcw .photos{margin-top:3mm}
.tc{display:flex;gap:6mm;align-items:flex-start}
.tc.flip{flex-direction:row-reverse}
.tc .txt{flex:1 1 0;min-width:0}.tc .txt h2{margin-top:0}
.tc .ph{flex:0 0 82mm}.tc .ph .photos{margin:0 0 2.5mm;gap:2.5mm}
.c2{break-inside:avoid}.c2 .cols{columns:2;column-gap:7mm}.c2 .cols li,.c2 .cols p{break-inside:avoid}
'''

def parse(md):
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S).strip()
    head, *secs = re.split(r'^## ', md, flags=re.M)
    lines = head.strip().split('\n')
    title = lines[0].lstrip('# ').strip()
    name, _, tag = title.partition(' — ')
    rest = '\n'.join(lines[1:]).strip()
    m = re.match(r'\*\*(.+?)\*\*\s*', rest)
    figs = [x.strip() for x in m.group(1).split('·')] if m else []
    intro = rest[m.end():] if m else rest
    sections = []
    for s in secs:
        h, _, body = s.partition('\n')
        sections.append((h.strip(), body.strip()))
    return name.strip(), tag.strip(), figs, intro, sections

def fig_cell(f):
    m = re.match(r'^([\d–\-]+[′\']?)\s+(.*)$', f)
    return f'<div><b>{m.group(1)}</b>{m.group(2)}</div>' if m else f'<div>{f}</div>'

def render_html(cfg, lang):
    name, tag, figs, intro, sections = parse((HERE / cfg['dir'] / f'{lang}.md').read_text(encoding='utf-8'))
    M = lambda s: markdown.markdown(s)
    contact_secs = sections[-2:]; body_secs = sections[:-2]
    cover_src, _ = photo(cfg['cover'], 1800)
    out = [f'<h1>{name}</h1>', f'<p class="tag">{tag}</p>', f'<p class="who">Cia. VENDAVAL · {LABEL[lang]}</p>',
           f'<img class="cover" src="{cover_src}" style="max-height:{cfg.get("cover_h", 120)}mm">', '<div class="figs">' + ''.join(fig_cell(f) for f in figs) + '</div>',
           f'<div class="intro">{M(intro)}</div>']
    rows = cfg.get('rows', {})
    for i, (h, body) in enumerate(body_secs):
        cls = ' class="long"' if len(body) > 900 else ''
        r = rows.get(str(i)); lay = r if isinstance(r, dict) and ('side' in r or 'wide' in r or 'cols' in r) else None
        if lay: r = lay.get('rows', [])
        rs = r if isinstance(r, list) else ([r] if r else [])
        extra = ''.join(row(x['photos'] if isinstance(x, dict) else x, x.get('h', cfg.get('row_h', 55)) if isinstance(x, dict) else cfg.get('row_h', 55)) for x in rs)
        if cfg.get('two_col'):  # magazine layout: text | photos side by side, sections without photos in 2 columns
            sw = (lay or {}).get('side', 82)
            wide = ''.join(row(x['photos'], x.get('h', 90), width_mm=178, gap=3) for x in (lay or {}).get('wide', []))
            if rs:
                side = ''.join(row(x['photos'] if isinstance(x, dict) else x, x.get('h', 80) if isinstance(x, dict) else 80, width_mm=sw, gap=2.5) for x in rs)
                flip = ' flip' if (lay or {}).get('flip', i % 2) else ''
                out.append(f'<div class="tcw"><div class="tc{flip}"><div class="txt"><h2>{h}</h2>{M(body)}</div><div class="ph" style="flex:0 0 {sw}mm">{side}</div></div>{wide}</div>')
            elif wide:
                out.append(f'<div class="tcw"><section><h2>{h}</h2>{M(body)}</section>{wide}</div>')
            elif (lay or {}).get('cols'):
                out.append(f'<section class="c2"><h2>{h}</h2><div class="cols">{M(body)}</div></section>')
            else:
                out.append(f'<section{cls}><h2>{h}</h2>{M(body)}</section>')
        elif cfg.get('keep_photos'):  # section and its photos never split across pages
            out.append(f'<div style="break-inside:avoid"><section><h2>{h}</h2>{M(body)}</section>{extra}</div>')
        else:
            out.append(f'<section{cls}><h2>{h}</h2>{M(body)}</section>{extra}')
    (th, tb), (ch, cb) = contact_secs
    cb = cb.replace('\n', '  \n')
    out.append(f'<div class="contact"><h2>{ch}</h2>{M(cb)}<p>{M(tb)[3:-4]}</p></div>')
    return f'<!doctype html><html lang="{lang}"><meta charset="utf-8"><style>{CSS}</style><body>{"".join(out)}</body></html>', name

HEAD_T = f'<div style="width:100%;margin:0;padding:0;-webkit-print-color-adjust:exact"><img src="{HEADER}" style="width:210mm;display:block;margin-top:5mm"></div>'
FOOT_T = '<div style="width:100%;font:8pt Inter,sans-serif;color:#666;text-align:right;padding:0 16mm 0 0"><span class="pageNumber"></span>/<span class="totalPages"></span></div>'

def finish(pdf, out, name):
    import pymupdf
    d = pymupdf.open(stream=pdf, filetype='pdf'); n = d.page_count
    hdr = (HERE / 'assets' / 'header.png').read_bytes()
    for i, p in enumerate(d):
        w = p.rect.width
        p.insert_image(pymupdf.Rect(0, 15, w, 15 + w * 315 / 2480), stream=hdr)
        p.insert_text((w - 45 - 18, p.rect.height - 28), f'{i + 1}/{n}', fontsize=8, color=(.4, .4, .4))
    d.set_metadata({'title': f'{name} · Cia. VENDAVAL', 'author': 'Cia. VENDAVAL'})
    d.save(out, garbage=3, deflate=True); print(f'{out.name}: {n} pages')

async def build(key, langs):
    cfg = json.loads((HERE / key / 'dossier.json').read_text()); cfg['dir'] = key
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        for lang in langs:
            html, name = render_html(cfg, lang)
            await pg.set_content(html, wait_until='load')
            out = OUT / cfg['file'].format(name=cfg['names'].get(lang, cfg['names']['*']), L=lang.upper())
            pdf = await pg.pdf(format='A4', print_background=True, prefer_css_page_size=True)
            finish(pdf, out, name)
        await b.close()

if __name__ == '__main__':
    key = sys.argv[1]
    langs = sys.argv[2:] or [p.stem for p in sorted((HERE / key).glob('*.md'))]
    asyncio.run(build(key, langs))
