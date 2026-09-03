#!/usr/bin/env python3
"""pre_prep_gate — the INPUT end of the legibility clean room (ADR-075, amendment A).

Before /recoil-prep fills a war-room or the forge renders a page, the account SSOT must carry a
`pre_prep` block that answers, from the raw sources, the questions that decide whether the RIGHT
artifact is being built at all. cold_reader_gate.py catches a wall on the way out; this catches
building the wrong thing well on the way in. Every check is a presence/shape test; the judgment
lives in the human who fills the block.

Required `pre_prep` block (in the counterpart SSOT json):
{
  "filed": "YYYY-MM-DD",                      # P0 filed BEFORE the build starts
  "raw_sources": [{"kind": "transcript|thread|profile", "path": "...", "verbatim": true}],
                                              # P1 at least one transcript/thread, on disk, verbatim (not a summary)
  "asks": [{"quote": "...", "source": "...", "answered_by": "..."|null}],
                                              # P2 counterpart's explicit asks, one verbatim quote each, >= 1
  "reader": {"who": "...", "stage": "before|during|after|share|compounds"},
                                              # P3 persona + Receipt Loop stage, one line each
  "subject": {"about": "...", "same_as_reader": true|false, "reader_asked_for_it": true|false},
                                              # P4 if about != for, the reader must have asked for it
  "format_spec": {"quote": "..."|null, "source": "..."|null, "none_found": true|false},
                                              # P5 the reader's own words on how they consume, or an explicit none
  "arriving_state": {"state": "in-fire|caught-breath", "quote": "..."},
                                              # P6 with the line that shows it
  "budget": {"build_minutes": N, "read_minutes": N}  # P7 read <= build/10
}

Retroactive contract: runtime/recoil/generated/2026-07-22-elsamadisi.json (as of 2026-09-03) FAILS
(no block; had one been filled honestly it would have failed P2/P4/P5: asks 7 and 9 unanswered,
subject = reader without the reader asking, format spec present in transcript but unused).

Usage: python3 scripts/pre_prep_gate.py <ssot.json> [--json]
Exit 0 pass, 1 fail, 2 usage. Stdlib only.
"""
import json, os, sys

STAGES = {"before", "during", "after", "share", "compounds"}
STATES = {"in-fire", "caught-breath"}


def check(path: str) -> dict:
    d = json.load(open(path, encoding="utf-8"))
    pp = d.get("pre_prep")
    res = {"ssot": path, "checks": {}, "notes": []}
    c = res["checks"]
    if not isinstance(pp, dict):
        for k in ["P0_filed_before_build", "P1_raw_sources_on_disk_verbatim", "P2_asks_enumerated_verbatim",
                  "P3_reader_and_stage_declared", "P4_subject_slot_consistent", "P5_format_spec_or_explicit_none",
                  "P6_arriving_state_with_quote", "P7_read_budget_le_tenth_build"]:
            c[k] = False
        res["notes"].append("no pre_prep block: nothing was framed before building")
        res["pass"] = False
        return res
    c["P0_filed_before_build"] = bool(pp.get("filed"))
    srcs = pp.get("raw_sources") or []
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ok_src = [s for s in srcs if s.get("kind") in ("transcript", "thread") and s.get("verbatim") is True
              and s.get("path") and (os.path.exists(s["path"]) or os.path.exists(os.path.join(root, s["path"])))]
    c["P1_raw_sources_on_disk_verbatim"] = len(ok_src) >= 1
    if srcs and not ok_src:
        res["notes"].append("raw_sources present but none is a verbatim transcript/thread that exists on disk")
    asks = pp.get("asks") or []
    c["P2_asks_enumerated_verbatim"] = len(asks) >= 1 and all(a.get("quote") and a.get("source") for a in asks)
    open_asks = [a["quote"] for a in asks if not a.get("answered_by")]
    if open_asks:
        res["notes"].append(f"{len(open_asks)} ask(s) still unanswered: " + " | ".join(q[:60] for q in open_asks))
    rd = pp.get("reader") or {}
    c["P3_reader_and_stage_declared"] = bool(rd.get("who")) and rd.get("stage") in STAGES
    sb = pp.get("subject") or {}
    c["P4_subject_slot_consistent"] = bool(sb.get("about")) and (sb.get("same_as_reader") is False or sb.get("reader_asked_for_it") is True)
    if sb.get("same_as_reader") is True and not sb.get("reader_asked_for_it"):
        res["notes"].append("artifact is ABOUT the reader and the reader did not ask for that: specimen risk")
    fs = pp.get("format_spec") or {}
    c["P5_format_spec_or_explicit_none"] = bool(fs.get("quote") and fs.get("source")) or fs.get("none_found") is True
    st = pp.get("arriving_state") or {}
    c["P6_arriving_state_with_quote"] = st.get("state") in STATES and bool(st.get("quote"))
    b = pp.get("budget") or {}
    try:
        c["P7_read_budget_le_tenth_build"] = float(b["read_minutes"]) <= float(b["build_minutes"]) / 10.0
    except (KeyError, TypeError, ValueError):
        c["P7_read_budget_le_tenth_build"] = False
    res["pass"] = all(c.values())
    return res


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        sys.stderr.write(__doc__)
        return 2
    results = [check(p) for p in args]
    if "--json" in argv:
        print(json.dumps(results, indent=1))
    else:
        for r in results:
            failed = [k for k, v in r["checks"].items() if not v]
            print(f"{'PASS' if r['pass'] else 'FAIL'}  {r['ssot']}" + (f"  failed: {', '.join(failed)}" if failed else ""))
            for n in r["notes"]:
                print(f"       note: {n}")
    return 0 if all(r["pass"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
