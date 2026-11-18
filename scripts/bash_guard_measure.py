#!/usr/bin/env python3
"""bash_guard_measure.py: score a Bash guard hook's verdict() against real past Bash calls.

Why (dreaming pass 15 ruling, 2026-11-18): the first bash32-shape-guard shipped on a guess and,
measured later, denied 77 working commands to catch 2 refusals. Re-measure here before adding or
changing a guard shape. Read-only; reads ~/.claude/projects/*arcs-v9*/*.jsonl.

For every Bash call in the window it records whether the harness refused it as too old for bash 3.2,
then reports how many calls the hook's verdict(command) would deny and how many of those the
harness really refused. A good shape denies few calls that ran fine.

Usage: python3 scripts/bash_guard_measure.py .claude/hooks/bash32-shape-guard.py [--days 7] [--show 5]
"""
import argparse, importlib.util, json, time
from pathlib import Path

REFUSED = "too old to run it reliably"


def calls(days):
    cut = time.time() - days * 86400
    for d in (Path.home() / ".claude" / "projects").iterdir():
        if "arcs-v9" not in d.name:
            continue
        for f in d.glob("*.jsonl"):
            if f.stat().st_mtime < cut:
                continue
            pending = {}
            for line in f.open(errors="ignore"):
                try:
                    content = (json.loads(line).get("message") or {}).get("content")
                except Exception:
                    continue
                if not isinstance(content, list):
                    continue
                for b in content:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "tool_use" and b.get("name") == "Bash":
                        pending[b.get("id")] = (b.get("input") or {}).get("command", "")
                    elif b.get("type") == "tool_result" and b.get("tool_use_id") in pending:
                        c = b.get("content")
                        text = c if isinstance(c, str) else " ".join(
                            x.get("text", "") for x in c or [] if isinstance(x, dict))
                        yield REFUSED in text, pending.pop(b.get("tool_use_id"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hook")
    ap.add_argument("--days", type=float, default=7)
    ap.add_argument("--show", type=int, default=5)
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("hook", a.hook)
    hook = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook)
    n = refused = denied = hit = 0
    missed, wrong = [], []
    for was_refused, cmd in calls(a.days):
        n += 1
        refused += was_refused
        d = hook.verdict(cmd)
        denied += d
        hit += d and was_refused
        if was_refused and not d:
            missed.append(cmd)
        if d and not was_refused:
            wrong.append(cmd)
    print(f"{a.hook}: {n} Bash calls in {a.days:g}d, {refused} refused by the harness")
    print(f"  denies {denied}: {hit} really refused, {denied - hit} ran fine (or were denied by the live hook)")
    print(f"  catches {hit} of {refused} refusals")
    for label, rows in (("missed", missed), ("denied but ran", wrong)):
        for cmd in rows[:a.show]:
            print(f"  {label}: {cmd[:160]!r}")


if __name__ == "__main__":
    main()
