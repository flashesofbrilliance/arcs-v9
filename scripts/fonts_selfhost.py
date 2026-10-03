#!/usr/bin/env python3
"""fonts_selfhost.py: serve every static page's web fonts from /fonts/, never from Google.

WHY (2026-10-03): 78 of 181 public pages loaded fonts through fonts.googleapis.com, a chain
(page -> Google CSS -> gstatic font file) that delays first paint and swaps the font in late,
so text visibly jumps. This tool replaces that chain with same-origin files the Vercel CDN
caches for a year (next.config.ts /fonts/* is immutable), a preload for the body face, and a
metric-matched fallback face so the swap no longer reflows the page. It also fixes the head
basics page_gate.py checks (doctype, utf-8 charset in the first 1024 bytes).

  fetch   download the faces in FAMILIES (latin + latin-ext subsets) into public/fonts/,
          write public/fonts/manifest.json (files, unicode ranges, fallback metrics).
          Needs network once. Fallback metrics use next/font's own formula and metric table
          (node_modules/next/dist/server/capsize-font-metrics.json), so a static page and an
          app route fall back identically.
  apply   rewrite pages from the manifest. Stdlib only, no network. Idempotent.
  check   list pages that still load Google Fonts (exit 1 if any).

Filenames carry a version (-v1). /fonts/* is cached immutable for a year, so a changed file
must get a new name; bump VERSION and re-fetch, never overwrite in place.
"""
import argparse
import glob
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "public", "fonts")
MANIFEST = os.path.join(ROOT, "runtime", "specs", "fonts-manifest.json")
METRICS = os.path.join(ROOT, "node_modules", "next", "dist", "server", "capsize-font-metrics.json")
VERSION = "v1"
SUBSETS = ("latin", "latin-ext")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# family -> css2 axis spec (variable ranges where Google serves them, so one file covers
# every weight a page asks for). Union of what the pages requested on 2026-10-03.
FAMILIES = {
    "Inter": "wght@100..900",
    "JetBrains Mono": "wght@100..800",
    "Newsreader": "ital,opsz,wght@0,6..72,200..800;1,6..72,200..800",
    "IBM Plex Mono": "wght@400;500;600;700",
    "IBM Plex Sans": "wght@400;500;600;700",
    "Work Sans": "wght@100..900",
    "Nunito Sans": "opsz,wght@6..12,200..1000",
    "Open Sans": "wght@300..800",
    "Instrument Serif": "ital@0;1",
}
# next/font picks Times New Roman for serif and Arial for everything else; a proportional
# fallback misaligns monospace text, so monospace falls back to Courier New instead.
FALLBACK = {"serif": "Times New Roman", "sans-serif": "Arial", "monospace": "Courier New"}
# Metric-compatible stand-ins (same advance widths and vertical metrics by design), so the
# override math holds on Linux and Android, which rarely ship the Microsoft core fonts.
LOCAL_ALIASES = {"Arial": ["Arial", "Liberation Sans", "Arimo"],
                 "Times New Roman": ["Times New Roman", "Liberation Serif", "Tinos"],
                 "Courier New": ["Courier New", "Liberation Mono", "Cousine"]}
OLD_SELF_HOSTED = {"/fonts/inter.woff2": "Inter", "/fonts/jbmono.woff2": "JetBrains Mono"}


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def metric_key(name):
    # next/font's formatName: first char lower, every capital or word start upper, no spaces
    out = re.sub(r"(?:^\w|[A-Z]|\b\w)", lambda m: m.group(0).lower() if m.start() == 0
                 else m.group(0).upper(), name)
    return re.sub(r"\s+", "", out)


def fallback_metrics(name, table):
    m = table[metric_key(name)]
    fb_name = FALLBACK.get(m["category"], "Arial")
    fb = table[metric_key(fb_name)]
    size = (m["xWidthAvg"] / m["unitsPerEm"]) / (fb["xWidthAvg"] / fb["unitsPerEm"])
    pct = lambda v: f"{abs(v / (m['unitsPerEm'] * size)) * 100:.2f}%"
    return {"local": LOCAL_ALIASES.get(fb_name, [fb_name]), "size_adjust": f"{size * 100:.2f}%", "ascent": pct(m["ascent"]),
            "descent": pct(m["descent"]), "line_gap": pct(m["lineGap"])}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def fetch():
    os.makedirs(FONTS, exist_ok=True)
    table = json.load(open(METRICS))
    manifest = {"version": VERSION, "families": {}}
    for name, axes in FAMILIES.items():
        css = get("https://fonts.googleapis.com/css2?family=%s:%s&display=swap"
                  % (name.replace(" ", "+"), axes)).decode()
        faces = []
        for subset, block in re.findall(r"/\*\s*([\w-]+)\s*\*/\s*@font-face\s*{([^}]*)}", css):
            if subset not in SUBSETS:
                continue
            style = re.search(r"font-style:\s*(\w+)", block).group(1)
            weight = re.search(r"font-weight:\s*([\d ]+);", block).group(1).strip()
            src = re.search(r"url\((https://[^)]+\.woff2)\)", block).group(1)
            urange = re.search(r"unicode-range:\s*([^;]+);", block).group(1).strip()
            fname = f"{slug(name)}-{style}-{weight.replace(' ', '-')}-{subset}-{VERSION}.woff2"
            path = os.path.join(FONTS, fname)
            if not os.path.exists(path):
                with open(path, "wb") as fh:
                    fh.write(get(src))
            faces.append({"style": style, "weight": weight, "subset": subset,
                          "file": "/fonts/" + fname, "unicode_range": urange,
                          "bytes": os.path.getsize(path)})
        if not faces:
            sys.exit(f"fetch: no latin faces returned for {name}")
        manifest["families"][name] = {"faces": faces, "fallback": fallback_metrics(name, table)}
        print(f"  {name:18} {len(faces)} faces, {sum(f['bytes'] for f in faces) // 1024} KB")
    with open(MANIFEST, "w") as fh:
        json.dump(manifest, fh, indent=1)
        fh.write("\n")
    print(f"wrote {os.path.relpath(MANIFEST, ROOT)}")


def face_css(name, fam):
    rules = []
    for f in fam["faces"]:
        rules.append(f"@font-face{{font-family:'{name}';font-style:{f['style']};"
                     f"font-weight:{f['weight']};font-display:swap;"
                     f"src:url('{f['file']}') format('woff2');unicode-range:{f['unicode_range']};}}")
    fb = fam["fallback"]
    local = ",".join("local('%s')" % n for n in fb["local"])
    rules.append(f"@font-face{{font-family:'{name} Fallback';src:{local};"
                 f"size-adjust:{fb['size_adjust']};ascent-override:{fb['ascent']};"
                 f"descent-override:{fb['descent']};line-gap-override:{fb['line_gap']};}}")
    return "\n".join(rules)


GOOGLE_LINK = re.compile(r"[ \t]*<link[^>]+href=[\"']https://fonts\.googleapis\.com/css2\?[^>]*>[ \t]*\n?", re.I)
GOOGLE_IMPORT = re.compile(r"[ \t]*@import\s+url\(\s*['\"]?https://fonts\.googleapis\.com/css2\?[^)]*\)\s*;?[ \t]*\n?", re.I)
PRECONNECT = re.compile(r"[ \t]*<link[^>]+rel=[\"']preconnect[\"'][^>]+fonts\.(?:googleapis|gstatic)\.com[^>]*>[ \t]*\n?", re.I)
OLD_PRELOAD = re.compile(r"[ \t]*<link[^>]+href=[\"'](?:/fonts/(?:inter|jbmono)\.woff2)[\"'][^>]*>[ \t]*\n?", re.I)
OLD_FACE = re.compile(r"[ \t]*@font-face\s*{[^}]*url\(['\"]?(/fonts/(?:inter|jbmono)\.woff2)['\"]?\)[^}]*}[ \t]*\n?", re.I)
BLOCK_START = "/* fonts_selfhost:begin (generated; edit scripts/fonts_selfhost.py) */"
BLOCK_END = "/* fonts_selfhost:end */"
# the whole generated unit: optional preload line + <style> + block + </style>. Removing only the
# block left an empty <style></style> and a stray preload behind on every re-run.
GENERATED = re.compile(r'(?:<link rel="preload" href="/fonts/[^"]+" as="font"[^>]*>\n)?<style>\n'
                       + re.escape(BLOCK_START) + r".*?" + re.escape(BLOCK_END) + r"\n</style>\n",
                       re.S)


def requested_families(src, manifest):
    names = []
    for url in re.findall(r"https://fonts\.googleapis\.com/css2\?[^\"')>\s]+", src):
        for spec in re.findall(r"family=([^&:]+)", url.replace("&amp;", "&")):
            names.append(spec.replace("+", " "))
    for path, fam in OLD_SELF_HOSTED.items():
        if path in src:
            names.append(fam)
    # a page already converted names its families inside the generated block; reading them
    # back is what makes apply idempotent (a manifest change refreshes every converted page)
    block = re.search(re.escape(BLOCK_START) + r"(.*?)" + re.escape(BLOCK_END), src, re.S)
    if block:
        names += [n for n in re.findall(r"font-family:'([^']+)'", block.group(1))
                  if not n.endswith(" Fallback")]
    unknown = [n for n in names if n not in manifest["families"]]
    if unknown:
        raise SystemExit(f"apply: family not in manifest, add it to FAMILIES and fetch: {unknown}")
    return list(dict.fromkeys(names))


def add_fallback_names(src, names):
    """'Newsreader' -> 'Newsreader','Newsreader Fallback' inside CSS, once per occurrence."""
    def css(text):
        for n in names:
            text = re.sub(r"(['\"])%s\1(?!\s*,\s*['\"]%s Fallback)" % (re.escape(n), re.escape(n)),
                          lambda m: f"{m.group(0)},{m.group(1)}{n} Fallback{m.group(1)}", text)
        return text
    src = re.sub(r"(<style[^>]*>)(.*?)(</style>)",
                 lambda m: m.group(1) + css(m.group(2)) + m.group(3), src, flags=re.S | re.I)
    # inline style="font-family:'Inter',..." attributes (single quotes inside double)
    return re.sub(r'(style=")([^"]*font-family[^"]*)(")',
                  lambda m: m.group(1) + css(m.group(2)) + m.group(3), src)


def ensure_head_basics(src, doctype):
    # charset is always safe to add: the server already sends utf-8, this only makes the file
    # self-describing. A doctype moves a page from quirks to standards mode and can shift its
    # layout, so it is added only on request (--doctype) and verified by screenshot.
    if doctype and not re.match(r"^﻿?\s*<!doctype html", src, re.I):
        src = "<!doctype html>\n" + src.lstrip("﻿")
    if not re.search(r"<meta[^>]+charset\s*=\s*[\"']?utf-8", src[:1024], re.I):
        src = re.sub(r"[ \t]*<meta[^>]+charset\s*=[^>]*>[ \t]*\n?", "", src, flags=re.I)
        head = re.search(r"<head[^>]*>", src[:1024], re.I)
        dt = re.match(r"^﻿?\s*<!doctype html[^>]*>", src, re.I)
        at = head.end() if head else (dt.end() if dt else 0)
        src = src[:at] + ('\n' if at else '') + '<meta charset="utf-8">' + ('' if at else '\n') + src[at:]
    return src


def apply(paths, doctype=False):
    manifest = json.load(open(MANIFEST))
    changed = 0
    for p in paths:
        src = orig = open(p, encoding="utf-8").read()
        names = requested_families(src, manifest)
        if names:
            src = PRECONNECT.sub("", src)
            src = GOOGLE_LINK.sub("", src)
            src = GOOGLE_IMPORT.sub("", src)
            src = OLD_FACE.sub("", src)
            src = OLD_PRELOAD.sub("", src)
            src = GENERATED.sub("", src)
            src = add_fallback_names(src, names)
            body = next(f for f in manifest["families"][names[0]]["faces"]
                        if f["subset"] == "latin" and f["style"] == "normal")
            block = (f'<link rel="preload" href="{body["file"]}" as="font" type="font/woff2" crossorigin>\n'
                     f"<style>\n{BLOCK_START}\n"
                     + "\n".join(face_css(n, manifest["families"][n]) for n in names)
                     + f"\n{BLOCK_END}\n</style>\n")
            src = re.sub(r"(<style[^>]*>)", lambda m: block + m.group(1), src, count=1) \
                if re.search(r"<style", src, re.I) else src.replace("</head>", block + "</head>", 1)
        src = ensure_head_basics(src, doctype)
        if src != orig:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(src)
            changed += 1
    print(f"apply: {changed} of {len(paths)} pages changed")


def check(paths):
    left = [p for p in paths if "fonts.googleapis.com" in open(p, encoding="utf-8", errors="replace").read()]
    for p in left:
        print("  still on Google Fonts:", p)
    print(f"check: {len(left)} page(s) still load Google Fonts")
    return 1 if left else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch")
    for c in ("apply", "check"):
        s = sub.add_parser(c)
        s.add_argument("pages", nargs="*")
        if c == "apply":
            s.add_argument("--doctype", action="store_true",
                           help="also add <!doctype html> (quirks -> standards; verify by screenshot)")
    a = ap.parse_args()
    if a.cmd == "fetch":
        return fetch()
    pages = a.pages or sorted(glob.glob(os.path.join(ROOT, "public", "*.html")))
    return apply(pages, a.doctype) if a.cmd == "apply" else check(pages)


if __name__ == "__main__":
    sys.exit(main())
