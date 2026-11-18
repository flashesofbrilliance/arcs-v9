#!/usr/bin/env python3
"""gate_shadow_eval: did a gate's wrong answer reveal itself? A read-only shadow eval over main's history.

Rules are pre-registered in _PATTERNS/2026-11-17-gate-shadow-eval-prereg.md (fixed before the first count):
  bypass event      a commit message records a gate override (--no-verify, INTEGRITY_GATE_BLOCK=0, --allow-hold,
                    or "bypass" near a gate name); the gate is attributed from the message
  revealed FP       a bypass that landed, was not reverted, and whose gate script a LATER commit changed
  bypass-held       a bypass that landed and was not reverted, gate not corrected yet (counted, not classified)
  revealed FN       a commit without a bypass that a later commit reverted ("This reverts commit <sha>")
  unrevealed        everything else: a count, never called "correct" (the upper bound on inliers)

Reads git only; never blocks, never writes unless --json PATH.
  python3 scripts/gate_shadow_eval.py [--rev origin/main] [--since 2026-08-01] [--json OUT]
  python3 scripts/gate_shadow_eval.py --self-test
"""
import argparse
import json
import re
import subprocess
import sys

OVERRIDES = [  # (pattern in the message, gate it names or None)
    (r"INTEGRITY_GATE_BLOCK=0", "integrity_gate"),
    (r"--allow-hold", "phosphor_build"),
    (r"--no-verify", None),
    (r"\bbypass(?:ed)?\b", None),
]
PHRASES = {  # message phrase -> gate script stem, for overrides that do not name their gate
    "kit ledger": "kit_periodic_table", "kit periodic table": "kit_periodic_table",
    "integrity gate": "integrity_gate", "universe snapshot": "universe_snapshot_emit",
}
REVERT = re.compile(r"This reverts commit ([0-9a-f]{7,40})")


def git(*a):
    return subprocess.run(("git",) + a, capture_output=True, text=True, check=True).stdout


def commits(rev, since):
    """[(sha, date, message)] oldest first, first-parent and merged branch commits alike."""
    args = ["log", "--reverse", "--format=%H%x1f%ad%x1f%B%x1e", "--date=short", rev]
    if since:
        args.insert(1, f"--since={since}")
    out = []
    for rec in git(*args).split("\x1e"):
        rec = rec.strip("\n")
        if rec:
            sha, date, msg = rec.split("\x1f", 2)
            out.append((sha, date, msg))
    return out


NEGATION = re.compile(r"\b(never|without|not|no|instead of)\b[^.\n]{0,25}$", re.I)


def attribute(msg, changed=()):
    """Gate stems this message overrides, or [] if it records no override.

    v2 (amendments A1-A3, 2026-11-17): an override token preceded by a negation does not count (A1); a commit
    that changes a gate's own script is documenting it, not bypassing it (A2); a gate is attributed only from
    the line that carries the override (A3)."""
    named, hit = set(), False
    for line in msg.splitlines():
        low = line.lower()
        for pat, gate in OVERRIDES:
            for m in re.finditer(pat, line, re.I):
                if NEGATION.search(line[:m.start()]):
                    continue
                if pat.startswith(r"\bbypass") and not re.search(r"\b(gate|hook|check)\b", low):
                    continue
                hit = True
                if gate:
                    named.add(gate)
                named |= set(re.findall(r"scripts/([a-z0-9_]+)\.py", line)) & set(PHRASES.values())
                named |= {g for ph, g in PHRASES.items() if ph in low}
    if not hit:
        return []
    if named and named <= set(changed):  # A2: the commit edits every gate it names, so it documents them
        return []
    named -= set(changed)
    return sorted(named) or ["unknown"]


SUBJECT_REVERT = re.compile(r"^(revert\b|revert\(|Revert \")", re.I)


def classify(rows, changed_by, fixed_after):
    """rows: commits oldest first. changed_by(i) -> gate stems commit i edits. fixed_after(stem, i) -> a LATER
    fix-typed commit within FIX_WINDOW days edits scripts/<stem>.py (A4). Returns per-commit verdicts."""
    linked = {}
    for sha, _, msg in rows:
        for t in REVERT.findall(msg):
            linked[t] = sha
    def is_reverted(sha):
        return any(sha.startswith(k) for k in linked)
    events = []
    for i, (sha, date, msg) in enumerate(rows):
        subject = msg.splitlines()[0] if msg else ""
        gates = attribute(msg, changed_by(i))
        ev = None
        if gates:
            if is_reverted(sha):
                kind = "bypass-reverted"
            else:
                kind = "revealed-fp" if any(g != "unknown" and fixed_after(g, i) for g in gates) else "bypass-held"
            ev = {"kind": kind, "gates": gates}
        elif is_reverted(sha):
            ev = {"kind": "revealed-fn", "gates": []}
        elif SUBJECT_REVERT.search(subject) and not REVERT.search(msg):
            ev = {"kind": "revert-unlinked", "gates": []}  # A5: a revert names no target sha; counted, not attributed
        if ev:
            ev.update(sha=sha[:8], date=date, subject=subject[:90])
            events.append(ev)
    return events


FIX_WINDOW = 30  # days (A4)


def main_run(rev, since):
    import datetime as dt
    rows = commits(rev, since)
    index = {sha: i for i, (sha, _, _) in enumerate(rows)}
    day = [dt.date.fromisoformat(d) for _, d, _ in rows]
    subj = [m.splitlines()[0].lower() if m else "" for _, _, m in rows]
    gate_stems = set(PHRASES.values()) | {g for _, g in OVERRIDES if g}
    edits = {}
    for stem in gate_stems:
        log = git("log", "--format=%H", rev, "--", f"scripts/{stem}.py")
        edits[stem] = sorted(index[x] for x in log.split() if x in index)
    by_commit = {}
    for stem, idx in edits.items():
        for j in idx:
            by_commit.setdefault(j, set()).add(stem)
    # A2: the pre-commit hook wires every gate, so a commit editing it documents all of them
    for x in git("log", "--format=%H", rev, "--", "scripts/git-hooks/pre-commit").split():
        if x in index:
            by_commit.setdefault(index[x], set()).update(gate_stems)

    def fixed_after(stem, i):
        return any(j > i and subj[j].startswith("fix") and (day[j] - day[i]).days <= FIX_WINDOW
                   for j in edits.get(stem, []))
    events = classify(rows, lambda i: by_commit.get(i, set()), fixed_after)
    counts = {}
    for e in events:
        counts[e["kind"]] = counts.get(e["kind"], 0) + 1
    counts["unrevealed"] = len(rows) - len(events)
    return {"rev": rev, "since": since, "rules": "v2 (A1-A5)", "commits": len(rows), "counts": counts, "events": events}


def self_test():
    rows = [
        ("a" * 40, "2026-11-01", "feat: x\n\nCommitted with --no-verify; the kit ledger check false-blocks merges."),
        ("b" * 40, "2026-11-02", "fix(ui-kit): kit ledger check accepts merges"),
        ("c" * 40, "2026-11-03", "merge: INTEGRITY_GATE_BLOCK=0 used once"),
        ("d" * 40, "2026-11-04", "feat: y"),
        ("e" * 40, "2026-11-05", "Revert \"feat: y\"\n\nThis reverts commit " + "d" * 12 + "."),
        ("f" * 40, "2026-11-06", "docs: we bypassed nothing here, just prose"),
        ("g" * 40, "2026-11-07", "fix(x): fixed the surface, never --no-verify"),                     # A1
        ("h" * 40, "2026-11-08", "feat(gate): integrity gate; INTEGRITY_GATE_BLOCK=0 opts out once"),  # A2
        ("i" * 40, "2026-11-09", "revert(ui): drop the logomark"),                                     # A5
        ("j" * 40, "2026-11-10", "chore: refactor integrity gate output"),                             # A4: not fix-typed
    ]
    changed = {1: {"kit_periodic_table"}, 7: {"integrity_gate"}, 9: {"integrity_gate"}}
    edits = {"kit_periodic_table": [1], "integrity_gate": [7, 9]}
    fixed_after = lambda stem, i: any(j > i and rows[j][2].startswith("fix") for j in edits.get(stem, []))
    ev = {e["sha"][0]: e for e in classify(rows, lambda i: changed.get(i, set()), fixed_after)}
    assert ev["a"]["kind"] == "revealed-fp" and ev["a"]["gates"] == ["kit_periodic_table"], ev["a"]
    assert ev["c"]["kind"] == "bypass-held" and ev["c"]["gates"] == ["integrity_gate"], ev["c"]  # j is chore, not fix
    assert ev["d"]["kind"] == "revealed-fn", ev["d"]
    assert ev["i"]["kind"] == "revert-unlinked", ev["i"]
    for k in "befgh j".replace(" ", ""):
        assert k not in ev, (k, ev.get(k))
    print("gate_shadow_eval: self-test ok (v1 rules + amendments A1-A5)")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rev", default="origin/main")
    ap.add_argument("--since", default="")
    ap.add_argument("--json")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    r = main_run(a.rev, a.since)
    if a.json:
        open(a.json, "w").write(json.dumps(r, indent=1) + "\n")
    print(f"gate_shadow_eval: {r['commits']} commits on {r['rev']}" + (f" since {r['since']}" if r["since"] else ""))
    print("  " + " · ".join(f"{k} {v}" for k, v in sorted(r["counts"].items())))
    for e in r["events"]:
        print(f"  {e['kind']:15} {e['sha']} {e['date']} [{','.join(e['gates'])}] {e['subject']}")


if __name__ == "__main__":
    sys.exit(main())
