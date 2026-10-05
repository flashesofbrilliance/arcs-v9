#!/usr/bin/env python3
"""Null-userId gate: a logged-out caller must never reach a `where: { userId }`.

Class: `const userId = session?.user?.id ?? null` then `prisma.x.findMany({ where:
{ userId } })`. Prisma reads `userId: null` as "IS NULL" (every anonymous row) and
`userId: undefined` as no filter at all (every row). Either way a logged-out
request reads or mutates rows it does not own.

Rule (per function body, approximated per file region): after a userId is taken
from `session?.user?.id`, any line that both mentions `where` and uses bare
`userId` (shorthand `{ userId }` / `userId,` / `userId: userId`) must be preceded
by a guard: `if (!userId)` (return/redirect/throw) or a `userId ?` ternary on the
same line. Writes (`data: { userId }`) are fine: anonymous rows are by design.

Usage: python3 scripts/null_userid_gate.py [files...]   (default: all of src/)
       python3 scripts/null_userid_gate.py --self-test
Exit 1 on any finding.
"""
import re
import sys
from pathlib import Path

ASSIGN = re.compile(r"\buserId\s*=\s*session\?\.user\?\.id\b")
GUARD = re.compile(r"if\s*\(\s*!\s*userId\b")
# bare userId used as a filter value: `userId }`, `userId,`, `userId: userId`
BARE = re.compile(r"\buserId\s*(?:[,}\n]|:\s*userId\b(?!\s*\?\s))")
# a truthiness check on userId: `userId ?` or `&& userId)` / `if (userId)`
TERNARY = re.compile(r"userId\s*\?(?!\?)|&&\s*userId\b|if\s*\(\s*userId\b")


FUNC = re.compile(r"^\s*(export\s+)?(async\s+)?function\b|^\s*export\s+const\s+\w+\s*=\s*(async\s*)?\(")


def scan(text: str, name: str) -> list[str]:
    out = []
    lines = text.splitlines()
    armed = False      # a session-derived userId is in scope and unguarded
    for i, line in enumerate(lines, 1):
        if FUNC.search(line):
            armed = False  # new handler: a guard in one function never covers the next
        if ASSIGN.search(line):
            armed = True
            continue
        if not armed:
            continue
        if GUARD.search(line):
            armed = False
            continue
        if "where" not in line:
            continue
        # the filter object may span lines: read from `where` up to 6 lines on
        window = "\n".join([line.split("where", 1)[1]] + lines[i:i + 6])
        window = window.split(")", 1)[0]  # stop at the end of the call
        if BARE.search(window) and not TERNARY.search("\n".join(lines[max(0, i - 3):i])):
            out.append(f"{name}:{i}: session userId reaches a where filter with no `if (!userId)` guard")
    return out


BAD = """
const session = await auth()
const userId = session?.user?.id ?? null
const rows = await prisma.receipt.findMany({ where: { userId } })
export async function POST() {
  const userId = session?.user?.id ?? undefined
  await prisma.receipt.findMany({
    where: {
      status: "OPEN",
      userId,
    },
  })
}
export async function PUT() {
  const userId = session?.user?.id
  await prisma.x.findMany({ where: { userId: userId ?? undefined } })
}
"""
GOOD = """
const session = await auth()
const userId = session?.user?.id ?? null
if (!userId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
const rows = await prisma.receipt.findMany({ where: { userId } })
const w = await prisma.receipt.findMany({ where: { ...(userId ? { userId } : {}) } })
await prisma.x.create({ data: { userId } })
const u = userId ? await prisma.user.findUnique({
  where: { id: userId },
}) : null
"""


def self_test() -> int:
    bad, good = scan(BAD, "bad"), scan(GOOD, "good")
    ok = len(bad) == 3 and not good
    print(f"self-test: bad={len(bad)} (want 3) good={len(good)} (want 0) -> {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    files = [Path(a) for a in argv] or [p for p in Path("src").rglob("*") if p.suffix in (".ts", ".tsx")]
    findings = []
    for p in files:
        if p.suffix in (".ts", ".tsx") and p.is_file():
            findings += scan(p.read_text(errors="replace"), str(p))
    for f in findings:
        print(f, file=sys.stderr)
    if findings:
        print(f"null_userid_gate: {len(findings)} finding(s). Return 401 before filtering by userId.", file=sys.stderr)
        return 1
    print(f"null_userid_gate: OK ({len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
