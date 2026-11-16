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
  E voice        with --counterpart only: scripts/voice_gate.py (royal "we" in visible text;
                 mark a truly joint we with data-voice="joint")

RENDER checks (headless Chromium via Playwright; skipped with --static):
  E overflow     document wider than the viewport at 375, 790, 1280
  E lede         at 1280 the hero lede's box ends short of its heading's lane (> 24px). The
                 narrow lede is invisible to overflow checks and the static lint's 120px
                 container/measure threshold missed it on 21 NFTT posts (2026-10-04), so it fails.
                 The one sanctioned exception, text INDEX pages that put the lede on the 680px
                 measure (2026-09-29), opts out explicitly: <p class="lede" data-measure="index">.

  W camera       DESIGN.md "The One-Camera Rule": a rotateX other than 0 or 38 degrees, any rotateY, rotateZ or rotate3d,
                 or a camera tilt with no prefers-reduced-motion rule. A vh-based perspective floor plane is allowed.
  E flex-text    a display:flex/inline-flex box with two or more loose text runs interleaved with element
                 children (full matrix: error; quick: warning). Each text run and each element becomes
                 its own flex item, so a mono label such as "BUILD TELEMETRY / DAY 0 / AS OF" breaks into
                 ragged columns at narrow widths (status page era line, 2026-11-12). Wrap the words in one
                 <span>, or make the row a block with inline pieces. data-flex-text="ok" opts one box out.

PDF checks (poppler: pdfinfo, pdffonts, pdftotext; a .pdf argument gets these instead of the above):
  E pdf-pages    at least one page
  E pdf-title    a real document title (not empty, about:blank, or a file name)
  E pdf-tagged   tagged PDF (screen readers and reflow depend on it)
  E pdf-fonts    every font embedded (else the reader's machine substitutes)
  E pdf-emdash   no em-dash in the text (house rule, same as the HTML wrap lint)
  E pdf-mojibake no UTF-8-as-1252 debris in the text
  E pdf-link     every link is https:// or mailto: (no file://, localhost or http://)
  W pdf-colon    a lowercase word after a colon (house style capitalizes a new idea; review by eye)
  Banked 2026-11-06: the Louisville proposal PDF shipped with no gate looking at it at all.

USAGE
  python3 scripts/page_gate.py [--static] [--no-wrap-lint] [--counterpart] FILE.html|FILE.pdf [...]
EXIT
  0 pass (warnings allowed) · 1 at least one error · 2 render checks requested but no browser
Stdlib only; the render step shells out to node + playwright (repo, main checkout or global install).
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
WIDTHS = (375, 790, 1280)  # kept for the lede check (widest) and callers that import it
# Device matrix for the render checks: each is a Playwright context. Intermediate widths are included on
# purpose (790, 1024): the wrap-regression class lives there. isMobile/hasTouch give the real touch paths.
DEVICES = [
    {"name": "reflow-320", "w": 320, "h": 568, "mobile": True, "touch": True, "dsf": 2},  # WCAG 1.4.10 reflow width
    {"name": "phone-375", "w": 375, "h": 667, "mobile": True, "touch": True, "dsf": 2},
    {"name": "phone-390", "w": 390, "h": 844, "mobile": True, "touch": True, "dsf": 3},
    {"name": "android-360", "w": 360, "h": 800, "mobile": True, "touch": True, "dsf": 3},
    {"name": "tablet-768", "w": 768, "h": 1024, "mobile": False, "touch": True, "dsf": 2},
    {"name": "band-790", "w": 790, "h": 900, "mobile": False, "touch": False, "dsf": 1},
    {"name": "laptop-1024", "w": 1024, "h": 768, "mobile": False, "touch": False, "dsf": 1},
    {"name": "desktop-1280", "w": 1280, "h": 800, "mobile": False, "touch": False, "dsf": 1},
    {"name": "wide-1440", "w": 1440, "h": 900, "mobile": False, "touch": False, "dsf": 1},
]
SCHEMES = ("light", "dark")
QUICK_DEVICES = ("phone-375", "band-790", "desktop-1280")  # the original three widths, light scheme only
BROWSERS = {
    "chrome": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "comet": "/Applications/Comet.app/Contents/MacOS/Comet",
}
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


PDF_TOOLS = ("pdfinfo", "pdffonts", "pdftotext")


def pdf_checks(path):
    """Return (errs, warns) for one PDF, or None if poppler is not installed."""
    if not all(shutil.which(t) for t in PDF_TOOLS):
        return None
    errs, warns = [], []
    run = lambda *a: subprocess.run(a, capture_output=True, text=True, errors="replace").stdout
    info = {}
    for line in run("pdfinfo", path).splitlines():
        k, _, v = line.partition(":")
        info[k.strip()] = v.strip()
    pages = int(info.get("Pages", "0") or 0)
    if pages < 1:
        errs.append("pdf-pages: no pages (not a PDF, or it failed to render)")
    title = info.get("Title", "")
    if not title or title.lower() in ("about:blank", "untitled") or re.search(r"\.(html?|pdf)$", title, re.I):
        errs.append(f"pdf-title: missing or placeholder title ({title!r}); set <title> before printing")
    if info.get("Tagged", "no") != "yes":
        errs.append("pdf-tagged: not a tagged PDF (print from Chrome, or export with tags on)")
    rows = run("pdffonts", path).splitlines()[2:]
    loose = sorted({r.split()[0] for r in rows if len(r.split()) >= 7 and r.split()[-5] != "yes"})
    if loose:
        errs.append("pdf-fonts: not embedded: " + ", ".join(loose[:6]))
    text = run("pdftotext", path, "-")
    if "\u2014" in text:
        errs.append(f"pdf-emdash: {text.count(chr(0x2014))} em-dash(es) in the text")
    if re.search(r"Â[·\xa0]|â€", text):
        errs.append("pdf-mojibake: UTF-8 decoded as Windows-1252 in the text")
    for line in run("pdfinfo", "-url", path).splitlines()[1:]:
        parts = line.split()
        url = parts[-1] if parts else ""
        if not (url.startswith("https://") or url.startswith("mailto:")):
            errs.append(f"pdf-link: page {parts[0] if parts else '?'} links to {url} (use https:// or mailto:)")
    lower = sorted(set(re.findall(r": ([a-z][a-z']+)", text)))
    if lower:
        warns.append("pdf-colon: lowercase after a colon: " + ", ".join(lower[:8]))
    return errs, warns


def camera_warnings(text):
    """The One-Camera Rule (DESIGN.md): X tilt only, 38 degrees, flat under reduced motion. Advisory: older pages predate it."""
    import re as _re
    out = []
    for m in _re.finditer(r'transform\s*:\s*([^;}]*)', text):
        v = m.group(1)
        if _re.search(r'perspective\(\s*[\d.]+vh', v):
            continue  # receding floor plane, a ground and not a camera
        for r in _re.finditer(r'rotateX\(\s*(-?[\d.]+)deg', v):
            if abs(float(r.group(1))) not in (0.0, 38.0):
                out.append(f"camera: rotateX({r.group(1)}deg) is not the 38 degree camera (DESIGN.md One-Camera Rule)")
        if _re.search(r'rotate(Y|Z|3d)\(', v) and 'perspective(' in v:
            out.append("camera: yaw, roll or rotate3d in a camera transform (DESIGN.md One-Camera Rule)")
        if _re.search(r'rotateX\(\s*38deg', v) and 'prefers-reduced-motion' not in text:
            out.append("camera: a 38 degree tilt with no prefers-reduced-motion rule that flattens it")
    return sorted(set(out))


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
    warns.extend(camera_warnings(src))
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
const path = require('path');
const fs = require('fs');
const http = require('http');
const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ico': 'image/x-icon', '.txt': 'text/plain' };
function serve(rootDir) {
  // Site pages use root-relative URLs (/fonts/...); over file:// those 404 and change the layout. Serve the web root instead.
  return new Promise(resolve => {
    const srv = http.createServer((req, res) => {
      const u = decodeURIComponent((req.url || '/').split('?')[0]);
      let f = path.join(rootDir, u);
      if (!f.startsWith(rootDir)) { res.writeHead(403); return res.end(); }
      if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
      if (!fs.existsSync(f) && fs.existsSync(f + '.html')) f = f + '.html';
      if (!fs.existsSync(f)) { res.writeHead(404); return res.end('not found'); }
      res.writeHead(200, { 'content-type': MIME[path.extname(f)] || 'application/octet-stream' });
      fs.createReadStream(f).pipe(res);
    });
    srv.listen(0, '127.0.0.1', () => resolve(srv));
  });
}

async function settle(p) {
  // wait until the scroll position stops changing (smooth scroll, script-driven jumps, a busy browser)
  await p.evaluate(() => new Promise(res => {
    let last = -1, stable = 0;
    const tick = () => { if (Math.abs(scrollY - last) < 0.5) stable++; else { stable = 0; last = scrollY; } stable >= 6 ? res() : requestAnimationFrame(tick); };
    setTimeout(res, 2500); tick();
  }));
}

async function snapCheck(p) {
  // Every in-page anchor must land its target below any sticky/fixed chrome and visibly on screen.
  await p.addStyleTag({ content: 'html{scroll-behavior:auto !important}' });
  const hrefs = await p.evaluate(() => [...new Set([...document.querySelectorAll('a[href^="#"]')]
    .map(a => a.getAttribute('href'))
    .filter(h => h.length > 1 && document.getElementById(h.slice(1))))]);
  const bad = [];
  for (const h of hrefs.slice(0, 80)) {
    // disclosure triggers (aria-expanded / aria-haspopup) open something instead of navigating: not anchors to snap
    const link = p.locator('a[href="' + h + '"]:visible:not([aria-expanded]):not([aria-haspopup])').first();
    if (!(await link.count())) continue;
    try { await link.scrollIntoViewIfNeeded({ timeout: 1500 }); await link.click({ timeout: 2000 }); } catch (e) { continue; }
    await settle(p);
    const r = await p.evaluate((id) => {
      const t = document.getElementById(id);
      if (!t) return null;
      const rect = t.getBoundingClientRect();
      if (rect.width === 0 && rect.height === 0) return null;
      let obs = 0;
      for (const e of document.querySelectorAll('body *')) {
        const cs = getComputedStyle(e);
        if ((cs.position === 'sticky' || cs.position === 'fixed') && cs.display !== 'none' && cs.visibility !== 'hidden') {
          const b = e.getBoundingClientRect();
          if (b.width > 0 && b.height > 0 && b.top <= 2 && b.bottom > 0) obs = Math.max(obs, b.bottom);
        }
      }
      const x = Math.min(innerWidth - 2, Math.max(2, rect.left + 12));
      const y = Math.min(innerHeight - 2, Math.max(2, rect.top + 6));
      const el = document.elementFromPoint(x, y);
      const covered = !(el && (t.contains(el) || el.contains(t)));
      return { top: Math.round(rect.top), obs: Math.round(obs), covered, vis: rect.bottom > 0 && rect.top < innerHeight };
    }, h.slice(1));
    if (r && (!r.vis || r.top < r.obs - 2 || r.covered)) bad.push(Object.assign({ href: h }, r));
  }
  return bad;
}

async function axeScan(p) {
  // Open-source axe-core (MPL-2.0) against WCAG 2.0/2.1/2.2 A and AA plus best practice.
  let path;
  try { path = require.resolve('axe-core/axe.min.js'); } catch (e) { return { missing: true, list: [] }; }
  // one retry: a browser can swap the execution context right after load (seen in Comet at 320px)
  for (let attempt = 0; ; attempt++) {
    try {
      await p.waitForLoadState('load');
      await p.addScriptTag({ path });
      const r = await p.evaluate(() => axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] } }));
      return { missing: false, list: r.violations.map(v => ({ id: v.id, impact: v.impact, n: v.nodes.length, help: v.help, target: v.nodes[0].target.join(' ').slice(0, 80) })) };
    } catch (e) {
      if (attempt >= 1 || !/context was destroyed|navigation/i.test(String(e.message || e))) throw e;
      await p.waitForTimeout(400);
    }
  }
}

// Headline clauses that must never wrap mid-phrase (Zach's hero rule): any h1 .hl span, or any element marked
// data-one-line, that renders on more than one line. Measured per device, so a clause that fits at 1280 but splits
// at 375 fails (2026-11-16: the Gravity headline split at ~530px while a single 1060px check passed).
async function oneLine(p) {
  return await p.evaluate(() => {
    const out = [];
    // When a clause's sentences (.hs) stack as blocks (the phone floor), each sentence is the unit. A wrap is allowed
    // only once the headline type sits at its --hl-floor: below that size the text would undercut the body copy.
    const units = [];
    for (const e of document.querySelectorAll('h1 .hl, [data-one-line]')) {
      const hs = [...e.querySelectorAll('.hs')];
      if (hs.length && getComputedStyle(hs[0]).display === 'block') units.push(...hs); else units.push(e);
    }
    for (const e of units) {
      if (!e.offsetParent && getComputedStyle(e).position !== 'fixed') continue;
      const h1 = e.closest('h1');
      const floor = h1 ? parseFloat(getComputedStyle(h1).getPropertyValue('--hl-floor')) : NaN;
      if (floor && parseFloat(getComputedStyle(e).fontSize) <= floor + 0.5) continue;
      const r = document.createRange(); r.selectNodeContents(e);
      const tops = new Set([...r.getClientRects()].filter(x => x.width > 1).map(x => Math.round(x.top)));
      if (tops.size > 1) out.push('"' + e.textContent.trim().slice(0, 48) + '" breaks onto ' + tops.size + ' lines');
    }
    return out;
  });
}

async function flexText(p) {
  return await p.evaluate(() => {
    const out = [];
    for (const e of document.body.querySelectorAll('*')) {
      if (e.closest('svg') || e.getAttribute('data-flex-text') === 'ok') continue;
      const d = getComputedStyle(e).display;
      if (d !== 'flex' && d !== 'inline-flex') continue;
      if (!e.children.length) continue;
      // One loose text run beside an icon or dot is one flex item and wraps as a paragraph. The break needs text
      // INTERLEAVED with elements: two or more loose runs, each its own item (the era line: text, span, text, span, text).
      const runs = [...e.childNodes].filter(n => n.nodeType === 3 && /[A-Za-z]/.test(n.textContent));
      if (runs.length >= 2) {
        const words = runs.map(n => n.textContent.trim()).join(' ').split(/\s+/).slice(0, 5).join(' ');
        out.push(e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/)[0] : '') + ': "' + words + '"');
      }
    }
    return [...new Set(out)].slice(0, 6);
  });
}

async function small(p) {
  return await p.evaluate(() => {
    const out = [];
    for (const e of document.querySelectorAll('button, a[href], input[type=range], [role=button]')) {
      if (e.closest('p, li, dd, td, .tip, .skip')) continue;
      if (e.classList.contains('skip')) continue;
      const b = e.getBoundingClientRect();
      if (b.width === 0 || b.height === 0) continue;
      const cs = getComputedStyle(e);
      if (cs.visibility === 'hidden' || cs.display === 'none') continue;
      if (b.height < 43.5 || b.width < 43.5) out.push(((e.textContent || e.getAttribute('aria-label') || e.tagName).trim().slice(0, 24)) + ' ' + Math.round(b.width) + 'x' + Math.round(b.height));
    }
    return [...new Set(out)].slice(0, 8);
  });
}

(async () => {
  const [files, devices, schemes] = [JSON.parse(process.argv[2]), JSON.parse(process.argv[3]), JSON.parse(process.argv[4])];
  const opts = process.env.PW_EXEC ? { executablePath: process.env.PW_EXEC } : {};
  const b = await chromium.launch(opts);
  const roots = JSON.parse(process.env.PG_ROOTS || '{}');   // {webRoot: true}
  const servers = {};
  const out = {};
  for (const f of files) {
    const res = { overflow: {}, lede: null, snap: [], errors: [], small: {}, custom: [], axe: [], axeMissing: false, flexText: [], oneLine: [] };
    let url = 'file://' + f;
    for (const r of Object.keys(roots)) {
      if (f.startsWith(r + path.sep)) {
        servers[r] = servers[r] || await serve(r);
        url = 'http://127.0.0.1:' + servers[r].address().port + '/' + path.relative(r, f).split(path.sep).join('/');
        break;
      }
    }
    const smokeFile = f.replace(/\.html?$/, '.smoke.cjs');
    const smoke = fs.existsSync(smokeFile) ? require(smokeFile) : null;
    for (const d of devices) {
      for (const scheme of schemes) {
        const ctx = await b.newContext({
          viewport: { width: d.w, height: d.h }, isMobile: d.mobile, hasTouch: d.touch,
          deviceScaleFactor: d.dsf, colorScheme: scheme,
        });
        const p = await ctx.newPage();
        const errs = [];
        p.on('pageerror', e => errs.push('pageerror: ' + String(e.message || e).slice(0, 120)));
        // Platform paths that only exist on the deployed host are expected to 404 here; any other 4xx/5xx is a real missing asset.
        const INFRA = /^\/(_vercel\/|api\/|_next\/data\/)|favicon\.ico$/;
        p.on('response', r => {
          if (r.status() < 400) return;
          let u; try { u = new URL(r.url()); } catch (e) { return; }
          if (u.hostname !== '127.0.0.1' && u.protocol !== 'file:') return;
          if (INFRA.test(u.pathname)) return;
          errs.push('asset: ' + r.status() + ' ' + u.pathname.slice(0, 90));
        });
        p.on('console', m => {
          if (m.type() !== 'error') return;
          const t = m.text();
          if (/Failed to load resource/.test(t)) return;                 // covered by the response listener above
          if (/blocked by CORS policy/.test(t) && /https:\/\//.test(t)) return;  // page calls the production API from a local origin
          errs.push('console: ' + t.slice(0, 120));
        });
        await p.goto(url, { waitUntil: 'load' });
        await p.waitForTimeout(150);
        const key = d.name + '/' + scheme;
        res.overflow[key] = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
        if (d.w === Math.max(...devices.map(x => x.w)) && scheme === 'light') {
          res.lede = await p.evaluate(() => {
            const h = document.querySelector('h1');
            const l = document.querySelector('.standfirst, .lede, .hero .lede, header p.lede');
            if (!h || !l) return null;
            const lane = h.parentElement.getBoundingClientRect();
            const cs = getComputedStyle(h.parentElement);
            const laneRight = lane.right - parseFloat(cs.paddingRight || 0);
            return { gap: Math.round(laneRight - l.getBoundingClientRect().right),
                     index: l.getAttribute('data-measure') === 'index' };
          });
        }
        try {
          const ax = await axeScan(p);
          if (ax.missing) res.axeMissing = true;
          for (const v of ax.list) res.axe.push(Object.assign({ where: key }, v));
        } catch (e) { res.errors.push(key + ' axe threw ' + String(e.message || e).slice(0, 100)); }
        if (scheme === 'light') {
          if (d.touch) res.small[d.name] = await small(p);
          for (const x of await flexText(p)) if (!res.flexText.includes(x)) res.flexText.push(x);
          for (const x of await oneLine(p)) res.oneLine.push(d.name + ': ' + x);
          const sn = await snapCheck(p);
          for (const x of sn) res.snap.push(Object.assign({ device: d.name }, x));
          if (smoke) {
            try {
              const c = await smoke(p, { device: d.name, touch: d.touch, mobile: d.mobile, w: d.w, h: d.h, snap: snapCheck, settle });
              for (const m of (c || [])) res.custom.push(d.name + ': ' + m);
            } catch (e) { res.custom.push(d.name + ': smoke threw ' + String(e.message || e).slice(0, 120)); }
          }
        }
        for (const e of errs) res.errors.push(key + ' ' + e);
        await ctx.close();
      }
    }
    out[f] = res;
  }
  for (const r of Object.keys(servers)) servers[r].close();
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(String(e)); process.exit(3); });
"""


def node_path():
    paths = [os.path.join(ROOT, "node_modules")]
    try:
        common = subprocess.run(["git", "-C", ROOT, "rev-parse", "--git-common-dir"], capture_output=True,
                                text=True, timeout=20).stdout.strip()
        if common:
            main_root = os.path.dirname(os.path.abspath(os.path.join(ROOT, common)))
            paths.append(os.path.join(main_root, "node_modules"))
    except (OSError, subprocess.TimeoutExpired):
        pass
    try:
        g = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, timeout=20)
        if g.returncode == 0:
            paths.append(g.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        pass
    seen, out = set(), []
    for p in paths:
        if p not in seen and os.path.isdir(os.path.join(p, "playwright")):
            seen.add(p)
            out.append(p)
    return out


def render_checks(files, browser=None, matrix="quick"):
    if not shutil.which("node"):
        return None, "node not found"
    candidates = node_path()
    if not candidates:
        return None, "playwright not installed (repo or global)"
    with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False) as fh:
        fh.write(RENDER_JS)
        js = fh.name
    why = "render failed"
    try:
        # Each playwright install expects its own browser build. In a cloud session the repo's
        # copy (after npm ci) has no browser while the global one matches /opt/pw-browsers, so
        # try every install until one launches.
        for np in candidates:
            env = dict(os.environ, NODE_PATH=np, PG_ROOTS=json.dumps({os.path.join(ROOT, "public"): True}))
            exe = os.environ.get("PW_EXEC") or (BROWSERS.get(browser) if browser else None)
            if exe is None and sys.platform == "darwin" and os.path.exists(BROWSERS["chrome"]):
                exe = BROWSERS["chrome"]  # no bundled browser in a worktree: use the installed Chrome
            if exe:
                if not os.path.exists(exe):
                    return None, f"browser not found: {exe}"
                env["PW_EXEC"] = exe
            r = subprocess.run(["node", js, json.dumps([os.path.abspath(f) for f in files]),
                                json.dumps(DEVICES if matrix == "full" else [d for d in DEVICES if d["name"] in QUICK_DEVICES]),
                                json.dumps(list(SCHEMES) if matrix == "full" else ["light"])], capture_output=True, text=True,
                               env=env, timeout=900)
            if r.returncode == 0:
                return json.loads(r.stdout.strip().splitlines()[-1]), None
            why = (r.stderr.strip().splitlines() or ["render failed"])[0]
    finally:
        os.unlink(js)
    return None, why


def main():
    ap = argparse.ArgumentParser(description="One gate for any standalone HTML page.")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--static", action="store_true", help="skip the headless render checks")
    ap.add_argument("--matrix", choices=("quick", "full"), default="quick",
                    help="quick (default): the original 375/790/1280 light sweep, new checks as warnings. "
                         "full: 8 devices x light/dark; anchor-snap and console errors fail the gate")
    ap.add_argument("--browser", choices=sorted(BROWSERS), help="run the render checks in this installed browser (default: Chrome)")
    ap.add_argument("--no-wrap-lint", action="store_true",
                    help="skip artifact_wrap_lint (when a hook already ran it)")
    ap.add_argument("--counterpart", action="store_true",
                    help="the page goes to a counterpart: also fail on the royal we (voice_gate.py)")
    a = ap.parse_args()

    results = {}
    pdfs = [f for f in a.files if f.lower().endswith(".pdf")]
    a.files = [f for f in a.files if f not in pdfs]
    pdf_skipped = None
    for f in pdfs:
        r = pdf_checks(f)
        if r is None:
            pdf_skipped = "poppler (pdfinfo, pdffonts, pdftotext) is not installed: brew install poppler"
            results[f] = ([], ["pdf: checks SKIPPED, " + pdf_skipped])
        else:
            results[f] = r
    for f in a.files:
        with open(f, "rb") as fh:
            results[f] = static_checks(f, fh.read(), not a.no_wrap_lint)
    if a.counterpart:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import voice_gate
        for f in a.files:
            with open(f, encoding="utf-8", errors="replace") as fh:
                for line, word, ctx in voice_gate.scan(f, fh.read()):
                    results[f][0].append(f"voice: royal \"{word}\" at line {line}: {ctx} "
                                         "(write it in I, or mark a joint we data-voice=\"joint\")")
        import token_tuner_inline
        for f in a.files:
            with open(f, encoding="utf-8", errors="replace") as fh:
                if token_tuner_inline.has_tuner(fh.read()):
                    results[f][0].append("tuner: the internal token tuner is in a counterpart page "
                                         "(python3 scripts/token_tuner_inline.py --strip FILE)")

    render_skipped = None
    if not a.static and a.files:
        data, why = render_checks(a.files, a.browser, a.matrix)
        if data is None:
            render_skipped = why
        else:
            for f in a.files:
                d = data.get(os.path.abspath(f), {})
                errs, warns = results[f]
                for key, px in sorted(d.get("overflow", {}).items()):
                    if px > 0:
                        errs.append(f"overflow: {px}px wider than the viewport on {key}")
                strict = a.matrix == "full"
                for x in d.get("snap", [])[:12]:
                    why_ = "off screen" if not x.get("vis") else "covered by sticky chrome"
                    (errs if strict else warns).append(f"anchor-snap: {x['href']} lands at y={x['top']} with {x['obs']}px of sticky chrome ({why_}) on {x['device']}")
                if d.get("axeMissing"):
                    warns.append("a11y: axe-core not found (npm i -D axe-core); the automated WCAG scan was skipped")
                seen_ax = set()
                for v in d.get("axe", []):
                    k = (v["id"], v["target"])
                    if k in seen_ax:
                        continue
                    seen_ax.add(k)
                    line = f"a11y (axe, WCAG): {v['id']} [{v['impact']}] x{v['n']}: {v['help']} | {v['target']} on {v['where']}"
                    (errs if strict and v["impact"] in ("critical", "serious") else warns).append(line)
                for e_ in d.get("errors", [])[:6]:
                    (errs if strict else warns).append("console: " + e_)
                for m_ in d.get("custom", [])[:12]:
                    errs.append("smoke: " + m_)
                for x in d.get("oneLine", [])[:8]:
                    errs.append(f"one-line: {x}; a headline clause must hold its own line at every width (size the type to fit, never wrap mid-phrase)")
                for x in d.get("flexText", []):
                    (errs if strict else warns).append(f"flex-text: {x}: loose words in a flex box become ragged columns; wrap them in one <span> or use a block with inline pieces")
                for dev, items in d.get("small", {}).items():
                    if items:
                        warns.append(f"touch-targets on {dev}: " + "; ".join(items))
                lede = d.get("lede")
                if lede and lede["gap"] > 24 and not lede.get("index"):
                    errs.append(f"lede: ends {lede['gap']}px short of the heading's lane at "
                                f"{max(WIDTHS)}px; span the lane (max-width:none), or on a text "
                                f"index page mark it <p class=\"lede\" data-measure=\"index\">")

    failed = 0
    for f, (errs, warns) in results.items():
        mark = "✖" if errs else "✓"
        kind = " (pdf)" if f.lower().endswith(".pdf") else (" (static only)" if a.static or render_skipped else "")
        print(f"{mark} page-gate: {f}" + kind)
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
    return 2 if (render_skipped or pdf_skipped) else 0


if __name__ == "__main__":
    sys.exit(main())
