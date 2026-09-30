#!/usr/bin/env python3
"""linkedin_render: turn a gated LinkedIn queue file into postable media, deterministically.

  exec cut        -> card.png        1080x1350 (LinkedIn portrait image)
  operational cut -> carousel.pdf    one 1080x1350 page per slide (LinkedIn document post)

Renders with the locally installed Google Chrome in headless mode (no new deps, no network, no
model calls; nothing leaves the machine). Colors come from the kit tokens, inlined verbatim.

Gate (exit 1 on any miss):
  - text overflow: the page measures every text box in the browser and reports overflow through
    --dump-dom; a card or slide whose text does not fit is a failure, never a silent clip
  - card.png is exactly 1080x1350 (read from the PNG header)
  - carousel.pdf page count == number of slides

Output goes to _ARTIFACTS/linkedin/<queue id>/ (gitignored scratch; the queue file is the SSOT).

  python3 scripts/linkedin_render.py [_QUEUE/linkedin/<id>.json ...]   # default: every queue file
  python3 scripts/linkedin_render.py --self-test                         # proves overflow fails
Stdlib only.
"""
import glob, html, json, os, re, struct, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
QUEUE = os.path.join(ROOT, "_QUEUE", "linkedin")
OUT = os.path.join(ROOT, "_ARTIFACTS", "linkedin")
TOKENS = os.path.join(ROOT, "src", "ui-kit", "recoil-report", "_tokens.css")
CHROME = os.environ.get("CHROME_BIN", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
W, H = 1080, 1350

CSS = """
@page { size: 1080px 1350px; margin: 0; }
* { box-sizing: border-box; margin: 0; }
html, body { background: var(--bg); color: var(--text); }
body { font-family: 'Inter', system-ui, -apple-system, sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 1080px; height: 1350px; padding: 96px 88px; display: flex; flex-direction: column; justify-content: space-between; page-break-after: always; overflow: hidden; }
.page:last-child { page-break-after: auto; }
.label { font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 30px; letter-spacing: 0.04em; color: var(--cyan); }
.fit { flex: 1; display: flex; align-items: center; overflow: hidden; }
.line { font-family: 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif; font-weight: 500; line-height: 1.2; }
.card .line { font-size: 84px; }
.slide .line { font-size: 58px; line-height: 1.3; }
.slide.first .line { font-size: 76px; line-height: 1.2; }
.foot { display: flex; justify-content: space-between; font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 28px; color: #94a3b8; border-top: 2px solid var(--border); padding-top: 32px; }
"""

JS = """<script>
addEventListener('load', function () {
  var bad = [];
  document.querySelectorAll('.page').forEach(function (p, i) {
    var f = p.querySelector('.fit'), l = p.querySelector('.line');
    if (f.scrollHeight > f.clientHeight + 1 || l.scrollWidth > l.clientWidth + 1) bad.push(i + 1);
  });
  document.body.setAttribute('data-overflow', bad.join(','));
  document.body.setAttribute('data-done', '1');
});
</script>"""


def page(kind, label, text, foot_l, foot_r, extra=""):
    e = html.escape
    return (f'<section class="page {kind} {extra}"><div class="label">{e(label)}</div>'
            f'<div class="fit"><p class="line">{e(text)}</p></div>'
            f'<div class="foot"><span>{e(foot_l)}</span><span>{e(foot_r)}</span></div></section>')


def doc(pages):
    tokens = open(TOKENS, encoding="utf-8").read()
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{tokens}\n{CSS}</style></head>'
            f'<body>{"".join(pages)}{JS}</body></html>')


def chrome(args, url):
    base = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
            "--no-default-browser-check", "--disable-extensions", "--virtual-time-budget=3000",
            f"--window-size={W},{H}", "--force-device-scale-factor=1"]
    return subprocess.run(base + args + [url], capture_output=True, text=True, timeout=120)


def overflow(html_path):
    r = chrome(["--dump-dom"], "file://" + html_path)
    m = re.search(r'data-overflow="([^"]*)"', r.stdout)
    if not m:
        return None  # measurement never ran: treat as a failure upstream
    return [int(x) for x in m.group(1).split(",") if x]


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24])


def pdf_pages(path):
    return len(re.findall(rb"/Type\s*/Page(?!s)", open(path, "rb").read()))


def render(qpath):
    q = json.load(open(qpath))
    cuts = {c["altitude"]: c for c in q["cuts"]}
    host = q["index_url"].replace("https://", "")
    out = os.path.join(OUT, q["id"]); os.makedirs(out, exist_ok=True)
    errs = []

    card_html = os.path.join(out, "card.html")
    open(card_html, "w").write(doc([page("card", q["show"].upper(), cuts["exec"]["card_line"], "Zach Harris", host)]))
    ov = overflow(card_html)
    if ov is None: errs.append("card: overflow measurement did not run")
    elif ov: errs.append("card: text overflows the 1080x1350 frame")
    card_png = os.path.join(out, "card.png")
    chrome([f"--screenshot={card_png}"], "file://" + card_html)
    if not os.path.exists(card_png): errs.append("card.png not written")
    elif png_size(card_png) != (W, H): errs.append(f"card.png is {png_size(card_png)}, want {(W, H)}")

    slides = cuts["operational"]["slides"]
    n = len(slides)
    pages = [page("slide" + (" first" if i == 0 else ""), f"{q['show'].upper()}  {i + 1}/{n}", s,
                  "Zach Harris", host) for i, s in enumerate(slides)]
    car_html = os.path.join(out, "carousel.html")
    open(car_html, "w").write(doc(pages))
    ov = overflow(car_html)
    if ov is None: errs.append("carousel: overflow measurement did not run")
    elif ov: errs.append(f"carousel: text overflows on slide(s) {ov}")
    car_pdf = os.path.join(out, "carousel.pdf")
    chrome([f"--print-to-pdf={car_pdf}", "--no-pdf-header-footer"], "file://" + car_html)
    if not os.path.exists(car_pdf): errs.append("carousel.pdf not written")
    elif pdf_pages(car_pdf) != n: errs.append(f"carousel.pdf has {pdf_pages(car_pdf)} pages, want {n}")
    return out, errs


def self_test():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "t.html")
        open(p, "w").write(doc([page("card", "TEST", "ok", "a", "b"),
                                page("card", "TEST", "overflow " * 400, "a", "b")]))
        ov = overflow(p)
        assert ov == [2], f"expected overflow on page 2 only, got {ov}"
    print("linkedin_render self-test: PASS (overflow detected on the overfull page only)")
    return 0


def main(a):
    if "--self-test" in a:
        return self_test()
    if not os.path.exists(CHROME):
        print(f"linkedin_render: Chrome not found at {CHROME} (set CHROME_BIN)"); return 2
    paths = [x for x in a if x.endswith(".json")] or sorted(glob.glob(os.path.join(QUEUE, "*.json")))
    bad = 0
    for p in paths:
        out, errs = render(p)
        print(f"[{'FAIL' if errs else 'PASS'}] {os.path.relpath(p, ROOT)} -> {os.path.relpath(out, ROOT)}/card.png, carousel.pdf")
        for e in errs: print(f"   - {e}")
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
