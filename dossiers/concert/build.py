"""VENDAVAL Brass · Concert in the audience: dossier (6 pages) and technical rider (2 pages), 8 languages -> static/pdf/
Usage (from the repo root): python3 dossiers/concert/build.py [ca es en de fr it pt ja]
Texts: dossiers/concert/<lang>.json · layout: template.html · photos: source-images/, always whole (never cropped)
Ported 29 Oct 2026 from the local build of 22 Oct 2026 (vendaval-docs legacy-build/concert-2026-10, WeasyPrint)."""
import sys, json, io, base64, pathlib, asyncio, functools
from PIL import Image, ImageOps
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
IMGSRC = ROOT/'source-images'
LOGOS = HERE.parent/'assets'/'logos'
FONTS = HERE.parent/'assets'/'fonts'
OUT = ROOT/'static'/'pdf'
DATE = '2026-10'
site = json.loads((ROOT/'content'/'data.json').read_text())['site']

PHOTOS = dict(
    cover='VENDAVAL_Unterwegs002.jpg',                      # band in the crowd
    cover_row=['VENDAVAL_passecalles_000.jpg', 'VENDAVAL_FiraVapor002.jpg', 'VENDAVAL_102.jpg'],
    show_row=['VENDAVAL_Unterwegs001.jpg', 'VENDAVAL_Unterwegs004.jpg'],
    music_row=['IMG_0780.JPG', 'VENDAVAL_Bobila001.jpg'],
    chars_row=['VENDAVAL_FiraVapor001.jpg', 'VENDAVAL_Unterwegs003.jpg'],
    access_row=['photo_2026-09-09_20-43-56.jpg', 'IMG_0677.JPG'],
    contact='VENDAVAL_FiraVapor002.jpg',                    # sea net
)
# team order as in the dossier; tyle's name (with pronoun) comes from <lang>.json
TEAM = [dict(name=n, photo=p) for n, p in [
    ('tyle fernández', 'portrait__3_tyle.jpg'), ('Juan Lichter', 'portrait__8_Juan.jpg'),
    ('Stefano Ferraro', 'portrait__2_Stefano.jpg'), ('Lucas Raiquen Pereyra', 'portrait__1_Lucas.jpg'),
    ('Alián Rodrigues', 'portrait__6_Ali_n.jpg'), ('Facundo Fernández Alberdi', 'portrait__7_Facu.jpg'),
    ('Albert Pérez', 'portrait__5_Albert.jpg'), ('Jordi Torrens', 'portrait__4_Jordi.jpg')]]
SUPPORT = [('tub-dassaig.png', 20), ('bobila.png', 13), ('apcc.svg', 12), ('filigranes.svg', 11)]  # logo, height in mm

def uri(data, mime): return f'data:{mime};base64,' + base64.b64encode(data).decode()

@functools.lru_cache(None)
def _open(name): return ImageOps.exif_transpose(Image.open(IMGSRC/name)).convert('RGB')

@functools.lru_cache(None)
def img(name, px=1600):
    im = _open(name).copy(); im.thumbnail((px, px))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=84); return uri(b.getvalue(), 'image/jpeg')

@functools.lru_cache(None)
def logo(name):
    f = LOGOS/name
    return uri(f.read_bytes(), 'image/svg+xml' if f.suffix == '.svg' else 'image/png')

@functools.lru_cache(None)
def font(stem): return uri((FONTS/f'{stem}.woff2').read_bytes(), 'font/woff2')

def row_sizes(names, width, gap):
    """photos side by side at one height, filling the width exactly (mm, never cropped)"""
    ars = [_open(n).width / _open(n).height for n in names]
    h = (width - gap * (len(names) - 1)) / sum(ars)
    return dict(h=round(h, 2), cells=[(n, round(h * a, 2)) for n, a in zip(names, ars)])

env = Environment(loader=FileSystemLoader(str(HERE)), autoescape=True)

def html(lang, kind):
    t = json.loads((HERE/f'{lang}.json').read_text(encoding='utf-8'))
    foot = t['foot_d'] if kind == 'dossier' else t['foot_r']
    return env.get_template('template.html').render(t=t, lang=lang, kind=kind, foot=foot, P=PHOTOS, team=TEAM, support=SUPPORT,
                                                    site=site, img=img, logo=logo, font=font, row_sizes=row_sizes)

async def main(langs):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        for lang in langs:
            for kind in ('dossier', 'rider'):
                await pg.set_content(html(lang, kind), wait_until='load')
                await pg.evaluate('document.fonts.ready')
                out = OUT/f'VENDAVAL-Brass-Concert-Placa_{lang.upper()}_{kind}_{DATE}.pdf'
                await pg.pdf(path=str(out), print_background=True, prefer_css_page_size=True)
                print(out.relative_to(ROOT))
        await b.close()

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1:] or ['ca', 'es', 'en', 'de', 'fr', 'it', 'pt', 'ja']))
