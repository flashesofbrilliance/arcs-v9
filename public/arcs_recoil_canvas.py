#!/usr/bin/env python3
"""ARCS Recoil Prep Receipt — pixel-perfect dashboard canvas"""

from PIL import Image, ImageDraw, ImageFont
import math, os

FONTS = "/Users/zharris/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/4abae05a-1a76-4db1-af1e-f90d4fd40ee1/72d29ca3-2a4b-4a6a-96b6-decd55199018/skills/canvas-design/canvas-fonts"
OUT = "/private/tmp/claude-501/-Users-zharris-arcs-v9--claude-worktrees-brave-chebyshev-cd6452/3ca6b02a-e645-4ffe-a0c7-31783f635dd5/scratchpad"

# ── Tokens ─────────────────────────────────────────────────────────────────
BG       = (2,   4,   8)
SURFACE  = (13,  17,  23)
SURFACE2 = (18,  24,  34)
BORDER   = (30,  41,  59)
TEXT     = (226, 232, 240)
MUTED    = (71,  85, 105)
DIMMED   = (100, 116, 139)
CYAN     = (0,   240, 255)
GREEN    = (0,   255, 157)
GOLD     = (255, 215,  0)
RED      = (255, 77,  109)
CYAN_DIM = (0,   120, 128)

W = 1600
MARGIN = 56

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

# Font palette
def fonts():
    return {
        "mono_sm":    font("GeistMono-Regular.ttf", 12),
        "mono_md":    font("GeistMono-Regular.ttf", 14),
        "mono_bold":  font("GeistMono-Bold.ttf", 14),
        "mono_lg":    font("GeistMono-Bold.ttf", 18),
        "mono_xl":    font("GeistMono-Bold.ttf", 26),
        "sans_xs":    font("InstrumentSans-Regular.ttf", 11),
        "sans_sm":    font("InstrumentSans-Regular.ttf", 13),
        "sans_md":    font("InstrumentSans-Regular.ttf", 15),
        "sans_bold":  font("InstrumentSans-Bold.ttf", 15),
        "sans_lg":    font("InstrumentSans-Bold.ttf", 19),
        "sans_xl":    font("InstrumentSans-Bold.ttf", 26),
        "sans_xxl":   font("InstrumentSans-Bold.ttf", 36),
        "display":    font("BricolageGrotesque-Bold.ttf", 48),
        "label":      font("WorkSans-Regular.ttf", 12),
        "label_bold": font("WorkSans-Bold.ttf", 12),
        "jb_mono":    font("JetBrainsMono-Regular.ttf", 12),
        "jb_bold":    font("JetBrainsMono-Bold.ttf", 14),
    }

# ── Drawing helpers ─────────────────────────────────────────────────────────

def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rounded_rect(draw, x0, y0, x1, y1, r=8, fill=None, outline=None, width=1):
    if fill:
        draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill)
    if outline:
        draw.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=outline, width=width)

def glow_rect(img, draw, x0, y0, x1, y1, r=8, color=CYAN, alpha=60):
    """Draw a glowing border by layering semi-transparent rounded rects"""
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for spread in [6, 4, 2]:
        a = int(alpha * (1 - spread/10))
        c = color + (a,)
        od.rounded_rectangle([x0-spread, y0-spread, x1+spread, y1+spread],
                              radius=r+spread, outline=c, width=1)
    img.paste(Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB'), (0,0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=color, width=1)
    return draw

def badge(draw, x, y, text, color, F, bg=None):
    """Draw a small badge chip"""
    f = F["sans_xs"]
    bbox = f.getbbox(text)
    tw = bbox[2] - bbox[0]
    pad_x, pad_y = 10, 5
    bw, bh = tw + pad_x*2, 18
    bg_col = tuple(max(0, c//5) for c in color) if bg is None else bg
    rounded_rect(draw, x, y, x+bw, y+bh, r=4, fill=bg_col, outline=color, width=1)
    draw.text((x+pad_x, y+pad_y-2), text, font=f, fill=color)
    return bw

def section_label(draw, x, y, text, F):
    draw.text((x, y), text.upper(), font=F["sans_xs"], fill=MUTED)

def divider(draw, y, x0=MARGIN, x1=None):
    if x1 is None: x1 = W - MARGIN
    draw.line([(x0, y), (x1, y)], fill=BORDER, width=1)

def txt(draw, x, y, text, f, color=TEXT, anchor="la"):
    draw.text((x, y), text, font=f, fill=color, anchor=anchor)

def progress_bar(draw, x, y, w, h, pct, color, bg=SURFACE2):
    rounded_rect(draw, x, y, x+w, y+h, r=h//2, fill=bg)
    fw = int(w * pct)
    if fw > h:
        rounded_rect(draw, x, y, x+fw, y+h, r=h//2, fill=color)

# ── Main build ──────────────────────────────────────────────────────────────

def build():
    # Measure sections to compute total height
    section_heights = {
        "header": 100,
        "arc":    150,
        "entity": 240,
        "delta":  260,
        "kairos": 280,
        "beats":  320,
        "prob":   240,
        "receipt":250,
        "footer": 70,
    }
    total_h = sum(section_heights.values()) + MARGIN*2 + 60  # separators
    img = Image.new('RGB', (W, total_h), BG)
    draw = ImageDraw.Draw(img)
    F = fonts()

    # subtle grid lines
    for gx in range(0, W, 80):
        draw.line([(gx, 0), (gx, total_h)], fill=(255,255,255,3) if False else (14,19,26), width=1)

    cy = MARGIN  # current y cursor

    # ── 1. HEADER ─────────────────────────────────────────────────────────
    hh = 84
    rounded_rect(draw, MARGIN, cy, W-MARGIN, cy+hh, r=10, fill=SURFACE, outline=BORDER, width=1)
    # Left accent strip
    draw.rounded_rectangle([MARGIN, cy, MARGIN+4, cy+hh], radius=4, fill=CYAN)

    # ARCS mark
    txt(draw, MARGIN+22, cy+10, "ARCS", F["display"], CYAN)
    txt(draw, MARGIN+22, cy+60, "RECOIL  RECEIPT", F["mono_sm"], MUTED)

    # Receipt ID — centered vertically in header
    rid = "ARCS-ORIENT-2026-07-01T12:30Z · fanatics-cj001"
    rid_f = F["jb_mono"]
    rb = rid_f.getbbox(rid)
    rw = rb[2]-rb[0]
    txt(draw, W//2 - rw//2, cy+20, rid, rid_f, DIMMED)

    # Y-gate (center-right)
    gate_txt = "GREEN / HIGH / KAIROS-ACTIVE"
    gf = F["sans_sm"]
    gb = gf.getbbox(gate_txt)
    gw = gb[2]-gb[0]
    gx2 = W//2 - gw//2
    rounded_rect(draw, gx2-14, cy+42, gx2+gw+14, cy+64, r=4,
                 fill=(0,40,24), outline=GREEN, width=1)
    draw.text((gx2, cy+46), gate_txt, font=gf, fill=GREEN)

    # NCI block — far right
    nci_label = "NCI"
    nci_val   = "91"
    nci_sub   = "SHARP"
    txt(draw, W-MARGIN-120, cy+10,  nci_label, F["mono_sm"], MUTED)
    txt(draw, W-MARGIN-120, cy+26,  nci_val,   F["mono_xl"], GREEN)
    txt(draw, W-MARGIN-120, cy+60,  nci_sub,   F["mono_sm"], CYAN)

    cy += section_heights["header"] + 16

    # ── 2. HYPERSTITION ARC ───────────────────────────────────────────────
    section_label(draw, MARGIN, cy, "§ Hyperstition Arc  ·  Current Stage", F)
    cy += 20

    nodes = [
        ("Ethereal",     MUTED,  False),
        ("Loki Test",    MUTED,  False),
        ("KAIROS LOCK",  CYAN,   True),   # active
        ("Receipt",      DIMMED, False),
        ("ROM Hard-Yes", DIMMED, False),
    ]
    node_w = (W - MARGIN*2 - 40) / len(nodes)
    node_r = 28
    arc_cy = cy + 54
    connector_y = arc_cy

    for i, (label, color, active) in enumerate(nodes):
        nx = int(MARGIN + 20 + node_w * i + node_w/2)

        # connector line (before node)
        if i > 0:
            prev_nx = int(MARGIN + 20 + node_w*(i-1) + node_w/2)
            line_color = CYAN if (nodes[i-1][2] or active) else BORDER
            draw.line([(prev_nx + node_r, connector_y),
                       (nx - node_r, connector_y)],
                      fill=line_color, width=2)
            # arrow tip
            ax = nx - node_r
            draw.polygon([(ax-6, connector_y-4), (ax, connector_y), (ax-6, connector_y+4)],
                         fill=line_color)

        if active:
            # glow effect layers
            for spread, alpha in [(12,20),(8,35),(4,55),(2,80)]:
                oc = (*CYAN, alpha)
                ov = Image.new('RGBA', img.size, (0,0,0,0))
                od = ImageDraw.Draw(ov)
                od.ellipse([nx-node_r-spread, arc_cy-node_r-spread,
                            nx+node_r+spread, arc_cy+node_r+spread],
                           outline=oc, width=1)
                img = Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
                draw = ImageDraw.Draw(img)

            draw.ellipse([nx-node_r, arc_cy-node_r, nx+node_r, arc_cy+node_r],
                         fill=(0,60,70), outline=CYAN, width=2)
            # pulsing inner dot
            draw.ellipse([nx-6, arc_cy-6, nx+6, arc_cy+6], fill=CYAN)
        else:
            draw.ellipse([nx-node_r, arc_cy-node_r, nx+node_r, arc_cy+node_r],
                         fill=SURFACE2, outline=color, width=1)
            if i < 2:  # completed
                draw.ellipse([nx-5, arc_cy-5, nx+5, arc_cy+5], fill=color)

        # label
        lf = F["mono_bold"] if active else F["mono_sm"]
        lc = CYAN if active else color
        bbox = lf.getbbox(label)
        lw = bbox[2]-bbox[0]
        draw.text((nx - lw//2, arc_cy + node_r + 10), label, font=lf, fill=lc)

    cy += section_heights["arc"] + 10
    divider(draw, cy)
    cy += 16

    # ── 3. ENTITY MAP ─────────────────────────────────────────────────────
    section_label(draw, MARGIN, cy, "§ Entities", F)
    cy += 18

    entities = [
        ("CJ Masopust",      "Talent Lead · Fanatics Collectibles",  "Gate to Chase",           GREEN, "WARM"),
        ("Chris Lamontagne", "SVP Growth · Fanatics",                 "HARD-YES signal",          CYAN, "LOCKED"),
        ("Chase (unknown)",  "Instant Rips Growth — Day-1 Beachhead","Not yet met",              GOLD, "PENDING"),
        ("Regina Marshall",  "EA to Chris · Cal management",          "Possibly AI agent",        DIMMED,"PASSIVE"),
    ]
    card_w = (W - MARGIN*2 - 12) // 2
    card_h = 76

    for i, (name, role, note, color, state) in enumerate(entities):
        col = i % 2
        row = i // 2
        ex = MARGIN + col * (card_w + 12)
        ey = cy + row * (card_h + 10)
        rounded_rect(draw, ex, ey, ex+card_w, ey+card_h, r=8, fill=SURFACE, outline=BORDER, width=1)
        # left color strip
        draw.rounded_rectangle([ex, ey, ex+4, ey+card_h], radius=4, fill=color)
        # name
        txt(draw, ex+18, ey+12, name, F["sans_bold"], TEXT)
        # role
        txt(draw, ex+18, ey+30, role, F["sans_sm"], MUTED)
        # note
        txt(draw, ex+18, ey+48, note, F["jb_mono"], DIMMED)
        # state badge
        badge(draw, ex+card_w-70, ey+12, state, color, F)

    cy += section_heights["entity"] + 10
    divider(draw, cy)
    cy += 16

    # ── 4. SIGNAL DELTA TABLE ─────────────────────────────────────────────
    section_label(draw, MARGIN, cy, "§ Pre-Call Signal Delta  ·  Expected State Going In", F)
    cy += 18

    col_xs = [MARGIN, MARGIN+360, MARGIN+780, MARGIN+1050]
    headers = ["Signal", "Expected State", "Confidence", "Δ Risk"]
    rows = [
        ("CJ has read your deck",          "Maybe — not explicitly forwarded",    "45%",  "MED"),
        ("CJ has a defined role brief",     "Unlikely — role is exploratory",      "20%",  "HIGH"),
        ("CJ knows Grayscale background",   "Only if she read the email chain",    "55%",  "MED"),
        ("Chase is actively hiring",        "Warm but not a confirmed req",        "40%",  "MED"),
        ("Call advances to Chase intro",    "Yes — if beachhead framing lands",    "75%",  "LOW"),
    ]
    row_h = 30
    thead_h = 28
    table_h = thead_h + row_h * len(rows) + 8
    rounded_rect(draw, MARGIN, cy, W-MARGIN, cy+table_h, r=8, fill=SURFACE, outline=BORDER, width=1)

    # Header row
    rounded_rect(draw, MARGIN, cy, W-MARGIN, cy+thead_h, r=8, fill=SURFACE2)
    for j, (hx, ht) in enumerate(zip(col_xs, headers)):
        txt(draw, hx+10, cy+8, ht, F["label_bold"], MUTED)

    for i, (sig, exp, conf, risk) in enumerate(rows):
        ry = cy + thead_h + i*row_h
        if i % 2 == 0:
            draw.rectangle([MARGIN+1, ry, W-MARGIN-1, ry+row_h], fill=(16,22,30))
        txt(draw, col_xs[0]+10, ry+8, sig,  F["jb_mono"], TEXT)
        txt(draw, col_xs[1]+10, ry+8, exp,  F["sans_sm"], DIMMED)
        conf_color = GREEN if int(conf[:-1]) >= 70 else (GOLD if int(conf[:-1]) >= 40 else RED)
        txt(draw, col_xs[2]+10, ry+8, conf, F["mono_bold"], conf_color)
        risk_color = RED if risk=="HIGH" else (GOLD if risk=="MED" else GREEN)
        badge(draw, col_xs[3]+10, ry+6, risk, risk_color, F)

    cy += section_heights["delta"] + 10
    divider(draw, cy)
    cy += 16

    # ── 5. KAIROS NODE CARDS ──────────────────────────────────────────────
    section_label(draw, MARGIN, cy, "§ Kairos Nodes  ·  Signal Taxonomy", F)
    cy += 18

    kairos = [
        ("⚡", "AHA Flash",         CYAN,  "She names the problem before you do"),
        ("🔱", "Mirror Shock",      GOLD,  "Org has been thinking about this"),
        ("🔴", "Productive Discord",RED,   "One person vs. team question"),
        ("⚠️","Quiet Signal",      MUTED, "Chase timeline hedge — don't push"),
        ("💎", "Hidden Alpha",      GREEN, "Second frustrated champion emerges"),
    ]
    kcard_w = (W - MARGIN*2 - 16*4) // 5
    kcard_h = 140

    for i, (icon, ktype, color, watch) in enumerate(kairos):
        kx = MARGIN + i*(kcard_w+16)
        ky = cy
        rounded_rect(draw, kx, ky, kx+kcard_w, ky+kcard_h, r=8, fill=SURFACE, outline=BORDER, width=1)
        # top color band
        rounded_rect(draw, kx, ky, kx+kcard_w, ky+4, r=4, fill=color)

        # icon
        try:
            draw.text((kx+14, ky+14), icon, font=F["sans_lg"], fill=color)
        except:
            draw.text((kx+14, ky+14), "•", font=F["sans_lg"], fill=color)

        txt(draw, kx+14, ky+42, ktype, F["sans_bold"], color)

        # wrap watch text into 2 lines
        words = watch.split()
        lines, cur = [], []
        for w in words:
            test = ' '.join(cur + [w])
            bb = F["jb_mono"].getbbox(test)
            if bb[2]-bb[0] > kcard_w-28 and cur:
                lines.append(' '.join(cur))
                cur = [w]
            else:
                cur.append(w)
        if cur: lines.append(' '.join(cur))
        for li, line in enumerate(lines[:3]):
            txt(draw, kx+14, ky+62+li*16, line, F["jb_mono"], DIMMED)

    cy += section_heights["kairos"] + 10
    divider(draw, cy)
    cy += 16

    # ── 6. FIVE BEATS ─────────────────────────────────────────────────────
    section_label(draw, MARGIN, cy, "§ Five Beats  ·  In Order", F)
    cy += 18

    beats = [
        ("Own the unusual path",    CYAN,  "ARCS found the signal before the post was widely visible. That's what the work does."),
        ("State the mandate",        GREEN, "Not title-shopping. The mandate: give the growth engine a memory."),
        ("Land on Instant Rips",    GOLD,  "High-velocity decisions every week. That's where I'd start."),
        ("Grayscale proof",          TEXT,  "$7B in digital assets, peak regulatory headwind, zero failures."),
        ("Choose-your-adventure",   CYAN,  "GM-style on one funnel, or horizontal intelligence layer. Which is more useful?"),
    ]
    beat_h = 48
    bw_inner = W - MARGIN*2

    for i, (title, color, body) in enumerate(beats):
        by = cy + i*(beat_h+8)
        rounded_rect(draw, MARGIN, by, W-MARGIN, by+beat_h, r=8,
                     fill=SURFACE, outline=BORDER, width=1)
        # number circle
        nr = 16
        nx2 = MARGIN+20+nr
        draw.ellipse([MARGIN+4, by+8, MARGIN+36, by+40], fill=color, outline=color)
        nc = BG
        nf = F["sans_bold"]
        nb = nf.getbbox(str(i+1))
        nw = nb[2]-nb[0]
        draw.text((nx2 - nw//2, by+14), str(i+1), font=nf, fill=nc)
        # title
        txt(draw, MARGIN+50, by+8, title, F["sans_bold"], color)
        # body
        txt(draw, MARGIN+50, by+26, body, F["jb_mono"], DIMMED)

    cy += section_heights["beats"] + 10
    divider(draw, cy)
    cy += 16

    # ── 7. PROBABILITY TREE ───────────────────────────────────────────────
    section_label(draw, MARGIN, cy, "§ Probability Tree  ·  Pre-Call Confidence", F)
    cy += 18

    probs = [
        ("Call advances to Chase intro",  0.75, GREEN),
        ("CJ has substantive context",    0.60, CYAN),
        ("Active req attached",           0.25, GOLD),
        ("Role shape named on this call", 0.40, GOLD),
        ("She asks to see the deck",      0.30, MUTED),
    ]
    bar_h = 24
    bar_total_w = W - MARGIN*2 - 300
    label_w = 280

    for i, (label, pct, color) in enumerate(probs):
        py = cy + i*(bar_h+16)
        txt(draw, MARGIN, py+4, label, F["sans_sm"], TEXT)
        bx2 = MARGIN + label_w
        progress_bar(draw, bx2, py, bar_total_w, bar_h, pct, color)
        pct_str = f"{int(pct*100)}%"
        pf = F["mono_bold"]
        pb = pf.getbbox(pct_str)
        pw = pb[2]-pb[0]
        txt(draw, bx2 + bar_total_w + 14, py+4, pct_str, pf, color)

    cy += section_heights["prob"] + 10
    divider(draw, cy)
    cy += 16

    # ── 8. PRE-CALL RECEIPT ───────────────────────────────────────────────
    section_label(draw, MARGIN, cy, "§ Pre-Call Receipt", F)
    cy += 18

    receipt_rows = [
        ("Core decision",        "Does this call unlock Chase + Instant Rips, or does it gate on a second conversation?"),
        ("True North",           "Exit with Chase intro confirmed or calendared"),
        ("Stated → watch",       "CJ says she needs to 'loop in the team'"),
        ("Revealed → weight",    "If she stays past 30 min or asks follow-up Qs — that's the signal"),
        ("Stop-loss",            "No Chase intro by Jul 8 → LinkedIn direct (Chris opened the door)"),
        ("NCI threshold",        "≥85 PROCEED · 65–84 CONDITIONAL · <65 HOLD + reassess with Chris"),
    ]
    rec_col = W // 2 - MARGIN//2
    rec_row_h = 30
    rec_table_h = rec_row_h * len(receipt_rows) + 8
    rounded_rect(draw, MARGIN, cy, W-MARGIN, cy+rec_table_h, r=8, fill=SURFACE, outline=BORDER, width=1)

    for i, (key, val) in enumerate(receipt_rows):
        ry = cy + 4 + i*rec_row_h
        if i % 2 == 0:
            draw.rectangle([MARGIN+1, ry, W-MARGIN-1, ry+rec_row_h], fill=(16,22,30))
        txt(draw, MARGIN+14, ry+8, key, F["label_bold"], MUTED)
        # vertical separator
        draw.line([(rec_col, ry+4),(rec_col, ry+rec_row_h-4)], fill=BORDER, width=1)
        txt(draw, rec_col+14, ry+8, val, F["jb_mono"], TEXT)

    cy += section_heights["receipt"] + 10

    # ── 9. STOP-LOSS FOOTER ───────────────────────────────────────────────
    footer_y = cy
    rounded_rect(draw, MARGIN, footer_y, W-MARGIN, footer_y+48, r=8,
                 fill=(40,10,20), outline=RED, width=1)
    stop_text = "STOP-LOSS  ·  If NCI drops below 65 on this call — HOLD and reassess with Chris before Chase intro."
    draw.text((MARGIN+20, footer_y+14), stop_text, font=F["mono_md"], fill=RED)
    # timestamp right
    ts = "07.01.2026  ·  12:30 ET  ·  THETA DECAY ACTIVE"
    tb = F["mono_sm"].getbbox(ts)
    tw = tb[2]-tb[0]
    draw.text((W-MARGIN-tw-10, footer_y+18), ts, font=F["mono_sm"], fill=(180,40,60))

    # ── Banked lesson watermark ────────────────────────────────────────────
    lesson = "Revealed preference > stated preference."
    lf = F["sans_md"]
    lb = lf.getbbox(lesson)
    lw = lb[2]-lb[0]
    # subtle centered at very bottom
    draw.text((W//2 - lw//2, total_h-28), lesson,
              font=lf, fill=(30,41,59))

    # ── Save ──────────────────────────────────────────────────────────────
    out_path = os.path.join(OUT, "arcs_recoil_cj_masopust.png")
    img.save(out_path, "PNG", dpi=(144, 144))
    print(f"Saved: {out_path}")
    print(f"Dimensions: {img.width}×{img.height}")
    return out_path

if __name__ == "__main__":
    build()
