"""Stilts workshops dossier (CA/ES/EN) -> static/pdf/  (WeasyPrint)
Usage (from the repo root): python3 dossiers/stilts-workshops/build.py [ca es en]
Text: dossiers/stilts-workshops/<lang>.md · Photos: source-images/ (never cropped)."""
import re, sys, pathlib, tempfile
from PIL import Image, ImageOps
from weasyprint import HTML

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
IMGSRC = ROOT/'source-images'
OUT = ROOT/'static'/'pdf'
TMP = pathlib.Path(tempfile.mkdtemp())

def norm(s): return re.sub(r'_+', '_', s.lower())
FILES = {norm(f.stem): f for f in IMGSRC.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png')}

def prep(n):
    """copy a source photo (downscaled, rotated upright) into the temp folder; returns its path"""
    dst = TMP/f'{n}.jpg'
    if not dst.exists():
        im = ImageOps.exif_transpose(Image.open(FILES[norm(n)]))
        if n.startswith('logo'):
            dst = TMP/f'{n}.png'; im.thumbnail((1200, 1200)); im.save(dst); return dst
        im = im.convert('RGB'); im.thumbnail((1600, 1600)); im.save(dst, quality=82)
    return dst

W = 174.0  # content width mm (A4 210 - 2*18)
GAP = 3.0

def ar(n):
    w, h = Image.open(prep(n)).size
    return w / h

def row(names, width=W):
    ars = [ar(n) for n in names]
    h = (width - GAP * (len(names) - 1)) / sum(ars)
    imgs = ''.join(f'<img src="{prep(n).as_uri()}" style="height:{h:.2f}mm;width:{h*a:.2f}mm">' for n, a in zip(names, ars))
    return f'<div class="row">{imgs}</div>'

def mosaic(big, smalls, width=W, flip=False):
    """Big photo + stacked column of smaller ones, exact heights, no cropping."""
    aB = ar(big); S = sum(1 / ar(n) for n in smalls); k = len(smalls)
    w2 = (width - GAP - aB * GAP * (k - 1)) / (aB * S + 1)
    H = w2 * S + GAP * (k - 1); w1 = aB * H
    bigh = f'<img src="{prep(big).as_uri()}" style="height:{H:.2f}mm;width:{w1:.2f}mm">'
    col = ''.join(f'<img src="{prep(n).as_uri()}" style="width:{w2:.2f}mm;height:{w2/ar(n):.2f}mm">' for n in smalls)
    colh = f'<div class="col" style="width:{w2:.2f}mm">{col}</div>'
    return f'<div class="row">{colh + bigh if flip else bigh + colh}</div>'

COVER = 'tallers_zancos_1'
LOGO = 'logo_vendaval_2025-04_sin_fondo'

def css():
    cw, ch = Image.open(prep(COVER)).size
    cover_h = 210 * ch / cw
    return f"""
@page {{ size: A4; margin: 16mm 18mm 26mm 18mm;
  @bottom-center {{ content: element(foot); width: 210mm; }} }}
@page :first {{ margin: 0 0 22mm 0; }}
@page nofoot {{ @bottom-center {{ content: none; }} }}
.lastpage {{ page: nofoot; }}
:root {{ --blue:#18DBF7; --purple:#A64CF5; --ink:#0f2238; }}
body {{ font-family: Inter; font-size: 10pt; line-height: 1.45; color: var(--ink); margin:0; }}
.foot {{ position: running(foot); background: var(--ink); color:#fff; font-size:7.5pt;
  padding: 3.5mm 18mm; display:flex; justify-content: space-between; }}
.foot b {{ color: var(--blue); font-weight:700; letter-spacing:.06em; display:block; font-size:6.5pt; }}
.cover {{ position: relative; }}
.cover img.photo {{ width:210mm; height:{cover_h:.2f}mm; display:block; }}
.cover .logo {{ position:absolute; top:12mm; left:14mm; width:62mm; }}
.kicker {{ position:absolute; top:5mm; left:14mm; right:14mm; color:#fff; font-size:7pt;
  font-weight:700; letter-spacing:.14em; display:flex; justify-content:space-between; }}
.coverbody {{ padding: 8mm 18mm 0 18mm; font-size:11.5pt; }}
h1 {{ font-family:"Inter Display"; font-weight:900; font-size:36pt; line-height:1; margin:0;
  color: var(--purple); text-transform:uppercase; letter-spacing:-.01em; }}
.sub {{ font-weight:700; color: var(--ink); margin: 1.5mm 0 4mm; font-size:11pt; }}
.keys {{ display:flex; gap:2mm; margin-bottom:5mm; }}
.keys div {{ flex:1; color:#fff; text-align:center; padding:4mm 1mm; }}
.keys div:nth-child(odd) {{ background: var(--purple); }}
.keys div:nth-child(even) {{ background: var(--blue); color: var(--ink); }}
.keys b {{ display:block; font-family:"Inter Display"; font-weight:900; font-size:26pt; line-height:1.05; }}
.keys span {{ font-size:7pt; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }}
.support {{ font-size:8.5pt; font-weight:700; color: var(--purple); letter-spacing:.05em; margin-top:2mm; }}
h2 {{ font-family:"Inter Display"; font-weight:900; font-size:20pt; line-height:1.1;
  color: var(--purple); text-transform:uppercase; margin: 10mm 0 3mm; }}
h2.first {{ margin-top: 0; }}
h3 {{ font-size:8.5pt; font-weight:800; letter-spacing:.14em; text-transform:uppercase;
  color: var(--ink); background: var(--blue); display:inline-block; padding:.6mm 2mm; margin: 4mm 0 2mm; }}
p {{ margin: 0 0 2.5mm; }}
ul {{ margin: 0 0 2mm; padding-left: 5mm; }}
li {{ margin-bottom: 1mm; }}
li::marker {{ color: var(--purple); }}
.row {{ display:flex; gap:{GAP}mm; margin: 4mm 0 0; }}
.row img {{ display:block; }}
.col {{ display:flex; flex-direction:column; gap:{GAP}mm; }}
.col img {{ display:block; }}
.keep {{ break-inside: avoid; }}
.newpage {{ break-before: page; }}
.contact {{ background: var(--ink); color:#fff; padding:6mm 7mm; margin-top:4mm; }}
.contact b {{ color: var(--blue); }}
a {{ color: inherit; text-decoration: none; }}
.nm {{ text-transform: none; }}
"""

LANG = {
 'en': dict(out='VENDAVAL_Stilts-Workshops_EN_dossier.pdf',
   kicker='DOSSIER · STILTS WORKSHOPS · 2026-10', sub='For kids, youth and adults',
   keys=[('8+', 'Ages'), ('2', 'Hours'), ('20', 'Participants max.'), ('0', 'Power needed')],
   foot=['CONTACT', 'EMAIL', 'TEL.', 'WEB'], who='tyle fernández (they/them)', title='VENDAVAL – Stilts workshops'),
 'ca': dict(out='VENDAVAL_Tallers-Xanques_CA_dossier.pdf',
   kicker='DOSSIER · TALLERS DE XANQUES · 2026-10', sub='Per a infants, joves i persones adultes',
   keys=[('8+', 'Anys'), ('2', 'Hores'), ('20', 'Participants màx.'), ('0', 'Endolls necessaris')],
   foot=['CONTACTE', 'CORREU', 'TEL.', 'WEB'], who='tyle fernández {elli}', title='VENDAVAL – Tallers de xanques'),
 'es': dict(out='VENDAVAL_Talleres-Zancos_ES_dossier.pdf',
   kicker='DOSSIER · TALLERES DE ZANCOS · 2026-10', sub='Para peques, jóvenes y personas adultas',
   keys=[('8+', 'Años'), ('2', 'Horas'), ('20', 'Participantes máx.'), ('0', 'Enchufes necesarios')],
   foot=['CONTACTO', 'CORREO', 'TEL.', 'WEB'], who='tyle fernández {elle}', title='VENDAVAL – Talleres de zancos'),
}

def inline(t):
    t = t.replace('&', '&amp;').replace('<', '&lt;')
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', t)
    # the name stays lowercase even in uppercase headings
    t = t.replace('tyle fernández', '<span class="nm">tyle fernández</span>')
    return t

def blocks(lines):
    out, ul = [], []
    def flush():
        if ul: out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in ul) + '</ul>'); ul.clear()
    for l in lines:
        l = l.rstrip()
        if l.startswith('- '): ul.append(l[2:]); continue
        flush()
        if not l: continue
        if l.startswith('### '): out.append(f'<h3>{inline(l[4:])}</h3>')
        else: out.append(f'<p>{inline(l)}</p>')
    flush()
    return '\n'.join(out)

# photo blocks after each section, by index (same structure in every language)
def after(code):
    w1, w6 = {'en': (110, 98), 'ca': (80, 100), 'es': (80, 100)}[code]
    return {
        0: row(['tallers_zancos_2', 'stilts_workshops_2']),
        1: row(['stilts_workshop_40', 'tyle_stilts_portfolio_3'], w1),
        2: row(['stilts_workshops_1']) + row(['stilts_30']),
        3: mosaic('vendaval_firavapor002', ['vendaval_unterwegs004', 'vendaval_102']),
        7: mosaic('tyle_stilts_circografia_01', ['tyle_stilts_portfolio_101', 'tyle_stilts_portfolio_8', 'tyle_stilts_portfolio_2'], w6),
    }
NEWPAGE = {0, 1, 2, 3, 6}

def build(code):
    L = LANG[code]
    md = (HERE/f'{code}.md').read_text(encoding='utf-8')
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)
    head, *secs = re.split(r'^## ', md, flags=re.M)
    hl = head.strip().splitlines()
    h1 = hl[0][2:].strip()
    paras = [l for l in hl[1:] if l.strip() and not l.startswith('**')]
    support = [p for p in paras if p.startswith('*')]
    intro = [p for p in paras if not p.startswith('*')]
    keys = ''.join(f'<div><b>{a}</b><span>{b}</span></div>' for a, b in L['keys'])
    f = L['foot']
    foot = f"""<div class="foot"><div><b>{f[0]}</b>{L['who']}</div><div><b>{f[1]}</b>VENDAVAL@anartist.org</div>
<div><b>{f[2]}</b>+34 644 389 757</div><div><b>{f[3]}</b>vendaval.cat</div></div>"""
    last_photos = (row(['tyle_stilts_portfolio_4', 'tyle_stilts_portfolio_1', 'tyle_performance_1', 'tyle_stilts_portfolio_5'])
                   + row(['tyle_performance_2', 'tyle_stilts_portfolio_6'], 165))
    A = after(code)
    body = []
    n = len(secs)
    for i, s in enumerate(secs):
        title, *rest = s.splitlines()
        if i == n - 1:  # contact
            r = [x for x in rest if x.strip()]
            box = f'<p style="font-size:12pt;font-weight:800">{inline(r[0])}</p><p>' + '<br>'.join(inline(x) for x in r[1:]) + '</p>'
            body.append(f'<div class="newpage lastpage"><div class="keep">{last_photos}</div>'
                        f'<div class="keep"><h2>{inline(title)}</h2><div class="contact">{box}</div></div></div>')
            continue
        cls = 'newpage keep' if i in NEWPAGE else ('' if i == 7 else 'keep')
        h2c = ' class="first"' if i in NEWPAGE else ''
        body.append(f'<div class="{cls}"><h2{h2c}>{inline(title)}</h2>\n{blocks(rest)}\n<div class="keep">{A.get(i, "")}</div></div>')
    html = f"""<!doctype html><html lang="{code}"><head><meta charset="utf-8"><title>{L['title']}</title><style>{css()}</style></head><body>
{foot}
<div class="cover"><img class="photo" src="{prep(COVER).as_uri()}">
<div class="kicker"><span>{L['kicker']}</span><span>BARCELONA · TERRASSA</span></div>
<img class="logo" src="{prep(LOGO).as_uri()}"></div>
<div class="coverbody"><h1>{inline(h1)}</h1><div class="sub">{L['sub']}</div><div class="keys">{keys}</div>
{''.join(f'<p>{inline(p)}</p>' for p in intro)}
{''.join(f'<div class="support">{inline(p.strip("*")).upper()}</div>' for p in support)}
</div>
{''.join(body)}
</body></html>"""
    out = OUT/L['out']
    HTML(string=html, base_url=str(TMP)).write_pdf(out)
    print(out.relative_to(ROOT))

if __name__ == '__main__':
    for c in (sys.argv[1:] or ['ca', 'es', 'en']):
        build(c)
