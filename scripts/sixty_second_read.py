#!/usr/bin/env python3
"""sixty_second_read.py — mechanical operator beats for the sixty-second-read skill.

The read is the SEED (witness 2026-08-29, germination-chain thesis): a four-beat
counterpart artifact (bet -> outcome -> spark -> move) with math-on-pull, whose envelope
IS the seed schema. Every longer form (NFTT post, atlas entry) is a condition-gated
RESYNTHESIS committed against the same SSOT via the Yoav Protocol — never re-derived,
never contradicting. This script holds every beat that is mechanically scorable
(AGENTS.md gotcha 11); agent judgment (cold inference, spark detection, synthesis
prose) lives in the skill, upstream of the seed JSON this consumes.

Subcommands (each prints an operator_client-shaped envelope to stdout, JSON):
    validate  <seed.json>              structural check against the seed schema
    gate      <seed.json>              temporal/provenance/plain-english gate (blocking)
    settle    <seed.json> [--pipe-evaluator] [--source REF=PATH ...]
                                       score the bet vs the outcome; emit a receipt dict;
                                       optionally pipe it through operators/receipt_evaluator.py.
                                       With --source mappings, runs the speaker-provenance
                                       lambda (scripts/attribution_provenance_lint.py — the
                                       ventriloquy paternity test, ADR-033 speaker coordinate):
                                       CONTAMINATED/UNSOURCED halts and writes the upstream
                                       resolution receipt.
    ripeness  <seed.json> --context <ctx.json>
                                       mechanical range-check of the context vector against the
                                       seed's germination axes (universal axes, per-seed ranges).
    render    <seed.json> <out.html>   deterministic HTML render (golden-reference template);
                                       run scripts/artifact_wrap_lint.py on the output after
    commit    <seed.json> --tier read|post|atlas [--log <path>] [--context <ctx.json>]
                                       serialize this tier through YoavStore. Tiers past `read`
                                       are SPROUTS: they require --context and a RIPE germination
                                       check; the decision (sprouted/refused) is appended to
                                       _SEEDS/ledger.jsonl with the conditions_present snapshot —
                                       a refusal without a receipt violates every-gate-a-detector.
                                       A commit that FAILS to serialize is never discarded: it
                                       writes an upstream resolution receipt next to the seed and
                                       exits 3 (bidirectional rule; ADR-051/052).

Envelope contract (stdout, matches operators/operator_client.py):
    {"operator": "SIXTY_READ", "mode": "api", "status": "ok|error|blocked", "exit_code": N,
     "raw": {...}, "envelope": {"operator", "version", "stage", "gate_status", "verdict",
                                 "findings": [...], "next_action", "operator_specific": {...}}}

Stdlib only. exit 0 = ok · 1 = error · 2 = gate fail · 3 = quarantined (resolution receipt written).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from string import Template

VERSION = "v1.0"
HERE = Path(__file__).resolve().parent
REPO = HERE.parent

SEED_STATES = ("dormant", "sprouted", "grown")
BEATS = ("bet", "outcome", "spark", "move")
TIERS = ("read", "post", "atlas")

# Germination: UNIVERSAL AXES, per-seed RANGES (witness 2026-08-29, second entry).
# The dimensions are objective and shared by every seed; only the ranges are per-seed
# and EARNED from settled outcomes, never decreed (mark ranges_provenance accordingly).
# moisture=attention/bandwidth · temperature=Kairos/timing · oxygen=live demand (an open
# question the seed answers) · light=exposure regime (some seeds REQUIRE dark =
# internal-first; some require light = public) · medium=substrate/provenance density.
# stratification=required dormancy; requires_gauntlet = serotiny (opens only under fire).
GERMINATION_AXES = ("moisture", "temperature", "oxygen", "light", "medium")
LEDGER_PATH = REPO / "_SEEDS" / "ledger.jsonl"

# Plain-English surface rule: no ARCS jargon in anything the counterpart reads.
# Mechanical lexicon (case-insensitive, word-ish match); math rows included on purpose.
JARGON = (
    "manifold", "kairos", "dewy", "nci", "notomation", "y-gate", "ygate",
    "superionic", "hyperstition", "ex-ante", "credence", "orthogonal",
    "serializ", "tributar", "recoil report", "coherence",
)
MDASH = ("—", "&mdash;", "&#8212;", "&#x2014;")
# The known menu tells (Ahmed hardening pass, PR #181): the move is ONE ask, never a menu.
MENU_TELLS = ("<ul", "<ol", "<li", "also happy to", "or i can also", "a few options")


# ── helpers ──────────────────────────────────────────────────────────────────

def _emit(stage, status, raw, envelope_extra=None, exit_code=0):
    env = {
        "operator": "SIXTY_READ",
        "version": VERSION,
        "stage": stage,
        "operator_specific": raw,
    }
    if envelope_extra:
        env.update(envelope_extra)
    print(json.dumps({
        "operator": "SIXTY_READ", "mode": "api", "status": status,
        "exit_code": exit_code, "raw": raw, "envelope": env,
    }, indent=2, default=str))
    return exit_code


def _load_seed(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"seed not found: {p}")
    with open(p, encoding="utf-8") as fh:
        seed = json.load(fh)
    if not isinstance(seed, dict):
        raise ValueError("seed must be a JSON object")
    return seed


def _walk_strings(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk_strings(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_strings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


# ── validate ─────────────────────────────────────────────────────────────────

def validate_seed(seed):
    """Structural findings; [] = valid. The contract is scripts/sixty-read.schema.json."""
    f = []
    for key in ("seed_id", "seed_state", "counterpart", "provenance", "beats"):
        if key not in seed:
            f.append(f"missing required key: {key}")
    if seed.get("seed_state") not in SEED_STATES:
        f.append(f"seed_state must be one of {SEED_STATES}, got {seed.get('seed_state')!r}")
    beats = seed.get("beats", {})
    for b in BEATS:
        if b not in beats:
            f.append(f"missing beat: {b} (the envelope is exactly bet -> outcome -> spark -> move)")
    extra = set(beats) - set(BEATS)
    if extra:
        f.append(f"unknown beats {sorted(extra)} — four beats only, no fifth")
    for b in ("bet", "outcome"):
        cards = beats.get(b, {}).get("cards")
        if not isinstance(cards, list) or not cards:
            f.append(f"beats.{b}.cards must be a non-empty list")
        else:
            for i, c in enumerate(cards):
                for k in ("label", "head", "body_html", "source_ref"):
                    if not c.get(k):
                        f.append(f"beats.{b}.cards[{i}].{k} missing/empty")
    spark = beats.get("spark", {})
    for k in ("quote", "source_ref", "body_html"):
        if not spark.get(k):
            f.append(f"beats.spark.{k} missing — the spark is a distinct, evidence-anchored beat "
                     "(the ignition moment; ADR-053), not a mood")
    if not beats.get("move", {}).get("panel_html"):
        f.append("beats.move.panel_html missing")
    srcs = seed.get("provenance", {}).get("sources")
    if not isinstance(srcs, list) or not srcs:
        f.append("provenance.sources must be a non-empty list")
    if "future_vector" in seed and not isinstance(seed["future_vector"], list):
        f.append("future_vector must be a list of dormant longer forms")
    return f


# ── gate ─────────────────────────────────────────────────────────────────────

def gate_seed(seed):
    """Temporal + provenance + plain-english + single-ask findings; [] = pass."""
    f = list(validate_seed(seed))
    beats = seed.get("beats", {})
    srcs = {s.get("ref"): s for s in seed.get("provenance", {}).get("sources", []) if isinstance(s, dict)}

    # provenance: every source_ref must resolve to a source with a non-empty `verified`
    def check_ref(where, ref):
        if ref not in srcs:
            f.append(f"{where}: source_ref {ref!r} does not resolve to provenance.sources")
        elif not srcs[ref].get("verified"):
            f.append(f"{where}: source {ref!r} has no `verified` note — a quote needs a source "
                     "actually read, not a memory jog")
    for b in ("bet", "outcome"):
        for i, c in enumerate(beats.get(b, {}).get("cards", []) or []):
            if c.get("source_ref"):
                check_ref(f"beats.{b}.cards[{i}]", c["source_ref"])
    if beats.get("spark", {}).get("source_ref"):
        check_ref("beats.spark", beats["spark"]["source_ref"])

    # temporal: the bet must be filed no later than the outcome it is scored against
    filed, dated = beats.get("bet", {}).get("filed"), beats.get("outcome", {}).get("date")
    if filed and dated and str(filed) > str(dated):
        f.append(f"temporal gate: bet.filed ({filed}) is after outcome.date ({dated}) — "
                 "a bet filed after the fact is reconstruction, not witness")

    # single ask: the move is one move, not a menu
    panel = (beats.get("move", {}).get("panel_html") or "").lower()
    for tell in MENU_TELLS:
        if tell in panel:
            f.append(f"single-ask gate: move panel contains menu tell {tell!r}")

    # plain-english surface: no em-dashes, no ARCS jargon in any string the counterpart reads
    surface = {k: seed.get(k) for k in ("hero", "beats", "math", "who") if k in seed}
    for path, s in _walk_strings(surface):
        low = s.lower()
        if any(m in s for m in MDASH):
            f.append(f"{path}: em-dash in surface copy")
        for j in JARGON:
            if re.search(r"(?<![a-z0-9])" + re.escape(j), low):
                f.append(f"{path}: ARCS jargon {j!r} on the surface — translate to plain english")
    return f


# ── settle ───────────────────────────────────────────────────────────────────

def settle_seed(seed, pipe_evaluator=False, sources=None, seed_path=None):
    """Score the bet vs the outcome from math.rows; build a receipt for the KINTSUGI gate.
    FATED maps 1:1 onto the beats; somatic/axioms are NEVER fabricated (upstream signal gap)."""
    rows = (seed.get("math") or {}).get("rows") or []
    tally = {}
    for r in rows:
        tally[r.get("gap", "?")] = tally.get(r.get("gap", "?"), 0) + 1
    beats = seed.get("beats", {})

    def plain(html):
        return re.sub(r"<[^>]+>", "", html or "").strip()

    receipt = {
        "receipt_id": seed.get("seed_id", "unknown"),
        "phase_id": "sixty_read",
        "fated": {
            "facts": " | ".join(plain(c.get("body_html")) for c in beats.get("outcome", {}).get("cards", [])),
            "assumptions": " | ".join(plain(c.get("body_html")) for c in beats.get("bet", {}).get("cards", [])),
            "tradeoffs": " | ".join(plain(c.get("body_html")) for c in beats.get("outcome", {}).get("cards", []) if c.get("miss")),
            "emotions": plain(beats.get("spark", {}).get("body_html")),
            "direction": plain(beats.get("move", {}).get("panel_html")),
        },
    }
    if isinstance((seed.get("math") or {}).get("nci"), (int, float)):
        receipt["nci_score"] = seed["math"]["nci"]

    raw = {"rows_scored": len(rows), "tally": tally, "receipt": receipt}

    # Speaker-provenance lambda (ventriloquy paternity test, ADR-033 speaker coordinate):
    # every counterpart-attributed quote must trace to a Them: turn or counterpart-authored
    # text. CONTAMINATED/UNSOURCED halts settle; the lint writes the resolution receipt.
    if sources:
        from attribution_provenance_lint import lint_artifact, write_resolution_receipt
        att = lint_artifact(seed_path, sources)
        dirty = any(f["verdict"] in ("CONTAMINATED", "UNSOURCED") for f in att["findings"])
        if dirty:
            att["resolution_receipt"] = write_resolution_receipt(seed_path, att)
        raw["attribution"] = {"counts": att["counts"], "dirty": dirty,
                              "findings": [f for f in att["findings"]
                                           if f["verdict"] not in ("CLEAN", "ANCHORED")],
                              "resolution_receipt": att.get("resolution_receipt")}
    if pipe_evaluator:
        proc = subprocess.run(
            [sys.executable, str(REPO / "operators" / "receipt_evaluator.py"), "--format", "json"],
            input=json.dumps(receipt), capture_output=True, text=True, timeout=120,
        )
        try:
            raw["kintsugi"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            raw["kintsugi"] = {"status": "error", "error": proc.stderr.strip()[:400]}
    return raw


# ── germination: ripeness + conditions ledger ────────────────────────────────

def ripeness_check(seed, ctx):
    """Mechanical range-check of a context vector against the seed's germination axes.

    ctx: {<axis>: 0..1, "days_dormant": N, "gauntlet_survived": bool}
    Returns {axes, stratification, ripe, missed}. Axes the seed declares no range for
    are unconstrained (matched by default) — a seed constrains only what matters to it.
    """
    germ = seed.get("germination", {})
    declared = germ.get("axes", {})
    axes, missed = {}, []
    for axis in GERMINATION_AXES:
        spec = declared.get(axis)
        if not spec or "range" not in spec:
            axes[axis] = {"range": None, "value": ctx.get(axis), "matched": True}
            continue
        lo, hi = spec["range"]
        val = ctx.get(axis)
        ok = val is not None and lo <= float(val) <= hi
        axes[axis] = {"range": [lo, hi], "value": val, "matched": ok}
        if not ok:
            missed.append(axis)
    strat = declared.get("stratification", {})
    strat_result = {}
    if strat.get("min_days") is not None:
        ok = float(ctx.get("days_dormant", 0)) >= float(strat["min_days"])
        strat_result["min_days"] = {"required": strat["min_days"],
                                    "value": ctx.get("days_dormant", 0), "matched": ok}
        if not ok:
            missed.append("stratification.min_days")
    if strat.get("requires_gauntlet"):
        ok = bool(ctx.get("gauntlet_survived"))
        strat_result["requires_gauntlet"] = {"required": True,
                                             "value": bool(ctx.get("gauntlet_survived")), "matched": ok}
        if not ok:
            missed.append("stratification.requires_gauntlet")
    return {"axes": axes, "stratification": strat_result,
            "ranges_provenance": germ.get("ranges_provenance", "provisional"),
            "ripe": not missed, "missed": missed}


def ledger_append(event):
    """Append a sprouted/refused event to the running conditions ledger
    (_SEEDS/ledger.jsonl; SIXTY_LEDGER env overrides — tests must never write the real
    ledger). Carries `seed` alongside `seed_id` for the pre-existing ledger readers.
    A refusal without a receipt violates every-gate-a-detector."""
    import datetime
    import os
    path = Path(os.environ.get("SIXTY_LEDGER", str(LEDGER_PATH)))
    event = {"ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
             "seed": event.get("seed_id"), **event}
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, default=str) + "\n")
    return str(path)


# ── render ───────────────────────────────────────────────────────────────────

# Golden reference: the hand-built Yuri artifact (claude.ai 17a1923c, source-verified
# 2026-08-30). Dark cockpit, IBM Plex pairing, ONE --measure px token, auto-fit minmax
# grids, balance/pretty wrapping, no per-role ch caps, math closed by default.
# Delta from the golden reference: the SPARK is its own beat (fourth read), so the page
# is four reads of fifteen seconds, and the spark carries its own accent (--spark).

_CSS = """
  :root{
    --bg:#0a0e14; --surface:#121a24; --surface-2:#0f151d;
    --border:#22303f; --border-soft:#1a2431;
    --text:#e8edf3; --muted:#aab4c1; --label:#8492a3; --faint:#76839a;
    --cyan:#5bdcec;   /* the bet   */
    --green:#63f3b2;  /* the truth */
    --amber:#f7ca5c;  /* the miss + the move */
    --spark:#c9a8ff;  /* the ignition */
    --mono:"IBM Plex Mono",ui-monospace,"SF Mono",Menlo,monospace;
    --sans:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
    --measure:768px;
    --s1:4px; --s2:8px; --s3:12px; --s4:16px; --s6:24px; --s8:32px; --s10:40px;
    --pad:clamp(20px,4.5vw,24px);
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  @media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
  body{margin:0;
    background:
      radial-gradient(1150px 640px at 84% -12%,rgba(99,243,178,.055),transparent 60%),
      radial-gradient(840px 520px at -10% 6%,rgba(91,220,236,.045),transparent 56%),
      var(--bg);
    color:var(--text);font-family:var(--sans);font-size:17px;line-height:1.6;
    letter-spacing:.002em;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
  .wrap{max-width:var(--measure);margin:0 auto;padding:0 var(--pad)}
  p{text-wrap:pretty} h1,h2,h3{text-wrap:balance}
  @keyframes rise{from{opacity:0;transform:translateY(9px)}to{opacity:1;transform:none}}
  .rise{animation:rise .68s cubic-bezier(.16,1,.3,1) both}
  .rise.d1{animation-delay:.05s}.rise.d2{animation-delay:.11s}.rise.d3{animation-delay:.17s}
  @media (prefers-reduced-motion:reduce){.rise{animation:none}}
  header.hero{padding:clamp(56px,10vh,116px) var(--pad) clamp(30px,6vh,52px)}
  .kicker{font-family:var(--mono);font-size:11.5px;letter-spacing:.22em;text-transform:uppercase;
    color:var(--label);display:flex;align-items:center;gap:11px;margin:0 0 var(--s6);flex-wrap:wrap}
  .kicker::before{content:"";width:24px;height:1px;background:var(--border);flex:none}
  .kicker b{color:var(--green);font-weight:600}
  h1{font-weight:600;letter-spacing:-.022em;font-size:clamp(30px,5.4vw,46px);line-height:1.07;margin:0}
  h1 em{color:var(--green);font-style:normal}
  h1 .keep{white-space:nowrap}
  .lead{font-size:clamp(17px,2.1vw,19.5px);color:#d3dbe4;margin:var(--s6) 0 0;line-height:1.55}
  .lead b{color:var(--text);font-weight:600}
  .promise{margin-top:var(--s8);font-family:var(--mono);font-size:12.5px;color:var(--muted);
    display:flex;flex-wrap:wrap;gap:var(--s2) var(--s6);align-items:center}
  .promise span{display:inline-flex;align-items:center;gap:10px;white-space:nowrap}
  .promise .dot{width:5px;height:5px;border-radius:50%;background:var(--green);
    box-shadow:0 0 8px rgba(99,243,178,.7);flex:none}
  .read{padding:clamp(40px,6.5vh,60px) var(--pad);border-top:1px solid var(--border-soft)}
  .read-head{margin:0 0 clamp(22px,3.4vh,30px)}
  .read-kicker{font-family:var(--mono);font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;
    display:flex;align-items:center;gap:12px;margin:0 0 var(--s3)}
  .read-kicker .rn{color:var(--faint)}
  .read-kicker .sep{width:14px;height:1px;background:var(--border);flex:none}
  .read-kicker .tm{color:var(--faint);font-variant-numeric:tabular-nums;white-space:nowrap}
  .bet-s .read-kicker .rn{color:var(--cyan)}
  .outcome-s .read-kicker .rn{color:var(--green)}
  .spark-s .read-kicker .rn{color:var(--spark)}
  .move-s .read-kicker .rn{color:var(--amber)}
  h2{font-family:var(--mono);font-weight:600;letter-spacing:-.01em;
    font-size:clamp(21px,3vw,27px);line-height:1.12;margin:0 0 var(--s3)}
  .read-sub{color:var(--muted);font-size:15px;line-height:1.5;margin:0}
  .grid{display:grid;gap:var(--s3);grid-template-columns:repeat(auto-fit,minmax(210px,1fr))}
  .card{border:1px solid var(--border);border-radius:14px;
    background:linear-gradient(180deg,var(--surface),var(--surface-2));
    padding:var(--s4) var(--s4) calc(var(--s4) + 2px);display:flex;flex-direction:column}
  .card .label{font-family:var(--mono);font-size:10.5px;letter-spacing:.11em;text-transform:uppercase;
    color:var(--label);display:flex;align-items:center;gap:8px;margin:0 0 var(--s3)}
  .card .label::before{content:"";width:6px;height:6px;border-radius:2px;background:currentColor;flex:none;opacity:.9}
  .bet-s .card .label{color:var(--cyan)}
  .outcome-s .card .label{color:var(--green)}
  .card.miss .label{color:var(--amber)}
  .card h3{font-weight:600;font-size:17px;letter-spacing:-.008em;line-height:1.26;margin:0 0 var(--s2)}
  .outcome-s .card:not(.miss) h3{color:var(--green)}
  .card.miss h3{color:var(--amber)}
  .card p{margin:0;color:var(--muted);font-size:14px;line-height:1.5}
  .card p q{color:#cfd7e0;font-style:normal;quotes:"\\201C" "\\201D"}
  .spark-s .ignite{border:1px solid rgba(201,168,255,.32);border-radius:16px;
    background:linear-gradient(180deg,rgba(201,168,255,.06),rgba(201,168,255,.015));
    padding:clamp(22px,3.6vw,28px)}
  .spark-s blockquote{margin:0 0 var(--s4);font-size:clamp(17px,2.2vw,20px);line-height:1.45;
    color:#e6ddf6;quotes:"\\201C" "\\201D"}
  .spark-s blockquote::before{content:open-quote;color:var(--spark)}
  .spark-s blockquote::after{content:close-quote;color:var(--spark)}
  .spark-s .attrib{font-family:var(--mono);font-size:12px;color:var(--faint);margin:0 0 var(--s4)}
  .spark-s .ignite p.why{margin:0;color:var(--muted);font-size:15px;line-height:1.55}
  .spark-s .ignite p.why b{color:var(--spark);font-weight:600}
  .move-s .panel{border:1px solid rgba(247,202,92,.32);border-radius:16px;
    background:linear-gradient(180deg,rgba(247,202,92,.055),rgba(247,202,92,.015));
    padding:clamp(22px,3.6vw,28px)}
  .move-s .panel p{margin:0;font-size:clamp(17px,2vw,19px);line-height:1.5;color:#e4e0d4}
  .move-s .panel p b{color:var(--amber);font-weight:600}
  details.work{margin-top:var(--s6);border:1px solid var(--border);border-radius:12px;
    background:var(--surface-2);overflow:hidden}
  details.work summary{list-style:none;cursor:pointer;padding:var(--s4);
    font-family:var(--mono);font-size:13px;letter-spacing:.02em;color:var(--muted);
    display:flex;align-items:center;justify-content:space-between;gap:var(--s3);transition:color .22s}
  details.work summary::-webkit-details-marker{display:none}
  details.work summary:hover{color:var(--text)}
  details.work summary:focus-visible{outline:2px solid var(--cyan);outline-offset:-3px;border-radius:12px}
  details.work summary .hint{color:var(--faint);font-size:11.5px;display:inline-flex;align-items:center;gap:8px;white-space:nowrap}
  details.work summary .chev{transition:transform .28s}
  details.work[open] summary .chev{transform:rotate(90deg)}
  .work-body{padding:var(--s2) var(--s4) var(--s6);border-top:1px solid var(--border-soft)}
  .work-body p{color:var(--muted);font-size:14px;line-height:1.55;margin:var(--s4) 0}
  .work-body p em{color:var(--text);font-style:normal;font-weight:600}
  .scroll{overflow-x:auto}
  table{width:100%;border-collapse:collapse;font-size:13.5px;font-variant-numeric:tabular-nums}
  th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--border-soft);vertical-align:top}
  th{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--label);font-weight:500}
  td:first-child{font-family:var(--mono);color:var(--muted);white-space:nowrap;font-size:12.5px}
  .b{color:var(--cyan)}.a{color:var(--green)}.g{color:var(--amber)}
  footer.wrap{padding:clamp(40px,6vh,56px) var(--pad) clamp(56px,9vh,84px);border-top:1px solid var(--border-soft)}
  .who{border:1px solid var(--border);border-radius:16px;background:var(--surface);padding:clamp(20px,3.4vw,26px)}
  .who h4{font-family:var(--mono);font-size:11.5px;letter-spacing:.13em;text-transform:uppercase;
    color:var(--label);font-weight:500;margin:0 0 var(--s4)}
  .who .row{display:grid;grid-template-columns:116px 1fr;gap:var(--s1) var(--s6);
    padding:var(--s3) 0;border-top:1px solid var(--border-soft)}
  .who .row:first-of-type{border-top:0;padding-top:0}
  @media(max-width:520px){.who .row{grid-template-columns:1fr;gap:var(--s1)}}
  .who .row .q{font-family:var(--mono);font-size:12.5px;color:var(--green);padding-top:2px}
  .who .row .a{color:var(--muted);font-size:15px;line-height:1.5}
  .fine{color:var(--faint);font-family:var(--mono);font-size:11.5px;line-height:1.75;margin:var(--s6) 0 0;letter-spacing:.01em}
"""

_PAGE = Template("""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>$title</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<meta name="description" content="$description">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>$css</style>
</head>
<body>
<header class="hero wrap">
  <p class="kicker rise"><b>the 60-second read</b><span>$meeting_label</span></p>
  <h1 class="rise d1">$title_html</h1>
  <p class="lead rise d2">$lead_html</p>
  <div class="promise rise d3">$promise</div>
</header>
$sections
<footer class="wrap">
$who
  <p class="fine">$fine_print</p>
</footer>
</body>
</html>
""")

_TIMES = {"bet": "0:00–0:15", "outcome": "0:15–0:30", "spark": "0:30–0:45", "move": "0:45–0:60"}


def _cards(beat_key, beat):
    out = ['<div class="grid">']
    for c in beat.get("cards", []):
        miss = " miss" if c.get("miss") else ""
        out.append(
            f'<div class="card{miss}"><div class="label">{c["label"]}</div>'
            f'<h3>{c["head"]}</h3><p>{c["body_html"]}</p></div>'
        )
    out.append("</div>")
    return "\n".join(out)


def _math_details(math):
    if not math:
        return ""
    rows = []
    for r in math.get("rows", []):
        gap_cls = {"on target": "a"}.get(r.get("gap", "").lower(), "g")
        rows.append(f'<tr><td>{r["read"]}</td><td class="b">{r["bet"]}</td>'
                    f'<td class="a">{r["actual"]}</td><td class="{gap_cls}">{r["gap"]}</td></tr>')
    return f"""
  <details class="work">
    <summary>
      <span>{math.get("summary_label", "Show the work · the scoring behind the read")}</span>
      <span class="hint">closed on purpose <span class="chev">›</span></span>
    </summary>
    <div class="work-body">
      <p>{math.get("summary_html", "")}</p>
      <div class="scroll">
        <table>
          <tr><th>Read</th><th>The bet I filed</th><th>What happened</th><th>Gap</th></tr>
          {''.join(rows)}
        </table>
      </div>
    </div>
  </details>"""


def render_seed(seed, out_path):
    beats = seed["beats"]
    names = {"bet": seed["beats"]["bet"].get("h2", "Before we talked"),
             "outcome": beats["outcome"].get("h2", "After we talked"),
             "spark": beats["spark"].get("h2", "The moment it caught"),
             "move": beats["move"].get("h2", "What to do about it")}
    sections = []
    for n, key in enumerate(BEATS, start=1):
        b = beats[key]
        head = (f'<div class="read-head">'
                f'<p class="read-kicker"><span class="rn">Read {n}</span><span class="sep"></span>'
                f'<span class="tm">{_TIMES[key]}</span></p>'
                f'<h2>{names[key]}</h2><p class="read-sub">{b.get("sub", "")}</p></div>')
        if key in ("bet", "outcome"):
            body = _cards(key, b)
        elif key == "spark":
            body = (f'<div class="ignite"><blockquote>{b["quote"]}</blockquote>'
                    f'<p class="attrib">{b.get("quote_attrib", "")}</p>'
                    f'<p class="why">{b["body_html"]}</p></div>')
        else:
            body = f'<div class="panel"><p>{b["panel_html"]}</p></div>' + _math_details(seed.get("math"))
        sections.append(f'<section class="read {key}-s wrap">\n{head}\n{body}\n</section>')

    who = ""
    if seed.get("who"):
        rows = "".join(f'<div class="row"><div class="q">{q}</div><div class="a">{a}</div></div>'
                       for q, a in seed["who"]["rows"])
        who = f'<div class="who"><h4>{seed["who"].get("h4", "So, who’s it for")}</h4>{rows}</div>'

    hero = seed.get("hero", {})
    promise = "".join(f'<span><i class="dot"></i>{p}</span>'
                      for p in hero.get("promise", ["Four reads", "Fifteen seconds each", "Then you have it"]))
    html = _PAGE.substitute(
        title=hero.get("title", f'The 60-Second Read · {seed["counterpart"]["name"]}'),
        description=hero.get("description", "A one-minute read: the bet, what happened, the moment it caught, and the one move."),
        css=_CSS,
        meeting_label=seed["counterpart"].get("meeting_label", ""),
        title_html=hero.get("title_html", "The 60-second read."),
        lead_html=hero.get("lead_html", ""),
        promise=promise,
        sections="\n".join(sections),
        who=who,
        fine_print=seed.get("provenance", {}).get("fine_print", ""),
    )
    Path(out_path).write_text(html, encoding="utf-8")
    return {"out": str(out_path), "bytes": len(html.encode("utf-8"))}


# ── commit (Yoav) ────────────────────────────────────────────────────────────

def commit_seed(seed, tier, log_path, seed_path, ctx=None):
    """Serialize one tier of the seed through the Yoav Protocol (arcs_yoav_store.py).

    FutureVector = the seed's superposition: the tier being committed plus every dormant
    longer form in future_vector. Commit = collapse to this tier. QUARANTINED never
    discards: it writes an upstream resolution receipt (conflict-quarantine mechanic).

    Tiers past `read` are SPROUTS: they require a ripe germination check (universal axes,
    per-seed ranges) and every decision — sprouted or refused — lands in the conditions
    ledger with the conditions_present snapshot. On a committed sprout, seed_state moves
    dormant -> sprouted in the seed file (a legal upstream write: seed_state IS SSOT state).
    """
    ripe_result = None
    if tier != "read":
        if ctx is None:
            return {"refused": True, "reason": "sprout tiers require --context (the conditions vector)",
                    "ripeness": None}
        ripe_result = ripeness_check(seed, ctx)
        if not ripe_result["ripe"]:
            ledger = ledger_append({
                "event": "refused", "seed_id": seed["seed_id"], "tier": tier,
                "conditions_present": ctx, "ripeness": ripe_result,
                "missed": ripe_result["missed"], "seed_path": str(seed_path),
            })
            return {"refused": True, "reason": f"not ripe: missed {ripe_result['missed']}",
                    "ripeness": ripe_result, "ledger": ledger}

    sys.path.insert(0, str(REPO / "operators"))
    from arcs_yoav_store import YoavStore, TimeSignature  # noqa: E402

    store = YoavStore(log_path=str(log_path))
    vec = store.create_vector(
        phase_id=f"sixty:{seed['seed_id']}",
        signal_label=tier,
        time_sig=TimeSignature.YOAV,
    )
    committed = store.add_future_state(
        vec.vector_id, label=f"{tier}:committed", probability=0.6,
        nci_estimate=float((seed.get("math") or {}).get("nci") or 70.0),
        signal_class="stable", reversibility=0.9,
        metadata={"seed_state": seed.get("seed_state")},
    )
    for fv in seed.get("future_vector", []):
        store.add_future_state(
            vec.vector_id, label=fv.get("label", "form"),
            probability=float(fv.get("probability", 0.2)),
            nci_estimate=float(fv.get("nci_estimate", 65.0)),
            signal_class="stable", reversibility=float(fv.get("reversibility", 0.95)),
            metadata={"conditions": fv.get("conditions", [])},
        )
    vec.normalize()
    commit, conflicts = store.commit(
        vector_id=vec.vector_id, state_id=committed.state_id,
        span_id=f"seed:{seed['seed_id']}", nci_at_commit=committed.nci_estimate,
        notes=f"sixty-second-read {tier} commit",
        metadata={"seed_path": str(seed_path), "tier": tier},
    )
    raw = {"commit": commit.to_dict(), "conflicts": [c.to_dict() for c in conflicts],
           "log": str(log_path)}
    if ripe_result is not None:
        raw["ripeness"] = ripe_result
    if tier != "read" and commit.status.value == "committed":
        raw["ledger"] = ledger_append({
            "event": "sprouted", "seed_id": seed["seed_id"], "tier": tier,
            "conditions_present": ctx, "ripeness": ripe_result,
            "commit_id": commit.commit_id, "commit_hash": commit.commit_hash,
            "seed_path": str(seed_path),
        })
        if seed.get("seed_state") == "dormant":
            seed["seed_state"] = "sprouted"
            Path(str(seed_path)).write_text(json.dumps(seed, indent=2, ensure_ascii=False) + "\n",
                                            encoding="utf-8")
            raw["seed_state"] = "sprouted (written back to seed)"
    if commit.status.value == "quarantined":
        receipt = {
            "type": "upstream_resolution_receipt",
            "seed_id": seed["seed_id"], "tier": tier,
            "rule": ("bidirectional: a resynthesis that fails to serialize is information "
                     "about ground truth. Do not discard it and do not patch the leaf; "
                     "resolve the conflict upstream in the SSOT, then re-commit."),
            "commit": commit.to_dict(),
            "conflicts": [c.to_dict() for c in conflicts],
        }
        rpath = Path(str(seed_path)).with_suffix(".resolution.json")
        rpath.write_text(json.dumps(receipt, indent=2, default=str), encoding="utf-8")
        raw["resolution_receipt"] = str(rpath)
    return raw


# ── entry point ──────────────────────────────────────────────────────────────

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("validate", "gate"):
        s = sub.add_parser(name)
        s.add_argument("seed")
    s = sub.add_parser("settle")
    s.add_argument("seed")
    s.add_argument("--pipe-evaluator", action="store_true")
    s.add_argument("--source", action="append", default=[], metavar="REF=PATH",
                   help="source file for the speaker-provenance lambda (repeatable)")
    s = sub.add_parser("ripeness")
    s.add_argument("seed")
    s.add_argument("--context", required=True, help="JSON file: the conditions vector")
    s = sub.add_parser("render")
    s.add_argument("seed")
    s.add_argument("out")
    s = sub.add_parser("commit")
    s.add_argument("seed")
    s.add_argument("--tier", choices=TIERS, required=True)
    s.add_argument("--log", default=None)
    s.add_argument("--context", default=None,
                   help="JSON file: conditions vector (required for sprout tiers)")
    args = ap.parse_args(argv)

    try:
        seed = _load_seed(args.seed)
    except Exception as e:
        return _emit(args.cmd, "error", {"error": str(e)}, {"gate_status": "halt"}, 1)

    if args.cmd == "validate":
        f = validate_seed(seed)
        ok = not f
        return _emit("validate", "ok" if ok else "blocked",
                     {"findings": f},
                     {"gate_status": "pass" if ok else "halt", "findings": f,
                      "verdict": "seed valid" if ok else f"{len(f)} structural finding(s)"},
                     0 if ok else 2)

    if args.cmd == "gate":
        f = gate_seed(seed)
        ok = not f
        return _emit("gate", "ok" if ok else "blocked",
                     {"findings": f},
                     {"gate_status": "pass" if ok else "halt", "findings": f,
                      "verdict": "gates pass" if ok else f"{len(f)} gate finding(s)",
                      "next_action": "render" if ok else "fix the seed upstream; never patch the render"},
                     0 if ok else 2)

    if args.cmd == "settle":
        sources = {}
        for spec in args.source:
            if "=" not in spec:
                return _emit("settle", "error", {"error": f"--source needs REF=PATH, got {spec!r}"},
                             {"gate_status": "halt"}, 1)
            ref, path = spec.split("=", 1)
            sources[ref] = path
        raw = settle_seed(seed, pipe_evaluator=args.pipe_evaluator,
                          sources=sources or None, seed_path=args.seed)
        att = raw.get("attribution") or {}
        gate = (raw.get("kintsugi") or {}).get("gate", "pass")
        verdict = f"settled {raw['rows_scored']} row(s): " + ", ".join(
            f"{v} {k}" for k, v in sorted(raw["tally"].items()))
        if att:
            verdict += " | attribution: " + " · ".join(
                f"{v} {k}" for k, v in sorted(att["counts"].items()))
        if att.get("dirty"):
            return _emit("settle", "blocked", raw,
                         {"gate_status": "halt", "verdict": verdict,
                          "findings": att["findings"],
                          "next_action": "ventriloquy/unsourced quote: resolve upstream per "
                                         + str(att.get("resolution_receipt"))},
                         2)
        return _emit("settle", "ok", raw, {"gate_status": gate, "verdict": verdict}, 0)

    if args.cmd == "ripeness":
        with open(args.context, encoding="utf-8") as fh:
            ctx = json.load(fh)
        raw = ripeness_check(seed, ctx)
        return _emit("ripeness", "ok" if raw["ripe"] else "blocked", raw,
                     {"gate_status": "pass" if raw["ripe"] else "halt",
                      "verdict": ("RIPE" if raw["ripe"] else f"NOT RIPE: missed {raw['missed']}")
                                 + f" (ranges {raw['ranges_provenance']})"},
                     0 if raw["ripe"] else 2)

    if args.cmd == "render":
        f = gate_seed(seed)
        if f:
            return _emit("render", "blocked", {"findings": f},
                         {"gate_status": "halt", "findings": f,
                          "verdict": "render refused: gate findings open (honesty refusal, no output)"},
                         2)
        raw = render_seed(seed, args.out)
        return _emit("render", "ok", raw,
                     {"gate_status": "pass", "verdict": f"rendered {raw['bytes']}B",
                      "next_action": f"python3 scripts/artifact_wrap_lint.py {args.out} && sweep 375/790/desktop"},
                     0)

    if args.cmd == "commit":
        log = args.log or str(Path(args.seed).with_suffix(".yoav.jsonl"))
        ctx = None
        if args.context:
            with open(args.context, encoding="utf-8") as fh:
                ctx = json.load(fh)
        raw = commit_seed(seed, args.tier, log, args.seed, ctx=ctx)
        if raw.get("refused"):
            return _emit("commit", "blocked", raw,
                         {"gate_status": "halt",
                          "verdict": f"sprout REFUSED: {raw['reason']}",
                          "next_action": "conditions logged to the ledger; wait for the "
                                         "window or earn the missing range, never force it"},
                         2)
        quarantined = raw["commit"]["status"] == "quarantined"
        return _emit("commit", "blocked" if quarantined else "ok", raw,
                     {"gate_status": "halt" if quarantined else "pass",
                      "verdict": ("QUARANTINED: resolution receipt written; resolve upstream"
                                  if quarantined else f"{args.tier} committed ({raw['commit']['commit_hash'][:12]})")},
                     3 if quarantined else 0)


if __name__ == "__main__":
    sys.exit(main())
