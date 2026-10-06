# Tight-crop the Mobius source for raster icon sizes + OG card. Stdlib-adjacent (PIL already present).
from PIL import Image
src = Image.open('arcs-mobius-source.png').convert('RGB')
for s in (180, 192, 512):
    src.resize((s, s), Image.LANCZOS).save(f'crop-{s}.png')
og = Image.new('RGB', (1200, 630), (0, 0, 0))
og.paste(src.resize((630, 630), Image.LANCZOS), (285, 0))
og.save('og-1200x630.png')
