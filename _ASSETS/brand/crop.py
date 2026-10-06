# Tight-crop the Mobius source for raster icon sizes + OG card. Pillow only (already present).
from PIL import Image
src = Image.open('arcs-mobius-source.png').convert('RGB')
for s in (180, 192, 512):
    src.resize((s, s), Image.LANCZOS).save(f'crop-{s}.png')
# OG card: centre the source on black and fade its left/right edges into the black
# side panels (the source background is dark grey, not black, so a hard edge shows).
og = Image.new('RGB', (1200, 630), (0, 0, 0))
tile = src.resize((630, 630), Image.LANCZOS)
fade = 90
mask = Image.new('L', (630, 630), 255)
px = mask.load()
for x in range(630):
    d = min(x, 629 - x)
    if d < fade:
        a = int(255 * (d / fade) ** 1.5)
        for y in range(630):
            px[x, y] = a
og.paste(tile, (285, 0), mask)
og.save('og-1200x630.png')
