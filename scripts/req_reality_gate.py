#!/usr/bin/env python3
"""req_reality gate (Frustration Gate for the manufactured-role failure class).

Fails a recoil SSOT that renders a CANDIDACY engagement GREEN while the req it is
chasing is not real. Root cause it blocks: Fanatics (Jul 2026) and HypeLab (Oct 2025)
were both rendered GREEN/HIGH on real warmth while req_reality was 1 (verbal shape, no
JD, no budget). The instrument saw it and the render ignored it. Post-mortem:
_STATE/job-search/postmortem-fanatics.md. Ledger: H3' (hypothesis-ledger.md).

Scale (opportunity.req_reality):
  0  no JD, no decision-owner met
  1  verbal shape, no JD or budget
  2  JD posted or cut, budget implied
  3  JD + budget + you have met the decision-owner

Rules (deterministic, stdlib-only):
  FAIL  candidacy SSOT (6-tab template schema) with req_reality missing / unparseable
  FAIL  candidacy SSOT with y_state GREEN and req_reality <= 1
  WARN  legacy-schema SSOT (cover.yGate / cover.ygate) GREEN with no req_reality
  PASS  everything else (non-candidacy engagements are never gated on this)

Usage: python3 scripts/req_reality_gate.py <ssot.json> [...]   (exit 1 on any FAIL)
"""
import json, sys

CANDIDACY = {"candidacy", "job", "role", "hire"}

def _y(d):
    o = d.get("opportunity") or {}
    for v in (o.get("y_state"), (d.get("cover") or {}).get("yGate"), (d.get("cover") or {}).get("ygate")):
        if isinstance(v, str) and not v.startswith("{{"):
            return v.strip().upper()
    return None

def _rr(d):
    o = d.get("opportunity") or {}
    v = o.get("req_reality")
    if v is None or (isinstance(v, str) and v.startswith("{{")):
        return None
    try:
        return int(str(v).strip())
    except ValueError:
        return "bad"

def check(path):
    try:
        d = json.load(open(path))
    except Exception as e:
        return ("FAIL", f"unreadable JSON ({e})")
    o = d.get("opportunity")
    et = str((o or {}).get("engagement_type", "")).strip().lower()
    y = _y(d)
    rr = _rr(d)
    legacy = o is None
    if legacy:
        if y == "GREEN" and rr is None:
            return ("WARN", "legacy schema rendered GREEN with no opportunity.req_reality (Fanatics-shaped; not blocking)")
        return ("PASS", "legacy schema")
    if et and et not in CANDIDACY:
        return ("PASS", f"engagement_type={et} (not a candidacy)")
    if not et:
        return ("WARN", "opportunity.engagement_type unset; treat as candidacy until declared")
    if rr is None:
        return ("FAIL", "candidacy with no opportunity.req_reality (0..3). Ask it on the first screen and record the answer.")
    if rr == "bad" or not (0 <= rr <= 3):
        return ("FAIL", f"opportunity.req_reality={o.get('req_reality')!r} is not an int 0..3")
    if y == "GREEN" and rr <= 1:
        return ("FAIL", f"y_state GREEN with req_reality={rr}. No req => no GREEN. Render YELLOW/DEGRADED, and spend artifacts only as pilot/product, never as a JD. (manufactured-role class)")
    if rr <= 1 and not o.get("req_reality_basis"):
        return ("WARN", f"req_reality={rr} with no req_reality_basis quote; cite their words")
    return ("PASS", f"y_state={y} req_reality={rr}")

def main(argv):
    if not argv:
        print(__doc__); return 0
    worst = 0
    for p in argv:
        v, msg = check(p)
        mark = {"PASS": "✓", "WARN": "⚠", "FAIL": "✖"}[v]
        print(f"{mark} req_reality_gate {v:4} {p}  — {msg}")
        if v == "FAIL": worst = 1
    return worst

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
