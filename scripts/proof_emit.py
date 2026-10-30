#!/usr/bin/env python3
"""proof_emit: render resume.arcs.care/proof (an infinite-zoom proof ledger) from one claims file.

Why (2026-10-30): the resume's deep profile was self-description no reader could check. This page
answers one question instead, "can I trust what he says about himself?", by linking every claim to
the record behind it and marking the ones whose record is private or missing.

Infinite zoom: each level is complete on its own and a tap opens the next in place.
  0  the 5-second card: one sentence and a computed scoreboard
  1  five questions a hiring manager asks, each answered in one line
  2  the claims under each question, with status and date
  3  the record: evidence, dated ledger entries, and the link out
Built on nested <details>, so every level is in the HTML (crawlers, no-JS readers, screen readers).

Sources
  runtime/specs/proof-claims.json      the claims (never edit the outputs by hand)
  _STATE/falsification-ledger.jsonl    ledger entries a claim cites by id
  src/ui-kit/recoil-report/_tokens.css inlined verbatim (token_source_gate)
Outputs
  public/proof.html          served at resume.arcs.care/proof
  public/proof-claims.json   served at resume.arcs.care/proof/claims.json

Usage
  python3 scripts/proof_emit.py           write both
  python3 scripts/proof_emit.py --check   exit 1 if either is stale, or a claim breaks the rules
Stdlib only.
"""
import html, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "runtime/specs/proof-claims.json")
LEDGER = os.path.join(ROOT, "_STATE/falsification-ledger.jsonl")
NFTT = os.path.join(ROOT, "runtime/specs/nftt-published.json")
TOKENS = os.path.join(ROOT, "src/ui-kit/recoil-report/_tokens.css")
OUT_HTML = os.path.join(ROOT, "public/proof.html")
OUT_JSON = os.path.join(ROOT, "public/proof-claims.json")
STATUS_LABEL = {"shown": "shown", "on-request": "on request", "not-yet": "not yet shown"}
GLYPH = {"shown": "\u25b2", "on-request": "\u25c6", "not-yet": "~"}  # kit Y-state glyphs: clarity ridge, locked, tilde

e = lambda s: html.escape(str(s), quote=True)


def problems(d, ledger):
    out = []
    for q in d["questions"]:
        for c in q["claims"]:
            where = f"{q['id']}/{c['id']}"
            if c["status"] not in STATUS_LABEL:
                out.append(f"{where}: unknown status {c['status']!r}")
            if c["status"] == "shown" and not c.get("url"):
                out.append(f"{where}: status shown needs a public url")
            if c["status"] != "shown" and c.get("url"):
                out.append(f"{where}: a url means the record is public; mark it shown")
            for fid in c.get("ledger", []):
                if fid not in ledger:
                    out.append(f"{where}: ledger id {fid} not in falsification ledger")
            if "—" in json.dumps(c, ensure_ascii=False):
                out.append(f"{where}: em-dash")
    return out


def render(d, ledger, tokens):
    claims = [c for q in d["questions"] for c in q["claims"]]
    n = {k: sum(c["status"] == k for c in claims) for k in STATUS_LABEL}
    total = len(claims)

    def pips(cs):
        return "".join(f'<i class="pip {c["status"]}" aria-hidden="true">{GLYPH[c["status"]]}</i>' for c in cs)

    def claim_html(c):
        rec = ""
        for fid in c.get("ledger", []):
            r = {k: (v.replace(" \u2014 ", "; ").replace("\u2014", ", ") if isinstance(v, str) else v) for k, v in ledger[fid].items()}
            rec += (f'<li class="entry"><span class="ref">{e(r["id"])} · {e(r["ts"])}</span>'
                    f'<p><b>Believed:</b> {e(r["claim"])}</p><p><b>Test:</b> {e(r["test"])}</p>'
                    f'<p><b>Found:</b> {e(r["delta"])}</p></li>')
        rec = f'<ol class="entries">{rec}</ol>' if rec else ""
        link = (f'<p class="ref">record: <a href="{e(c["url"])}">{e(c["label"])}</a></p>' if c.get("url")
                else f'<p class="ref">{e(d["statuses"][c["status"]])}</p>')
        return (f'<details class="claim z2" data-status="{e(c["status"])}"><summary>'
                f'<span class="meta"><span class="led {e(c["status"])}">{e(STATUS_LABEL[c["status"]])}</span>'
                f'<span class="date">{e(c["date"])}</span></span>'
                f'<span class="claim-text">{e(c["claim"])}</span>'
                f'</summary><div class="record z3"><p>{e(c["evidence"])}</p>{rec}{link}</div></details>')

    qs = ""
    nq = len(d["questions"])
    for i, q in enumerate(d["questions"], 1):
        qs += (f'<details class="q z1" id="{e(q["id"])}"><summary>'
               f'<span class="meta"><span class="qn">{i:02d} / {nq:02d}</span><span class="pips">{pips(q["claims"])}</span></span>'
               f'<span class="ask">{e(q["ask"])}</span><span class="answer">{e(q["answer"])}</span></summary>'
               f'<div class="claims">{"".join(claim_html(c) for c in q["claims"])}</div></details>')

    lede = (f"Every claim below links to the record behind it. Where the record is private it says so, and "
            f"{'one claim is' if n['not-yet'] == 1 else str(n['not-yet']) + ' claims are'} marked not yet shown.")
    person = {"@context": "https://schema.org", "@type": "ProfilePage", "url": "https://zach.md/proof",
              "dateModified": d["as_of"], "mainEntity": {"@type": "Person", "name": d["subject"],
              "url": d["profile"], "sameAs": d["same_as"]}}
    return TEMPLATE.format(
        jsonld=json.dumps(person, ensure_ascii=False).replace("</", "<\\/"), tokens=tokens, subject=e(d["subject"]), lede=e(lede), total=total, shown=n["shown"],
        onreq=n["on-request"], notyet=n["not-yet"], questions=qs, as_of=e(d["as_of"]),
        profile=e(d["profile"]))


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Proof · {subject}</title>
<meta name="description" content="{lede}">
<link rel="canonical" href="https://zach.md/proof">
<script type="application/ld+json">{jsonld}</script>
<link rel="alternate" type="application/json" href="https://zach.md/proof/claims.json">
<link rel="alternate" type="text/markdown" href="https://zach.md/index.md">
<script defer src="/_vercel/insights/script.js"></script>
<style>
{tokens}
</style>
<style>
/* page layer: tokens above are the kit, verbatim. Zoom levels z0..z3. */
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{ --measure: 720px; --accent: var(--cyan); --fs-meta: 0.8125rem; }}
body {{ background: var(--bg); color: var(--text); font-family: var(--ds-font-sans); font-size: var(--fs-body); line-height: 1.6; }}
main {{ max-width: var(--measure); margin: 0 auto; padding: 56px 16px 72px; }}
a {{ color: var(--accent); text-decoration: none; }}
a:hover, a:focus-visible {{ text-decoration: underline; }}
:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; border-radius: var(--ds-r-xs); }}
.section-label {{ font-family: var(--ds-font-mono); font-size: var(--fs-meta); font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); }}
.ref {{ font-family: var(--ds-font-mono); font-size: var(--fs-meta); letter-spacing: 0.04em; color: var(--dimmed); }}
.led {{ display: inline-flex; align-items: center; gap: 8px; font-family: var(--ds-font-mono); font-size: var(--fs-meta); letter-spacing: 0.1em; text-transform: uppercase; color: var(--dimmed); white-space: nowrap; }}
/* status glyphs from the kit's Y-state vocabulary (src/ui/tokens.ts yWeather; DESIGN.md: the tilde is the honesty marker):
   shown = ▲ clarity ridge, on request = ◆ locked, not yet shown = ~ fog, admitted. Shape carries the state, not color alone. */
.led::before, .pip {{ font-family: var(--ds-font-mono); font-style: normal; line-height: 1; flex: none; }}
.led::before {{ font-size: var(--fs-meta); }}
.led.shown::before {{ content: "▲"; }}
.led.shown::before, .pip.shown {{ color: var(--green); }}
.led.on-request::before {{ content: "◆"; }}
.led.on-request::before, .pip.on-request {{ color: var(--cyan); }}
.led.not-yet::before {{ content: "~"; }}
.led.not-yet::before, .pip.not-yet {{ color: var(--gold); font-weight: 700; }}

/* z0: the 5-second card */
.card {{ border: 1px solid var(--border); border-radius: var(--ds-r-md); background: var(--surface); padding: 32px 24px 28px; text-align: center; }}
h1 {{ font-family: var(--ds-font-mono); font-size: var(--fs-display); font-weight: 700; letter-spacing: -0.01em; line-height: 1.1; margin: 10px 0 14px; }}
.lede {{ font-family: var(--ds-font-display); font-size: var(--fs-headline); line-height: 1.5; max-width: none; }}
.score {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border); }}
.score b {{ display: block; font-family: var(--ds-font-mono); font-size: var(--fs-display); line-height: 1.1; color: var(--text); }}
.score > div {{ display: flex; flex-direction: column; align-items: center; padding: 0 8px; }}
.score > div + div {{ border-left: 1px solid var(--border); }}
.score .led {{ margin-top: 6px; white-space: normal; }}
.hint {{ margin: 28px 0 12px; display: flex; justify-content: space-between; gap: 12px; align-items: baseline; }}
.hint button {{ background: none; border: 0; color: var(--accent); font: inherit; cursor: pointer; }}

/* z1: questions */
details > summary {{ list-style: none; cursor: pointer; }}
details > summary::-webkit-details-marker {{ display: none; }}
.q {{ border-top: 1px solid var(--border); }}
.q:last-of-type {{ border-bottom: 1px solid var(--border); }}
.q > summary {{ display: flex; flex-direction: column; gap: 4px; padding: 18px 0; }}
.meta {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; }}
.q > summary:hover .ask {{ color: var(--accent); }}
.qn {{ font-family: var(--ds-font-mono); font-size: var(--fs-meta); color: var(--muted); }}
.ask {{ font-weight: 600; font-size: var(--fs-headline); line-height: 1.35; transition: color var(--dur-fast, 120ms); }}
.answer {{ color: var(--text-secondary); }}
.pips {{ display: flex; gap: 4px; }}
.pip {{ display: block; font-size: var(--fs-meta); }}
.q[open] > summary .ask {{ color: var(--accent); }}

/* z2: claims */
.claims {{ padding: 0 0 18px; display: flex; flex-direction: column; gap: 8px; }}
.claim {{ border: 1px solid var(--border); border-radius: var(--ds-r-sm); background: var(--surface); }}
.claim > summary {{ display: flex; flex-direction: column; gap: 6px; padding: 14px 16px; }}
.claim > summary:hover {{ background: var(--surface-2); }}
.claim[open] {{ border-color: var(--text-secondary); }}
.date {{ font-family: var(--ds-font-mono); font-size: var(--fs-meta); color: var(--muted); white-space: nowrap; }}

/* z3: the record */
.record {{ padding: 0 16px 16px; display: flex; flex-direction: column; gap: 10px; color: var(--text-secondary); }}
.entries {{ list-style: none; display: flex; flex-direction: column; gap: 10px; }}
.entry {{ border-left: 2px solid var(--gold); padding: 2px 0 2px 12px; }}
.entry b {{ color: var(--text); font-weight: 600; }}

.z1[open] > .claims, .z2[open] > .record {{ animation: zoom-in var(--dur-base, 240ms) var(--ease-out, ease-out); }}
@keyframes zoom-in {{ from {{ opacity: 0; transform: translateY(-4px) scale(0.99); }} to {{ opacity: 1; transform: none; }} }}
@media (prefers-reduced-motion: reduce) {{ .z1[open] > .claims, .z2[open] > .record {{ animation: none; }} }}

@media (max-width: 480px) {{
  .score .led {{ flex-direction: column; gap: 4px; text-align: center; }}
  .hint {{ flex-direction: column; align-items: flex-start; gap: 6px; }}
}}
footer {{ margin-top: 28px; display: flex; flex-wrap: wrap; justify-content: center; gap: 4px 16px; }}
footer a {{ display: inline-block; padding: 14px 4px; min-width: 44px; text-decoration: underline; text-underline-offset: 3px; }}
@media print {{ details > * {{ display: block !important; }} }}
</style>
</head>
<body>
<main>
<section class="card z0" aria-label="Summary">
<p class="ref">Proof ledger · as of {as_of}</p>
<h1 aria-label="{subject}"><span id="name" aria-hidden="true">{subject}</span></h1>
<p class="lede">{lede}</p>
<div class="score" role="list">
<div role="listitem"><b>{shown}</b><span class="led shown">shown</span></div>
<div role="listitem"><b>{onreq}</b><span class="led on-request">on request</span></div>
<div role="listitem"><b>{notyet}</b><span class="led not-yet">not yet shown</span></div>
</div>
</section>
<p class="hint"><span class="ref">{total} claims · tap any line to zoom in</span><button type="button" id="all" class="ref" hidden>open everything</button></p>
{questions}
<footer>
<span class="ref"><a href="https://resume.arcs.care">resume</a></span>
<span class="ref"><a href="{profile}">zach.md</a> (for agents)</span>
<span class="ref"><a href="https://zach.md/proof/claims.json">claims.json</a></span>
</footer>
</main>
<script>
// progressive enhancement only: the page is complete without it
(function () {{
  // the one glitch: the name decrypts from scrambled glyphs, ~600ms, skipped under reduced motion
  var h = document.getElementById('name');
  if (!h || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var real = h.textContent, glyphs = '01#%&*<>/\\|=+', t0 = performance.now(), dur = 600;
  (function tick(now) {{
    var p = Math.min((now - t0) / dur, 1), done = Math.floor(p * real.length), s = '';
    for (var i = 0; i < real.length; i++) s += (i < done || real[i] === ' ') ? real[i] : glyphs[(Math.random() * glyphs.length) | 0];
    h.textContent = s;
    if (p < 1) requestAnimationFrame(tick);
  }})(t0);
}})();
(function () {{
  var b = document.getElementById('all'); if (!b) return; b.hidden = false;
  b.addEventListener('click', function () {{
    var all = document.querySelectorAll('details'), open = [].some.call(all, function (d) {{ return !d.open; }});
    [].forEach.call(all, function (d) {{ d.open = open; }});
    b.textContent = open ? 'close everything' : 'open everything';
  }});
}})();
</script>
</body>
</html>
"""


def main(argv):
    d = json.load(open(SRC, encoding="utf-8"))
    # counts come from their own ledgers, never typed: {nftt_count} {nftt_first} {nftt_last}
    pubs = sorted(v["published_at"][:10] for v in json.load(open(NFTT, encoding="utf-8"))["posts"].values())
    fill = {"nftt_count": str(len(pubs)), "nftt_first": pubs[0], "nftt_last": pubs[-1]}
    for q in d["questions"]:
        for c in q["claims"]:
            for k in ("claim", "evidence", "date"):
                for name, val in fill.items():
                    c[k] = c[k].replace("{" + name + "}", val)
    ledger = {}
    for line in open(LEDGER, encoding="utf-8"):
        if line.strip():
            r = json.loads(line); ledger[r["id"]] = r
    bad = problems(d, ledger)
    if bad:
        print("proof_emit: claims break the rules:\n  " + "\n  ".join(bad)); return 1
    tokens = open(TOKENS, encoding="utf-8").read().rstrip()
    page = render(d, ledger, tokens)
    data = dict(d)
    data["claims_total"] = sum(len(q["claims"]) for q in d["questions"])
    for q in data["questions"]:
        for c in q["claims"]:
            for fid in c.get("ledger", []):
                c.setdefault("ledger_entries", []).append({k: ledger[fid][k] for k in ("id", "ts", "claim", "test", "delta")})
    js = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if "--check" in argv:
        stale = [p for p, want in ((OUT_HTML, page), (OUT_JSON, js))
                 if not os.path.exists(p) or open(p, encoding="utf-8").read() != want]
        if stale:
            print("proof_emit: stale, run python3 scripts/proof_emit.py: " + ", ".join(os.path.relpath(p, ROOT) for p in stale)); return 1
        print(f"proof_emit: current ({data['claims_total']} claims)"); return 0
    open(OUT_HTML, "w", encoding="utf-8").write(page)
    open(OUT_JSON, "w", encoding="utf-8").write(js)
    print(f"proof_emit: wrote {os.path.relpath(OUT_HTML, ROOT)} and {os.path.relpath(OUT_JSON, ROOT)} ({data['claims_total']} claims)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
