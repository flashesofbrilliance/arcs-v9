#!/usr/bin/env python3
"""Generate resume-tailor PWA icons — diamond glyph with 'RT' mark, distinct from personal-resume icons."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "public"
SIZE_192 = 192
SIZE_512 = 512
BG = (2, 4, 8, 255)
CYAN = (0, 240, 255, 255)
GOLD = (255, 215, 0, 255)

def diamond(draw, cx, cy, r, fill, outline):
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    draw.polygon(pts, fill=fill, outline=outline)

def draw_icon(size, out_path):
    img = Image.new("RGBA", (size, size), BG)
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    # outer diamond ring
    diamond(d, cx, cy, size * 0.40, (10, 16, 23, 255), (0, 240, 255, 60))
    # inner diamond
    diamond(d, cx, cy, size * 0.26, (14, 22, 32, 255), (0, 240, 255, 120))
    # center glow
    diamond(d, cx, cy, size * 0.12, (0, 240, 255, 40), (0, 240, 255, 180))
    # RT text — try a font, fall back to default
    try:
        font = ImageFont.truetype("/usr/share/fontfiles/JetBrainsMono-Regular.ttf", int(size * 0.16))
    except Exception:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(size * 0.16))
        except Exception:
            font = ImageFont.load_default()
    txt = "RT"
    tb = d.textbbox((0, 0), txt, font=font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    tx = cx - tw // 2
    ty = cy - th // 2 - 1
    d.text((tx, ty), txt, font=font, fill=CYAN)
    # subtle glow behind text
    d.text((tx - 1, ty - 1), txt, font=font, fill=(0, 240, 255, 40))
    img.save(out_path, "PNG")
    print(f"wrote {out_path} ({size}x{size})")

draw_icon(SIZE_192, OUT / "resume-tailor-icon-192.png")
draw_icon(SIZE_512, OUT / "resume-tailor-icon-512.png")
print("done")
