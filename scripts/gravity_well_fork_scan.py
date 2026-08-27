#!/usr/bin/env python3
"""gravity_well_fork_scan — the ziggurat decomposition detector.

A net-new folksonomy cluster is not flat forever. Once it accretes enough MASS
(member count) and GRAVITY (cross-repo/cross-domain spread), it should DECOMPOSE
into its own organism — a dedicated spec / ADR family / seed — rather than stay a
line item. This is the mechanized version of the manual Norse-witness-stack fork
(runtime/specs/ROM-CANDIDATES-norse-witness.md).

It does NOT fork anything. It DETECTS density and emits a FORK RECOMMENDATION into
the canon-propagation queue (kind:"fork", default "no"). The human forks via
/canon-review. NOTOMATION: detect + recommend, never author under write-lock.

  score = mass (count) × gravity (distinct repos among member_refs)
  fork recommended when score >= FORK_SCORE_MIN AND count >= FORK_MASS_MIN.

High-value SINGLE-repo net-news (e.g. the Norse stack: 8 members, 1 repo) do NOT
fork on mass×gravity — their pull is value, not cross-domain mass; they graduate
via the ESCALATE→promotion path instead. That distinction is intentional.

Usage:  python3 scripts/gravity_well_fork_scan.py <folksonomy.json> [--emit]
        --emit appends fork items to _INBOX/canon-propagation-queue.json.
Stdlib only. Exit 0 always.
"""
import json, os, sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
QUEUE = os.path.join(ROOT, "_INBOX/canon-propagation-queue.json")

FORK_SCORE_MIN = 16   # e.g. count 8 × 2 repos, or 6 × 3 — a real cross-domain well
FORK_MASS_MIN = 5     # floor: a cluster under 5 members isn't dense enough to fork


def repos_of(member_refs):
    out = set()
    for r in member_refs or []:
        out.add(r.split(":", 1)[0].strip() if ":" in r else "?")
    return out


def scan(folk):
    recs = []
    for c in folk.get("clusters", []):
        mass = int(c.get("count", 0))
        repos = repos_of(c.get("member_refs"))
        gravity = len(repos)
        score = mass * gravity
        if score >= FORK_SCORE_MIN and mass >= FORK_MASS_MIN:
            recs.append({
                "id": f"fork-{c.get('tag','?')}",
                "kind": "fork",
                "default": "no",
                "title": f"{c.get('tag','?')} ({mass} members × {gravity} repos = {score})",
                "proposal": (f"gravity-well: cluster '{c.get('tag')}' has mass {mass} across "
                             f"{gravity} repos ({', '.join(sorted(repos))}) — dense enough to fork "
                             f"into its own organism (spec/ADR/seed). {c.get('promotion_pattern','')}"),
                "score": score,
            })
    recs.sort(key=lambda r: -r["score"])
    return recs


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    emit = "--emit" in sys.argv
    if not args:
        print("usage: gravity_well_fork_scan.py <folksonomy.json> [--emit]")
        return
    folk = json.load(open(args[0], encoding="utf-8"))
    recs = scan(folk)
    print(f"gravity-well: {len(recs)} fork-worthy cluster(s) (score>={FORK_SCORE_MIN}, mass>={FORK_MASS_MIN})")
    for r in recs:
        print(f"  FORK  score={r['score']:>3}  {r['title']}")
    if emit and recs:
        q = {"items": []}
        if os.path.exists(QUEUE):
            try:
                q = json.load(open(QUEUE, encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
        existing = {i.get("id") for i in q.get("items", [])}
        added = [r for r in recs if r["id"] not in existing]
        q.setdefault("items", []).extend(added)
        json.dump(q, open(QUEUE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"gravity-well: appended {len(added)} fork item(s) to the canon-propagation queue")
    elif not emit:
        print("gravity-well: dry-run (pass --emit to append fork recommendations to the queue)")


if __name__ == "__main__":
    main()
