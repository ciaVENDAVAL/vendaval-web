"""VENDAVAL Brass postcard for programmers and distributors: ONE trilingual card (CA · ES · EN).
A6 landscape (148 x 105 mm), 2 pages (front, back), 3 mm bleed on every side for the print shop (PDF page = 154 x 111 mm).
Usage: python3 tools/postcard.py  ->  postcard/VENDAVAL-Brass_CA-ES-EN_postal_<yyyy-mm>.pdf
Languages are told apart by style, always the same: CA bold · ES plain · EN italic. When CA and ES are identical, ES is left out.
Photos: back photos whole and sharp; front photo trimmed top/bottom (sidewalk, building; never people, tyle 22 Oct 2026), left edge fading into the navy.
Credits: VENDAVAL Brass only (Tropidelia belongs to Amigui Imaginari and the website footer, not here).
No prices or private data: this is public promoter material."""
import html, pathlib, datetime
import qrcode
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT/'source-images', ROOT/'postcard'
DFONTS, SFONTS, LOGOS = ROOT/'dossiers/assets/fonts', ROOT/'static/fonts', ROOT/'dossiers/assets/logos'
FRONT = 'VENDAVAL_FiraVapor001.jpg'                                      # whole band in front of the modernista building
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
           (('Vestuari', 'Vestuario', 'Costumes'), 'Imaginario de Mónica'),
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
/* FRONT: deep-sea navy; the portrait photo on the right, its left edge fading into the navy */
.front{{background:#0F2C40}}
/* front photo: tyle's choice (22 Oct 2026) to crop sidewalk and building, never people: full width kept, top and bottom trimmed */
.front .photo{{position:absolute;right:0;top:0;height:111mm;width:100mm;display:block;object-fit:cover;object-position:50% 60%;{FADE_LEFT}}}
.front .col{{position:absolute;left:6.5mm;top:7.5mm;width:46mm;height:95mm;display:flex;flex-direction:column}}
.front .logo{{width:42mm;filter:drop-shadow(0 0 .35mm rgba(245,237,220,.95)) drop-shadow(0 0 .2mm rgba(245,237,220,.9))}}
.front h1{{font:400 31pt/.95 Anton,sans-serif;color:#F5EDDC;letter-spacing:.3mm;margin-top:4mm}}
.front h1 span{{color:#EBA53B;display:block}}
.front .kick{{font:600 6.2pt Oswald,sans-serif;letter-spacing:.45mm;color:#9FDCEC;margin-top:2.6mm;position:relative;padding-top:2.6mm}}
.front .kick .wave{{top:-.6mm;width:40mm}}
.front .sup{{margin-top:auto;display:grid;grid-template-columns:repeat(2,auto);justify-content:start;align-items:center;gap:1.6mm 3mm;
  background:#F5EDDC;border-radius:1.6mm;padding:1.6mm 2.4mm;align-self:flex-start}}
.front .sup img{{height:5.6mm;max-width:17mm;object-fit:contain;justify-self:center}}
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
.figs{{display:grid;grid-template-columns:repeat(4,1fr);gap:1.4mm}}
.fig .n{{font:400 12pt/1 Anton,sans-serif;color:#B5401C}}
.fig .l{{font-size:5.3pt;line-height:1.2;margin-top:.4mm}}
ul{{list-style:none;font-size:5.4pt;line-height:1.3;margin-top:1mm}}
li::before{{content:"\\2693\\FE0E";color:#B5401C;margin-right:1mm;font-size:4.6pt}}
.cr{{margin-top:1mm;font-size:5.2pt;line-height:1.32;color:#55636D}}
.cr .nm{{font-weight:700;color:#1E2A33}}
.foot{{margin-top:auto;display:flex;gap:3mm;align-items:center;background:#0F2C40;color:#F5EDDC;border-radius:2mm;padding:1.6mm 2.6mm;margin-top:1.4mm}}
.clogo{{height:11mm;filter:drop-shadow(0 0 .3mm rgba(245,237,220,.95)) drop-shadow(0 0 .2mm rgba(245,237,220,.9))}}
.ct{{flex:1;font-size:6pt;line-height:1.5}}
.ct .co{{font:600 6.6pt Oswald,sans-serif;letter-spacing:.3mm;color:#EBA53B}}
.ct i{{color:#9FDCEC}}
.qr{{flex:0 0 14mm;text-align:center;font:600 4.6pt Oswald,sans-serif;letter-spacing:.2mm;color:#9FDCEC}}
.qr svg{{display:block;width:100%;margin-bottom:.5mm;background:#F5EDDC;padding:.8mm;border-radius:.6mm}}
.pics{{position:absolute;left:95mm;top:3mm;width:56mm;height:105mm;display:flex;flex-direction:column;justify-content:center;gap:1mm}}
.pics .g{{width:56mm;display:block;border-radius:1.2mm}}
</style>
<section class="pg front">
  <img class="photo" src="{img(FRONT)}" alt="">
  <div class="col">
    <img class="logo" src="{LOGO}" alt="VENDAVAL">
    <h1>VENDAVAL <span>BRASS</span></h1>
    <div class="kick">{WAVE}FUNK · BALKAN · SWING · CUMBIA</div>
    <div class="sup">{logos}</div>
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
      <img class="clogo" src="{LOGO}" alt="VENDAVAL"><div class="ct"><span class="co">Cia. VENDAVAL</span><br><b>+34 644 389 757</b> · VENDAVAL@anartist.org<br>www.VENDAVAL.cat · <i>@vendaval.brass</i></div>
      <div class="qr">{qr_svg(QR_URL)}VÍDEO · DOSSIER</div>
    </div>
  </div>
  <div class="pics">{games}</div>
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
