#!/usr/bin/env python3
"""
token_kaizen.py — the ARCS window-cost kaizen instrument.

Kaizen = one small, continuous improvement per cycle. This script measures the
FIXED PER-TURN FLOOR (the cost paid on every turn of every session, before any
work happens) deterministically, appends a dated row to a ledger, and reports:

  (a) the current floor broken down by source,
  (b) the delta vs the last run — i.e. whether last cycle's cut LANDED,
  (c) a ranked shortlist of candidate cuts, biggest measured lever first.

MECHANICAL vs JUDGMENT (NOTOMATION): this script only *measures and ranks*. It
never picks or applies the cut — that stays human-owned (or the weekly session's
judgment). Choosing exactly ONE cut and recording its rationale is the human step;
the script scaffolds the decision, it does not make it.

Effective-token weighting (per 2026-09-08 analysis): cache_read x0.1, cache_write
x2, output x5. The floor is re-read every turn, so most of it is cache_read after
turn 1 — but it is still paid, and it caps how lean a session can ever be. This
script measures the *raw* floor (the thing a cut actually shrinks); the effective
multipliers are documented here so the weekly write-up can translate raw -> billed.

stdlib only. Run from anywhere; paths resolve against the repo root (git toplevel).
"""
from __future__ import annotations
import json, os, subprocess, sys, datetime, glob

CHARS_PER_TOKEN = 4  # coarse but stable estimator; consistent across runs is what matters

def repo_root() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True,
            stderr=subprocess.DEVNULL).strip()
    except Exception:
        return os.getcwd()

ROOT = repo_root()
LEDGER = os.path.join(ROOT, "_STATE", "token-kaizen", "ledger.jsonl")

# Docs auto-loaded into the system prompt on every turn (CLAUDE.md @-imports the others).
AUTOLOADED_DOCS = ["CLAUDE.md", "AGENTS.md", "WORLD.md"]

def bytes_of(path: str) -> int:
    try:
        return os.path.getsize(os.path.join(ROOT, path))
    except OSError:
        return 0

def tok(nbytes: int) -> int:
    return round(nbytes / CHARS_PER_TOKEN)

def measure() -> dict:
    docs = {f: bytes_of(f) for f in AUTOLOADED_DOCS}
    docs_bytes = sum(docs.values())

    # Local MCP roster (the piece a script can see). App-level connectors/plugins
    # live outside the repo and are pruned per-session in the client, not here —
    # flagged as a lever, not measured.
    mcp_servers = []
    for cfg in [os.path.join(ROOT, ".mcp.json"),
                os.path.expanduser("~/.claude/mcp.json")]:
        try:
            with open(cfg) as fh:
                mcp_servers += list(json.load(fh).get("mcpServers", {}).keys())
        except Exception:
            pass

    allow = 0
    for s in [os.path.join(ROOT, ".claude/settings.json"),
              os.path.join(ROOT, ".claude/settings.local.json")]:
        try:
            with open(s) as fh:
                allow += len(json.load(fh).get("permissions", {}).get("allow", []))
        except Exception:
            pass

    return {
        "docs_bytes": docs,
        "docs_tokens_est": tok(docs_bytes),
        "mcp_servers_local": sorted(set(mcp_servers)),
        "settings_allow": allow,
    }

def rank_levers(m: dict) -> list[dict]:
    """Deterministic candidate shortlist, biggest measured lever first."""
    levers = []
    # 1. Biggest auto-loaded doc — every byte here is paid every turn, forever.
    biggest = max(m["docs_bytes"].items(), key=lambda kv: kv[1])
    levers.append({
        "lever": "lean-autoloaded-doc",
        "target": biggest[0],
        "measured": f"{biggest[1]}B (~{tok(biggest[1])} tok/turn)",
        "note": "Trim dead history / relocate to _ARCHIVE (not @-imported). "
                "Largest of the three files auto-loaded every turn.",
    })
    # 2. Session-level connector/plugin prune (the floor's biggest chunk per the
    #    2026-09-08 analysis — hundreds of deferred tool schemas re-read each turn).
    levers.append({
        "lever": "prune-session-connectors",
        "target": "app connector/plugin roster",
        "measured": "not repo-visible; enumerate via /mcp + plugin list per session",
        "note": "Biggest floor cut available. Turn off connectors a session won't "
                "use (stripe/supabase/chrome/computer-use/resend...) before starting.",
    })
    # 3. Allow-list rot — legibility more than tokens, but cheap and measurable.
    if m["settings_allow"] >= 50:
        levers.append({
            "lever": "collapse-allow-list",
            "target": ".claude/settings.json",
            "measured": f"{m['settings_allow']} allow entries",
            "note": "Collapse opaque MCP-UUID tools to named servers; config debt.",
        })
    return levers

def last_row() -> dict | None:
    try:
        with open(LEDGER) as fh:
            rows = [json.loads(l) for l in fh if l.strip()]
        return rows[-1] if rows else None
    except FileNotFoundError:
        return None

def main():
    m = measure()
    prev = last_row()
    today = datetime.date.today().isoformat()

    delta = None
    cut_landed = None
    if prev:
        pf = prev["floor"]["docs_tokens_est"]
        cf = m["docs_tokens_est"]
        delta = {
            "docs_tokens_est": cf - pf,
            "settings_allow": m["settings_allow"] - prev["floor"]["settings_allow"],
        }
        # "Landed" = did the floor actually shrink since the cut was proposed.
        pc = prev.get("this_cut") or {}
        if pc:
            landed = cf < pf if pc.get("lever") in (
                "lean-autoloaded-doc",) else None
            cut_landed = {
                "proposed": pc.get("lever"),
                "target": pc.get("target"),
                "docs_delta_tokens": cf - pf,
                "landed": landed,  # None = not mechanically verifiable here (human confirms)
            }

    row = {
        "date": today,
        "floor": m,
        "delta_vs_last": delta,
        "last_cut_status": cut_landed,
        "candidate_levers": rank_levers(m),
        # this_cut is filled by the human/weekly session AFTER choosing ONE cut.
        # The script leaves it null; a chosen cut is written back via --record-cut.
        "this_cut": None,
    }

    if "--record-cut" in sys.argv:
        # scaffold: token_kaizen.py --record-cut lean-autoloaded-doc AGENTS.md "why"
        i = sys.argv.index("--record-cut")
        args = sys.argv[i+1:i+4]
        if len(args) >= 2:
            row["this_cut"] = {
                "lever": args[0], "target": args[1],
                "rationale": args[2] if len(args) > 2 else "",
            }

    if "--dry-run" in sys.argv:
        print(json.dumps(row, indent=2))
        return

    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "a") as fh:
        fh.write(json.dumps(row) + "\n")

    # Human-readable summary
    print(f"[token-kaizen] {today}  floor(docs)=~{m['docs_tokens_est']} tok  "
          f"allow={m['settings_allow']}")
    for f, b in m["docs_bytes"].items():
        print(f"    {f:12s} {b:>7}B  ~{tok(b)} tok")
    if delta:
        d = delta["docs_tokens_est"]
        arrow = "DOWN" if d < 0 else ("UP" if d > 0 else "flat")
        print(f"  delta vs last run: docs {d:+d} tok ({arrow})")
    if cut_landed:
        print(f"  last cut: {cut_landed['proposed']} -> {cut_landed['target']} "
              f"({cut_landed['docs_delta_tokens']:+d} tok, landed={cut_landed['landed']})")
    print("  candidate cuts (pick ONE, human judgment):")
    for lv in row["candidate_levers"]:
        print(f"    - {lv['lever']}: {lv['target']}  [{lv['measured']}]")
    print(f"  ledger: {LEDGER}")

if __name__ == "__main__":
    main()
