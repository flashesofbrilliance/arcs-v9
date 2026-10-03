#!/usr/bin/env python3
"""page_gate.py: one gate for any standalone HTML page (public/, _ARTIFACTS/, _PROPOSALS/).

WHY: every page family grew its own partial gate (nftt-gates.sh and nftt_meta_gate.py are
NFTT-only; the pre-commit wrap guard only sees ADDED public/ and _ARTIFACTS/ files), so a draft
in _PROPOSALS/ shipped to a phone with no charset and rendered the middle dot as "Â·"
(719ed7f, 2026-10-03), and 30 public pages carry no doctype. This is the class-level stop
(AGENTS.md gotcha 15, Frustration Gate): one script, every page, cheapest checks first.

STATIC checks (stdlib, no browser):
  E doctype      document starts with <!doctype html> (else the browser uses quirks mode)
  E charset      <meta charset="utf-8"> inside the first 1024 bytes (the HTML spec's prescan
                 window: a declaration later than that is ignored and the browser guesses)
  E viewport     <meta name="viewport"> present (else phones render a zoomed-out desktop page)
  E mojibake     UTF-8 decoded as Windows-1252 already baked into the file ("Â·", "â€”", ...)
  E wrap-lint    scripts/artifact_wrap_lint.py (em-dash, ch caps, container/measure mismatch)
  W en-dash      en-dash in visible text (sometimes a legitimate range; reviewed by eye)
  W google-fonts page depends on fonts.googleapis.com (render-blocking chain, swap jump)
  W analytics    a public/ page without the /_vercel/insights snippet

RENDER checks (headless Chromium via Playwright; skipped with --static):
  E overflow     document wider than the viewport at 375, 790, 1280
  W lede         at 1280 the hero lede ends short of its heading's lane. Warning, not error:
                 index pages put the lede on the 680px measure on purpose (2026-09-29 exception).

USAGE
  python3 scripts/page_gate.py [--static] [--no-wrap-lint] FILE.html [FILE2.html ...]
EXIT
  0 pass (warnings allowed) · 1 at least one error · 2 render checks requested but no browser
Stdlib only; the render step shells out to node + playwright (repo or global install).
"""
import argparse
import html.parser
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIDTHS = (375, 790, 1280)
MOJIBAKE = ("Â·", "Â ", "â€", "Ã©", "Ã¨", "â†")


class Visible(html.parser.HTMLParser):
    """Collect text a reader sees: skip <style>, <script>, comments."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.text = []

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)


def static_checks(path, raw, run_wrap):
    errs, warns = [], []
    src = raw.decode("utf-8", errors="replace")
    head = raw[:1024].decode("utf-8", errors="replace").lower()

    if not re.match(r"^﻿?\s*(<!--.*?-->\s*)*<!doctype html", src, re.I | re.S):
        errs.append("doctype: file does not start with <!doctype html> (quirks mode)")
    if not re.search(r"<meta[^>]+charset\s*=\s*[\"']?utf-8", head):
        where = "missing" if "charset" not in src.lower() else "declared after byte 1024"
        errs.append(f"charset: <meta charset=\"utf-8\"> {where}; opened without a server header, "
                    "the browser guesses the encoding")
    if not re.search(r"<meta[^>]+name\s*=\s*[\"']viewport", src, re.I):
        errs.append("viewport: no <meta name=\"viewport\">; phones render a zoomed-out desktop page")
    bad = [m for m in MOJIBAKE if m in src]
    if bad:
        errs.append(f"mojibake: {', '.join(repr(m) for m in bad)} already in the file "
                    "(UTF-8 text was once decoded as Windows-1252)")

    vis = Visible()
    vis.feed(src)
    visible = "".join(vis.text)
    n_en = visible.count("–")
    if n_en:
        warns.append(f"en-dash: {n_en} in visible text (fine for a range, otherwise reword)")
    if "fonts.googleapis.com" in src:
        warns.append("google-fonts: loads fonts from Google (render-blocking chain; self-host)")
    rel = os.path.relpath(os.path.abspath(path), ROOT)
    if rel.startswith("public" + os.sep) and "/_vercel/insights/script.js" not in src:
        warns.append("analytics: public page without the /_vercel/insights snippet")

    if run_wrap:
        lint = os.path.join(ROOT, "scripts", "artifact_wrap_lint.py")
        if os.path.exists(lint):
            r = subprocess.run([sys.executable, lint, path], capture_output=True, text=True)
            if r.returncode != 0:
                detail = (r.stderr or r.stdout).strip().splitlines()
                errs.append("wrap-lint: " + " | ".join(detail[-4:]))
    return errs, warns


RENDER_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const [files, widths] = [JSON.parse(process.argv[2]), JSON.parse(process.argv[3])];
  const opts = process.env.PW_EXEC ? { executablePath: process.env.PW_EXEC } : {};
  const b = await chromium.launch(opts);
  const out = {};
  for (const f of files) {
    const res = { overflow: {}, lede: null };
    for (const w of widths) {
      const p = await b.newPage({ viewport: { width: w, height: 900 } });
      await p.goto('file://' + f, { waitUntil: 'load' });
      res.overflow[w] = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      if (w === Math.max(...widths)) {
        res.lede = await p.evaluate(() => {
          const h = document.querySelector('h1');
          const l = document.querySelector('.standfirst, .lede, .hero .lede, header p.lede');
          if (!h || !l) return null;
          const lane = h.parentElement.getBoundingClientRect();
          const cs = getComputedStyle(h.parentElement);
          const laneRight = lane.right - parseFloat(cs.paddingRight || 0);
          return { gap: Math.round(laneRight - l.getBoundingClientRect().right) };
        });
      }
      await p.close();
    }
    out[f] = res;
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(String(e)); process.exit(3); });
"""


def node_path():
    paths = [os.path.join(ROOT, "node_modules")]
    try:
        g = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, timeout=20)
        if g.returncode == 0:
            paths.append(g.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        pass
    return [p for p in paths if os.path.isdir(os.path.join(p, "playwright"))]


def render_checks(files):
    if not shutil.which("node"):
        return None, "node not found"
    np = node_path()
    if not np:
        return None, "playwright not installed (repo or global)"
    env = dict(os.environ, NODE_PATH=os.pathsep.join(np))
    with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False) as fh:
        fh.write(RENDER_JS)
        js = fh.name
    try:
        r = subprocess.run(["node", js, json.dumps([os.path.abspath(f) for f in files]),
                            json.dumps(list(WIDTHS))], capture_output=True, text=True, env=env,
                           timeout=300)
    finally:
        os.unlink(js)
    if r.returncode != 0:
        return None, (r.stderr.strip().splitlines() or ["render failed"])[-1]
    return json.loads(r.stdout.strip().splitlines()[-1]), None


def main():
    ap = argparse.ArgumentParser(description="One gate for any standalone HTML page.")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--static", action="store_true", help="skip the headless render checks")
    ap.add_argument("--no-wrap-lint", action="store_true",
                    help="skip artifact_wrap_lint (when a hook already ran it)")
    a = ap.parse_args()

    results = {}
    for f in a.files:
        with open(f, "rb") as fh:
            results[f] = static_checks(f, fh.read(), not a.no_wrap_lint)

    render_skipped = None
    if not a.static:
        data, why = render_checks(a.files)
        if data is None:
            render_skipped = why
        else:
            for f in a.files:
                d = data.get(os.path.abspath(f), {})
                errs, warns = results[f]
                for w, px in sorted(d.get("overflow", {}).items(), key=lambda kv: int(kv[0])):
                    if px > 0:
                        errs.append(f"overflow: {px}px wider than the viewport at {w}px")
                lede = d.get("lede")
                if lede and lede["gap"] > 24:
                    warns.append(f"lede: ends {lede['gap']}px short of the heading's lane at "
                                 f"{max(WIDTHS)}px (fine on an index page, else span the lane)")

    failed = 0
    for f, (errs, warns) in results.items():
        mark = "✖" if errs else "✓"
        print(f"{mark} page-gate: {f}" + (" (static only)" if a.static or render_skipped else ""))
        for e in errs:
            print(f"    ERROR {e}")
        for w in warns:
            print(f"    warn  {w}")
        failed += bool(errs)
    if render_skipped:
        print(f"! render checks SKIPPED: {render_skipped}. Overflow and lede were not verified.",
              file=sys.stderr)
    print(f"page-gate: {len(results) - failed}/{len(results)} pass")
    if failed:
        return 1
    return 2 if render_skipped else 0


if __name__ == "__main__":
    sys.exit(main())
