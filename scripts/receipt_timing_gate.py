#!/usr/bin/env python3
"""receipt_timing_gate: a Receipt create path must persist horizon+reviewDate and
time its debrief by horizon — never a blind T+7.

Class it blocks (2026-09-24): both Receipt create paths (src/app/api/compass/route.ts
and src/app/api/receipts/save/route.ts) wrote `window`/`reminderDate` but never the
canonical, @@index([horizon])-indexed `horizon` column nor `reviewDate` — 0/249 rows
in prod carried either. Every receipt got a flat `Date.now() + 7 * 86400000`
reminderDate, so the debrief asked "did this land?" 7 days out even for a 3-year
decision. The timing engine was blind by construction. See
_QUEUE/induced-backlog.jsonl :: outcome-loop-timing-wiring-* and src/lib/horizon.ts.

Rule (deterministic, stdlib-only): a checked file that contains a Prisma Receipt
`.create(` MUST
  (a) set a `horizon:` key in the create data,
  (b) set a `reviewDate:` key, and
  (c) NOT assign `reminderDate:` from a raw `Date.now() + <n> * 86400000` literal
      (the blind-offset anti-pattern) — route it through reminderDateForWindow.
A file with no Receipt `.create(` is PASS (not a create path). This makes a NEW,
third create path born without horizon-timing UN-COMMITTABLE.

Usage: python3 scripts/receipt_timing_gate.py <file.ts> [...]   (exit 1 on any FAIL)
       (no args → checks the two known create-path routes)
"""
import re, sys, os

DEFAULT_TARGETS = [
    "src/app/api/compass/route.ts",
    "src/app/api/receipts/save/route.ts",
]

# `prisma.receipt.create(` / `tx.receipt.create(` / `.receipt.create(` — the create path.
CREATE_RE = re.compile(r"\.receipt\.create\s*\(", re.I)
HORIZON_KEY_RE = re.compile(r"\bhorizon\s*:", re.I)
REVIEWDATE_KEY_RE = re.compile(r"\breviewDate\s*:")
# Blind-offset anti-pattern: reminderDate assigned from a hardcoded N-day literal.
BLIND_REMINDER_RE = re.compile(
    r"reminderDate\s*:\s*[^,\n}]*Date\.now\(\)\s*\+\s*\d+\s*\*\s*86400000"
)


def analyze(text):
    if not CREATE_RE.search(text):
        return ("PASS", "no Receipt .create( — not a create path")
    problems = []
    if not HORIZON_KEY_RE.search(text):
        problems.append("missing `horizon:` in the create data")
    if not REVIEWDATE_KEY_RE.search(text):
        problems.append("missing `reviewDate:` in the create data")
    m = BLIND_REMINDER_RE.search(text)
    if m:
        problems.append(
            "blind reminderDate offset `%s` — use reminderDateForWindow(window, ...)"
            % m.group(0).strip()
        )
    if problems:
        return ("FAIL", "; ".join(problems))
    return ("PASS", "persists horizon+reviewDate; reminderDate horizon-scaled")


def main(argv):
    targets = argv[1:] or DEFAULT_TARGETS
    any_fail = False
    for path in targets:
        if not os.path.isfile(path):
            # A staged deletion or a path outside the repo — nothing to gate.
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            verdict, detail = analyze(fh.read())
        print(f"{verdict}  {path}  — {detail}")
        if verdict == "FAIL":
            any_fail = True
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
