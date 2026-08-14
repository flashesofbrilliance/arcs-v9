#!/usr/bin/env python3
"""oracle — a sequence + time authority for the distributed multi-session model.

The problem: parallel sessions/branches guess "the next ADR number" independently and
COLLIDE (on main today: ADR-024/025/031/032 each doubled). Humans cannot hand-allocate a
shared namespace concurrently — it needs a *serialization authority*, exactly as git
serializes file order.

The realization (honest scope): this is a **logical clock backed by git**, not GPS/atomic
hardware. "Atomic clock oracle" is the north-star metaphor; what actually enforces atomicity
is **git's non-fast-forward rejection**. Allocation = read the committed counter, take next,
commit the increment. If two sessions both take 57, the second's push is rejected (non-ff);
it re-fetches and takes 58. Git IS the atomic gate — the same guarantee germinate's SPEC names
for tracked files. Wall-clock is *grounded* (system clock, surfaced explicitly) to prevent the
confabulated-timestamp failure the session-start hook already guards against; it MAY later be
backed by NTP, but is never silently trusted.

Counter registry: _SEEDS/_oracle.json  e.g. {"adr": 56, "seed": 11, "receipt": 340}

  oracle now                 grounded ISO-8601 timestamp (host clock; explicit, not confabulated)
  oracle peek <ns>           show the current high-water mark for a namespace (no allocation)
  oracle next <ns>           allocate: bump the counter, print the new id. Caller MUST commit
                             _SEEDS/_oracle.json — the commit (and git's non-ff lock) is what
                             makes the allocation authoritative across sessions.
  oracle audit adr           scan _DECISIONS on the working tree: collisions, gaps, next-free
                             (read-only; the authority for reconciling the existing mess)

Stdlib only. Exit 0 on success; non-zero only on misuse.
"""
import json, os, sys, glob, re, subprocess, datetime

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
ORACLE = os.path.join(ROOT, "_SEEDS", "_oracle.json")
DECISIONS = os.path.join(ROOT, "_DECISIONS")


def _load():
    if os.path.exists(ORACLE):
        try:
            return json.load(open(ORACLE))
        except Exception:
            pass
    return {}


def _save(d):
    os.makedirs(os.path.dirname(ORACLE), exist_ok=True)
    with open(ORACLE, "w") as f:
        json.dump(d, f, indent=2, sort_keys=True)
        f.write("\n")


def now():
    # Host clock, surfaced explicitly. Honest: this is the machine's time, not a hardware
    # atomic reference. Callers stamp with THIS, never with a guessed date.
    print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))


def _adr_numbers():
    nums = {}
    for p in glob.glob(os.path.join(DECISIONS, "ADR-*.md")):
        m = re.search(r"ADR-(\d+)", os.path.basename(p))
        if m:
            nums.setdefault(int(m.group(1)), []).append(os.path.basename(p))
    return nums


def audit_adr():
    nums = _adr_numbers()
    collisions = {n: files for n, files in nums.items() if len(files) > 1}
    used = sorted(nums)
    hi = used[-1] if used else 0
    gaps = [n for n in range(1, hi + 1) if n not in nums]
    print(f"oracle/adr: {len(nums)} numbers, high-water {hi}, next-free {hi + 1}")
    if collisions:
        print(f"oracle/adr: {len(collisions)} COLLISION(s):")
        for n in sorted(collisions):
            print(f"  ADR-{n:03d} x{len(collisions[n])}: {', '.join(collisions[n])}")
    if gaps:
        print(f"oracle/adr: gaps (free numbers below high-water): {gaps}")
    if not collisions and not gaps:
        print("oracle/adr: clean — dense, no collisions")
    return collisions, hi, gaps


def peek(ns):
    print(_load().get(ns, 0))


def nxt(ns):
    d = _load()
    # seed the counter from live truth on first use of the adr namespace
    if ns == "adr" and "adr" not in d:
        hi = max(_adr_numbers() or [0])
        d["adr"] = hi
    new = d.get(ns, 0) + 1
    d[ns] = new
    _save(d)
    print(new)
    sys.stderr.write(
        f"oracle: allocated {ns}={new}. COMMIT _SEEDS/_oracle.json now; "
        f"if the push is non-ff-rejected, re-fetch and re-run (someone took {new}).\n"
    )


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__.strip().splitlines()[0]); return
    cmd = args[0]
    if cmd == "now":
        now()
    elif cmd == "peek" and len(args) > 1:
        peek(args[1])
    elif cmd == "next" and len(args) > 1:
        nxt(args[1])
    elif cmd == "audit" and len(args) > 1 and args[1] == "adr":
        audit_adr()
    else:
        sys.stderr.write("usage: oracle now | peek <ns> | next <ns> | audit adr\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
