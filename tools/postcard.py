"""VENDAVAL Brass postcard for programmers and distributors: ONE trilingual card (CA · ES · EN).
A6 landscape (148 x 105 mm), 2 pages (front, back), 3 mm bleed on every side for the print shop (PDF page = 154 x 111 mm).
Usage: python3 tools/postcard.py  ->  postcard/VENDAVAL-Brass_CA-ES-EN_postal_<yyyy-mm>.pdf
Languages are told apart by style, always the same: CA bold · ES plain · EN italic. When CA and ES are identical, ES is left out.
Photos: back photos whole and sharp; front photo (VENDAVAL_003, 16:9) shown whole across the full width.
Credits: VENDAVAL Brass only (Tropidelia belongs to Amigui Imaginari and the website footer, not here).
No prices or private data: this is public promoter material."""
import html, pathlib, datetime
import qrcode
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT/'source-images', ROOT/'postcard'
DFONTS, SFONTS, LOGOS = ROOT/'dossiers/assets/fonts', ROOT/'static/fonts', ROOT/'dossiers/assets/logos'
FRONT = 'VENDAVAL_003.jpg'                                               # band on the move (unicycle, flags, stilts), 16:9, shown whole
GAMES = ['VENDAVAL_salvavidas_publico.jpg', 'VENDAVAL_FiraVapor002.jpg']   # lifebuoy game · sea-net game
QR_URL = 'https://vendaval.cat/es/brass/'   # show page (video, photos, dossier, rider, language switcher)
LOGO = (LOGOS/'vendaval.png').as_uri()
e = html.escape

def tri(ca, es, en, sep='<br>'):
    """Same text in CA (bold), ES (plain), EN (italic); ES dropped when it equals CA."""
    parts = [f'<b lang="ca">{e(ca)}</b>'] + ([] if es == ca else [f'<span lang="es">{e(es)}</span>']) + [f'<i lang="en">{e(en)}</i>']
    return sep.join(parts)

BODY = ("Una cúmbia esclata al carrer: sis músics i dues criatures del mar, en xanques i monocicle, converteixen la plaça "
        "en una pista de ball. La banda es dirigeix amb senyals de mà, i el públic acaba dirigint&#8209;la.",
        "Una cumbia estalla en la calle: seis músicos y dos criaturas del mar, en zancos y monociclo, convierten la plaza "
        "en una pista de baile. La banda se dirige con señas de mano, y el público acaba dirigiéndola.",
        "A cumbia bursts into the street: six musicians and two sea creatures, on stilts and a unicycle, turn the square "
        "into a dance floor. The band is conducted with hand signals, and the audience ends up conducting it.")
FIGS = [('30′', ('passis', 'pases', 'sets')), ('8', ('artistes', 'artistas', 'artists')),
        ('0', ('tècnics', 'técnicos', 'technicians')), ('100%', ('acústic', 'acústico', 'acoustic'))]
LINES = [('Tots els públics, de dia o de nit', 'Todos los públicos, de día o de noche', 'All ages, day or night'),
         ('Diversos passis al dia, des de 4 músics', 'Varios pases al día, desde 4 músicos', 'Several sets a day, from 4 musicians'),
         ('També amplificat: Concert enmig del públic', 'También amplificado: Concierto entre el público', 'Also amplified: Concert in the audience')]
CREDITS = [(('Direcció artística', 'Dirección artística', 'Artistic direction'), 'tyle fernández'),
           (('Música', 'Música', 'Music'), 'Cia. VENDAVAL'),
           (('Vestuari', 'Vestuario', 'Clothing'), 'Imaginario de Mónica'),
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

def qr_svg(url, fill='#0F2C40'):
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M); q.add_data(url); q.make()
    m = q.get_matrix(); n = len(m)
    rects = ''.join(f'<rect x="{x}" y="{y}" width="1.02" height="1.02"/>' for y, r in enumerate(m) for x, v in enumerate(r) if v)
    return f'<svg viewBox="0 0 {n} {n}" xmlns="http://www.w3.org/2000/svg" fill="{fill}">{rects}</svg>'

WAVE = ('<svg class="wave" viewBox="0 0 600 20" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M0 10 Q 25 0 50 10 T 100 10 T 150 10 T 200 10 T 250 10 T 300 10 T 350 10 T 400 10 T 450 10 T 500 10 T 550 10 T 600 10" '
        'fill="none" stroke="#EBA53B" stroke-width="2.2"/></svg>')

# soft edge: the photo stays whole, only its outer few millimetres fade into the background
FADE_ALL = ('-webkit-mask-image:linear-gradient(to right,transparent,#000 9%,#000 91%,transparent),linear-gradient(to bottom,transparent,#000 9%,#000 91%,transparent);'
            '-webkit-mask-composite:source-in;mask-image:linear-gradient(to right,transparent,#000 9%,#000 91%,transparent),linear-gradient(to bottom,transparent,#000 9%,#000 91%,transparent);mask-composite:intersect;')
FADE_LEFT = ('-webkit-mask-image:linear-gradient(to right,transparent,#000 7%);mask-image:linear-gradient(to right,transparent,#000 7%);')

def page():
    img = lambda f: (SRC/f).as_uri()
    figs = ''.join(f'<div class="fig"><div class="n">{e(n)}</div><div class="l">{tri(*l)}</div></div>' for n, l in FIGS)
    lines = ''.join(f'<li>{tri(*l, sep=" · ")}</li>' for l in LINES)
    credits = ''.join(f'<div>{tri(*r, sep=" · ")}: <span class="nm">{e(n)}</span></div>' for r, n in CREDITS)
    body = (f'<p><b>{BODY[0]}</b></p><p>{e(BODY[1])}</p><p><i>{e(BODY[2])}</i></p>')
    logos = ''.join(f'<img src="{(LOGOS/f).as_uri()}" alt="">' for f in ['tub-dassaig.png', 'filigranes.svg', 'bobila.png', 'apcc.svg'])
    contact = ('<span class="co">Cia. VENDAVAL</span><span>+34 644 389 757</span>'
               '<span>VENDAVAL@anartist.org</span><span>www.VENDAVAL.cat</span>')
    games = ''.join(f'<img class="g" src="{img(f)}" alt="">' for f in GAMES)
    return f'''<!doctype html><html lang="ca"><meta charset="utf-8"><title>VENDAVAL Brass · postal</title>
<style>{FONTCSS}
@page{{size:154mm 111mm;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{-webkit-print-color-adjust:exact;print-color-adjust:exact;color:#1E2A33;font-family:Atk,sans-serif}}
b{{font-weight:700;font-style:normal}} i{{font-style:italic;font-weight:400}} span[lang]{{font-weight:400}}
p,li,div{{text-wrap:pretty}}
.pg{{width:154mm;height:111mm;position:relative;overflow:hidden;page-break-after:always}}
.wave{{position:absolute;left:0;width:100%;height:3.2mm}}
/* FRONT: 16:9 photo across the full width, shown whole; logo on the photo top right; cream bar at the bottom with title + contact */
.front{{background:#F5EDDC}}
.front .photo{{position:absolute;left:0;top:0;width:154mm;height:86.6mm;display:block}}
.front .logo{{position:absolute;right:6mm;top:5.5mm;width:22mm;transform:rotate(-10deg);transform-origin:center}}
.strip{{position:absolute;left:0;top:86.6mm;width:154mm;height:24.4mm;background:#F5EDDC;padding:3mm 9mm 3mm 6.5mm;
  display:flex;align-items:center;justify-content:space-between;gap:5mm;color:#0F2C40}}
.strip .wave{{top:-1.6mm}}
.strip h1{{font:400 22pt/.95 Anton,sans-serif;letter-spacing:.3mm;color:#0F2C40;white-space:nowrap}}
.strip h1 span{{color:#B5401C}}
.strip .kick{{font:600 6pt Oswald,sans-serif;letter-spacing:.45mm;color:#B5401C;margin-top:1.2mm}}
.strip .ct2{{display:grid;grid-template-columns:auto auto;gap:1mm 6mm;font-size:7.4pt;font-weight:700;white-space:nowrap;text-align:left}}
.strip .co{{font:600 8pt Oswald,sans-serif;letter-spacing:.35mm;color:#B5401C}}
/* back: supporters inside the contact box */
.bsup{{display:flex;align-items:center;gap:4.5mm}}
.bsup img{{height:6mm;max-width:17mm;object-fit:contain}}
/* BACK: plain sand; text left, game photos right, edges fading into the sand */
.back{{background:#F5EDDC}}
.back .txt{{position:absolute;left:8mm;top:7mm;width:84mm;height:97mm;display:flex;flex-direction:column}}
.head{{display:flex;align-items:center;gap:2.4mm}}
.head img{{height:8.6mm}}
.head h1{{font:400 18pt/1 Anton,sans-serif;color:#0F2C40;letter-spacing:.15mm}}
.head h1 span{{color:#B5401C}}
.body{{margin-top:1.6mm}}
.body p{{font-size:5.9pt;line-height:1.25;margin-bottom:.6mm}}
.games{{font-size:6.1pt;line-height:1.3;color:#B5401C}}
.genres{{font:600 5.8pt Oswald,sans-serif;letter-spacing:.35mm;color:#0F2C40;border-top:.3mm solid #EBA53B;border-bottom:.3mm solid #EBA53B;padding:.5mm 0;text-align:center;margin:.8mm 0 1.2mm}}
.figs{{display:grid;grid-template-columns:repeat(4,1fr);gap:1.4mm;justify-items:center;text-align:center}}
.fig .n{{font:400 12pt/1 Anton,sans-serif;color:#B5401C}}
.fig .l{{font-size:5.3pt;line-height:1.2;margin-top:.4mm}}
ul{{list-style:none;font-size:5.4pt;line-height:1.3;margin-top:1mm}}
li{{padding-left:2.6mm;text-indent:-2.6mm}}
li [lang],.cr [lang]{{white-space:nowrap}}
li::before{{content:"\\2693\\FE0E";color:#B5401C;display:inline-block;width:2.6mm;text-indent:0;font-size:4.6pt}}
.cr{{margin-top:1.6mm;font-size:5.6pt;line-height:1.42;color:#55636D}}
.cr .nm{{font-weight:700;color:#1E2A33}}
.foot{{margin-top:auto;display:flex;gap:4mm;align-items:center;border-top:.3mm solid #EBA53B;padding-top:2mm}}
.foot .lab{{font-size:5.4pt;color:#55636D;margin-bottom:1.4mm}}
.clogo{{height:11mm;filter:drop-shadow(.35mm 0 0 #fff) drop-shadow(-.35mm 0 0 #fff) drop-shadow(0 .35mm 0 #fff) drop-shadow(0 -.35mm 0 #fff)}}
.ct{{flex:1;min-width:0;font-size:6pt;line-height:1.5}}
.ct .co{{font:600 6.6pt Oswald,sans-serif;letter-spacing:.3mm;color:#EBA53B}}
.qr{{text-align:right;font:600 5pt/1.3 Oswald,sans-serif;letter-spacing:.25mm;color:#0F2C40}}

.pics{{position:absolute;left:97mm;top:7mm;width:50mm;height:97mm;display:flex;flex-direction:column;gap:1.2mm}}
.pics .g{{width:50mm;display:block;border-radius:1.2mm}}
.pics .qr{{margin-top:auto;display:flex;justify-content:flex-end;align-items:center;gap:2mm}}
.pics .qr svg{{width:12mm;height:12mm;display:block}}
</style>
<section class="pg front">
  <img class="photo" src="{img(FRONT)}" alt="">
  <img class="logo" src="{LOGO}" alt="VENDAVAL">
  <div class="strip">{WAVE}
    <div><h1>VENDAVAL <span>BRASS</span></h1><div class="kick">FUNK · BALKAN · SWING · CUMBIA</div></div>
    <div class="ct2">{contact}</div>
  </div>
</section>
<section class="pg back">
  <div class="txt">
    <div class="head"><h1>VENDAVAL <span>BRASS</span></h1></div>
    <div class="body">{body}</div>
    <div class="genres">FUNK · BALKAN · SWING · CUMBIA</div>
    <div class="figs">{figs}</div>
    <ul>{lines}</ul>
    <div class="cr">{credits}</div>
    <div class="foot">
      <div class="ct"><div class="lab">{tri("Amb el suport de", "Con el apoyo de", "Supported by", sep=" · ")}</div><div class="bsup">{logos}</div></div>
    </div>
  </div>
  <div class="pics">{games}<div class="qr"><span>VÍDEO ·<br>DOSSIER ›</span>{qr_svg(QR_URL)}</div></div>
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
    import sys
    build()
