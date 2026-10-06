#!/usr/bin/env python3
"""write_lock — serialize the COLLISION POINTS (writes to main, hot files), not sessions. ADR-085.

The atomic primitive is the same one scripts/oracle.py uses: git's refusal to move a ref to a
commit that does not descend from the ref's current value. Every state change is a new commit
whose parent is the state it was computed from, pushed WITHOUT force. Two racers that read the
same state both build a child of it; the remote accepts the first push and rejects the second
(non-fast-forward / stale old-value). The loser re-reads and re-decides. No server, no daemon.

State lives on dedicated refs on the remote, never on a branch, so the registry is not itself
a hot file and never lands in main's history:
  refs/locks/<name>      lock.json    one write-lock (default name "main")
  refs/locks/leases      leases.json  hot-file leases: path -> holder + expiry

  write_lock.py lock acquire  [--name main] [--ttl 1800] [--reason TXT] [--wait SECS]
  write_lock.py lock release  [--name main]          only the holder may release
  write_lock.py lock status   [--name main]          exit 0 free, 3 held (live), 4 held (stale)
  write_lock.py lock takeover [--name main] [--ttl]  only when expires_at + grace has passed
  write_lock.py lease claim   PATH... [--ttl 7200] [--reason TXT]   all-or-nothing
  write_lock.py lease release PATH...                only your own leases
  write_lock.py lease list
  write_lock.py lease check   PATH... [--block]      warn (exit 0) or block (exit 1) on a
                                                     live lease held by ANOTHER session
  write_lock.py --self-test   local bare repo + two clones; touches nothing else

Global options (before the subcommand): --remote NAME|URL (default origin) · --repo DIR
(default cwd) · --session ID (default $WRITE_LOCK_SESSION, else user@host:<worktree path>) ·
--grace SECS (clock-skew allowance on expiry, default 120) · --prefix REF (default
refs/locks/; use refs/heads/locks/ if a host refuses custom ref namespaces).

Exit codes: 0 ok · 1 refused (held / not yours / leased) · 2 usage · 5 remote unreachable ·
6 push refused with no competing write (hook / ruleset / permission).
TTL is clamped: lock <= 2h, lease <= 4h (re-acquire to extend; a squatter cannot hold forever).
Stdlib only. Expiry is wall-clock: a lock is a lease with a TTL, never a forever-hold.
"""
import getpass, json, os, socket, subprocess, sys, time, datetime

GRACE = 120
ATTEMPTS = 8
MAX_TTL = {"lock": 7200, "lease": 14400}   # anti-squatting: nobody holds past this without re-claiming


class Refused(Exception):
    pass


class Unreachable(Exception):
    pass


class Rejected(Exception):
    """push refused with no competing write (a hook, ruleset or permission), not 'offline'"""


def iso(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Store:
    """CAS over one remote ref holding one JSON file."""

    def __init__(self, repo, remote, ref, fname):
        self.repo, self.remote, self.ref, self.fname = repo, remote, ref, fname
        self.cache = "refs/write-lock-cache/" + ref.replace("/", "_")

    def git(self, *a, check=True, inp=None, env=None):
        p = subprocess.run(["git", "-C", self.repo, *a], input=inp, capture_output=True, text=True,
                           env=dict(os.environ, GIT_TERMINAL_PROMPT="0", **(env or {})))
        if check and p.returncode:
            raise RuntimeError(f"git {' '.join(a)}: {p.stderr.strip()}")
        return p

    def read(self):
        """-> (tip_sha or None, state dict or None). Always from the remote, never a cache."""
        p = self.git("ls-remote", self.remote, self.ref, check=False)
        if p.returncode:
            raise Unreachable(p.stderr.strip() or "ls-remote failed")
        line = p.stdout.strip()
        if not line:
            return None, None
        tip = line.split()[0]
        self.git("fetch", "-q", "--no-tags", self.remote, f"+{self.ref}:{self.cache}")
        return tip, json.loads(self.git("show", f"{tip}:{self.fname}").stdout)

    def write(self, parent, state, msg):
        blob = self.git("hash-object", "-w", "--stdin", inp=json.dumps(state, indent=2, sort_keys=True) + "\n").stdout.strip()
        tree = self.git("mktree", inp=f"100644 blob {blob}\t{self.fname}\n").stdout.strip()
        ident = {"GIT_AUTHOR_NAME": "write-lock", "GIT_AUTHOR_EMAIL": "write-lock@localhost",
                 "GIT_COMMITTER_NAME": "write-lock", "GIT_COMMITTER_EMAIL": "write-lock@localhost"}
        args = ["commit-tree", tree, "-m", msg] + (["-p", parent] if parent else [])
        commit = self.git(*args, env=ident).stdout.strip()
        pause = os.environ.get("WRITE_LOCK_TEST_PAUSE")       # self-test barrier only
        if pause and not getattr(self, "_paused", False):
            self._paused = True
            open(f"{pause}.{os.getpid()}.ready", "w").close()
            for _ in range(200):
                if os.path.exists(pause + ".go"):
                    break
                time.sleep(0.05)
        if os.environ.get("WRITE_LOCK_UNSAFE_FORCE"):
            # Negative control ONLY: a blind last-writer-wins write (force, retried, never re-decided).
            # --force alone is not enough to break it: receive-pack still compare-and-swaps the old value.
            for _ in range(5):
                if self.git("push", "-q", "--no-verify", "--force", self.remote, f"{commit}:{self.ref}", check=False).returncode == 0:
                    return True, ""
            return False, "unsafe push failed"
        p = self.git("push", "-q", "--no-verify", self.remote, f"{commit}:{self.ref}", check=False)
        return p.returncode == 0, p.stderr.strip()

    def cas(self, mutate, msg):
        """Read, decide, write a child commit; on rejection re-read and re-decide. mutate may raise Refused."""
        for attempt in range(ATTEMPTS):
            tip, state = self.read()
            new = mutate(state)
            if new is None:
                return state
            ok, err = self.write(tip, new, msg)
            if ok:
                return new
            tip2, _ = self.read()
            if tip2 == tip:
                raise Rejected(f"push refused without a competing write: {err}")
            sys.stderr.write(f"write_lock: lost race on {self.ref} (attempt {attempt + 1}); re-reading\n")
        raise Refused(f"gave up after {ATTEMPTS} contended attempts on {self.ref}")


# ---------------------------------------------------------------- lock
def lock_cmd(o, verb):
    st = Store(o["repo"], o["remote"], o["prefix"] + o["name"], "lock.json")
    me, now = o["session"], time.time()

    def held_live(s):
        return s and s.get("state") == "held" and now <= s["expires_at"] + o["grace"]

    def held_msg(s):
        return (f"held by {s['holder']} since {s['acquired_at_iso']} until {iso(s['expires_at'])}"
                f" ({s.get('reason') or 'no reason'})")

    def grant(s, takeover_from=None):
        return {"name": o["name"], "state": "held", "holder": me, "host": socket.gethostname(),
                "pid": os.getpid(), "reason": o["reason"], "ttl": o["ttl"],
                "acquired_at": now, "acquired_at_iso": iso(now), "expires_at": now + o["ttl"],
                "seq": (s or {}).get("seq", 0) + 1, "took_over_from": takeover_from}

    if verb == "status":
        _, s = st.read()
        if not s or s["state"] == "free":
            print(f"lock {o['name']}: free" + (f" (last holder {s['holder']})" if s else ""))
            return 0
        live = held_live(s)
        print(f"lock {o['name']}: {'LIVE' if live else 'STALE'}, {held_msg(s)}")
        return 3 if live else 4

    if verb == "acquire":
        def m(s):
            if s and s["state"] == "held":
                if s["holder"] == me and held_live(s):
                    return grant(s)                       # re-entrant: extend own lock
                if held_live(s):
                    raise Refused(held_msg(s))
                raise Refused(held_msg(s) + " -- EXPIRED; declare it with `lock takeover`")
            return grant(s)
        deadline = now + o["wait"]
        while True:
            try:
                s = st.cas(m, f"acquire {o['name']} by {me}")
                print(f"lock {o['name']}: acquired by {me} until {iso(s['expires_at'])}")
                return 0
            except Refused as e:
                if time.time() >= deadline:
                    raise
                sys.stderr.write(f"write_lock: {e}; waiting\n")
                time.sleep(min(10, max(1, deadline - time.time())))
                now = time.time()

    if verb == "release":
        def m(s):
            if not s or s["state"] == "free":
                return None
            if s["holder"] != me:
                raise Refused(f"not yours: {held_msg(s)}")
            return dict(s, state="free", released_at_iso=iso(now), seq=s["seq"] + 1)
        st.cas(m, f"release {o['name']} by {me}")
        print(f"lock {o['name']}: free")
        return 0

    if verb == "takeover":
        def m(s):
            if not s or s["state"] == "free":
                raise Refused("lock is free; use acquire")
            if held_live(s):
                raise Refused(f"not stale: {held_msg(s)} (+{o['grace']}s grace)")
            return grant(s, takeover_from=s["holder"])
        s = st.cas(m, f"takeover {o['name']} by {me}")
        print(f"lock {o['name']}: TAKEN OVER from {s['took_over_from']} by {me} until {iso(s['expires_at'])}")
        return 0
    raise SystemExit(2)


# ---------------------------------------------------------------- leases
def lease_cmd(o, verb, paths):
    st = Store(o["repo"], o["remote"], o["prefix"] + "leases", "leases.json")
    me, now = o["session"], time.time()
    top = subprocess.run(["git", "-C", o["repo"], "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or o["repo"]
    rtop, cwd = os.path.realpath(top), os.path.realpath(os.getcwd())
    base = cwd if (cwd + os.sep).startswith(rtop + os.sep) else rtop      # relative = from cwd if inside the repo, else from its root
    norm = sorted({os.path.relpath(os.path.realpath(os.path.join(base, p)), rtop) for p in paths})
    outside = [p for p in norm if p.startswith("..")]
    if outside:
        raise Refused(f"path(s) outside the repo: {' '.join(outside)}")

    def live(l):
        return l and now <= l["expires_at"] + o["grace"]

    def foreign(s):
        return {p: l for p, l in ((s or {}).get("leases", {})).items() if live(l) and l["holder"] != me}

    if verb == "list":
        _, s = st.read()
        rows = sorted((s or {}).get("leases", {}).items())
        if not rows:
            print("leases: none")
        for p, l in rows:
            print(f"{'live ' if live(l) else 'STALE'} {p}  {l['holder']}  until {iso(l['expires_at'])}  {l.get('reason') or ''}")
        return 0

    if verb == "check":
        try:
            _, s = st.read()
        except Unreachable as e:
            print(f"lease check: remote unreachable ({e}); lease state UNKNOWN")
            return 1 if o["block"] else 0
        hits = {p: l for p, l in foreign(s).items() if p in norm}
        for p, l in sorted(hits.items()):
            print(f"lease check: {p} is leased by {l['holder']} until {iso(l['expires_at'])} ({l.get('reason') or ''})")
        if hits and o["block"]:
            return 1
        if not hits:
            print(f"lease check: {len(norm)} path(s) clear")
        return 0

    if verb == "claim":
        def m(s):
            s = s or {"leases": {}, "seq": 0}
            taken = {p: l for p, l in foreign(s).items() if p in norm}
            if taken:
                raise Refused("; ".join(f"{p} leased by {l['holder']} until {iso(l['expires_at'])}" for p, l in sorted(taken.items())))
            leases = {p: l for p, l in s["leases"].items() if live(l)}          # garbage-collect expired
            for p in norm:
                leases[p] = {"holder": me, "claimed_at_iso": iso(now), "expires_at": now + o["ttl"], "reason": o["reason"]}
            return {"leases": leases, "seq": s["seq"] + 1}
        st.cas(m, f"lease claim {' '.join(norm)} by {me}")
        print(f"leased to {me} until {iso(now + o['ttl'])}: {' '.join(norm)}")
        return 0

    if verb == "release":
        def m(s):
            if not s:
                return None
            mine = [p for p in norm if s["leases"].get(p, {}).get("holder") == me]
            other = [p for p in norm if p in foreign(s)]
            if other:
                raise Refused(f"not yours: {' '.join(other)}")
            if not mine:
                return None
            return {"leases": {p: l for p, l in s["leases"].items() if p not in mine}, "seq": s["seq"] + 1}
        st.cas(m, f"lease release {' '.join(norm)} by {me}")
        print(f"released: {' '.join(norm)}")
        return 0
    raise SystemExit(2)


# ---------------------------------------------------------------- cli
def default_session(repo):
    if os.environ.get("WRITE_LOCK_SESSION"):
        return os.environ["WRITE_LOCK_SESSION"]
    # The worktree PATH, not the branch: two clones on one host, or two detached-HEAD worktrees,
    # must never share an identity (they would extend and release each other's lock). Stable
    # across calls from the same checkout, so a later `release` still matches. Callers that run
    # several independent holders from ONE checkout (merge_train.sh) pass --session explicitly.
    top = subprocess.run(["git", "-C", repo, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    return f"{getpass.getuser()}@{socket.gethostname().split('.')[0]}:{top or repo}"


USAGE = __doc__.split("\n\n")[2]


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    o = {"remote": "origin", "repo": os.getcwd(), "session": None, "grace": GRACE, "prefix": "refs/locks/",
         "name": "main", "ttl": None, "reason": "", "wait": 0, "block": False}
    valued = {"--remote": str, "--repo": str, "--session": str, "--grace": int, "--prefix": str,
              "--name": str, "--ttl": int, "--reason": str, "--wait": int}
    pos, i = [], 0
    while i < len(argv):
        a = argv[i]
        if a in valued:
            if i + 1 >= len(argv):
                sys.stderr.write(f"write_lock: {a} needs a value\n{USAGE}\n"); return 2
            try:
                o[a[2:]] = valued[a](argv[i + 1])
            except ValueError:
                sys.stderr.write(f"write_lock: bad value for {a}\n"); return 2
            i += 2; continue
        if a == "--block":
            o["block"] = True
        elif a in ("-h", "--help"):
            print(__doc__); return 0
        elif a.startswith("-"):
            sys.stderr.write(f"write_lock: unknown flag {a!r} (refusing to ignore it)\n{USAGE}\n"); return 2
        else:
            pos.append(a)
        i += 1
    if len(pos) < 2 or pos[0] not in ("lock", "lease"):
        sys.stderr.write(USAGE + "\n"); return 2
    kind, verb, rest = pos[0], pos[1], pos[2:]
    o["repo"] = os.path.abspath(o["repo"])
    o["session"] = o["session"] or default_session(o["repo"])
    if not o["prefix"].endswith("/"):
        o["prefix"] += "/"
    try:
        if kind == "lock":
            if verb not in ("acquire", "release", "status", "takeover") or rest:
                sys.stderr.write(USAGE + "\n"); return 2
            o["ttl"] = min(o["ttl"] or 1800, MAX_TTL["lock"])
            return lock_cmd(o, verb)
        if verb not in ("claim", "release", "list", "check") or (verb != "list" and not rest) or (verb == "list" and rest):
            sys.stderr.write(USAGE + "\n"); return 2
        o["ttl"] = min(o["ttl"] or 7200, MAX_TTL["lease"])
        return lease_cmd(o, verb, rest)
    except Refused as e:
        print(f"write_lock: REFUSED: {e}"); return 1
    except Unreachable as e:
        print(f"write_lock: remote unreachable: {e}"); return 5
    except Rejected as e:
        print(f"write_lock: {e}"); return 6


# ---------------------------------------------------------------- self-test
def self_test():
    import tempfile, threading
    me = os.path.abspath(__file__)
    fails = []

    def check(cond, label):
        print(f"  {'PASS' if cond else 'FAIL'} {label}")
        if not cond:
            fails.append(label)

    with tempfile.TemporaryDirectory() as T:
        g = lambda *a, cwd=T: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd, capture_output=True, text=True)
        g("init", "-q", "--bare", "-b", "main", "origin.git")
        for c in ("A", "B"):
            g("clone", "-q", "origin.git", c)

        def run(clone, *a, env=None, grace="0"):
            e = {k: v for k, v in os.environ.items() if not k.startswith("WRITE_LOCK_")}
            e.update(WRITE_LOCK_SESSION=f"session-{clone}", **(env or {}))
            p = subprocess.run([sys.executable, me, "--repo", os.path.join(T, clone), "--grace", grace, *a],
                               capture_output=True, text=True, env=e)
            return p.returncode, p.stdout + p.stderr

        def race(*a, unsafe=False):
            bar = os.path.join(T, f"bar{time.time_ns()}")
            env = {"WRITE_LOCK_TEST_PAUSE": bar}
            if unsafe:
                env["WRITE_LOCK_UNSAFE_FORCE"] = "1"
            out = {}
            ts = [threading.Thread(target=lambda c=c: out.__setitem__(c, run(c, *a, env=env))) for c in ("A", "B")]
            [t.start() for t in ts]
            for _ in range(200):                      # both racers have read state + built a commit
                if len([f for f in os.listdir(T) if f.startswith(os.path.basename(bar)) and f.endswith(".ready")]) >= 2:
                    break
                time.sleep(0.05)
            open(bar + ".go", "w").close()
            [t.join() for t in ts]
            return out

        print("(1) two racers, same state, acquire main -> exactly one wins")
        r = race("lock", "acquire")
        rcs = sorted(v[0] for v in r.values())
        check(rcs == [0, 1], f"exit codes {rcs} == [0, 1]")
        loser = "A" if r["A"][0] else "B"
        winner = "B" if loser == "A" else "A"
        check("lost race" in r[loser][1] and f"held by session-{winner}" in r[loser][1], "loser saw the rejection, re-read, named the winner")
        rc, out = run("A", "lock", "status")
        check(rc == 3 and f"session-{winner}" in out, f"status: HELD by session-{winner}")

        print("(2) wrong session cannot release; live lock cannot be taken over")
        rc, _ = run(loser, "lock", "release")
        check(rc == 1, "non-holder release refused")
        rc, _ = run(loser, "lock", "takeover")
        check(rc == 1, "takeover of a live lock refused")
        rc, _ = run(winner, "lock", "release")
        check(rc == 0, "holder release ok")
        rc, out = run("A", "lock", "status")
        check(rc == 0 and "free" in out, "release frees the lock")

        print("(3) stale lock (TTL expired) -> acquire refuses, takeover wins and records it")
        run("A", "lock", "acquire", "--ttl", "1")
        time.sleep(2)
        rc, out = run("B", "lock", "status")
        check(rc == 4, "status reports STALE (exit 4)")
        rc, out = run("B", "lock", "acquire")
        check(rc == 1 and "takeover" in out, "plain acquire refuses an expired lock (takeover must be declared)")
        rc, out = run("B", "lock", "takeover")
        check(rc == 0 and "from session-A" in out, "takeover ok, names the previous holder")
        rc, _ = run("A", "lock", "release")
        check(rc == 1, "crashed holder coming back cannot release the new holder's lock")
        run("B", "lock", "release")

        print("(4) hot-file leases")
        rc, _ = run("A", "lease", "claim", "src/app/jobs/JobsBoard.tsx", "CLAUDE.md", "--ttl", "600")
        check(rc == 0, "A claims two paths")
        rc, out = run("B", "lease", "claim", "CLAUDE.md")
        check(rc == 1 and "session-A" in out, "B's claim on a leased path is refused")
        rc, out = run("B", "lease", "check", "CLAUDE.md", "README.md")
        check(rc == 0 and "leased by session-A" in out, "check warns (exit 0) by default")
        rc, _ = run("B", "lease", "check", "--block", "CLAUDE.md")
        check(rc == 1, "check --block exits 1")
        rc, _ = run("B", "lease", "check", "--block", "README.md")
        check(rc == 0, "check --block passes an unleased path")
        rc, _ = run("A", "lease", "check", "--block", "CLAUDE.md")
        check(rc == 0, "holder's own lease never blocks the holder")
        rc, _ = run("B", "lease", "release", "CLAUDE.md")
        check(rc == 1, "B cannot release A's lease")
        rc, _ = run("A", "lease", "release", "CLAUDE.md")
        check(rc == 0, "A releases")
        rc, _ = run("B", "lease", "claim", "CLAUDE.md")
        check(rc == 0, "release frees it: B claims")
        rc, out = run("A", "lease", "list")
        check("JobsBoard.tsx  session-A" in out and "CLAUDE.md  session-B" in out, "list shows both holders")
        run("A", "lease", "claim", "tmp/short.txt", "--ttl", "1")
        time.sleep(2)
        rc, _ = run("B", "lease", "claim", "tmp/short.txt")
        check(rc == 0, "expired lease does not block a new claimer")

        print("(4b) default identity: two clones, no WRITE_LOCK_SESSION, must not share the lock")
        e0 = {k: v for k, v in os.environ.items() if not k.startswith("WRITE_LOCK_")}
        d = lambda c, *a: subprocess.run([sys.executable, me, "--repo", os.path.join(T, c), *a], capture_output=True, text=True, env=e0)
        check(d("A", "lock", "acquire").returncode == 0, "A acquires with the default identity")
        check(d("B", "lock", "acquire").returncode == 1, "B (same host, same branch) is refused, not re-entrant")
        check(d("B", "lock", "release").returncode == 1, "B cannot release A's lock")
        check(d("A", "lock", "release").returncode == 0, "A releases")
        print("(4c) lease paths match however they are spelled")
        run("A", "lease", "claim", "docs/x.md")
        rc, out = run("B", "lease", "check", "--block", os.path.join(T, "B", "docs", "x.md"))
        check(rc == 1, "absolute path matches a repo-relative lease")
        rc, _ = run("B", "lease", "check", "--block", "./docs/../docs/x.md")
        check(rc == 1, "un-normalized relative path matches")

        print("(5) two racers claim the same path -> exactly one lease")
        r = race("lease", "claim", "scripts/git-hooks/pre-commit")
        rcs = sorted(v[0] for v in r.values())
        check(rcs == [0, 1], f"exit codes {rcs} == [0, 1]")

        print("(6) negative control: blind force writes MUST double-grant, or check (1) proves nothing")
        g("update-ref", "-d", "refs/locks/main", cwd=os.path.join(T, "origin.git"))
        r = race("lock", "acquire", unsafe=True)
        rcs = sorted(v[0] for v in r.values())
        check(rcs == [0, 0], f"unsafe mode double-grants {rcs} (so check (1) is not vacuous)")

        print("(7) usage guard")
        rc, out = run("A", "lease", "claim", "squat.txt", "--ttl", "999999")
        check(rc == 0 and iso(time.time() + 14400)[:13] in out, "lease TTL clamped to 4h (anti-squatting)")
        rc, _ = run("A", "lock", "acquire", "--bogus")
        check(rc == 2, "unknown flag rejected (exit 2)")
        rc, _ = run("A", "--remote", os.path.join(T, "nope.git"), "lock", "status")
        check(rc == 5, "unreachable remote -> exit 5")
        rc, out = run("A", "--remote", os.path.join(T, "nope.git"), "lease", "check", "x")
        check(rc == 0 and "UNKNOWN" in out, "offline lease check fails OPEN in warn mode")
        rc, _ = run("A", "--remote", os.path.join(T, "nope.git"), "lease", "check", "--block", "x")
        check(rc == 1, "offline lease check fails CLOSED with --block")

    print(f"self-test: {'ALL PASS' if not fails else f'{len(fails)} FAIL'}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
