"""Make logo variants with a thick white outline (sticker style), so the black parts of the
VENDAVAL logo stay visible on dark or photo backgrounds. Rule (tyle, 31 Oct 2026): never put the
transparent logo on a background that swallows part of it; no square/box behind the logo.
Usage: python3 tools/logo_outline.py"""
import pathlib
import numpy as np
from scipy import ndimage
from PIL import Image, ImageFilter
ROOT = pathlib.Path(__file__).resolve().parent.parent

def outline(src, dst, frac=0.022):
    im = Image.open(src).convert('RGBA')
    pad = int(im.width * frac) + 4
    big = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    big.paste(im, (pad, pad), im)
    a = ndimage.binary_fill_holes(np.array(big.split()[-1]) > 40)
    d = ndimage.distance_transform_edt(~a)
    r = im.width * frac
    ring = Image.fromarray((np.clip(r + 1 - d, 0, 1) * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.6))
    white = Image.new('RGBA', big.size, (255, 255, 255, 255)); white.putalpha(ring)
    white.alpha_composite(big)
    white.save(dst)
    print(dst.relative_to(ROOT), white.size)

outline(ROOT/'dossiers/assets/logos/vendaval.png', ROOT/'dossiers/assets/logos/vendaval-outline.png')
outline(ROOT/'static/img/logo.webp', ROOT/'static/img/logo-outline.webp')
