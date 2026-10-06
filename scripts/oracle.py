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
  oracle next <ns> --dry-run print the id `next` WOULD allocate; writes nothing (no counter,
                             no pulse beat)
  oracle --self-test         prove the argument guard in a throwaway dir (never touches ROOT)

Unknown flags and extra arguments are REJECTED (exit 2), never ignored. On 2026-10-03 a
`next seed --dry-run` was silently treated as a real `next seed`: the counter moved and a
pulse beat was stamped for an allocation nobody meant to make.
  oracle next handoff        the handoff namespace counts MINOR versions of `# Handoff — v3.N.0`
                             blocks (scripts/handoff_fold.py molt takes its version from here and
                             never computes one). Before allocating, the counter is raised to the
                             highest v3.N.0 already on disk (CLAUDE.md + _ARCHIVE/handoffs.md), so
                             an off-oracle mint can never be re-issued. 2026-10-06: fold computed
                             its own highest+1 and v3.101.0 shipped twice (#893, #894).
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


HANDOFF_TITLE = re.compile(r"^# Handoff — v3\.(\d+)\.\d+ ", re.M)


def _handoff_high():
    """Highest minor N among '# Handoff — v3.N.x' titles in CLAUDE.md and the archive."""
    hi = 0
    for rel in ("CLAUDE.md", os.path.join("_ARCHIVE", "handoffs.md")):
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            hi = max([hi] + [int(n) for n in HANDOFF_TITLE.findall(open(p, encoding="utf-8").read())])
    return hi


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


def nxt(ns, dry_run=False):
    d = _load()
    # seed the counter from live truth on first use of the adr namespace
    if ns == "adr" and "adr" not in d:
        hi = max(_adr_numbers() or [0])
        d["adr"] = hi
    # handoff: never below what is already on disk (a hand-written block must not be re-issued)
    if ns == "handoff":
        d["handoff"] = max(d.get("handoff", 0), _handoff_high())
    new = d.get(ns, 0) + 1
    if dry_run:
        # a preview must look without touching: no counter write, no pulse beat
        print(new)
        sys.stderr.write(f"oracle: dry run, {ns} would allocate {new}. Nothing written.\n")
        return
    d[ns] = new
    _save(d)
    # oracle -> pulse strand: an allocation is a beat. Stamp the pulse's `oracle`
    # subsystem so its flatline guard has an activity signal beyond the committed
    # counter's git timestamp. Best-effort, never fails an allocation (local-first;
    # pulse may be absent on another machine). The git timestamp of _oracle.json
    # remains the authoritative, tamper-evident proof-of-life either way.
    try:
        subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "pulse.py"),
                        "stamp", "oracle"], capture_output=True, timeout=10)
    except Exception:
        pass
    print(new)
    sys.stderr.write(
        f"oracle: allocated {ns}={new}. COMMIT _SEEDS/_oracle.json now; "
        f"if the push is non-ff-rejected, re-fetch and re-run (someone took {new}).\n"
    )


def sync(ns, to=None):
    """Reconcile a lagging counter to live truth (adr: audit high-water; else --to N).
    Refuses to move a counter DOWN — that would re-issue taken numbers."""
    d = _load()
    cur = d.get(ns, 0)
    if ns == "adr" and to is None:
        to = max(_adr_numbers() or [0])
    if ns == "handoff" and to is None:
        to = _handoff_high()
    if to is None:
        sys.stderr.write(f"oracle: sync {ns} needs --to N (only adr and handoff can self-derive)\n"); sys.exit(2)
    to = int(to)
    if to < cur:
        sys.stderr.write(f"oracle: refusing to lower {ns} {cur} -> {to} (would re-issue taken ids)\n"); sys.exit(1)
    d[ns] = to
    _save(d)
    print(f"oracle: {ns} synced {cur} -> {to}. COMMIT _SEEDS/_oracle.json.")


USAGE = "usage: oracle now | peek <ns> | next <ns> [--dry-run] | audit adr | sync <ns> [--to N] | --self-test\n"

# command -> (positional count after the command, flags with no value, flags taking one value)
SPEC = {
    "now":   (0, set(), set()),
    "peek":  (1, set(), set()),
    "next":  (1, {"--dry-run"}, set()),
    "audit": (1, set(), set()),
    "sync":  (1, set(), {"--to"}),
}


def _usage_error(msg):
    sys.stderr.write(f"oracle: {msg}\n" + USAGE)
    sys.exit(2)


def _parse(args):
    """Strict parse: every token must be a known positional or flag for this command.
    Returns (cmd, positionals, flags dict). Exits 2 on anything unrecognized."""
    cmd, rest = args[0], args[1:]
    if cmd not in SPEC:
        _usage_error(f"unknown command {cmd!r}")
    npos, bools, valued = SPEC[cmd]
    pos, flags, i = [], {}, 0
    while i < len(rest):
        tok = rest[i]
        if tok in bools:
            flags[tok] = True
        elif tok in valued:
            if i + 1 >= len(rest) or rest[i + 1].startswith("--"):
                _usage_error(f"{tok} needs a value")
            flags[tok] = rest[i + 1]
            i += 1
        elif tok.startswith("-"):
            _usage_error(f"unknown flag {tok!r} for {cmd!r} (refusing to ignore it)")
        else:
            pos.append(tok)
        i += 1
    if len(pos) != npos:
        _usage_error(f"{cmd!r} takes {npos} argument(s), got {len(pos)}: {pos}")
    return cmd, pos, flags


def self_test():
    """Run the CLI in a throwaway project dir and assert the guard holds. Never touches ROOT."""
    import tempfile
    me = os.path.abspath(__file__)
    fails = 0
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, CLAUDE_PROJECT_DIR=tmp)
        counter = os.path.join(tmp, "_SEEDS", "_oracle.json")

        def run(*a):
            return subprocess.run([sys.executable, me, *a], env=env, capture_output=True, text=True)

        def check(name, ok):
            nonlocal fails
            print(("PASS " if ok else "FAIL ") + name)
            fails += 0 if ok else 1

        r = run("next", "seed", "--dry-run")
        check("next --dry-run previews 1", r.returncode == 0 and r.stdout.strip() == "1")
        check("next --dry-run writes no counter", not os.path.exists(counter))
        r = run("next", "seed", "--dryrun")
        check("unknown flag on next exits 2", r.returncode == 2)
        check("unknown flag writes no counter", not os.path.exists(counter))
        check("peek with extra arg exits 2", run("peek", "seed", "extra").returncode == 2)
        check("sync --to with no value exits 2", run("sync", "seed", "--to").returncode == 2)
        check("sync with unknown flag exits 2", run("sync", "seed", "--to", "5", "--force").returncode == 2)
        check("unknown command exits 2", run("allocate", "seed").returncode == 2)
        r = run("next", "seed")
        check("real next allocates 1", r.returncode == 0 and r.stdout.strip() == "1")
        check("real next writes the counter", json.load(open(counter)).get("seed") == 1)
        r = run("next", "seed", "--dry-run")
        check("dry run after allocation previews 2", r.stdout.strip() == "2")
        check("dry run leaves counter at 1", json.load(open(counter)).get("seed") == 1)
        open(os.path.join(tmp, "CLAUDE.md"), "w").write("# Handoff — v3.112.0 (2026-10-06)\n\nx\n")
        json.dump({"handoff": 50}, open(counter, "w"))
        r = run("next", "handoff")
        check("handoff next lifts a stale counter past disk (50 -> 113)", r.stdout.strip() == "113")
        r = run("next", "handoff")
        check("handoff next is monotonic (114)", r.stdout.strip() == "114")
    print(f"oracle self-test: {14 - fails}/14")
    sys.exit(1 if fails else 0)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__.strip().splitlines()[0]); return
    if args == ["--self-test"]:
        self_test()
    cmd, pos, flags = _parse(args)
    if cmd == "now":
        now()
    elif cmd == "peek":
        peek(pos[0])
    elif cmd == "next":
        nxt(pos[0], dry_run=flags.get("--dry-run", False))
    elif cmd == "audit":
        if pos[0] != "adr":
            _usage_error(f"audit supports only 'adr', got {pos[0]!r}")
        audit_adr()
    elif cmd == "sync":
        sync(pos[0], flags.get("--to"))


if __name__ == "__main__":
    main()
