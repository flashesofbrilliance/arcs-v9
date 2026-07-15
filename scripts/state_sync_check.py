#!/usr/bin/env python3
"""State-sync drift check — advisory only, never fails the build.

Compares specific claims in canon files (CLAUDE.md, AGENTS.md) against what
actually exists in the codebase. Each check is a narrow, literal assertion
(a grep, a file-exists) — not a heuristic — so false positives should mean
the check itself is wrong, not that judgment was involved.

Extend CHECKS below as new stale-canon findings surface (e.g. from the
Drift Sentry routine or a manual audit). This script only ever reports;
it never edits canon (canon collisions escalate to a human, per repo
governance — see _CANON and the Drift Sentry scheduled task).
"""
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def read(path: str) -> str:
    p = REPO_ROOT / path
    return p.read_text() if p.exists() else ""


def grep(pattern: str, path: str) -> bool:
    return bool(re.search(pattern, read(path)))


def path_exists(path: str) -> bool:
    return (REPO_ROOT / path).exists()


def any_file_contains(glob: str, pattern: str) -> bool:
    for p in REPO_ROOT.glob(glob):
        if p.is_file() and re.search(pattern, p.read_text(errors="ignore")):
            return True
    return False


# Each check: (id, claim, assertion) — assertion returns True if the canon
# claim still matches reality; False means drift (canon says X, code says not-X).
CHECKS = [
    (
        "atg-not-built",
        "CLAUDE.md: 'What's NOT built yet' lists ATG as backlog",
        lambda: not grep(r'"tributaries":\s*\[', "src/app/api/compass/route.ts"),
    ),
    (
        "outcome-handler-backlog",
        "AGENTS.md: Outcome handler (PATCH /api/receipts/[id]) listed as P1 backlog",
        lambda: not path_exists("src/app/api/receipts/[receiptId]/outcome"),
    ),
    (
        "sage-wired",
        "AGENTS.md: Sage operator listed READY with no wiring note — check it's still unwired",
        lambda: not any_file_contains("src/**/*.ts*", r"svc/sage"),
    ),
]


def main() -> int:
    drift = []
    for check_id, claim, assertion in CHECKS:
        ok = assertion()
        status = "OK" if ok else "DRIFT"
        print(f"[{status}] {check_id}: {claim}")
        if not ok:
            drift.append((check_id, claim))

    summary_path = subprocess.os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a") as f:
            f.write("### State-sync drift check (advisory)\n\n")
            if drift:
                f.write("| id | canon claim contradicted by code |\n|---|---|\n")
                for check_id, claim in drift:
                    f.write(f"| `{check_id}` | {claim} |\n")
                f.write(
                    "\n_Advisory only — does not block merge. "
                    "Fix by editing the canon file directly (never resolve "
                    "unilaterally if the claim is contested)._\n"
                )
            else:
                f.write("No known drift. All tracked canon claims match code.\n")

    # Always exit 0 — this check reports, it does not gate.
    return 0


if __name__ == "__main__":
    sys.exit(main())
