#!/usr/bin/env python3
"""
chronicle_render.py — render the Chronicle (Reading Room tenant #3, "Drishti") from
runtime/specs/chronicle-books.json into the self-contained _ARTIFACTS/atlas/chronicle.html.

Five books (the time axis) x five fathoms (the depth axis, _SPECS/profile-scan-spec-v1.md "Five
Fathoms"), each book closed by a Shavasana (Operator 25, runtime/specs/operator-25-shavasana-v0.md).

What is authored vs computed (the rule this script enforces on itself):
  authored  (the JSON): prose at fathoms 1-3, the surgical claim list, the Shavasana written half.
  computed  (git + ledger, at render time): every fathom-4 count and the Shavasana mechanical half.
  canon     (_CANON/tao-proverbs.jsonl): epigraph TEXT, looked up by id; the JSON stores the id only.

Hard failures (exit 1): a boundary sha that does not resolve or is not an ancestor of the next
boundary, an epigraph id missing from canon, an em-dash in any authored string.

Usage:
  python3 scripts/chronicle_render.py            # render
  python3 scripts/chronicle_render.py --check    # exit 1 if the committed render is stale
  python3 scripts/chronicle_render.py --self-test
Stdlib only. Local, deterministic, zero-delegation (same seam as concordance_render.py).
"""
from __future__ import annotations

import argparse
import html
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "runtime" / "specs" / "chronicle-books.json"
OUT = ROOT / "_ARTIFACTS" / "atlas" / "chronicle.html"
TAO = ROOT / "_CANON" / "tao-proverbs.jsonl"
TOKENS = ROOT / "src" / "ui-kit" / "recoil-report" / "_tokens.css"
FLEDGER = ROOT / "_STATE" / "falsification-ledger.jsonl"
EM = "—"


def _shav():
    """Reuse Operator 25's marker definitions so the Chronicle and the handoff read breath the same way."""
    spec = importlib.util.spec_from_file_location("shavasana_handoff", ROOT / "scripts" / "shavasana_handoff.py")
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def git(*a: str) -> str:
    r = subprocess.run(["git", *a], capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        raise SystemExit(f"chronicle: git {' '.join(a)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def resolve(sha: str) -> tuple[str, str]:
    full = git("rev-parse", "--verify", f"{sha}^{{commit}}")
    return full[:8], git("log", "-1", "--format=%ad", "--date=short", full)


def book_commits(open_: str, close: str, root: bool) -> list[str]:
    rng = [f"{open_}..{close}"] + ([open_] if root else [])
    out: list[str] = []
    for r in rng:
        out += [l for l in git("log", "--format=%h\t%ad\t%s", "--date=short", *([r] if ".." in r else ["-1", r])).splitlines() if l]
    return out


def tactical(open_: str, close: str, root: bool, d0: str, d1: str, shav) -> dict:
    rows = book_commits(open_, close, root)
    subjects = [r.split("\t", 2)[2] for r in rows]
    merges = sum(1 for s in subjects if s.startswith("Merge pull request"))
    adr_args = ["log", "--diff-filter=A", "--name-only", "--format=", f"{open_}..{close}", "--", "_DECISIONS/ADR-*.md"]
    adrs = len({l for l in git(*adr_args).splitlines() if l})
    frows = 0
    if FLEDGER.exists():
        for l in FLEDGER.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(l)
            except Exception:
                continue
            if r.get("verdict") == "FALSIFIED" and d0 <= str(r.get("ts", ""))[:10] <= d1:
                frows += 1
    blob = "\n".join(subjects)
    dissent = len(shav.DISSENT_RE.findall(blob)) + frows
    agree = len(shav.AGREE_RE.findall(blob)) + merges
    ratio = round(agree / (dissent + 1), 2)
    verdict = ("SILENT: no agreement or dissent markers to weigh" if (agree == 0 and dissent == 0)
               else "RETURN: agreement with no dissent on record" if (agree >= 5 and dissent == 0)
               else "THIN: high agreement, little dissent" if ratio > 4 else "OK: dissent present")
    if rows and not dissent:
        balance = "manifesto (exhale, no inhale)"
    elif not rows and dissent:
        balance = "mirror (inhale, no exhale)"
    else:
        balance = "breathing (both directions)"
    return {"commits": len(rows), "merges": merges, "adrs_added": adrs, "falsified": frows,
            "dissent": dissent, "agree": agree, "ratio": ratio, "verdict": verdict, "balance": balance}


def tao_index() -> dict[str, str]:
    idx = {}
    for l in TAO.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(l)
            idx[r["id"]] = r["text"]
        except Exception:
            pass
    return idx


def walk_strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from walk_strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk_strings(v)


def build(src: dict) -> dict:
    """Validate + compute. Returns the render model; raises SystemExit on a hard failure."""
    bad = [s for s in walk_strings(src) if EM in s]
    if bad:
        raise SystemExit(f"chronicle: em-dash in authored text: {bad[0][:80]!r}")
    tao = tao_index()
    shav = _shav()
    books = []
    prev_close = None
    for b in src["books"]:
        o_sha, o_date = resolve(b["open"])
        c_sha, c_date = resolve(b["close"])
        if subprocess.run(["git", "merge-base", "--is-ancestor", o_sha, c_sha], cwd=ROOT).returncode:
            raise SystemExit(f"chronicle: {b['name']} open {o_sha} is not an ancestor of close {c_sha}")
        if prev_close and prev_close != o_sha:
            raise SystemExit(f"chronicle: {b['name']} opens at {o_sha} but the previous book closed at {prev_close}")
        prev_close = c_sha
        ep = b.get("epigraph")
        if ep and ep not in tao:
            raise SystemExit(f"chronicle: epigraph {ep} not in {TAO.relative_to(ROOT)}")
        m = dict(b, open_sha=o_sha, open_date=o_date, close_sha=c_sha, close_date=c_date,
                 epigraph_text=tao.get(ep) if ep else None,
                 t=tactical(o_sha, c_sha, b["n"] == 1, o_date, c_date, shav))
        books.append(m)
    return {"title": src["title"], "subtitle": src["subtitle"], "fathoms": src["fathoms"],
            "unreached": src.get("unreached", []), "books": books,
            "head": resolve(src["books"][-1]["close"])[0]}


E = html.escape


def sentence(s: str) -> str:
    """Display-only sentence case for canon text stored lowercase; the canon row is never rewritten."""
    import re
    return re.sub(r"(^|[.?!]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), s.strip())


def render_book(b: dict, fathoms: list) -> str:
    alt = {f["n"]: f["altitude"] for f in fathoms}
    res = {f["n"]: f["resolution"] for f in fathoms}
    t = b["t"]
    written = b.get("status") == "written"
    ep = (f'<blockquote class="ep"><p>{E(sentence(b["epigraph_text"]))}</p><cite>{E(b["epigraph"])} · _CANON/tao-proverbs.jsonl</cite></blockquote>'
          if b.get("epigraph_text") else
          '')  # no canon proverb chosen: render nothing (never coin one here; mints go through /tao-mint)
    head = (f'<header class="bh"><div class="eyebrow">Book {["I","II","III","IV","V"][b["n"]-1]} · {E(b["chakra"])} ({E(b["chakra_gloss"])})</div>'
            f'<h2>{E(b["name"])}</h2><div class="theme">{E(b["theme"])}</div>'
            f'<div class="span"><code>{b["open_sha"]}</code> {b["open_date"]} to <code>{b["close_sha"]}</code> {b["close_date"]} · cut: {E(b["cut"])}</div></header>')
    if written:
        f1 = f'<p class="exec">{E(b["executive"])}</p>'
        st = b["strategic"]
        f2 = ('<dl class="turn">'
              f'<div><dt>Left behind</dt><dd>{E(st["left"])}</dd></div>'
              f'<div><dt>Taken up</dt><dd>{E(st["taken"])}</dd></div>'
              f'<div class="seam"><dt>The seam</dt><dd>{E(st["seam"])}</dd></div></dl>')
        lead = ' class="lead"'
        f3 = "".join(f'<p{lead if i == 0 else ""}>{E(p)}</p>' for i, p in enumerate(b["operational"]))
        f5 = "".join(
            f'<li class="{"ok" if c["proven"] else "seam"}"><span class="tag">{"proven" if c["proven"] else "unproven"}</span> {E(c["text"])} <code>{E(c["ref"])}</code></li>'
            for c in b["claims"])
        f5 = f'<ul class="claims">{f5}</ul>'
    else:
        seam = lambda what: f'<p class="seam-note">Not yet written: {what}. The counts at 100 ft are already live.</p>'
        f1, f2, f3 = seam("the view from 30,000 ft"), seam("what was left behind and what was taken up"), seam("the story")
        f5 = '<ul class="claims"><li class="seam"><span class="tag">unproven</span> No claims authored yet.</li></ul>'
    f4 = ('<dl class="stats">'
          f'<div><dt>commits</dt><dd>{t["commits"]}</dd></div>'
          f'<div><dt>PR merges</dt><dd>{t["merges"]}</dd></div>'
          f'<div><dt>ADRs added</dt><dd>{t["adrs_added"]}</dd></div>'
          f'<div><dt>falsified</dt><dd>{t["falsified"]}</dd></div>'
          '</dl><p class="src">Computed at render from <code>git log</code> over the range and <code>_STATE/falsification-ledger.jsonl</code> by date.</p>')
    sh = b.get("shavasana") or {}
    shav = (f'<section class="shav" data-depth="1"><div class="eyebrow">Shavasana · Operator 25</div><ul>'
            f'<li><b>Exhale</b> {t["commits"]} commits, {t["merges"]} pull-request merges.</li>'
            f'<li><b>Inhale</b> {t["falsified"]} falsification rows, {t["dissent"] - t["falsified"]} dissent markers in commit subjects.</li>'
            f'<li><b>Breath balance</b> {E(t["balance"])}.</li>'
            f'<li><b>Sycophancy check</b> agreement {t["agree"]} / dissent {t["dissent"]} (ratio {t["ratio"]}) : {E(t["verdict"])}.</li>'
            f'<li><b>Attachment release</b> {E(sh.get("release", "pending: the book is unwritten, so nothing is held yet."))}</li>'
            f'<li><b>Somatic read</b> {E(sh.get("somatic", "pending"))} <span class="tag">somatic: pending Zach</span></li>'
            f'<li><b>Disposition</b> {E(sh.get("disposition", "pending"))}</li>'
            '</ul><p class="src">This block asserts nothing new. The first four lines are computed; the last three are the written half.</p></section>')
    layers = "".join(f'<section class="f" data-depth="{n}"><div class="flab">{alt[n]} · {res[n]} · {name}</div>{body}</section>'
                     for n, name, body in [(1, "Executive", f1), (2, "Strategic", ep + f2), (3, "Operational", f3),
                                           (4, "Tactical", f4), (5, "Surgical", f5)] if body)
    return f'<article class="book" id="{b["id"]}" data-status="{E(b.get("status", ""))}">{head}{layers}{shav}</article>'


CSS = """
:root{--text-2:#94a3b8;--serif:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif;--sans:'Inter',system-ui,-apple-system,sans-serif;--mono:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--serif);font-size:1.15rem;line-height:1.65}
.wrap{max-width:calc(var(--measure) + 48px);margin:0 auto;padding:32px 16px 96px}
p,li,blockquote{max-width:var(--measure);text-wrap:pretty;overflow-wrap:anywhere}
h1,h2{font-family:var(--serif);font-weight:500;text-wrap:balance;margin:0;font-size:clamp(1.5rem, 4vw, 2.4rem);line-height:1.2}
code{font-family:var(--mono);font-size:.925rem;color:var(--gold);white-space:nowrap}
.eyebrow,.flab,.theme,.span,.tag,.src,.byline,.tl,.fbar{font-family:var(--mono);font-size:.925rem;max-width:none;text-wrap:balance}
.eyebrow{color:var(--cyan)}
.lede{max-width:none;font-style:italic}
.byline,.src,.theme,.span,.flab{color:var(--text-2)}
.fbar{position:sticky;top:0;z-index:2;background:var(--bg);border-bottom:1px solid var(--border);padding:10px 0;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.fbar button{font:inherit;background:transparent;color:var(--text-2);border:1px solid var(--border);border-radius:3px;padding:6px 10px;cursor:pointer;white-space:nowrap}
.fbar button:focus-visible{outline:1px solid var(--cyan);outline-offset:-1px}
.fbar button[aria-pressed=true]{color:var(--cyan);border-color:var(--cyan)}
.fbar button{flex:1 1 0;min-width:118px;text-align:left;white-space:normal}
.fbar button b{display:block;font-weight:700}
.fbar button small{display:block;font-size:.925rem}
body[data-fathom="1"] .f{font-family:var(--mono);letter-spacing:.04em;font-weight:400}
body[data-fathom="2"] .f{letter-spacing:.02em}
body[data-fathom="5"] .f{letter-spacing:-.01em}
.tl{display:flex;flex-wrap:wrap;gap:6px;margin:16px 0 8px}
.tl a{flex:1 1 130px;text-decoration:none;color:var(--text);background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:8px}
.tl small{display:block;color:var(--text-2);font-size:.925rem;white-space:nowrap}
.tl .gone{flex:1 1 130px;color:var(--text-2);border:1px dashed var(--border);border-radius:6px;padding:8px}
.book{border-top:1px solid var(--border);margin-top:48px;padding-top:24px}
.f{margin-top:22px}
.flab{margin-bottom:6px}
.lead::first-letter{color:var(--cyan)}
.ep{margin:0 0 14px;border-left:2px solid var(--cyan);padding:4px 0 4px 14px}
.ep p{margin:0;font-style:italic}
.ep cite{display:block;font-family:var(--mono);font-size:.925rem;color:var(--text-2);font-style:normal;margin-top:4px}
.seam,.seam-note{color:var(--gold)}
.ep.seam{border-left-color:var(--gold)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin:0}
.stats div{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:8px 10px}
.stats dt{font-family:var(--mono);font-size:.925rem;color:var(--text-2)}
.stats dd{margin:0;font-family:var(--mono);font-size:1.15rem;color:var(--cyan);white-space:nowrap}
.claims{list-style:none;padding:0;margin:0}
.claims li{padding:6px 0;border-bottom:1px solid var(--border)}
.claims li code{white-space:normal;overflow-wrap:anywhere}
.tag{border:1px solid var(--border);border-radius:3px;padding:1px 5px;white-space:nowrap}
.ok .tag{color:var(--green)}
.seam .tag{color:var(--gold)}
.shav{margin-top:28px;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px 18px}
.shav ul{padding-left:18px;margin:8px 0}
.shav li{margin:4px 0;max-width:none}
.shav p.src{max-width:none}
.unreached{margin-top:48px;border-top:1px dashed var(--border);padding-top:20px;color:var(--text-2)}
.unreached p{max-width:none}
body[data-fathom="1"] .f:not([data-depth="1"]),body[data-fathom="2"] .f:not([data-depth="2"]),body[data-fathom="3"] .f:not([data-depth="3"]),body[data-fathom="4"] .f:not([data-depth="4"]),body[data-fathom="5"] .f:not([data-depth="5"]){display:none}
.turn{display:grid;gap:8px;margin:0}
.turn div{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:10px 14px}
.turn dt{font-family:var(--mono);font-size:.925rem;color:var(--text-2)}
.turn .seam dt{color:var(--gold)}
.turn dd{margin:4px 0 0}
"""

JS = """
(function(){var b=document.body,btns=document.querySelectorAll('[data-fathom-btn]');
function set(n){b.setAttribute('data-fathom',n);btns.forEach(function(x){x.setAttribute('aria-pressed',String(x.getAttribute('data-fathom-btn')===String(n)))});
try{localStorage.setItem('chronicle-fathom',n)}catch(e){}}
btns.forEach(function(x){x.addEventListener('click',function(){set(x.getAttribute('data-fathom-btn'))})});
var s=null;try{s=localStorage.getItem('chronicle-fathom')}catch(e){}set(s||'3');})();
"""


def render(model: dict) -> str:
    tokens = TOKENS.read_text(encoding="utf-8")
    fbar = "".join(f'<button type="button" data-fathom-btn="{f["n"]}" aria-pressed="false"><b>{E(f["altitude"])}</b><small>{E(f["resolution"])}</small><small>{E(f["name"])}</small></button>' for f in model["fathoms"])
    tl = "".join(f'<a href="#{b["id"]}" data-status="{b.get("status","")}">{E(b["name"])}<small>{b["open_date"]}</small><small>{b["t"]["commits"]} commits</small></a>' for b in model["books"])
    tl += "".join(f'<span class="gone" title="{E(u["why"])}">{E(u["chakra"])}<small>not yet reached</small></span>' for u in model["unreached"])
    un = "".join(f'<p><b>{E(u["chakra"])}</b> ({E(u["gloss"])}): {E(u["why"])}.</p>' for u in model["unreached"])
    body = "".join(render_book(b, model["fathoms"]) for b in model["books"])
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ARCS Chronicle</title><meta name="robots" content="noindex, nofollow">
<style>
{tokens}
:root{{--measure:640px}}
{CSS}
</style></head>
<body data-fathom="3"><div class="wrap">
<div class="eyebrow">Reading Room · Chronicle · how did we get here?</div>
<h1>{E(model["title"])}: {E(model["subtitle"])}</h1>
<p class="lede">Five books from Day 0 to now. Start at 30,000 feet, where each book is a single coarse line, and descend to the ground, where every claim sits beside the commit that proves it. Each book closes with a Shavasana, a pause that adds no claim.</p>
<div class="byline">rendered from <code>runtime/specs/chronicle-books.json</code> at main <code>{model["head"]}</code> · counts computed from git · proverbs from <code>_CANON/tao-proverbs.jsonl</code></div>
<nav class="fbar" aria-label="Descend">{fbar}</nav>
<nav class="tl" aria-label="Books">{tl}</nav>
{body}
<section class="unreached"><div class="eyebrow">Not yet reached</div>{un}</section>
</div><script>{JS}</script></body></html>
"""


def self_test() -> int:
    ok = True
    def check(label, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + label)
        ok = ok and cond
    src = json.loads(SRC.read_text(encoding="utf-8"))
    model = build(src)
    out = render(model)
    check("five books", len(model["books"]) == 5)
    check("genesis holds root + close (2 commits)", model["books"][0]["t"]["commits"] == 2)
    check("genesis epigraph resolves from canon", bool(model["books"][0]["epigraph_text"]))
    check("no em-dash in visible render", EM not in out.split("</style>", 1)[1])
    check("token sentinel inlined", "/* ARCS Recoil Report" in out)
    check("five fathom buttons", out.count("data-fathom-btn=") == 5)
    bad = json.loads(json.dumps(src)); bad["books"][0]["executive"] += " " + EM
    try:
        build(bad); check("em-dash in source fails", False)
    except SystemExit:
        check("em-dash in source fails", True)
    bad = json.loads(json.dumps(src)); bad["books"][0]["epigraph"] = "tao-999999"
    try:
        build(bad); check("unknown epigraph fails", False)
    except SystemExit:
        check("unknown epigraph fails", True)
    bad = json.loads(json.dumps(src)); bad["books"][1]["open"] = bad["books"][2]["open"]
    try:
        build(bad); check("non-contiguous boundary fails", False)
    except SystemExit:
        check("non-contiguous boundary fails", True)
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    out = render(build(json.loads(SRC.read_text(encoding="utf-8"))))
    if a.check:
        cur = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if cur != out:
            print(f"chronicle: {OUT.relative_to(ROOT)} is stale; run python3 scripts/chronicle_render.py")
            return 1
        print("chronicle: render current")
        return 0
    OUT.write_text(out, encoding="utf-8")
    print(f"chronicle: wrote {OUT.relative_to(ROOT)} ({len(out)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
