"""VENDAVAL Brass dossier (7 pages) and technical rider (2 pages), 8 languages -> static/pdf/
Usage (from the repo root): python3 dossiers/brass/build.py [ca es en de fr it pt ja]
Texts: dossiers/brass/<lang>.json · layout: template.html + parts.html · photos: source-images/, framed (cropped) as in the canvas, by tyle's choice for this dossier
Based on the Design canvas "VENDAVAL Brass — dossier CA v2" (Oct 2026)."""
import sys, json, io, base64, pathlib, asyncio, functools
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
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

PHOTOS = dict(cover='VENDAVAL_FiraVapor001.jpg', street='IMG_0677.JPG', net='IMG_0780.JPG',
              games1='VENDAVAL_Unterwegs001.jpg', games2='VENDAVAL_102.jpg', tech='VENDAVAL_Unterwegs002.jpg',
              contact='IMG_0622.JPG', tech_row=['VENDAVAL_Unterwegs002.jpg', 'VENDAVAL_003.jpg'])
CREW = [
    dict(id='tyle', pos='center 15%', name='tyle fernández', photo='portrait__3_tyle.jpg', **{'from': 'US / DE'}, link='https://linktr.ee/bicialta', link_label='linktr.ee/bicialta'),
    dict(id='alian', pos='center 20%', name='Alián Rodrigues', photo='portrait__6_Ali_n.jpg', **{'from': 'AR / PT'}, link='https://linktr.ee/a.alian.n', link_label='linktr.ee/a.alian.n'),
    dict(id='facu', pos='center 15%', name='Facundo Fernández Alberdi', photo='portrait__7_Facu.jpg', **{'from': 'AR / ES'}, link='https://instagram.com/ffa_musica', link_label='@ffa_musica'),
    dict(id='lucas', pos='center 15%', name='Lucas Raiquen Pereyra', photo='portrait__1_Lucas.jpg', **{'from': 'AR'}, link='https://instagram.com/lukasraiquen', link_label='@lukasraiquen'),
    dict(id='juan', pos='center 15%', name='Juan Lichter', photo='portrait__8_Juan.jpg', **{'from': 'AR'}, link='https://instagram.com/juanlichter90', link_label='@juanlichter90'),
    dict(id='stefano', pos='center 15%', name='Stefano Ferraro', photo='portrait__2_Stefano.jpg', **{'from': 'IT'}, link='https://linktr.ee/stefano.ferraro', link_label='linktr.ee/stefano.ferraro'),
    dict(id='albert', pos='center 20%', name='Albert Pérez', photo='portrait__5_Albert.jpg', **{'from': 'CAT · Cia. Filigranes'}, link='https://ciafiligranes.net', link_label='ciafiligranes.net'),
    dict(id='jordi', pos='center 10%', name='Jordi Torrens', photo='portrait__4_Jordi.jpg', **{'from': 'CAT · Cia. Filigranes'}, link='https://ciafiligranes.net', link_label='ciafiligranes.net'),
]
NAMES = {'ca': ('VENDAVAL-Brass_CA_dossier', 'VENDAVAL-Brass_CA_rider')}  # file stems: VENDAVAL-Brass_<LANG>_<kind>_<date>.pdf

def uri(data, mime): return f'data:{mime};base64,' + base64.b64encode(data).decode()

@functools.lru_cache(None)
def img(name, px=1600):
    im = ImageOps.exif_transpose(Image.open(IMGSRC/name)).convert('RGB'); im.thumbnail((px, px))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=84); return uri(b.getvalue(), 'image/jpeg')

@functools.lru_cache(None)
def blur(name):
    im = ImageOps.exif_transpose(Image.open(IMGSRC/name)).convert('RGB'); im.thumbnail((400, 400))
    im = ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(14))).enhance(.72)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=70); return uri(b.getvalue(), 'image/jpeg')

@functools.lru_cache(None)
def logo(name):
    f = LOGOS/name
    return uri(f.read_bytes(), 'image/svg+xml' if f.suffix == '.svg' else 'image/png')

@functools.lru_cache(None)
def font(stem): return uri((FONTS/f'{stem}.woff2').read_bytes(), 'font/woff2')

def row(names, width, gap):
    """photos side by side at one height, filling the width exactly (never cropped)"""
    ars = []
    for n in names:
        im = ImageOps.exif_transpose(Image.open(IMGSRC/n)); ars.append(im.width / im.height)
    h = (width - gap * (len(names) - 1)) / sum(ars)
    return dict(h=round(h, 1), cells=[(n, round(h * a, 1)) for n, a in zip(names, ars)])

env = Environment(loader=FileSystemLoader(str(HERE)), autoescape=True)
env.loader.get_source = (lambda orig: lambda e, n: orig(e, n if n.endswith('.html') else n + '.html'))(env.loader.get_source)

def html(lang, kind):
    t = json.loads((HERE/f'{lang}.json').read_text(encoding='utf-8'))
    return env.get_template('template.html').render(t=t, lang=lang, kind=kind, P=PHOTOS, crew=CREW, site=site,
                                                    img=img, blur=blur, logo=logo, font=font, row=row)

async def main(langs):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 794, 'height': 1123})
        for lang in langs:
            for kind in ('dossier', 'rider'):
                await pg.set_content(html(lang, kind), wait_until='load')
                await pg.evaluate('document.fonts.ready')
                out = OUT/f'VENDAVAL-Brass_{lang.upper()}_{kind}_{DATE}.pdf'
                await pg.pdf(path=str(out), width='794px', height='1123px', print_background=True, prefer_css_page_size=True)
                print(out.relative_to(ROOT))
        await b.close()

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1:] or ['ca', 'es', 'en', 'de', 'fr', 'it', 'pt', 'ja']))
