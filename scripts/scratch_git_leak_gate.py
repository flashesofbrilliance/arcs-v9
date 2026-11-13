#!/usr/bin/env python3
"""scratch_git_leak_gate.py: no self-test may write to the repo that runs it.

Why: git exports GIT_DIR and GIT_INDEX_FILE to a pre-commit hook (GIT_DIR always, when
committing from a worktree). A self-test that builds a scratch repo with `git -C <tmp> init`
or `git config user.email t@t` inherits those vars, so git ignores `-C` and the cwd and writes
to the REAL repo instead: core.bare flipped to true, user.name=t, user.email=t@t in the shared
.git/config (seen 2026-11-12). Commits then go out authored `t <t@t>` and Vercel blocks them.

How: for each script whose --self-test makes a scratch git repo, build a fresh sandbox host
repo plus a worktree, run the self-test with the exact env a worktree pre-commit hook exports
(GIT_DIR, GIT_INDEX_FILE, GIT_CONFIG_PARAMETERS), then diff the host's config and refs. Any
change is a leak. The host is a throwaway; the real .git is never touched.

  python3 scripts/scratch_git_leak_gate.py            # every scratch-git self-test
  python3 scripts/scratch_git_leak_gate.py a.py b.sh  # only these
  python3 scripts/scratch_git_leak_gate.py --list     # what it would run
  python3 scripts/scratch_git_leak_gate.py --self-test

The fix in a leaking self-test: drop every GIT_* var before the first scratch git call
(`for k in [k for k in os.environ if k.startswith("GIT_")]: del os.environ[k]` in Python,
`unset $(env | sed -n 's/^\\(GIT_[A-Z_]*\\)=.*/\\1/p')` in shell). AGENTS.md gotcha 15.
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
# a scratch git repo is born here: `git init` in any spelling, or a git call that names "init"
INIT = re.compile(r"""git\s+(-C\s+\S+\s+)?init\b|["']init["']\s*,\s*["']-q|\(\s*["']init["']|["']git["']\s*,\s*["']init["']""")
SELFTEST = re.compile(r"--self-test")
TIMEOUT = 180


def discover(root=HERE):
    out = []
    for p in sorted(list(root.glob("*.py")) + list(root.glob("*.sh"))):
        if p.name == Path(__file__).name:
            continue
        t = p.read_text(errors="replace")
        if SELFTEST.search(t) and INIT.search(t):
            out.append(p)
    return out


def _g(*a, cwd=None, env=None):
    return subprocess.run(["git", *a], cwd=cwd, env=env, capture_output=True, text=True)


def _clean_env():
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def sandbox(root: Path):
    """A host repo with one commit and a linked worktree, like the real checkout."""
    env = _clean_env()
    main, wt = root / "host", root / "wt"
    _g("init", "-q", "-b", "main", str(main), env=env)
    _g("-c", "user.name=h", "-c", "user.email=h@h", "commit", "-q", "--allow-empty", "-m", "h", cwd=main, env=env)
    _g("worktree", "add", "-q", str(wt), cwd=main, env=env)
    gitdir = main / ".git" / "worktrees" / "wt"
    hook_env = {**env, "GIT_DIR": str(gitdir), "GIT_INDEX_FILE": str(gitdir / "index"),
                "GIT_CONFIG_PARAMETERS": "'core.hookspath'='/dev/null'", "GIT_PREFIX": ""}
    return main, wt, hook_env


def fingerprint(main: Path):
    env = _clean_env()
    cfg = (main / ".git" / "config").read_text()
    refs = _g("for-each-ref", "--format=%(refname) %(objectname)", cwd=main, env=env).stdout
    head = _g("rev-parse", "HEAD", cwd=main, env=env).stdout
    return cfg, refs + head


def keys(cfg_text: str):
    """The identity, bare and hook-switch keys a leak has been seen to write, read from the config text."""
    sec, got = "", {}
    for line in cfg_text.splitlines():
        s = line.strip()
        m = re.match(r"\[([^\]\s\"]+)", s)
        if m:
            sec = m.group(1).lower()
            continue
        if "=" in s:
            k, v = (x.strip() for x in s.split("=", 1))
            name = f"{sec}.{k.lower()}"
            if name in ("user.name", "user.email", "core.bare", "core.hookspath", "commit.gpgsign"):
                got[name] = v
    return got


def run_one(script: Path):
    """Return (leaked: bool, detail: str)."""
    with tempfile.TemporaryDirectory() as td:
        main, wt, env = sandbox(Path(td))
        before = fingerprint(main)
        cmd = ["bash", str(script), "--self-test"] if script.suffix == ".sh" else [sys.executable, str(script), "--self-test"]
        try:
            subprocess.run(cmd, cwd=wt, env=env, capture_output=True, text=True, timeout=TIMEOUT,
                           stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            pass  # a hang is not this gate's finding; the writes, if any, already happened
        after = fingerprint(main)
        if before == after:
            return False, ""
        kb, ka = keys(before[0]), keys(after[0])
        bits = [f"{k}: {kb.get(k, '-')} -> {ka.get(k, '-')}" for k in sorted(set(kb) | set(ka)) if kb.get(k) != ka.get(k)]
        if before[0] != after[0] and not bits:
            bits.append("other .git/config lines changed")
        if before[1] != after[1]:
            bits.append("host refs or HEAD moved")
        return True, "; ".join(bits)


def gate(paths):
    leaks = 0
    for p in paths:
        leaked, detail = run_one(p)
        rel = os.path.relpath(p, HERE.parent)
        print(f"  {'LEAK' if leaked else 'ok  '}  {rel}{'  ' + detail if leaked else ''}")
        leaks += leaked
    if leaks:
        print(f"✖ scratch-git-leak: {leaks} self-test(s) write to the repo that runs them. "
              "Drop every GIT_* env var before the first scratch git call (see this file's docstring).", file=sys.stderr)
        return 1
    print(f"scratch-git-leak: {len(paths)} self-test(s), 0 leaks")
    return 0


def self_test():
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok = ok and cond

    bad = ('import subprocess, sys, tempfile\n'
           'if "--self-test" in sys.argv:\n'
           '    d = tempfile.mkdtemp()\n'
           '    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):\n'
           '        subprocess.run(["git", "-C", d, *a], capture_output=True)\n')
    good = bad.replace('    d = tempfile.mkdtemp()\n',
                       '    import os\n    for k in [k for k in os.environ if k.startswith("GIT_")]: del os.environ[k]\n'
                       '    d = tempfile.mkdtemp()\n')
    bad_sh = '#!/usr/bin/env bash\n[ "$1" = --self-test ] || exit 0\nt=$(mktemp -d); git -C "$t" init -q; git -C "$t" config user.name t\n'
    good_sh = bad_sh.replace('t=$(mktemp -d);', "unset $(env | sed -n 's/^\\(GIT_[A-Z_]*\\)=.*/\\1/p'); t=$(mktemp -d);")
    with tempfile.TemporaryDirectory() as td:
        files = {}
        for name, body in (("bad.py", bad), ("good.py", good), ("bad.sh", bad_sh), ("good.sh", good_sh)):
            files[name] = Path(td) / name
            files[name].write_text(body)
        leaked, detail = run_one(files["bad.py"])
        check("a self-test that inits and configures a scratch repo under a hook env is caught",
              leaked and "core.bare: false -> true" in detail and "user.email: - -> t@t" in detail)
        check("the same self-test with GIT_* dropped passes", run_one(files["good.py"]) == (False, ""))
        check("a shell self-test that leaks is caught", run_one(files["bad.sh"])[0])
        check("the shell self-test with GIT_* unset passes", run_one(files["good.sh"]) == (False, ""))
        check("gate() exits 1 on a leak and 0 when clean",
              gate([files["bad.py"]]) == 1 and gate([files["good.py"]]) == 0)
        (Path(td) / "plain.py").write_text('import sys\nif "--self-test" in sys.argv: print("ok")\n')
        (Path(td) / "lib.py").write_text('subprocess.run(["git", "init", "-q", d])\n')
        names = {p.name for p in discover(Path(td))}
        check("discovery finds python and shell self-tests that init a scratch repo",
              {"bad.py", "good.py", "bad.sh", "good.sh"} <= names)
        check("discovery skips a self-test with no scratch git, and scratch git with no self-test",
              not names & {"plain.py", "lib.py"})
    print("self-test: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if argv == ["--self-test"]:
        return self_test()
    if argv == ["--list"]:
        for p in discover():
            print(os.path.relpath(p, HERE.parent))
        return 0
    paths = [Path(a).resolve() for a in argv] if argv else discover()
    return gate(paths)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
