"""Amigui Imaginari / Imaginary Friend postcard for programmers and distributors: ONE trilingual card (CA · ES · EN).
Same VENDAVAL design as the Brass postcard (tools/postcard.py), on a yellow background.
A6 landscape (148 x 105 mm), 2 pages, 3 mm bleed (PDF page = 154 x 111 mm).
Usage: python3 tools/postcard_amigui.py  ->  postcard/VENDAVAL_Amigui-Imaginari_CA-ES-EN_postal_<yyyy-mm>.pdf
       plus a flattened 300 dpi print PDF (…_print-300dpi.pdf) for the print shop.
Languages: CA bold · ES plain · EN italic; ES left out where it equals CA.
Photos: front zancos_peluche_5 (4:3) trimmed top/bottom (stage ceiling and floor only; heads clear of the 3 mm bleed, feet and stilt tips whole);
back photos whole. Credits: Tropidelia belongs on Amigui material (costume label EN "Costume", not "Clothing").
No prices or private data: this is public promoter material."""
import datetime, subprocess, tempfile, pathlib
from playwright.sync_api import sync_playwright
from postcard import tri, FONTCSS, qr_svg, LOGO, SRC, OUT, e

FRONT = 'zancos_peluche_5.jpg'                          # acrobat + plush creature on stilts (format 1, "Bedtime")
PICS = ['zancos_peluche_7.jpg', 'footer_images_12.jpg']  # creature whole, in daylight · with a live performer
QR_URL = 'https://vendaval.cat/'                         # home page (opens in the reader's language)
BG, TITLE, ACC, TXT, MUT = '#FFD23F', '#0F2C40', '#B5401C', '#14303F', '#4A4A3A'

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
LINES = [("Hora d'anar a dormir: amb acròbata", 'Hora de dormir: con acróbata', 'Bedtime: with an acrobat'),
         ('Amb música en viu', 'Con música en vivo', 'With live music'),
         ('Sol: el peluix i jocs amb el públic', 'Solo: el peluche y juegos con el público', 'Solo: the creature and games with the audience'),
         ('Tots els públics, de dia o de nit · carrer o interior', 'Todos los públicos, de día o de noche · calle o interior', 'All ages, day or night · street or indoors')]
CREDITS = [(('Xanques', 'Zancos', 'Stilts'), 'tyle fernández'),
           (('Producció', 'Producción', 'Production'), 'cia. VENDAVAL'),
           (('Vestuari', 'Vestuario', 'Costume'), 'Tropidelia · cia. Victoria Sickness'),
           (('Fotografia', 'Fotografía', 'Photography'), 'Albert Garcia')]

def page():
    img = lambda f: (SRC/f).as_uri()
    figs = ''.join(f'<div class="fig"><div class="n">{e(n)}</div><div class="l">{tri(*l)}</div></div>' for n, l in FIGS)
    lines = ''.join(f'<li>{tri(*l, sep=" · ")}</li>' for l in LINES)
    credits = ''.join(f'<div>{tri(*r, sep=" · ")}: <span class="nm">{e(n)}</span></div>' for r, n in CREDITS)
    body = f'<p><b>{e(BODY[0])}</b></p><p>{e(BODY[1])}</p><p><i>{e(BODY[2])}</i></p>'
    contact = ('<span class="co">Cia. VENDAVAL</span><span>+34 644 389 757</span>'
               '<span>VENDAVAL@anartist.org</span><span>www.VENDAVAL.cat</span>')
    pics = ''.join(f'<img class="g" src="{img(f)}" alt="">' for f in PICS)
    return f'''<!doctype html><html lang="ca"><meta charset="utf-8"><title>Amigui Imaginari · postal</title>
<style>{FONTCSS}
@page{{size:154mm 111mm;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{-webkit-print-color-adjust:exact;print-color-adjust:exact;color:{TXT};font-family:Atk,sans-serif}}
b{{font-weight:700;font-style:normal}} i{{font-style:italic;font-weight:400}} span[lang]{{font-weight:400}}
p,li,div{{text-wrap:pretty}}
.pg{{width:154mm;height:111mm;position:relative;overflow:hidden;page-break-after:always;background:{BG}}}
.wave{{position:absolute;left:0;width:100%;height:3.2mm}}
/* FRONT: 4:3 photo trimmed top/bottom (stage ceiling and floor only: heads clear of the bleed, feet and stilt tips whole) */
.front .photo{{position:absolute;left:0;top:0;width:154mm;height:92mm;display:block;object-fit:cover;object-position:50% 55%}}
.front .logo{{position:absolute;right:6mm;top:5.5mm;width:22mm;transform:rotate(-10deg);transform-origin:center}}
.strip{{position:absolute;left:0;top:92mm;width:154mm;height:19mm;background:{BG};padding:1.6mm 9mm 3mm 6.5mm;
  display:flex;align-items:center;justify-content:space-between;gap:5mm;color:{TITLE}}}
.strip .wave{{top:-1.6mm}}
.strip h1{{font:400 22pt/.95 Anton,sans-serif;letter-spacing:.3mm;color:{TITLE};white-space:nowrap}}
.strip h1 span{{color:{ACC}}}
.strip .kick{{font-size:6.2pt;color:{ACC};margin-top:1.2mm;white-space:nowrap}}
.strip .ct2{{display:grid;grid-template-columns:auto auto;gap:1mm 6mm;font-size:7.4pt;font-weight:700;white-space:nowrap}}
.strip .co{{font:600 8pt Oswald,sans-serif;letter-spacing:.35mm;color:{ACC}}}
/* BACK: text left, two photos right (whole), QR at the bottom left */
.back .txt{{position:absolute;left:8mm;top:7mm;width:84mm;height:97mm;display:flex;flex-direction:column}}
.head h1{{font:400 18pt/1 Anton,sans-serif;color:{TITLE};letter-spacing:.15mm}}
.head h1 span{{color:{ACC}}}
.head .en{{font-style:italic;font-size:6.6pt;color:{MUT};margin-top:.6mm}}
.body{{margin-top:1.6mm}}
.body p{{font-size:5.9pt;line-height:1.25;margin-bottom:.6mm}}
.band{{font:600 5.8pt Oswald,sans-serif;letter-spacing:.35mm;color:{TITLE};border-top:.3mm solid {TITLE};border-bottom:.3mm solid {TITLE};padding:.5mm 0;text-align:center;margin:.8mm 0 1.2mm}}
.figs{{display:grid;grid-template-columns:repeat(4,1fr);gap:1.4mm;justify-items:center;text-align:center}}
.fig .n{{font:400 12pt/1 Anton,sans-serif;color:{ACC}}}
.fig .l{{font-size:5.3pt;line-height:1.2;margin-top:.4mm}}
ul{{list-style:none;font-size:5.4pt;line-height:1.3;margin-top:1.2mm}}
li{{padding-left:2.6mm;text-indent:-2.6mm}}
li [lang],.cr [lang]{{white-space:nowrap}}
li::before{{content:"\\2605\\FE0E";color:{ACC};display:inline-block;width:2.6mm;text-indent:0;font-size:4.6pt}}
.cr{{margin-top:1.6mm;font-size:5.6pt;line-height:1.42;color:{MUT}}}
.cr .nm{{font-weight:700;color:{TXT}}}
.foot{{margin-top:auto;display:flex;align-items:center;gap:2.4mm;border-top:.3mm solid {TITLE};padding-top:2mm;
  font:600 5pt/1.3 Oswald,sans-serif;letter-spacing:.25mm;color:{TITLE}}}
.foot svg{{width:12mm;height:12mm;display:block}}
.pics{{position:absolute;left:97mm;top:7mm;width:50mm;display:flex;flex-direction:column;gap:1.2mm}}
.pics .g{{width:50mm;display:block;border-radius:1.2mm}}
</style>
<section class="pg front">
  <img class="photo" src="{img(FRONT)}" alt="">
  <img class="logo" src="{LOGO}" alt="VENDAVAL">
  <div class="strip">{wave(TITLE)}
    <div><h1>AMIGUI <span>IMAGINARI</span></h1><div class="kick">{tri(*KICK, sep=" · ")}</div></div>
    <div class="ct2">{contact}</div>
  </div>
</section>
<section class="pg back">
  <div class="txt">
    <div class="head"><h1>AMIGUI <span>IMAGINARI</span></h1><div class="en">Imaginary Friend</div></div>
    <div class="body">{body}</div>
    <div class="band">{BAND}</div>
    <div class="figs">{figs}</div>
    <ul>{lines}</ul>
    <div class="cr">{credits}</div>
    <div class="foot">{qr_svg(QR_URL)}<span>www.VENDAVAL.cat ›</span></div>
  </div>
  <div class="pics">{pics}</div>
</section></html>'''

def build():
    OUT.mkdir(exist_ok=True); stamp = datetime.date.today().strftime('%Y-%m')
    out = OUT/f'VENDAVAL_Amigui-Imaginari_CA-ES-EN_postal_{stamp}.pdf'
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        f = OUT/'_postcard_amigui.html'; f.write_text(page())
        pg.goto(f.as_uri()); pg.wait_for_load_state('networkidle')
        pg.pdf(path=str(out), width='154mm', height='111mm', print_background=True, prefer_css_page_size=True)
        f.unlink(); b.close()
    # flattened 300 dpi copy for the print shop
    from PIL import Image
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['pdftoppm', '-r', '300', '-png', str(out), f'{d}/p'], check=True)
        ims = [Image.open(x).convert('RGB') for x in sorted(pathlib.Path(d).glob('p-*.png'))]
        ims[0].save(out.with_name(out.stem + '_print-300dpi.pdf'), save_all=True, append_images=ims[1:], resolution=300, quality=95)
    print('built', out.relative_to(OUT.parent))

if __name__ == '__main__':
    build()
