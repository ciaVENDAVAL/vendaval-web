"""VENDAVAL Brass: green rider and access rider (1 page each), 8 languages -> static/pdf/
Usage (from the repo root): python3 dossiers/riders-brass/build.py [ca es en de fr it pt ja]
Texts: dossiers/riders-brass/<lang>.json · layout: template.html · photos: source-images/, always whole (never cropped)
Source text (EN, approved by tyle 5 Nov 2026): Project doc `master/VENDAVAL Brass riders and pitch - drafts.md`."""
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
DATE = '2026-11'
site = json.loads((ROOT/'content'/'data.json').read_text())['site']
PHOTOS = dict(green=['VENDAVAL_FiraVapor002.jpg', 'VENDAVAL_Unterwegs001.jpg'],
              access=['VENDAVAL_salvavidas_publico.jpg', 'IMG_0677.JPG'])
FILES = dict(green='green-rider', access='access-rider')

def uri(data, mime): return f'data:{mime};base64,' + base64.b64encode(data).decode()

@functools.lru_cache(None)
def _open(name): return ImageOps.exif_transpose(Image.open(IMGSRC/name)).convert('RGB')

@functools.lru_cache(None)
def img(name, px=1400):
    im = _open(name).copy(); im.thumbnail((px, px))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=82); return uri(b.getvalue(), 'image/jpeg')

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
    return env.get_template('template.html').render(t=t, r=t[kind], lang=lang, kind=kind, photos=PHOTOS[kind],
                                                    site=site, img=img, logo=logo, font=font, row_sizes=row_sizes)

async def main(langs):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        for lang in langs:
            for kind in ('green', 'access'):
                await pg.set_content(html(lang, kind), wait_until='load')
                await pg.evaluate('document.fonts.ready')
                out = OUT/f'VENDAVAL-Brass_{lang.upper()}_{FILES[kind]}_{DATE}.pdf'
                await pg.pdf(path=str(out), print_background=True, prefer_css_page_size=True)
                print(out.relative_to(ROOT))
        await b.close()

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1:] or ['ca', 'es', 'en', 'de', 'fr', 'it', 'ja']))
