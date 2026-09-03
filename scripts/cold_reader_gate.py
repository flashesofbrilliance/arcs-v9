#!/usr/bin/env python3
"""cold_reader_gate — the mechanical half of the pre-render legibility gate (ADR-075).

Scores a RENDERED counterpart page (the HTML a cold reader actually sees) against the rules
Ahmed Elsamadisi calibrated on 2026-09-03 after two "hard to follow" strikes, and that Jeben
(re Harry Wilson, Apr 2026) and Robin (Aug 2026) had already named from outside:

  R1 verdict-first     : a one-sentence verdict AND an instance from the reader's world (a quotation, or a
                         figure with a unit) exist above the fold (first ~1200 chars of body text). Amended
                         2026-09-03 after the corpus read: "show me" outnumbered "too dense" 9 to 3.
  R2 first-screen budget: text before the first disclosure/section break <= 250 words
  R3 depth is pulled   : evidence lives behind <details> (or is absent); no more than 1 open figure
                         (table/svg/img) before the first <details>
  R4 one figure per step: no <details> block contains more than one table/svg/img
  R5 read-time stamp   : page declares its read time (e.g. "90 seconds", "N minutes", "Read time")
  R6 no em-dashes      : plain-language rule (WORLD/PRODUCT)
  R7 fold has an action: an imperative/task cue appears above the fold ("pick", "bring", "ask", "do", ...)
  R0 input validity   : the file has readable static text; a script-rendered page (near-empty static body)
                         FAILS with a note to score the rendered DOM instead. Source is not what the reader sees.

Each rule is a grep or a DOM count; no judgment. The judgment half is the cold-reader facet in
counterpart-gauntlet (what / why / do from the first screen only). This script is a TRIPWIRE, not a
verdict (see memory mechanized-frontend-gate-is-tripwire-not-verdict).

Calibration contract (must hold or the gate is wrong, not the pages):
  public/ahmed-ext.html            -> FAIL   (counterpart said "lost", twice)
  public/saul.html                 -> FAIL   (counterpart's live A/B preferred the ChatGPT version)
  the verdict-first re-render      -> PASS   (the acceptance test; Ahmed reads it in < 2 minutes)

Usage: python3 scripts/cold_reader_gate.py <page.html> [...] [--json] [--fold-chars 1200]
Exit 0 if every page passes, 1 if any fails. Stdlib only.
"""
import html as htmlmod, json, re, sys

VERDICT_CUES = re.compile(r"(if (you|i) (read|know) (only )?(one thing|nothing)|the (verdict|short version|one[- ]line|takeaway|bottom line)|in one (line|sentence)|tl;?dr|start here|what you are looking at)", re.I)
ACTION_CUES = re.compile(r"\b(pick|bring|ask|open|read this first|do this|your task|before the call|next step|reply|choose)\b", re.I)
READTIME = re.compile(r"(\b(\d+|one|two|three|four|five|ten|ninety)\s*(seconds?|secs?|minutes?|mins?)\b|read time)", re.I)
FIG = re.compile(r"<(table|svg|img)\b", re.I)
# an INSTANCE above the fold: a quotation, or a figure with a unit/percent/currency, i.e. something from the reader's world
INSTANCE = re.compile(r'("[^"]{12,}"|“[^”]{12,}”|\$\s?\d|\b(\d[\d,]*(\.\d+)?|a million|one million|a thousand)\s?(million|thousand|k\b|m\b|x\b)?\s?(\w+\s)?(%|percent|hours?|days?|weeks?|months?|years?|customers?|deals?|calls?|countries|people|rows?|sites?)\b)', re.I)


def text_of(fragment: str) -> str:
    fragment = re.sub(r"<(script|style)\b.*?</\1>", " ", fragment, flags=re.S | re.I)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", htmlmod.unescape(fragment)).strip()


def score(path: str, fold_chars: int = 1200) -> dict:
    raw = open(path, encoding="utf-8", errors="replace").read()
    body = re.search(r"<body\b[^>]*>(.*)</body>", raw, flags=re.S | re.I)
    body = body.group(1) if body else raw
    body = re.sub(r"<(script|style)\b.*?</\1>", " ", body, flags=re.S | re.I)  # never cut inside a script
    # first screen = everything before the first <details> or the second <h2>/<section>, whichever first
    cut_points = [m.start() for m in re.finditer(r"<details\b", body, flags=re.I)]
    h2s = [m.start() for m in re.finditer(r"<(h2|section)\b", body, flags=re.I)]
    if len(h2s) >= 2:
        cut_points.append(h2s[1])
    first_screen_html = body[: min(cut_points)] if cut_points else body
    first_text = text_of(first_screen_html)
    fold_text = text_of(body)[:fold_chars]
    details = re.findall(r"<details\b.*?</details>", body, flags=re.S | re.I)
    figs_before_details = len(FIG.findall(first_screen_html))
    figs_per_details = [len(FIG.findall(d)) for d in details]
    total_figs = len(FIG.findall(body))
    static_words = len(text_of(body).split())
    script_rendered = static_words < 50 and bool(re.search(r"<script\b", raw, re.I))
    checks = {
        "R0_static_or_rendered_input": not script_rendered,
        "R1_verdict_first": bool(VERDICT_CUES.search(fold_text)) and bool(INSTANCE.search(fold_text)),
        "R2_first_screen_le_250_words": len(first_text.split()) <= 250,
        "R3_depth_pulled": (len(details) > 0 or total_figs <= 1) and figs_before_details <= 1,
        "R4_one_figure_per_step": all(n <= 1 for n in figs_per_details),
        "R5_read_time_stamp": bool(READTIME.search(fold_text)),
        "R6_no_em_dashes": "—" not in raw,
        "R7_fold_has_action": bool(ACTION_CUES.search(fold_text)),
    }
    return {
        "page": path,
        "pass": all(checks.values()),
        "checks": checks,
        "first_screen_words": len(first_text.split()),
        "details_blocks": len(details),
        "figures_total": total_figs,
        "figures_before_first_disclosure": figs_before_details,
        "static_words": static_words,
        "note": ("page is script-rendered; score a saved rendered DOM (browser 'save page' or get_page_text), not the source" if script_rendered else ""),
    }


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    as_json = "--json" in argv
    fold = int(argv[argv.index("--fold-chars") + 1]) if "--fold-chars" in argv else 1200
    if not args:
        sys.stderr.write(__doc__)
        return 2
    results = [score(p, fold) for p in args]
    if as_json:
        print(json.dumps(results, indent=1))
    else:
        for r in results:
            failed = [k for k, v in r["checks"].items() if not v]
            print(f"{'PASS' if r['pass'] else 'FAIL'}  {r['page']}  words@first-screen={r['first_screen_words']} details={r['details_blocks']} figs={r['figures_total']}" + (f"  failed: {', '.join(failed)}" if failed else ""))
            if r.get("note"):
                print(f"       note: {r['note']}")
    return 0 if all(r["pass"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
