"""VENDAVAL Brass postcard for programmers and distributors: A6 landscape (148 x 105 mm), 2 pages (front, back),
with 3 mm bleed on every side for professional printing (PDF page = 154 x 111 mm).
Usage: python3 tools/postcard.py ca [es en ...]  ->  postcard/VENDAVAL-Brass_<LANG>_postal_<yyyy-mm>.pdf
Texts: short versions of dossiers/brass/<lang>.json, kept in T below. Add a language here before building it.
No prices or private data: this is public promoter material."""
import sys, json, html, io, base64, pathlib, datetime
import qrcode
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT/'source-images', ROOT/'postcard'
FONTS, LOGOS = ROOT/'dossiers/assets/fonts', ROOT/'dossiers/assets/logos'
QR_URL = 'https://vendaval.cat/dossier/brass'      # opens the dossier in the reader's language
FRONT, BACK = 'VENDAVAL_003.jpg', 'VENDAVAL_passecalles_000.jpg'
e = html.escape

T = {
 'ca': {
  'kicker': 'CIA. VENDAVAL',
  'tag': 'JOCS & MÚSICA EN VIU · CIRC DE CARRER',
  'sub': 'La festa que obre camí',
  'text': "Una cúmbia esclata al carrer i la tripulació es posa a caminar. Dues criatures del mar, una dalt de les xanques i "
          "l'altra sobre el monocicle, fan volar les maces mentre sis músics converteixen la plaça en una pista de ball. "
          "La banda es dirigeix amb senyals de mà, i el públic acaba dirigint-la.",
  'line': 'Funk, balcànic, swing i cúmbia, amb xarxes, salvavides i jocs per a totes les persones.',
  'credits_lab': 'Fitxa artística',
  'credits': [('Direcció artística', 'tyle fernández'), ('Música', 'Cia. VENDAVAL'),
              ('Vestuari', 'Imaginario de Mónica · Tropidelia'), ('Coproducció', 'Cia. Filigranes'),
              ('Fotografia', 'ROAR · Barbara Walzer · Jordi Largo · Albert Garcia')],
  'spec_lab': 'Especificacions',
  'spec': ["Passis de 30′, diversos al dia · Tots els públics, de dia o de nit",
           "Itinerant i acústic · Cap tècnic necessari",
           "6 músics i 2 artistes de circ (format reduït des de 4 músics)",
           "També amplificat a la plaça: Concert enmig del públic"],
  'qr': 'Dossier i fitxa tècnica',
 },
}

def font(name): return (FONTS/f'{name}.woff2').as_uri()

def qr_svg():
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M); q.add_data(QR_URL); q.make()
    m = q.get_matrix(); n = len(m)
    rects = ''.join(f'<rect x="{x}" y="{y}" width="1.02" height="1.02"/>' for y, r in enumerate(m) for x, v in enumerate(r) if v)
    return f'<svg viewBox="0 0 {n} {n}" xmlns="http://www.w3.org/2000/svg" fill="#0F2C40">{rects}</svg>'

WAVE = ('<svg class="wave" viewBox="0 0 600 20" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M0 10 Q 25 0 50 10 T 100 10 T 150 10 T 200 10 T 250 10 T 300 10 T 350 10 T 400 10 T 450 10 T 500 10 T 550 10 T 600 10" '
        'fill="none" stroke="#EBA53B" stroke-width="2.2"/></svg>')

def page(lang):
    t = T[lang]; img = lambda f: (SRC/f).as_uri()
    credits = ''.join(f'<div><b>{e(k)}:</b> {e(v)}</div>' for k, v in t['credits'])
    spec = ''.join(f'<li>{e(s)}</li>' for s in t['spec'])
    logos = ''.join(f'<img src="{(LOGOS/f).as_uri()}" alt="">' for f in ['tub-dassaig.png', 'filigranes.svg', 'bobila.png', 'apcc.svg'])
    return f'''<!doctype html><html lang="{lang}"><meta charset="utf-8"><title>VENDAVAL Brass · postal</title>
<style>
@font-face{{font-family:Anton;src:url({font('anton-latin-400-normal')})}}
@font-face{{font-family:Anton;src:url({font('anton-latin-ext-400-normal')});unicode-range:U+0100-024F,U+1E00-1EFF}}
@font-face{{font-family:Oswald;font-weight:500;src:url({font('oswald-latin-500-normal')})}}
@font-face{{font-family:Oswald;font-weight:600;src:url({font('oswald-latin-600-normal')})}}
@font-face{{font-family:Oswald;font-weight:600;src:url({font('oswald-latin-ext-600-normal')});unicode-range:U+0100-024F,U+1E00-1EFF}}
@font-face{{font-family:Atk;font-weight:400;src:url({(ROOT/'static/fonts/atkinson-hyperlegible-latin-400-normal.woff2').as_uri()})}}
@font-face{{font-family:Atk;font-weight:700;src:url({(ROOT/'static/fonts/atkinson-hyperlegible-latin-700-normal.woff2').as_uri()})}}
@page{{size:154mm 111mm;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{-webkit-print-color-adjust:exact;print-color-adjust:exact;color:#1E2A33}}
.pg{{width:154mm;height:111mm;position:relative;overflow:hidden;page-break-after:always;background:#0F2C40}}
/* FRONT: whole 16:9 photo across the full width (bleed included), title band below */
.front .photo{{position:absolute;left:0;top:0;width:154mm;height:86.6mm;display:block}}
.front .band{{position:absolute;left:0;top:86.6mm;width:154mm;height:24.4mm;background:#0F2C40;padding:2.4mm 8mm 0}}
.wave{{position:absolute;left:0;top:-1.6mm;width:154mm;height:3.2mm}}
.front .kick{{font:600 6.4pt Oswald,sans-serif;letter-spacing:.5mm;color:#9FDCEC}}
.front h1{{font:400 25pt/1 Anton,sans-serif;color:#F5EDDC;letter-spacing:.3mm;margin-top:.6mm}}
.front h1 span{{color:#EBA53B}}
.front .tag{{position:absolute;right:8mm;bottom:8.6mm;text-align:right;font:600 6.6pt/1.5 Oswald,sans-serif;letter-spacing:.35mm;color:#F5EDDC}}
.front .tag i{{font-style:normal;color:#9FDCEC}}
/* BACK: text panel left (sand), photo + contact right (sea) */
.back .txt{{position:absolute;left:0;top:0;width:91mm;height:111mm;background:#F5EDDC;padding:7.5mm 4.5mm 0 8mm;display:flex;flex-direction:column}}
.back h1{{font:400 15.5pt/1 Anton,sans-serif;color:#0F2C40;letter-spacing:.2mm}}
.back h1 span{{color:#B5401C}}
.back .sub{{font:600 6.4pt Oswald,sans-serif;letter-spacing:.35mm;color:#B5401C;text-transform:uppercase;margin:.8mm 0 1.6mm}}
.back p{{font:400 6.5pt/1.32 Atk,sans-serif}}
.back p.line{{font-weight:700;color:#0F2C40;margin-top:1mm}}
.back h2{{font:600 6.6pt Oswald,sans-serif;letter-spacing:.35mm;color:#0F2C40;text-transform:uppercase;margin:2.2mm 0 .7mm;border-bottom:.3mm solid #EBA53B;padding-bottom:.4mm}}
.back .cr div{{font:400 5.9pt/1.36 Atk,sans-serif}}
.back ul{{list-style:none;font:400 5.9pt/1.36 Atk,sans-serif}}
.back li::before{{content:"\\2693\\FE0E";color:#B5401C;margin-right:1.2mm;font-size:5pt}}
.logos{{margin-top:auto;margin-bottom:7.5mm;display:flex;align-items:center;gap:3.6mm}}
.logos img{{height:6.4mm;max-width:17mm;object-fit:contain}}
.back .ph{{position:absolute;left:91mm;top:0;width:63mm;height:80.15mm;display:block}}
.back .ct{{position:absolute;left:91mm;top:80.15mm;width:63mm;height:30.85mm;padding:2.6mm 8mm 0 3.6mm;display:flex;gap:2.8mm;color:#F5EDDC}}
.back .ct .wave{{left:0;width:63mm}}
.ct .lines{{font:400 6.2pt/1.6 Atk,sans-serif;white-space:nowrap}}
.ct .lines b{{font:600 6.6pt Oswald,sans-serif;letter-spacing:.3mm;color:#EBA53B}}
.ct .qr{{flex:0 0 15mm;text-align:center;font:500 4.6pt/1.2 Oswald,sans-serif;letter-spacing:.15mm;color:#9FDCEC}}
.ct .qr div{{background:#F5EDDC;padding:1.2mm;border-radius:.8mm;margin-bottom:.8mm}}
.ct .qr svg{{display:block;width:100%}}
</style>
<section class="pg front">
  <img class="photo" src="{img(FRONT)}" alt="">
  <div class="band">{WAVE}
    <div class="kick">{e(t['kicker'])}</div>
    <h1>VENDAVAL <span>BRASS</span></h1>
    <div class="tag">{e(t['tag'])}<br><i>{e(t['sub'])}</i></div>
  </div>
</section>
<section class="pg back">
  <div class="txt">
    <h1>VENDAVAL <span>BRASS</span></h1>
    <div class="sub">{e(t['sub'])}</div>
    <p>{e(t['text'])}</p>
    <p class="line">{e(t['line'])}</p>
    <h2>{e(t['credits_lab'])}</h2><div class="cr">{credits}</div>
    <h2>{e(t['spec_lab'])}</h2><ul>{spec}</ul>
    <div class="logos">{logos}</div>
  </div>
  <img class="ph" src="{img(BACK)}" alt="">
  <div class="ct">{WAVE}
    <div class="lines"><b>Cia. VENDAVAL</b><br>@vendaval.brass<br>+34 644 389 757<br>VENDAVAL@anartist.org<br>www.VENDAVAL.cat</div>
    <div class="qr"><div>{qr_svg()}</div>{e(t['qr'])}</div>
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
    build(sys.argv[1:] or ['ca'])
