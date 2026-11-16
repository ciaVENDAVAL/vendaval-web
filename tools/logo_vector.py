"""Logo files for the downloads page (Graphics), all without background:
  static/graphics/VENDAVAL_logo.svg / .pdf                  vector, traced from the 2048 px PNG
  static/graphics/VENDAVAL_logo_outline.svg / .pdf          vector with the thick white outline (for dark backgrounds)
  static/graphics/VENDAVAL_logo_outline_2048px.png / _web-600px.png
The PNG versions of the plain logo are made by build.py. Run this only when the logo changes:
  pip install vtracer --break-system-packages ; python3 tools/logo_vector.py
Tracing: upscale ×2, snap every pixel to the 4 logo colours (black, cyan, orange, white) with a hard
alpha edge, trace with vtracer, then snap every fill in the SVG to the same 4 colours."""
import pathlib, re, sys, asyncio
import numpy as np
from PIL import Image
import vtracer

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT/'source-images'/'logo_VENDAVAL_2025-04_sin_fondo.png'
OUT = ROOT/'static'/'graphics'; OUT.mkdir(parents=True, exist_ok=True)
PAL = np.array([[0, 0, 0], [24, 219, 247], [249, 150, 26], [255, 255, 255]], np.float32)
TMP = ROOT/'.logo-tmp'; TMP.mkdir(exist_ok=True)

def snap_png(im, dst):
    im = im.convert('RGBA'); im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    a = np.array(im); rgb = a[:, :, :3].astype(np.float32)
    idx = np.stack([((rgb - p) ** 2).sum(2) for p in PAL]).argmin(0)
    out = np.zeros(a.shape, np.uint8); out[:, :, :3] = PAL.astype(np.uint8)[idx]
    out[:, :, 3] = np.where(a[:, :, 3] > 128, 255, 0)
    Image.fromarray(out).save(dst)
    return im.size

def nearest(hexcol):
    c = np.array([int(hexcol[i:i + 2], 16) for i in (0, 2, 4)], np.float32)
    p = PAL[((PAL - c) ** 2).sum(1).argmin()].astype(int)
    return '#%02X%02X%02X' % tuple(p)

def trace(im, name):
    q = TMP/f'{name}.png'; w, h = snap_png(im, q)
    svg = TMP/f'{name}.svg'
    vtracer.convert_image_to_svg_py(str(q), str(svg), colormode='color', hierarchical='stacked', mode='spline',
                                    filter_speckle=6, color_precision=8, layer_difference=8, corner_threshold=60,
                                    length_threshold=4.0, max_iterations=10, splice_threshold=45, path_precision=2)
    s = svg.read_text()
    s = re.sub(r'fill="#([0-9A-Fa-f]{6})"', lambda m: f'fill="{nearest(m.group(1))}"', s)
    s = re.sub(r'<svg ([^>]*)width="\d+" height="\d+"', rf'<svg \1width="{w}" height="{h}" viewBox="0 0 {w} {h}"', s, count=1)
    s = s.replace('<!-- Generator: visioncortex VTracer', '<!-- Cia. VENDAVAL logo · www.VENDAVAL.cat · traced with VTracer', 1)
    (OUT/f'{name}.svg').write_text(s)
    return w, h

async def to_pdf(name, w, h):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        mm_w, mm_h = 200, 200 * h / w        # 20 cm wide; vector, so it scales to any size
        await pg.set_content(f'<style>@page{{size:{mm_w}mm {mm_h:.2f}mm;margin:0}}html,body{{margin:0}}img{{width:{mm_w}mm;height:{mm_h:.2f}mm;display:block}}</style>'
                             f'<img src="data:image/svg+xml;base64,{__import__("base64").b64encode((OUT/f"{name}.svg").read_bytes()).decode()}">')
        await pg.wait_for_timeout(300)
        await pg.pdf(path=str(OUT/f'{name}.pdf'), width=f'{mm_w}mm', height=f'{mm_h:.2f}mm', print_background=False)
        await b.close()

def outline_png():
    # same white sticker outline as tools/logo_outline.py (website logo)
    from scipy import ndimage
    from PIL import ImageFilter
    src = Image.open(SRC).convert('RGBA'); frac = 0.022
    pad = int(src.width * frac) + 4
    big = Image.new('RGBA', (src.width + 2 * pad, src.height + 2 * pad), (0, 0, 0, 0)); big.paste(src, (pad, pad), src)
    a = ndimage.binary_fill_holes(np.array(big.split()[-1]) > 40)
    d = ndimage.distance_transform_edt(~a); r = src.width * frac
    ring = Image.fromarray((np.clip(r + 1 - d, 0, 1) * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.6))
    im = Image.new('RGBA', big.size, (255, 255, 255, 255)); im.putalpha(ring); im.alpha_composite(big)
    dst = OUT/'VENDAVAL_logo_outline_2048px.png'
    im.thumbnail((2048, 2048)); im.save(dst, optimize=True)
    w = im.copy(); w.thumbnail((600, 600)); w.save(OUT/'VENDAVAL_logo_outline_web-600px.png', optimize=True)
    return im

if __name__ == '__main__':
    w, h = trace(Image.open(SRC), 'VENDAVAL_logo'); asyncio.run(to_pdf('VENDAVAL_logo', w, h))
    w, h = trace(outline_png(), 'VENDAVAL_logo_outline'); asyncio.run(to_pdf('VENDAVAL_logo_outline', w, h))
    import shutil; shutil.rmtree(TMP)
    for f in sorted(OUT.iterdir()): print(f.relative_to(ROOT), f.stat().st_size // 1024, 'KB')
