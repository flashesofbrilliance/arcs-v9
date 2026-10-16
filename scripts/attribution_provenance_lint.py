#!/usr/bin/env python3
"""attribution_provenance_lint.py — the speaker-provenance lambda (ventriloquy paternity test).

VENTRILOQUY (ADR-033 Serialization Pathogen Family, sixth coordinate: SPEAKER — admitted
2026-08-29, case: _PATTERNS/2026-08-29-ventriloquy-pathogen-investigation.md): language
authored by one speaker migrates to another across serialization hops. The speaker
coordinate is dropped at compression, then reinferred at resynthesis by plausibility —
warm counterparts are maximally plausible false hosts. Payload is autoimmune: recoil
scores its own echo; the belief-updater becomes a mirror. 4 confirmed instances since
July, two of which passed every register/render detector. This is the mechanism-first
gate those detectors lacked.

RULE: every quote or stance attributed to the COUNTERPART must fuzzy-match a `Them:`
(or named-counterpart) turn in the source transcript, or text the counterpart authored
(a DM, an email they sent). Match against a `Me:` turn -> CONTAMINATED. No match in any
loaded source -> UNSOURCED (paraphrase-label it or strike it). A failed check is never
just discarded: it writes an upstream resolution receipt next to the artifact
(bidirectional rule — artifacts forward-propagate, truth back-propagates; every gate a
detector, ADR-051/052). Fix the SSOT/memory that carried the contamination, then re-run.

USAGE
  # sixty-read seed (source_ref-aware: each --source maps a provenance ref to a file)
  python3 scripts/attribution_provenance_lint.py --artifact seed.60s.json \
      --source transcript=/path/granola.txt --source dm=/path/dm.txt

  # any SSOT/HTML artifact (sources pooled, every extracted quote checked)
  python3 scripts/attribution_provenance_lint.py --artifact page.html \
      --source transcript=/path/granola.txt

  A file containing `Me:`/`Them:` turns is parsed as a speaker-tagged transcript
  (Granola format; `Me` = the note-taker/Zach, `Them`/names = the counterpart).
  Any other file is treated as counterpart-authored text (them-side).

VERDICTS per quote
  CLEAN        verbatim-anchored in a counterpart turn (best window ratio >= 0.80)
  ANCHORED     filler-cleaned/composite but grounded in ONE counterpart turn
               (content-token coverage >= 0.70) — passes, noted
  CONTAMINATED matches a Me: turn, not a counterpart turn — ventriloquy
  UNSOURCED    matches nothing loaded — paraphrase-label or strike
  SKIPPED      the quote's declared source_ref has no --source mapping loaded

exit 0 = all CLEAN/ANCHORED/SKIPPED · 2 = CONTAMINATED or UNSOURCED (receipt written)
Stdlib only. Envelope output matches operators/operator_client.py.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

VERSION = "v1.0"
VERBATIM_T = 0.80
COVERAGE_T = 0.70
STOPWORDS = frozenset(
    "a an the and or but so of to in on at for with is are was were be been am i you we they it "
    "he she this that these those my your our their like just kind sort really very".split())


# ── sources ──────────────────────────────────────────────────────────────────

SPEAKER_RE = re.compile(r"\b(Me|Them|[A-Z][a-z]{2,15})\s*:\s+")


def parse_source(path, me_labels=("Me",)):
    """Return {"me": [turns], "them": [turns]}. A file with no speaker tags is
    counterpart-authored text: one them-side turn."""
    text = Path(path).read_text(encoding="utf-8")
    parts = SPEAKER_RE.split(text)
    if len(parts) < 3:
        return {"me": [], "them": [text.strip()]}
    turns = {"me": [], "them": []}
    # parts = [pre, label, text, label, text, ...]
    for label, body in zip(parts[1::2], parts[2::2]):
        side = "me" if label in me_labels else "them"
        body = body.strip()
        if body:
            turns[side].append(body)
    return turns


# ── quote extraction ─────────────────────────────────────────────────────────

Q_TAG_RE = re.compile(r"<q>(.*?)</q>", re.S)
CURLY_RE = re.compile(r"“(.*?)”", re.S)


def extract_quotes(artifact_path):
    """Yield (where, quote_text, source_ref_or_None) for counterpart-attributed spans.

    JSON: <q> spans and curly-quoted spans inside any string, plus any key named
    `quote` or ending in `_quote` (the sixty-read spark beat, SSOT grounding quotes).
    source_ref: the sibling `source_ref` of the carrying object when present.
    HTML: <q> spans and curly-quoted spans in the rendered copy.
    """
    p = Path(artifact_path)
    if p.suffix.lower() in (".html", ".htm"):
        html = p.read_text(encoding="utf-8")
        html = re.sub(r"<(style|script)\b.*?</\1>", "", html, flags=re.S | re.I)
        for m in Q_TAG_RE.finditer(html):
            yield ("html:<q>", re.sub(r"<[^>]+>", "", m.group(1)), None)
        text_only = re.sub(r"<[^>]+>", " ", html)
        for m in CURLY_RE.finditer(text_only):
            yield ("html:curly", m.group(1), None)
        return

    data = json.loads(p.read_text(encoding="utf-8"))

    def walk(obj, path, ctx_ref):
        if isinstance(obj, dict):
            ref = obj.get("source_ref", ctx_ref)
            for k, v in obj.items():
                kp = f"{path}.{k}" if path else k
                if isinstance(v, str):
                    if k == "quote" or k.endswith("_quote"):
                        yield (kp, v, ref)
                    for m in Q_TAG_RE.finditer(v):
                        yield (kp, m.group(1), ref)
                    for m in CURLY_RE.finditer(v):
                        yield (kp, m.group(1), ref)
                else:
                    yield from walk(v, kp, ref)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                yield from walk(v, f"{path}[{i}]", ctx_ref)

    yield from walk(data, "", None)


# ── matching ─────────────────────────────────────────────────────────────────

def _tokens(s):
    s = re.sub(r"<[^>]+>", " ", s)
    return re.findall(r"[a-z0-9']+", s.lower())


def score_against_turn(quote_toks, turn_toks):
    """(window_ratio, coverage) of the quote against one turn."""
    if not quote_toks or not turn_toks:
        return 0.0, 0.0
    n = len(quote_toks)
    win = max(n, 3)
    best_ratio = 0.0
    step = max(1, win // 3)
    for start in range(0, max(1, len(turn_toks) - win // 2), step):
        window = turn_toks[start:start + int(win * 1.5)]
        r = SequenceMatcher(None, quote_toks, window).ratio()
        if r > best_ratio:
            best_ratio = r
    content = [t for t in quote_toks if t not in STOPWORDS] or quote_toks
    turn_set = set(turn_toks)
    bigrams = list(zip(turn_toks, turn_toks[1:]))
    bigram_set = set(bigrams)
    q_bigrams = [b for b in zip(quote_toks, quote_toks[1:])
                 if b[0] not in STOPWORDS or b[1] not in STOPWORDS]
    uni_cov = sum(1 for t in content if t in turn_set) / len(content)
    bi_cov = (sum(1 for b in q_bigrams if b in bigram_set) / len(q_bigrams)) if q_bigrams else 0.0
    coverage = 0.5 * uni_cov + 0.5 * bi_cov
    return best_ratio, coverage


def best_side_score(quote, turns):
    """Best (ratio, coverage, turn_index) across a side's turns."""
    qt = _tokens(quote.strip().strip("…."))
    best = (0.0, 0.0, -1)
    for i, turn in enumerate(turns):
        r, c = score_against_turn(qt, _tokens(turn))
        if max(r, c) > max(best[0], best[1]):
            best = (r, c, i)
    return best


def judge(quote, them_turns, me_turns):
    tr, tc, ti = best_side_score(quote, them_turns)
    mr, mc, mi = best_side_score(quote, me_turns)
    them_hit = tr >= VERBATIM_T or tc >= COVERAGE_T
    me_hit = mr >= VERBATIM_T or mc >= COVERAGE_T
    if them_hit:
        verdict = "CLEAN" if tr >= VERBATIM_T else "ANCHORED"
    elif me_hit:
        verdict = "CONTAMINATED"
    else:
        verdict = "UNSOURCED"
    return {
        "verdict": verdict,
        "them": {"ratio": round(tr, 3), "coverage": round(tc, 3), "turn": ti},
        "me": {"ratio": round(mr, 3), "coverage": round(mc, 3), "turn": mi},
    }


# ── driver ───────────────────────────────────────────────────────────────────

def lint_artifact(artifact, sources, me_labels=("Me",)):
    """sources: {ref_name: path}. Returns the raw result dict (findings + counts)."""
    parsed = {ref: parse_source(path, me_labels) for ref, path in sources.items()}
    pooled_them = [t for s in parsed.values() for t in s["them"]]
    pooled_me = [t for s in parsed.values() for t in s["me"]]

    findings = []
    for where, quote, ref in extract_quotes(artifact):
        quote = quote.strip()
        if len(_tokens(quote)) < 3:
            continue
        if ref is not None and sources and ref not in sources:
            findings.append({"where": where, "quote": quote, "source_ref": ref,
                             "verdict": "SKIPPED",
                             "note": f"declared source_ref {ref!r} not loaded — pass --source {ref}=<path> to check it"})
            continue
        if ref is not None and ref in parsed:
            them, me = parsed[ref]["them"], pooled_me or parsed[ref]["me"]
        else:
            them, me = pooled_them, pooled_me
        f = judge(quote, them, me)
        f.update({"where": where, "quote": quote[:160], "source_ref": ref})
        findings.append(f)

    counts = {}
    for f in findings:
        counts[f["verdict"]] = counts.get(f["verdict"], 0) + 1
    return {"artifact": str(artifact), "sources": {k: str(v) for k, v in sources.items()},
            "findings": findings, "counts": counts}


def write_resolution_receipt(artifact, raw):
    bad = [f for f in raw["findings"] if f["verdict"] in ("CONTAMINATED", "UNSOURCED")]
    receipt = {
        "type": "upstream_resolution_receipt",
        "pathogen": "ventriloquy (ADR-033, speaker coordinate)",
        "artifact": str(artifact),
        "rule": ("bidirectional: a failed attribution check is information about ground truth. "
                 "Do not delete the quote at the leaf; correct the SSOT/memory that carried it "
                 "(re-attribute to the true speaker, paraphrase-label, or strike upstream), then re-run."),
        "findings": bad,
    }
    rpath = Path(str(artifact)).with_suffix(".attribution-resolution.json")
    rpath.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return str(rpath)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--artifact", required=True, help="seed/SSOT json or rendered html")
    ap.add_argument("--source", action="append", default=[],
                    metavar="REF=PATH", help="map a provenance ref to a source file (repeatable)")
    ap.add_argument("--me-label", action="append", default=[],
                    help="extra speaker label(s) that mean the note-taker (default: Me)")
    args = ap.parse_args(argv)

    sources = {}
    for s in args.source:
        if "=" not in s:
            print(f"Error: --source needs REF=PATH, got {s!r}", file=sys.stderr)
            return 1
        ref, path = s.split("=", 1)
        if not Path(path).exists():
            print(f"Error: source file not found: {path}", file=sys.stderr)
            return 1
        sources[ref] = path
    if not sources:
        print("Error: at least one --source REF=PATH is required", file=sys.stderr)
        return 1

    me_labels = tuple(["Me"] + args.me_label)
    try:
        raw = lint_artifact(args.artifact, sources, me_labels)
    except Exception as e:
        print(json.dumps({"operator": "ATTRIBUTION_LINT", "mode": "api", "status": "error",
                          "exit_code": 1, "raw": {"error": str(e)}}))
        return 1

    dirty = any(f["verdict"] in ("CONTAMINATED", "UNSOURCED") for f in raw["findings"])
    if dirty:
        raw["resolution_receipt"] = write_resolution_receipt(args.artifact, raw)
    status = "blocked" if dirty else "ok"
    verdict = " · ".join(f"{v} {k}" for k, v in sorted(raw["counts"].items())) or "no quotes found"
    print(json.dumps({
        "operator": "ATTRIBUTION_LINT", "mode": "api", "status": status,
        "exit_code": 2 if dirty else 0, "raw": raw,
        "envelope": {"operator": "ATTRIBUTION_LINT", "version": VERSION,
                     "gate_status": "halt" if dirty else "pass",
                     "verdict": verdict,
                     "findings": [f for f in raw["findings"] if f["verdict"] not in ("CLEAN", "ANCHORED")],
                     "next_action": ("resolve upstream per the resolution receipt, then re-run"
                                     if dirty else "proceed"),
                     "operator_specific": raw},
    }, indent=2))
    return 2 if dirty else 0


if __name__ == "__main__":
    sys.exit(main())
