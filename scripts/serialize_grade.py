#!/usr/bin/env python3
"""serialize_grade.py — grade a serialized pre-call briefing against the outcome.

A briefing (e.g. a champion's serialization of a target) makes a set of
predictions. After the call, reality either confirms, diverges from, or ignores
each one. But grading ONLY the briefing's stated claims overfits to its taxonomy:
it is structurally blind to what reality surfaced that no one thought to brief.

So this grades in two opposing passes and reports their tension:

  DEDUCTIVE / taxonomic  -> FIDELITY : of the briefing's own claims, how many held.
  ABDUCTIVE / folksonomic-> COVERAGE : how much load-bearing outcome signal had NO
                                       briefing parent (the blind spots / orphans).

The orphan emergent tags ARE the net-new tributaries to fork off the thread.

The combined grade is the harmonic mean of the two, so a briefing cannot win by
acing its own predictions while missing everything that actually mattered.

Scoring is deterministic and stdlib-only. No LLM in the scoring path: an LLM may
DRAFT the ledger (extraction), but only human-`locked` rows are graded when
--require-locked is set. See the ledger schema below.

LEDGER SCHEMA (v1) -- a JSON file:
{
  "meta":   { "briefing": [...], "outcome": "...", "title": "..." },
  "lineage":{ "parent": "<briefing id>", "child": "<outcome id>", "fork": "<name>" },
  "taxonomic_claims": [
    { "id":"T0", "statement":"...", "source":"...", "confidence":0.8,
      "load_bearing":true, "verdict":"confirmed|partial|diverged|unaddressed",
      "evidence":"...", "locked":false }
  ],
  "emergent_tags": [
    { "id":"E0", "tag":"...", "outcome_evidence":"...", "load_bearing":true,
      "briefing_parent":null, "locked":false }
  ]
}

USAGE:
  scripts/serialize_grade.py --ledger FILE
      [--weights loadbearing=2,normal=1]
      [--credit confirmed=1,partial=0.5,diverged=0,unaddressed=0]
      [--format json|md] [--require-locked]
      [--set taxonomic_claims.T2.verdict=diverged ...]
      [--out FILE]

Exit codes: 0 ok · 2 bad input/ledger.
"""
import argparse, json, sys

VERDICTS = ("confirmed", "partial", "diverged", "unaddressed")


def die(msg):
    sys.stderr.write("serialize_grade: " + msg + "\n")
    sys.exit(2)


def parse_kv(s, cast=float):
    """'a=2,b=1' -> {'a':2.0,'b':1.0}."""
    out = {}
    if not s:
        return out
    for pair in s.split(","):
        if not pair.strip():
            continue
        if "=" not in pair:
            die("bad key=value: %r" % pair)
        k, v = pair.split("=", 1)
        out[k.strip()] = cast(v.strip())
    return out


def apply_set(ledger, expr):
    """--set taxonomic_claims.T2.verdict=diverged  (id-addressed, audit-logged)."""
    if "=" not in expr:
        die("bad --set (need path=value): %r" % expr)
    path, value = expr.split("=", 1)
    parts = path.split(".")
    if len(parts) != 3:
        die("--set path must be <section>.<id>.<field>: %r" % path)
    section, rid, field = parts
    rows = ledger.get(section)
    if not isinstance(rows, list):
        die("--set unknown section: %r" % section)
    for row in rows:
        if row.get("id") == rid:
            old = row.get(field)
            # keep types sane for the fields we grade on
            if field in ("load_bearing", "locked"):
                value_cast = value.lower() in ("1", "true", "yes")
            elif field == "confidence":
                value_cast = float(value)
            else:
                value_cast = value
            row[field] = value_cast
            row.setdefault("_overrides", []).append(
                {"field": field, "from": old, "to": value_cast})
            return
    die("--set: no row id %r in %s" % (rid, section))


def weight_of(row, w):
    return w["loadbearing"] if row.get("load_bearing") else w["normal"]


def grade(ledger, w, credit, require_locked):
    tax = ledger.get("taxonomic_claims", []) or []
    emg = ledger.get("emergent_tags", []) or []

    def usable(row):
        return (not require_locked) or bool(row.get("locked"))

    tax_used = [c for c in tax if usable(c)]
    emg_used = [e for e in emg if usable(e)]
    tax_skipped = len(tax) - len(tax_used)
    emg_skipped = len(emg) - len(emg_used)

    # ── DEDUCTIVE: fidelity of the briefing's own claims ──
    fid_num = fid_den = 0.0
    tally = {v: 0 for v in VERDICTS}
    for c in tax_used:
        v = c.get("verdict", "unaddressed")
        if v not in VERDICTS:
            die("claim %s: bad verdict %r" % (c.get("id"), v))
        tally[v] += 1
        wt = weight_of(c, w)
        fid_num += credit[v] * wt
        fid_den += wt
    fidelity = (fid_num / fid_den) if fid_den else None

    # ── ABDUCTIVE: coverage over LOAD-BEARING OUTCOME signal only ──
    # Outcome signal = what reality actually surfaced. Two sources:
    #   (i)  taxonomic claims reality ADDRESSED (verdict != unaddressed), and
    #   (ii) emergent tags (reality surfaced them, briefed or not).
    # Anticipated = (i) + emergent tags that HAD a briefing parent.
    # Blind = orphan emergent (no parent). Restricted to load_bearing so padding
    # the ledger with trivial (or unaddressed) claims cannot move coverage.
    lb = lambda r: r.get("load_bearing")
    addressed_tax = [c for c in tax_used if lb(c) and c.get("verdict") != "unaddressed"]
    parented_emg = [e for e in emg_used if lb(e) and e.get("briefing_parent")]
    blind = [e for e in emg_used if lb(e) and not e.get("briefing_parent")]
    anticipated_w = sum(weight_of(c, w) for c in addressed_tax) + \
        sum(weight_of(e, w) for e in parented_emg)
    blind_w = sum(weight_of(e, w) for e in blind)
    denom = anticipated_w + blind_w
    coverage = (anticipated_w / denom) if denom else None
    orphans = blind  # load-bearing, unparented = the net-new tributaries to fork

    # ── combined grade: harmonic mean (F1-style) ──
    if fidelity is None or coverage is None:
        combined = None
    elif fidelity == 0 and coverage == 0:
        combined = 0.0
    else:
        combined = 2 * fidelity * coverage / (fidelity + coverage)

    provisional = (not require_locked) and (
        any(not c.get("locked") for c in tax) or any(not e.get("locked") for e in emg))

    return {
        "lineage": ledger.get("lineage", {}),
        "meta": ledger.get("meta", {}),
        "scores": {
            "fidelity": round(fidelity, 4) if fidelity is not None else None,
            "coverage": round(coverage, 4) if coverage is not None else None,
            "serialization_grade": round(combined, 4) if combined is not None else None,
        },
        "verdict_tally": tally,
        "unaddressed": [c["id"] for c in tax_used if c.get("verdict") == "unaddressed"],
        "diverged": [c["id"] for c in tax_used if c.get("verdict") == "diverged"],
        # A diverged claim means the briefing was WRONG (fidelity miss) — but wrong
        # can be favorable (reality over-delivered) or adverse. Fidelity credits it 0
        # either way (his claim didn't hold); this split keeps the grade from being
        # MISREAD as "the meeting went badly" when a claim diverged upward.
        "diverged_favorable": [c["id"] for c in tax_used
                               if c.get("verdict") == "diverged" and c.get("direction") == "amplify"],
        "diverged_adverse": [c["id"] for c in tax_used
                             if c.get("verdict") == "diverged" and c.get("direction") == "dampen"],
        "fork_tributaries": [  # orphan load-bearing emergent tags = net-new tributaries
            {"id": e.get("id"), "tag": e.get("tag"),
             "load_bearing": bool(e.get("load_bearing")),
             "evidence": e.get("outcome_evidence")}
            for e in orphans
        ],
        "counts": {
            "taxonomic_claims": len(tax_used), "emergent_tags": len(emg_used),
            "orphans": len(orphans),
            "skipped_unlocked": {"taxonomic": tax_skipped, "emergent": emg_skipped},
        },
        "provisional": provisional,
        "require_locked": require_locked,
    }


def as_md(r, show_draft_number=False):
    s = r["scores"]
    # When provisional, WITHHOLD the numbers by default: a bold "61%" copied into a
    # slide leaves its ⚠ banner behind and gets quoted as a measured fact. The grade
    # is an LLM-drafted opinion until a human locks rows. --draft-number reveals it
    # for internal use; JSON always carries the figures (machines read `provisional`).
    mask = r["provisional"] and not show_draft_number
    def pct(x): return "—" if x is None else ("%.0f%%" % (x * 100))
    def show(x): return "DRAFT" if mask else pct(x)
    L = r["lineage"]
    c = r["counts"]
    locked_note = ""
    out = []
    out.append("# Serialization grade — %s" % (r["meta"].get("title", "(untitled)")))
    if L:
        out.append("")
        out.append("**Fork lineage:** `%s` → `%s`  ·  net-new tributary: **%s**"
                   % (L.get("parent", "?"), L.get("child", "?"), L.get("fork", "?")))
    if r["provisional"]:
        out.append("")
        out.append("> ⚠ **PROVISIONAL / NOT LOCKABLE** — every score below is an LLM-drafted "
                   "opinion until a human locks the rows. Numbers are withheld to stop a bare "
                   "figure being quoted as measured fact. Lock the ledger (or pass "
                   "`--require-locked`) to grade; `--draft-number` to see the interim figure.")
    out.append("")
    out.append("| | score | reads |")
    out.append("|---|---|---|")
    out.append("| **Fidelity** (deductive — did his claims hold) | %s | of the briefing's own predictions |"
               % show(s["fidelity"]))
    out.append("| **Coverage** (abductive — was it blind) | %s | load-bearing outcome signal it *anticipated* |"
               % show(s["coverage"]))
    out.append("| **Serialization grade** (harmonic mean) | **%s** | can't win by acing claims while blind |"
               % show(s["serialization_grade"]))
    t = r["verdict_tally"]
    out.append("")
    out.append("**Claim verdicts:** %d confirmed · %d partial · %d diverged · %d unaddressed"
               % (t["confirmed"], t["partial"], t["diverged"], t["unaddressed"]))
    if r.get("diverged_favorable"):
        out.append("")
        out.append("_Note: %s diverged **favorably** (%s) — the briefing was wrong in the good "
                   "direction; a low fidelity here is not a bad meeting._"
                   % (len(r["diverged_favorable"]), ", ".join(r["diverged_favorable"])))
    if r["fork_tributaries"]:
        out.append("")
        out.append("## Net-new tributaries to fork (reality surfaced, briefing was blind)")
        for f in r["fork_tributaries"]:
            lb = " · load-bearing" if f["load_bearing"] else ""
            out.append("- **%s**%s — %s" % (f["tag"], lb, f.get("evidence") or ""))
    c = r["counts"]
    out.append("")
    out.append("_graded %d claims + %d emergent tags (%d orphans)%s._" % (
        c["taxonomic_claims"], c["emergent_tags"], c["orphans"],
        "" if not r["require_locked"] else " · locked-only"))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Grade a briefing serialization against its outcome.")
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--weights", default="loadbearing=2,normal=1")
    ap.add_argument("--credit", default="confirmed=1,partial=0.5,diverged=0,unaddressed=0")
    ap.add_argument("--format", choices=("json", "md"), default="md")
    ap.add_argument("--require-locked", action="store_true",
                    help="grade only human-locked rows (no draft counts toward the grade)")
    ap.add_argument("--draft-number", action="store_true",
                    help="reveal the interim numeric grade even while provisional (internal use)")
    ap.add_argument("--set", action="append", default=[], dest="sets",
                    help="override a row field, e.g. taxonomic_claims.T2.verdict=diverged")
    ap.add_argument("--out", help="write result here instead of stdout")
    a = ap.parse_args()

    try:
        with open(a.ledger) as fh:
            ledger = json.load(fh)
    except (OSError, ValueError) as e:
        die("cannot read ledger: %s" % e)

    for expr in a.sets:
        apply_set(ledger, expr)

    w = {"loadbearing": 2.0, "normal": 1.0}
    w.update(parse_kv(a.weights))
    credit = {"confirmed": 1.0, "partial": 0.5, "diverged": 0.0, "unaddressed": 0.0}
    credit.update(parse_kv(a.credit))
    for v in VERDICTS:
        if v not in credit:
            die("missing credit for verdict %r" % v)

    result = grade(ledger, w, credit, a.require_locked)
    text = json.dumps(result, indent=2) if a.format == "json" else as_md(result, a.draft_number)

    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text + "\n")
        sys.stderr.write("wrote %s\n" % a.out)
    else:
        print(text)


if __name__ == "__main__":
    main()
