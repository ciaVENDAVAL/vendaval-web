"""Icons (favicon, app icons) from the logo and 1200x630 link-preview images (WhatsApp, Telegram…).
Photo pages: the whole photo on a blurred copy of itself (never cropped). Pages without a photo: a screenshot.
Run by build.py; `python3 build.py --og` remakes every preview."""
import json, pathlib, re, threading, functools, http.server, io
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGO = ROOT/'source-images'/'logo_VENDAVAL_2025-04_sin_fondo.png'
W, H = 1200, 630

def icon(size, pad=0.08, radius=0.22):
    logo = Image.open(LOGO).convert('RGBA')
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], int(size * radius), fill=255)
    im.paste(Image.new('RGBA', (size, size), 'white'), (0, 0), mask)
    inner = int(size * (1 - 2 * pad)); lg = logo.copy(); lg.thumbnail((inner, inner), Image.LANCZOS)
    im.alpha_composite(lg, ((size - lg.width) // 2, (size - lg.height) // 2))
    return im

def make_icons(out):
    img = out/'img'
    big = icon(512)
    big.save(img/'icon-512.png'); icon(192).save(img/'icon-192.png')
    a = icon(180, radius=0); a.convert('RGB').save(img/'apple-touch-icon.png')
    icon(192).save(img/'favicon.png')
    icon(48, pad=0.03).save(out/'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
    (out/'site.webmanifest').write_text(json.dumps({'name': 'Cia. VENDAVAL', 'short_name': 'VENDAVAL', 'start_url': './',
        'display': 'browser', 'background_color': '#ffffff', 'theme_color': '#082f40',
        'icons': [{'src': 'img/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
                  {'src': 'img/icon-512.png', 'sizes': '512x512', 'type': 'image/png'}]}, indent=1))

def photo_card(src, dst):
    ph = Image.open(src).convert('RGB')
    bg = ph.copy(); s = max(W / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * s) + 1, int(bg.height * s) + 1))
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(28))).enhance(0.8)
    fg = ph.copy(); fg.thumbnail((W, H), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    for q in (85, 78, 70, 62):
        b = io.BytesIO(); bg.save(b, 'JPEG', quality=q, optimize=True, progressive=True)
        if b.tell() < 290_000: break
    dst.write_bytes(b.getvalue())

def make(out, force=False):
    out = pathlib.Path(out); make_icons(out); (out/'og').mkdir(exist_ok=True)
    wanted = {}
    for f in out.glob('*/**/index.html'):
        m = re.search(r'property="og:image" content="[^"]*?/(og/[^"]+)"', f.read_text(encoding='utf-8'))
        if m: wanted.setdefault(m.group(1), f.relative_to(out).parent.as_posix() + '/')
    shots = []
    for rel, page in sorted(wanted.items()):
        dst = out/rel
        if dst.exists() and not force: continue
        name = pathlib.Path(rel).stem
        if name.startswith('photo-'): photo_card(out/'img'/(name[6:] + '-1600.webp'), dst)
        else: shots.append((page, dst))
    for f in (out/'og').glob('*.jpg'):
        if 'og/' + f.name not in wanted: f.unlink()
    if shots: screenshots(out, shots)

def screenshots(out, shots):
    from playwright.sync_api import sync_playwright
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(out))
    h.log_message = lambda *a: None
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), h); port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=1)
            for page, dst in shots:
                pg.goto(f'http://127.0.0.1:{port}/{page}', wait_until='networkidle')
                pg.add_style_tag(content='.a11y-btn,.a11y,[class*="a11y-toggle"]{display:none!important}')
                pg.wait_for_timeout(400)
                pg.screenshot(path=str(dst), type='jpeg', quality=82)
            b.close()
    finally:
        srv.shutdown()
