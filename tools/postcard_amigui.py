"""Amigui Imaginari / Imaginary Friend postcard for programmers and distributors: ONE trilingual card (CA · ES · EN).
Same VENDAVAL design as the Brass postcard (tools/postcard.py), on a yellow background, PORTRAIT.
A6 portrait (105 x 148 mm), 2 pages, 3 mm bleed (PDF page = 111 x 154 mm).
Usage: python3 tools/postcard_amigui.py  ->  postcard/VENDAVAL_Amigui-Imaginari_CA-ES-EN_postal_<yyyy-mm>.pdf
       plus a flattened 300 dpi print PDF (…_print-300dpi.pdf) for the print shop.
Languages: CA bold · ES plain · EN italic; ES left out where it equals CA.
Photos whole, never cropped: front zancos_peluche_7 (the creature, white wall), back _MG_7306 (acrobat on top of the creature).
Credits: Tropidelia belongs on Amigui material (costume label EN "Costume", not "Clothing"). Supporters: Tub d'assaig, APCC.
No prices or private data: this is public promoter material."""
import datetime, subprocess, tempfile, pathlib
from playwright.sync_api import sync_playwright
from postcard import tri, FONTCSS, qr_svg, LOGO, LOGOS, SRC, OUT, e

FRONT = 'zancos_peluche_7.jpg'        # the creature whole, against a white wall
BACK = '_MG_7306.jpg'                 # Format 1: the acrobat on top of the creature
QR_URL = 'https://vendaval.cat/es/imaginary-friend/'   # Amigui show page (video, photos, dossier, rider, language switcher)
SUPPORT = ['tub-dassaig.png', 'apcc.svg']
BG, TITLE, ACC, TXT, MUT = '#FFD23F', '#0F2C40', '#B5401C', '#14303F', '#4A4A3A'
W, H = 111, 154                       # page in mm, bleed included

def wave(color):
    return ('<svg class="wave" viewBox="0 0 600 20" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">'
            '<path d="M0 10 Q 25 0 50 10 T 100 10 T 150 10 T 200 10 T 250 10 T 300 10 T 350 10 T 400 10 T 450 10 T 500 10 T 550 10 T 600 10" '
            f'fill="none" stroke="{color}" stroke-width="2.2"/></svg>')

KICK = ('Peluix amb xanques', 'Peluche en zancos', 'Stuffed toy on stilts')
BODY = ("Un peluix gegant ens ve a visitar: me'l vaig imaginar i, de sobte, va sortir de sota el llit. Passeja amb xanques "
        "entre el públic buscant amics per jugar. Si tu també el veus, juguem plegats!",
        "Un peluche gigante viene de visita: me lo imaginé y, de repente, salió de debajo de la cama. Pasea en zancos entre "
        "el público buscando amigos con quien jugar. Si tú también lo ves, ¡ven a jugar!",
        "A giant stuffed animal has come to visit: I dreamed it up, and suddenly it crawled out from under the bed. It wanders "
        "through the crowd on stilts, looking for friends to play with. If you can see it too, let's play together!")
BAND = 'ITINERANT · PASACALLES · WALKABOUT'
FIGS = [('1–2', ('artistes', 'artistas', 'artists')), ('30′', ('minuts', 'minutos', 'minutes')),
        ('0', ('tècnics', 'técnicos', 'technicians')), ('3', ('formats', 'formatos', 'formats'))]
FORMATS_TITLE = ('Formats', 'Formatos', 'Formats')
FORMATS = [(("Hora d'anar a dormir", 'Hora de dormir', 'Bedtime'), ('amb acròbata', 'con acróbata', 'with an acrobat')),
           (('Amb música en viu', 'Con música en vivo', 'With live music'), ('saxo, trompeta o bombardí', 'saxo, trompeta o bombardino', 'sax, trumpet or euphonium')),
           (('Sol', 'Solo', 'Solo'), ('el peluix i jocs amb el públic', 'el peluche y juegos con el público', 'the creature and games with the audience'))]
ALL = ('Tots els públics, de dia o de nit · carrer o interior', 'Todos los públicos, de día o de noche · calle o interior', 'All ages, day or night · street or indoors')
CREDITS = [(('Xanques', 'Zancos', 'Stilts'), 'tyle fernández'),
           (('Producció', 'Producción', 'Production'), 'cia. VENDAVAL'),
           (('Vestuari', 'Vestuario', 'Costume'), 'Tropidelia · cia. Victoria Sickness'),
           (('Fotografia', 'Fotografía', 'Photography'), 'Albert Garcia')]
SUP_LAB = ('Amb el suport de', 'Con el apoyo de', 'Supported by')

def page():
    img = lambda f: (SRC/f).as_uri()
    figs = ''.join(f'<div class="fig"><div class="n">{e(n)}</div><div class="l">{tri(*l)}</div></div>' for n, l in FIGS)
    fmts = ''.join(f'<li><span class="nr">{i}</span><div>{tri(*name, sep=" · ")}<div class="d">{tri(*desc, sep=" · ")}</div></div></li>'
                   for i, (name, desc) in enumerate(FORMATS, 1))
    credits = ''.join(f'<div>{tri(*r, sep=" · ")}: <span class="nm">{e(n)}</span></div>' for r, n in CREDITS)
    body = f'<p><b>{e(BODY[0])}</b></p><p>{e(BODY[1])}</p><p><i>{e(BODY[2])}</i></p>'
    logos = ''.join(f'<img src="{(LOGOS/f).as_uri()}" alt="">' for f in SUPPORT)
    return f'''<!doctype html><html lang="ca"><meta charset="utf-8"><title>Amigui Imaginari · postal</title>
<style>{FONTCSS}
@page{{size:{W}mm {H}mm;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{-webkit-print-color-adjust:exact;print-color-adjust:exact;color:{TXT};font-family:Atk,sans-serif}}
b{{font-weight:700;font-style:normal}} i{{font-style:italic;font-weight:400}} span[lang]{{font-weight:400}}
p,li,div{{text-wrap:pretty}}
.pg{{width:{W}mm;height:{H}mm;position:relative;overflow:hidden;page-break-after:always;background:{BG}}}
.wave{{position:absolute;left:0;width:100%;height:3.2mm}}
/* FRONT: the creature photo whole across the full width; logo top right on the white wall; yellow bar with title + contact */
.front .photo{{position:absolute;left:0;top:0;width:{W}mm;display:block}}
.front .logo{{position:absolute;right:6.5mm;top:7mm;width:24mm;transform:rotate(-10deg);transform-origin:center}}
.strip{{position:absolute;left:0;bottom:0;width:{W}mm;height:24mm;background:{BG};padding:2.6mm 7mm 4.6mm;color:{TITLE};
  display:flex;flex-direction:column;justify-content:center}}
.strip .wave{{top:-1.6mm}}
.strip h1{{font:400 23pt/.95 Anton,sans-serif;letter-spacing:.3mm;color:{TITLE};white-space:nowrap}}
.strip h1 span{{color:{ACC}}}
.strip .kick{{font-size:6.2pt;color:{ACC};margin-top:1mm;white-space:nowrap}}
.strip .ct2{{display:flex;justify-content:space-between;font-size:6.4pt;font-weight:700;margin-top:1.6mm;white-space:nowrap}}
.strip .co{{font:600 6.8pt Oswald,sans-serif;letter-spacing:.3mm;color:{ACC}}}
/* BACK: text on top, formats as a numbered section, then credits + supporters + QR beside the photo */
.back .in{{position:absolute;left:7.5mm;top:7.5mm;right:7.5mm;bottom:7.5mm;display:flex;flex-direction:column}}
.head{{display:flex;align-items:baseline;gap:2.4mm}}
.head h1{{font:400 17pt/1 Anton,sans-serif;color:{TITLE};letter-spacing:.15mm}}
.head h1 span{{color:{ACC}}}
.head .en{{font-style:italic;font-size:6.6pt;color:{MUT}}}
.body{{margin-top:1.4mm}}
.body p{{font-size:6pt;line-height:1.27;margin-bottom:.6mm}}
.band{{font:600 5.6pt Oswald,sans-serif;letter-spacing:.35mm;color:{TITLE};border-top:.3mm solid {TITLE};border-bottom:.3mm solid {TITLE};padding:.5mm 0;text-align:center;margin:.6mm 0 1.2mm}}
.figs{{display:grid;grid-template-columns:repeat(4,1fr);gap:1.2mm;justify-items:center;text-align:center}}
.fig .n{{font:400 12pt/1 Anton,sans-serif;color:{ACC}}}
.fig .l{{font-size:5.2pt;line-height:1.2;margin-top:.4mm}}
h2{{font:600 6.6pt Oswald,sans-serif;letter-spacing:.35mm;text-transform:uppercase;color:{TITLE};margin:2.6mm 0 1.2mm}}
h2 b,h2 i,h2 span{{font:inherit}} h2 i{{font-style:italic}}
ol{{list-style:none;font-size:5.9pt;line-height:1.3}}
ol li{{display:flex;gap:1.6mm;margin-bottom:.8mm}}
.nr{{flex:0 0 3.6mm;height:3.6mm;border-radius:50%;background:{TITLE};color:{BG};font:600 5.4pt/3.6mm Oswald,sans-serif;text-align:center}}
ol .d{{font-size:5.2pt;color:{MUT}}}
.all{{font-size:5.4pt;margin-top:.4mm}}
.lower{{margin-top:auto;display:flex;gap:4mm;align-items:flex-end}}
.lower .left{{flex:1;min-width:0;display:flex;flex-direction:column;gap:2mm}}
.cr{{font-size:5.4pt;line-height:1.45;color:{MUT}}}
.cr .nm{{font-weight:700;color:{TXT};white-space:nowrap}}
.cr [lang]{{white-space:nowrap}}
.sup .lab{{font-size:5pt;color:{MUT};margin-bottom:1mm}}
.sup .row{{display:flex;gap:4mm;align-items:center}}
.sup img{{height:6mm;max-width:20mm;object-fit:contain}}
.qr{{display:flex;align-items:center;gap:2mm;font:600 5pt/1.3 Oswald,sans-serif;letter-spacing:.25mm;color:{TITLE}}}
.qr svg{{width:12mm;height:12mm;display:block}}
.lower .ph{{width:44mm;display:block;border-radius:1.2mm}}
</style>
<section class="pg front">
  <img class="photo" src="{img(FRONT)}" alt="">
  <img class="logo" src="{LOGO}" alt="VENDAVAL">
  <div class="strip">{wave(TITLE)}
    <h1>AMIGUI <span>IMAGINARI</span></h1>
    <div class="kick">{tri(*KICK, sep=" · ")}</div>
    <div class="ct2"><span class="co">Cia. VENDAVAL</span><span>+34 644 389 757</span><span>VENDAVAL@anartist.org</span></div>
  </div>
</section>
<section class="pg back"><div class="in">
  <div class="head"><h1>AMIGUI <span>IMAGINARI</span></h1><div class="en">Imaginary Friend</div></div>
  <div class="body">{body}</div>
  <div class="band">{BAND}</div>
  <div class="figs">{figs}</div>
  <h2>{tri(*FORMATS_TITLE, sep=" · ")}</h2>
  <ol>{fmts}</ol>
  <div class="all">{tri(*ALL, sep=" · ")}</div>
  <div class="lower">
    <div class="left">
      <div class="cr">{credits}</div>
      <div class="sup"><div class="lab">{tri(*SUP_LAB, sep=" · ")}</div><div class="row">{logos}</div></div>
      <div class="qr">{qr_svg(QR_URL)}<span>VÍDEO · DOSSIER ›<br>www.VENDAVAL.cat</span></div>
    </div>
    <img class="ph" src="{img(BACK)}" alt="">
  </div>
</div></section></html>'''

def build():
    OUT.mkdir(exist_ok=True); stamp = datetime.date.today().strftime('%Y-%m')
    out = OUT/f'VENDAVAL_Amigui-Imaginari_CA-ES-EN_postal_{stamp}.pdf'
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        f = OUT/'_postcard_amigui.html'; f.write_text(page())
        pg.goto(f.as_uri()); pg.wait_for_load_state('networkidle')
        pg.pdf(path=str(out), width=f'{W}mm', height=f'{H}mm', print_background=True, prefer_css_page_size=True)
        f.unlink(); b.close()
    from PIL import Image   # flattened 300 dpi copy for the print shop
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['pdftoppm', '-r', '300', '-png', str(out), f'{d}/p'], check=True, stderr=subprocess.DEVNULL)
        ims = [Image.open(x).convert('RGB') for x in sorted(pathlib.Path(d).glob('p-*.png'))]
        ims[0].save(out.with_name(out.stem + '_print-300dpi.pdf'), save_all=True, append_images=ims[1:], resolution=300, quality=95)
    print('built', out.relative_to(OUT.parent))

if __name__ == '__main__':
    build()
