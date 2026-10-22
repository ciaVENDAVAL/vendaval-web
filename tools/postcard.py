"""VENDAVAL Brass postcard for programmers and distributors: A6 landscape (148 x 105 mm), 2 pages (front, back),
with 3 mm bleed on every side for professional printing (PDF page = 154 x 111 mm).
Usage: python3 tools/postcard.py ca es en  ->  postcard/VENDAVAL-Brass_<LANG>_postal_<yyyy-mm>.pdf
Texts: short versions of dossiers/brass/<lang>.json, kept in T below. Add a language here before building it.
Text levels are told apart by size and weight/style (bold, plain, italic), not by colour alone.
No prices or private data: this is public promoter material."""
import sys, html, pathlib, datetime
import qrcode
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT/'source-images', ROOT/'postcard'
DFONTS, SFONTS, LOGOS = ROOT/'dossiers/assets/fonts', ROOT/'static/fonts', ROOT/'dossiers/assets/logos'
FRONT, BACK = 'VENDAVAL_003.jpg', 'VENDAVAL_passecalles_000.jpg'   # back photo is mirrored so the band faces left (into the card)
QR_LANG = {'ca': 'es', 'es': 'es', 'en': 'en'}                     # dossier language each card's QR opens
e = html.escape
LOGO = (LOGOS/'vendaval.png').as_uri()

T = {
 'ca': {
  'tag': 'JOCS & MÚSICA EN VIU · CIRC DE CARRER', 'sub': 'La festa que obre camí',
  'text': "Una cúmbia esclata al carrer i la tripulació es posa a caminar. Dues criatures del mar, una dalt de les xanques i "
          "l'altra sobre el monocicle, fan volar les maces mentre sis músics converteixen la plaça en una pista de ball. "
          "La banda es dirigeix amb senyals de mà, i el públic acaba dirigint-la.",
  'line': 'Funk, balcànic, swing i cúmbia, amb xanques i jocs per a totes les persones.',
  'credits_lab': 'Fitxa artística',
  'credits': [('Direcció artística', 'tyle fernández'), ('Música', 'Cia. VENDAVAL'),
              ('Vestuari', 'Imaginario de Mónica · Tropidelia'), ('Coproducció', 'Cia. Filigranes'),
              ('Fotografia', 'ROAR · Albert Garcia')],
  'spec_lab': 'Especificacions',
  'spec': [('Passis de 30′', ', diversos al dia'), ('Tots els públics', ', de dia o de nit'),
           ('Itinerant i acústic', ' · cap tècnic necessari'),
           ('6 músics i 2 artistes de circ', ' · format reduït des de 4 músics'),
           ('També amplificat a la plaça:', ' Concert enmig del públic')],
  'qr': 'Dossier i fitxa tècnica',
 },
 'es': {
  'tag': 'JUEGOS & MÚSICA EN VIVO · CIRCO DE CALLE', 'sub': 'La fiesta que abre camino',
  'text': "Una cumbia estalla en la calle y la tripulación se pone en marcha. Dos criaturas del mar, una sobre zancos y "
          "otra en monociclo, hacen volar las mazas mientras seis músicos convierten la plaza en una pista de baile. "
          "La banda se dirige con señas de mano, y el público acaba dirigiéndola.",
  'line': 'Funk, balcánico, swing y cumbia, con zancos y juegos para todas las personas.',
  'credits_lab': 'Ficha artística',
  'credits': [('Dirección artística', 'tyle fernández'), ('Música', 'Cia. VENDAVAL'),
              ('Vestuario', 'Imaginario de Mónica · Tropidelia'), ('Coproducción', 'Cia. Filigranes'),
              ('Fotografía', 'ROAR · Albert Garcia')],
  'spec_lab': 'Especificaciones',
  'spec': [('Pases de 30′', ', varios al día'), ('Todos los públicos', ', de día o de noche'),
           ('Pasacalles acústico', ' · sin necesidad de técnicos'),
           ('6 músicos y 2 artistas de circo', ' · formato reducido desde 4 músicos'),
           ('También amplificado en la plaza:', ' Concierto entre el público')],
  'qr': 'Dossier y ficha técnica',
 },
 'en': {
  'tag': 'GAMES & LIVE MUSIC · STREET CIRCUS', 'sub': 'The party that leads the way',
  'text': "A cumbia bursts into the street and the crew sets off. Two sea creatures, one on stilts and one on a unicycle, "
          "send clubs flying while six musicians turn the square into a dance floor. The band is conducted with hand "
          "signals, and the audience ends up conducting it.",
  'line': 'Funk, Balkan, swing and cumbia, with stilts and games for everyone.',
  'credits_lab': 'Credits',
  'credits': [('Artistic direction', 'tyle fernández'), ('Music', 'Cia. VENDAVAL'),
              ('Costumes', 'Imaginario de Mónica · Tropidelia'), ('Co-production', 'Cia. Filigranes'),
              ('Photography', 'ROAR · Albert Garcia')],
  'spec_lab': 'Key facts',
  'spec': [('30-minute sets', ', several a day'), ('All ages', ', day or night'),
           ('Acoustic roaming show', ' · no technicians needed'),
           ('6 musicians and 2 circus artists', ' · smaller format from 4 musicians'),
           ('Also amplified on the square:', ' Concert in the audience')],
  'qr': 'Dossier and technical rider',
 },
}

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

def page(lang):
    t = T[lang]; img = lambda f: (SRC/f).as_uri()
    credits = ''.join(f'<div><i>{e(k)}</i> <b>{e(v)}</b></div>' for k, v in t['credits'])
    spec = ''.join(f'<li><b>{e(a)}</b>{e(b)}</li>' for a, b in t['spec'])
    logos = ''.join(f'<img src="{(LOGOS/f).as_uri()}" alt="">' for f in ['tub-dassaig.png', 'filigranes.svg', 'bobila.png', 'apcc.svg'])
    return f'''<!doctype html><html lang="{lang}"><meta charset="utf-8"><title>VENDAVAL Brass · postal</title>
<style>{FONTCSS}
@page{{size:154mm 111mm;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{-webkit-print-color-adjust:exact;print-color-adjust:exact;color:#1E2A33;font-family:Atk,sans-serif}}
b{{font-weight:700}} i{{font-style:italic}}
.pg{{width:154mm;height:111mm;position:relative;overflow:hidden;page-break-after:always;background:#0F2C40}}
/* FRONT: whole 16:9 photo across the full width (bleed included), title band below */
.front .photo{{position:absolute;left:0;top:0;width:154mm;height:86.6mm;display:block}}
.front .band{{position:absolute;left:0;top:86.6mm;width:154mm;height:24.4mm;background:#0F2C40;padding:2.4mm 8mm 0}}
.wave{{position:absolute;left:0;top:-1.6mm;width:154mm;height:3.2mm}}
.front .kick{{font:600 6.6pt Oswald,sans-serif;letter-spacing:.45mm;color:#9FDCEC;margin-top:.8mm}}
.front h1{{font:400 22pt/1 Anton,sans-serif;color:#F5EDDC;letter-spacing:.3mm;margin-top:.6mm}}
.front h1 span{{color:#EBA53B}}
.front .logo{{position:absolute;right:8mm;top:2.6mm;height:15.5mm;background:#F5EDDC;border-radius:2mm;padding:1.2mm 2mm}}
.front .logo img{{height:100%;display:block}}
.back .head{{display:flex;align-items:flex-start;justify-content:space-between}}
.back .head img{{height:13mm;margin-top:-2.5mm}}
.front .tag{{position:absolute;right:38mm;bottom:9.4mm;text-align:right;color:#F5EDDC}}
.front .tag .t{{font:600 6.6pt Oswald,sans-serif;letter-spacing:.35mm}}
.front .tag .s{{font:italic 400 9pt/1.3 Atk,sans-serif;color:#9FDCEC}}
/* BACK: text panel left (sand), mirrored photo + contact right (sea) */
.back .txt{{position:absolute;left:0;top:0;width:91mm;height:111mm;background:#F5EDDC;padding:7.5mm 4.5mm 0 8mm;display:flex;flex-direction:column}}
.back h1{{font:400 15.5pt/1 Anton,sans-serif;color:#0F2C40;letter-spacing:.2mm}}
.back h1 span{{color:#B5401C}}
.back .sub{{font:italic 700 8pt/1.2 Atk,sans-serif;color:#B5401C;margin:.6mm 0 1.6mm}}
.back p{{font:400 6.5pt/1.34 Atk,sans-serif}}
.back p.line{{font:700 7pt/1.3 Atk,sans-serif;color:#0F2C40;margin-top:1.1mm}}
.back h2{{font:600 6.4pt Oswald,sans-serif;letter-spacing:.4mm;color:#0F2C40;text-transform:uppercase;margin:2.2mm 0 .7mm;border-bottom:.3mm solid #EBA53B;padding-bottom:.4mm}}
.back .cr div{{font-size:5.9pt;line-height:1.38}}
.back .cr i{{font-weight:400;color:#55636D}}
.back ul{{list-style:none;font-size:5.9pt;line-height:1.38}}
.back li::before{{content:"\\2693\\FE0E";color:#B5401C;margin-right:1.2mm;font-size:5pt}}
.logos{{margin-top:auto;margin-bottom:7.5mm;display:flex;align-items:center;gap:3.6mm}}
.logos img{{height:6.4mm;max-width:17mm;object-fit:contain}}
.back .ph{{position:absolute;left:91mm;top:0;width:63mm;height:80.15mm;display:block;transform:scaleX(-1)}}
.back .ct{{position:absolute;left:91mm;top:80.15mm;width:63mm;height:30.85mm;padding:2.6mm 8mm 0 3.6mm;display:flex;gap:2.8mm;color:#F5EDDC}}
.back .ct .wave{{left:0;width:63mm}}
.ct .lines{{font:400 6.2pt/1.58 Atk,sans-serif;white-space:nowrap}}
.ct .lines .co{{font:600 6.8pt Oswald,sans-serif;letter-spacing:.3mm;color:#EBA53B}}
.ct .lines i{{color:#9FDCEC}}
.ct .qr{{flex:0 0 15mm;text-align:center;font:italic 400 4.9pt/1.2 Atk,sans-serif;color:#9FDCEC}}
.ct .qr div{{background:#F5EDDC;padding:1.2mm;border-radius:.8mm;margin-bottom:.8mm}}
.ct .qr svg{{display:block;width:100%}}
</style>
<section class="pg front">
  <img class="photo" src="{img(FRONT)}" alt="">
  <div class="band">{WAVE}
    <div class="kick">{e(t['tag'])}</div>
    <h1>VENDAVAL <span>BRASS</span></h1>
    <div class="logo"><img src="{LOGO}" alt="VENDAVAL"></div>
    <div class="tag"><div class="s">{e(t['sub'])}</div></div>
  </div>
</section>
<section class="pg back">
  <div class="txt">
    <div class="head"><div><h1>VENDAVAL <span>BRASS</span></h1>
    <div class="sub">{e(t['sub'])}</div></div><img src="{LOGO}" alt="VENDAVAL"></div>
    <p>{e(t['text'])}</p>
    <p class="line">{e(t['line'])}</p>
    <h2>{e(t['credits_lab'])}</h2><div class="cr">{credits}</div>
    <h2>{e(t['spec_lab'])}</h2><ul>{spec}</ul>
    <div class="logos">{logos}</div>
  </div>
  <img class="ph" src="{img(BACK)}" alt="">
  <div class="ct">{WAVE}
    <div class="lines"><span class="co">Cia. VENDAVAL</span><br><i>@vendaval.brass</i><br><b>+34 644 389 757</b><br>VENDAVAL@anartist.org<br>www.VENDAVAL.cat</div>
    <div class="qr"><div>{qr_svg('https://vendaval.cat/dossier/brass/' + QR_LANG[lang])}</div>{e(t['qr'])}</div>
  </div>
</section></html>'''

def build(langs):
    OUT.mkdir(exist_ok=True); stamp = datetime.date.today().strftime('%Y-%m')
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        for lang in langs:
            f = OUT/f'_postcard_{lang}.html'; f.write_text(page(lang))
            pg.goto(f.as_uri()); pg.wait_for_load_state('networkidle')
            out = OUT/f'VENDAVAL-Brass_{lang.upper()}_postal_{stamp}.pdf'
            pg.pdf(path=str(out), width='154mm', height='111mm', print_background=True, prefer_css_page_size=True)
            f.unlink(); print('built', out.relative_to(ROOT))
        b.close()

if __name__ == '__main__':
    build(sys.argv[1:] or ['ca', 'es', 'en'])
