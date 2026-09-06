#!/usr/bin/env python3
"""snapshot_prune_ui_artifacts.py — keep _STATE/snapshot.json `ui_artifacts` honest.

Drops every call_briefs / product_status_pages entry whose `file` no longer exists in the
tracked tree (git ls-files), and records what was pruned. Mechanical; run after retiring a
brief. Found necessary 2026-09-06 when integrity_gate flagged 9 retired public/*.html cites.

    python3 scripts/snapshot_prune_ui_artifacts.py            # apply
    python3 scripts/snapshot_prune_ui_artifacts.py --dry-run  # report only
"""
import json, subprocess, sys
from datetime import datetime, timezone

SNAP = "_STATE/snapshot.json"
dry = "--dry-run" in sys.argv
tracked = set(subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split("\n"))
snap = json.load(open(SNAP))
ui = snap.get("ui_artifacts", {})
pruned = []
for key in ("call_briefs", "product_status_pages"):
    keep = []
    for row in ui.get(key, []):
        (keep if row.get("file") in tracked else pruned).append(row)
    ui[key] = keep
for r in pruned:
    print(f"prune {r.get('file')}  ({r.get('subdomain')})")
if not pruned:
    print("nothing to prune")
elif not dry:
    ui["_note"] = (ui.get("_note", "").split(" STALE ")[0].strip()
                   + f" Pruned {len(pruned)} retired entries on {datetime.now(timezone.utc).date()} via scripts/snapshot_prune_ui_artifacts.py.")
    ui["pruned"] = ui.get("pruned", []) + [{"file": r.get("file"), "subdomain": r.get("subdomain"), "pruned_at": str(datetime.now(timezone.utc).date())} for r in pruned]
    json.dump(snap, open(SNAP, "w"), indent=2, ensure_ascii=False); open(SNAP, "a").write("\n")
    print(f"wrote {SNAP}")
