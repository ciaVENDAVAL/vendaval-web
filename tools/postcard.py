"""VENDAVAL Brass postcard for programmers and distributors: ONE trilingual card (CA · ES · EN).
A6 landscape (148 x 105 mm), 2 pages (front, back), 3 mm bleed on every side for the print shop (PDF page = 154 x 111 mm).
Usage: python3 tools/postcard.py  ->  postcard/VENDAVAL-Brass_CA-ES-EN_postal_<yyyy-mm>.pdf
Languages are told apart by style, always the same: CA bold · ES plain · EN italic.
Photos are never cropped: each one is shown whole and fades into a blurred copy of itself that fills the card.
Texts: short versions of dossiers/brass/<lang>.json. No prices or private data: this is public promoter material."""
import html, pathlib, datetime
import qrcode
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT/'source-images', ROOT/'postcard'
DFONTS, SFONTS, LOGOS = ROOT/'dossiers/assets/fonts', ROOT/'static/fonts', ROOT/'dossiers/assets/logos'
FRONT, BACK = 'VENDAVAL_003.jpg', 'VENDAVAL_passecalles_000.jpg'
QR_URL = 'https://vendaval.cat/dossier/brass/es'
LOGO = (LOGOS/'vendaval.png').as_uri()
e = html.escape

def tri(ca, es, en, sep='<br>'):
    """Same text in CA (bold), ES (plain), EN (italic)."""
    return sep.join([f'<b lang="ca">{e(ca)}</b>', f'<span lang="es">{e(es)}</span>', f'<i lang="en">{e(en)}</i>'])

BODY = ("Una cúmbia esclata al carrer: sis músics i dues criatures del mar, en xanques i monocicle, converteixen la plaça "
        "en una pista de ball. La banda es dirigeix amb senyals de mà, i el públic acaba dirigint-la.",
        "Una cumbia estalla en la calle: seis músicos y dos criaturas del mar, en zancos y monociclo, convierten la plaza "
        "en una pista de baile. La banda se dirige con señas de mano, y el público acaba dirigiéndola.",
        "A cumbia bursts into the street: six musicians and two sea creatures, on stilts and a unicycle, turn the square "
        "into a dance floor. The band is conducted with hand signals, and the audience ends up conducting it.")
FIGS = [('30′', ('passis', 'pases', 'sets')),
        ('8', ('artistes', 'artistas', 'artists')),
        ('0', ('tècnics', 'técnicos', 'technicians')),
        ('100%', ('acústic', 'acústico', 'acoustic'))]
LINES = [('Tots els públics, de dia o de nit', 'Todos los públicos, de día o de noche', 'All ages, day or night'),
         ('Diversos passis al dia, des de 4 músics', 'Varios pases al día, desde 4 músicos', 'Several sets a day, from 4 musicians'),
         ('També amplificat: Concert enmig del públic', 'También amplificado: Concierto entre el público', 'Also amplified: Concert in the audience')]
CREDITS = [(('Direcció artística', 'Dirección artística', 'Artistic direction'), 'tyle fernández'),
           (('Música', 'Música', 'Music'), 'Cia. VENDAVAL'),
           (('Vestuari', 'Vestuario', 'Costumes'), 'Imaginario de Mónica · Tropidelia'),
           (('Coproducció', 'Coproducción', 'Co-production'), 'Cia. Filigranes'),
           (('Fotografia', 'Fotografía', 'Photography'), 'ROAR · Albert Garcia')]

def ff(fam, path, weight=400, style='normal', ext=False):
    rng = ';unicode-range:U+0100-024F,U+1E00-1EFF' if ext else ''
    return f"@font-face{{font-family:{fam};font-weight:{weight};font-style:{style};src:url({path.as_uri()}){rng}}}"

FONTCSS = ''.join([
    ff('Anton', DFONTS/'anton-latin-400-normal.woff2'), ff('Anton', DFONTS/'anton-latin-ext-400-normal.woff2', ext=True),
    ff('Oswald', DFONTS/'oswald-latin-600-normal.woff2', 600), ff('Oswald', DFONTS/'oswald-latin-ext-600-normal.woff2', 600, ext=True),
    *[ff('Atk', SFONTS/f'atkinson-hyperlegible-latin{x}-{w}-{s}.woff2', w, s, ext=bool(x))
      for x in ('', '-ext') for w in (400, 700) for s in ('normal', 'italic')]])

def qr_svg(url):
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M); q.add_data(url); q.make()
    m = q.get_matrix(); n = len(m)
    rects = ''.join(f'<rect x="{x}" y="{y}" width="1.02" height="1.02"/>' for y, r in enumerate(m) for x, v in enumerate(r) if v)
    return f'<svg viewBox="0 0 {n} {n}" xmlns="http://www.w3.org/2000/svg" fill="#0F2C40">{rects}</svg>'

WAVE = ('<svg class="wave" viewBox="0 0 600 20" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M0 10 Q 25 0 50 10 T 100 10 T 150 10 T 200 10 T 250 10 T 300 10 T 350 10 T 400 10 T 450 10 T 500 10 T 550 10 T 600 10" '
        'fill="none" stroke="#EBA53B" stroke-width="2.2"/></svg>')

def page():
    img = lambda f: (SRC/f).as_uri()
    figs = ''.join(f'<div class="fig"><div class="n">{e(n)}</div><div class="l">{tri(*l)}</div></div>' for n, l in FIGS)
    lines = ''.join(f'<li>{tri(*l, sep=" · ")}</li>' for l in LINES)
    credits = ''.join(f'<div>{tri(*r, sep=" · ")}: <span class="nm">{e(n)}</span></div>' for r, n in CREDITS)
    body = ''.join(f'<p>{x}</p>' for x in [f'<b>{e(BODY[0])}</b>', e(BODY[1]), f'<i>{e(BODY[2])}</i>'])
    logos = ''.join(f'<img src="{(LOGOS/f).as_uri()}" alt="">' for f in ['tub-dassaig.png', 'filigranes.svg', 'bobila.png', 'apcc.svg'])
    return f'''<!doctype html><html lang="ca"><meta charset="utf-8"><title>VENDAVAL Brass · postal</title>
<style>{FONTCSS}
@page{{size:154mm 111mm;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{-webkit-print-color-adjust:exact;print-color-adjust:exact;color:#1E2A33;font-family:Atk,sans-serif}}
b{{font-weight:700;font-style:normal}} i{{font-style:italic;font-weight:400}} span[lang]{{font-weight:400}}
.pg{{width:154mm;height:111mm;position:relative;overflow:hidden;page-break-after:always;background:#0F2C40}}
.blur{{position:absolute;left:-8mm;top:-8mm;width:170mm;height:127mm;object-fit:cover;filter:blur(5mm) saturate(1.15)}}
.wave{{position:absolute;left:0;width:100%;height:3.2mm}}
/* FRONT: whole 16:9 photo, its bottom edge melting into the blurred copy; title band over the blur */
.front .photo{{position:absolute;left:0;top:0;width:154mm;height:86.6mm;display:block;
  -webkit-mask-image:linear-gradient(to bottom,#000 90%,transparent 100%);mask-image:linear-gradient(to bottom,#000 90%,transparent 100%)}}
.front .band{{position:absolute;left:0;top:84mm;width:154mm;height:27mm;padding:3.6mm 8mm 0;
  background:linear-gradient(to bottom,rgba(15,44,64,.5),rgba(15,44,64,.88) 35%)}}
.front .band .wave{{top:1mm}}
.front h1{{font:400 27pt/1 Anton,sans-serif;color:#F5EDDC;letter-spacing:.3mm;margin-top:1.2mm;text-shadow:0 .3mm 1mm rgba(0,0,0,.35)}}
.front h1 span{{color:#EBA53B}}
.front .sup{{position:absolute;right:8mm;top:6.4mm;display:flex;align-items:center;gap:2.6mm;background:rgba(245,237,220,.92);border-radius:1.6mm;padding:1.4mm 2.4mm}}
.front .sup img{{height:6mm;max-width:16mm;object-fit:contain}}
.front .kick{{font:600 6.4pt Oswald,sans-serif;letter-spacing:.45mm;color:#9FDCEC;margin-top:1mm}}
.front .sub{{position:absolute;right:37mm;top:5.2mm;text-align:right;font-size:7.4pt;line-height:1.3;color:#F5EDDC}}
.front .sub i{{color:#9FDCEC}}
.front .logo{{position:absolute;right:7mm;top:7mm;height:17mm;background:rgba(245,237,220,.92);border-radius:2mm;padding:1.2mm 2mm;box-shadow:0 .5mm 2mm rgba(0,0,0,.25)}}
.front .logo img{{height:100%;display:block}}
/* BACK: whole photo on the left (as shot), right edge melting into the blur; trilingual text card on the right */
.back .photo{{position:absolute;left:5mm;top:4mm;width:64mm;height:81.4mm;display:block;
  -webkit-mask-image:radial-gradient(ellipse 72% 70% at 50% 50%,#000 78%,transparent 100%);mask-image:radial-gradient(ellipse 72% 70% at 50% 50%,#000 78%,transparent 100%)}}
.card{{position:absolute;left:72mm;top:7mm;width:75mm;height:97mm;background:rgba(245,237,220,.95);border-radius:2.4mm;
  padding:3mm 3.6mm 2.6mm;display:flex;flex-direction:column;box-shadow:0 .6mm 3mm rgba(0,0,0,.25)}}
.head{{display:flex;align-items:center;gap:2.2mm}}
.head img{{height:9.5mm}}
.head h1{{font:400 17pt/1 Anton,sans-serif;color:#0F2C40;letter-spacing:.15mm}}
.head h1 span{{color:#B5401C}}
.head .sub{{font-size:5.6pt;line-height:1.25;color:#B5401C;margin-top:.6mm}}
.body{{margin-top:1.2mm}}
.body p{{font-size:6pt;line-height:1.26;margin-bottom:.8mm}}
.genres{{font:600 5.6pt Oswald,sans-serif;letter-spacing:.35mm;color:#0F2C40;border-top:.3mm solid #EBA53B;border-bottom:.3mm solid #EBA53B;padding:.5mm 0;text-align:center;margin:.4mm 0 1.4mm}}
.figs{{display:grid;grid-template-columns:repeat(4,1fr);gap:1.4mm}}
.fig .n{{font:400 12pt/1 Anton,sans-serif;color:#B5401C}}
.fig .l{{font-size:5.2pt;line-height:1.2;margin-top:.4mm}}
ul{{list-style:none;font-size:5.4pt;line-height:1.35;margin-top:1.3mm}}
li::before{{content:"\\2693\\FE0E";color:#B5401C;margin-right:1mm;font-size:4.4pt}}
.cr{{margin-top:1.3mm;font-size:5.2pt;line-height:1.36;color:#55636D}}
.cr .nm{{font-weight:700;color:#1E2A33}}
.foot{{position:absolute;left:8mm;top:84mm;width:61mm;height:20mm;display:flex;gap:2.6mm;align-items:center;background:rgba(15,44,64,.86);border-radius:2mm;padding:2mm 2.4mm;color:#F5EDDC}}
.ct{{flex:1;font-size:5.9pt;line-height:1.5;white-space:nowrap}}
.ct .co{{font:600 6.4pt Oswald,sans-serif;letter-spacing:.3mm;color:#EBA53B}}
.ct .logos{{display:flex;align-items:center;gap:2mm;margin-top:1.4mm}}
.ct .logos img{{height:4.6mm;max-width:12mm;object-fit:contain}}
.qr{{flex:0 0 14.5mm;text-align:center;font:600 4.6pt Oswald,sans-serif;letter-spacing:.2mm;color:#9FDCEC}}
.qr svg{{display:block;width:100%;margin-bottom:.5mm;background:#F5EDDC;padding:.8mm;border-radius:.6mm}}
</style>
<section class="pg front">
  <img class="blur" src="{img(FRONT)}" alt="">
  <img class="photo" src="{img(FRONT)}" alt="">
  <div class="band">{WAVE}
    <h1>VENDAVAL <span>BRASS</span></h1>
    <div class="kick">CIA. VENDAVAL · FUNK · BALKAN · SWING · CUMBIA</div>
    <div class="sup">{logos}</div>
  </div>
  <div class="logo"><img src="{LOGO}" alt="VENDAVAL"></div>
</section>
<section class="pg back">
  <img class="blur" src="{img(BACK)}" alt="">
  <img class="photo" src="{img(BACK)}" alt="">
  <div class="card">
    <div class="head"><img src="{LOGO}" alt="VENDAVAL"><h1>VENDAVAL <span>BRASS</span></h1></div>
    <div class="body">{body}</div>
    <div class="genres">FUNK · BALKAN · SWING · CUMBIA</div>
    <div class="figs">{figs}</div>
    <ul>{lines}</ul>
    <div class="cr">{credits}</div>
  </div>
    <div class="foot">
      <div class="ct"><span class="co">Cia. VENDAVAL</span><br><b>+34 644 389 757</b><br>VENDAVAL@anartist.org<br>www.VENDAVAL.cat · <i>@vendaval.brass</i>
</div>
      <div class="qr">{qr_svg(QR_URL)}DOSSIER</div>
    </div>
</section></html>'''

def build():
    OUT.mkdir(exist_ok=True); stamp = datetime.date.today().strftime('%Y-%m')
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        f = OUT/'_postcard.html'; f.write_text(page())
        pg.goto(f.as_uri()); pg.wait_for_load_state('networkidle')
        out = OUT/f'VENDAVAL-Brass_CA-ES-EN_postal_{stamp}.pdf'
        pg.pdf(path=str(out), width='154mm', height='111mm', print_background=True, prefer_css_page_size=True)
        f.unlink(); print('built', out.relative_to(ROOT))
        b.close()

if __name__ == '__main__':
    build()
