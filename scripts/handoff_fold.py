#!/usr/bin/env python3
"""handoff_fold — per-session handoff fragments, folded into CLAUDE.md once. ADR-085 part (d).

Why: every /handoff used to edit the same lines of CLAUDE.md (prepend a block, renumber, relocate
the oldest to _ARCHIVE/handoffs.md). Two sessions finishing within a minute collided on it
(#893 and #894 both shipped "v3.101.0" on 2026-10-06). A fragment is a NEW file per session, so
writing one never conflicts. The version number and the CLAUDE.md edit happen in one place, fold,
run by one session (ideally while holding the main write-lock: scripts/write_lock.py).

  handoff_fold.py new [--branch B] < body.md    write _HANDOFFS/fragments/<utc-ts>--<branch>.md
                                                (body = the block WITHOUT its "# Handoff — vX" title;
                                                prints the path; the caller commits it)
  handoff_fold.py list                          unfolded fragments, oldest first
  handoff_fold.py fold [--dry-run] [--keep 2]   oldest fragment first: assign the next version,
                                                prepend to CLAUDE.md, move overflow blocks to the TOP
                                                of _ARCHIVE/handoffs.md, delete folded fragments.
                                                Never deletes history: overflow is relocated.
  handoff_fold.py --self-test                   throwaway dir; touches nothing else

Root: $CLAUDE_PROJECT_DIR, else cwd. Stdlib only. Exit 0 ok, 1 refused, 2 usage.
"""
import datetime, os, re, subprocess, sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
TITLE = re.compile(r"^# Handoff — v(\d+)\.(\d+)\.(\d+) \((\d{4}-\d{2}-\d{2})\)\s*$", re.M)


def paths(root):
    return (os.path.join(root, "CLAUDE.md"), os.path.join(root, "_ARCHIVE", "handoffs.md"),
            os.path.join(root, "_HANDOFFS", "fragments"))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "detached"


def fragments(root):
    d = paths(root)[2]
    return sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".md")) if os.path.isdir(d) else []


def parse_fragment(p):
    """-> (meta dict, body). Front matter is a leading <!-- key: value ... --> comment."""
    text = open(p).read()
    meta, body = {}, text
    m = re.match(r"<!--\n(.*?)\n-->\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
        body = text[m.end():]
    if TITLE.search(body):
        raise ValueError(f"{p}: fragment carries its own '# Handoff — vX' title; fold assigns the version")
    return meta, body.strip("\n")


def new(root, branch):
    body = sys.stdin.read().strip("\n")
    if not body:
        sys.stderr.write("handoff_fold: empty body on stdin\n"); return 2
    if TITLE.search(body):
        sys.stderr.write("handoff_fold: drop the '# Handoff — vX' title; fold assigns the version\n"); return 2
    if not branch:
        branch = subprocess.run(["git", "-C", root, "rev-parse", "--abbrev-ref", "HEAD"],
                                capture_output=True, text=True).stdout.strip()
    head = subprocess.run(["git", "-C", root, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    now = datetime.datetime.now(datetime.timezone.utc)
    d = paths(root)[2]
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{now:%Y%m%dT%H%M%SZ}--{slug(branch)}.md")
    if os.path.exists(p):
        sys.stderr.write(f"handoff_fold: {p} exists\n"); return 1
    with open(p, "w") as f:
        f.write(f"<!--\nbranch: {branch}\nhead: {head}\ncreated_at: {now:%Y-%m-%dT%H:%M:%SZ}\n-->\n{body}\n")
    print(os.path.relpath(p, root))
    return 0


def split_blocks(text):
    """-> (preamble, [blocks newest-first]); a block runs from its '# Handoff' title to the next."""
    starts = [m.start() for m in TITLE.finditer(text)]
    if not starts:
        return text, []
    pre = text[:starts[0]]
    blocks = [text[a:b].rstrip("\n") for a, b in zip(starts, starts[1:] + [len(text)])]
    return pre, blocks


def fold(root, dry, keep):
    cm, arch, _ = paths(root)
    frags = fragments(root)
    if not frags:
        print("handoff_fold: no fragments to fold"); return 0
    text = open(cm).read()
    pre, blocks = split_blocks(text)
    versions = [tuple(map(int, m.groups()[:3])) for m in TITLE.finditer(text)]
    if os.path.exists(arch):
        versions += [tuple(map(int, m.groups()[:3])) for m in TITLE.finditer(open(arch).read())]
    major, minor, _ = max(versions) if versions else (3, 0, 0)
    new_blocks = []
    for p in frags:
        meta, body = parse_fragment(p)
        minor += 1
        date = (meta.get("created_at") or "")[:10] or datetime.date.today().isoformat()
        src = f"\n\n> Folded from `{os.path.relpath(p, root)}` (branch `{meta.get('branch', '?')}`, head `{meta.get('head', '?')}`)."
        new_blocks.append(f"# Handoff — v{major}.{minor}.0 ({date})\n\n{body}{src}")
        print(f"fold: {os.path.relpath(p, root)} -> v{major}.{minor}.0")
    blocks = list(reversed(new_blocks)) + blocks          # newest first
    live, overflow = blocks[:keep], blocks[keep:]
    out = pre + "\n\n".join(live) + "\n"
    if dry:
        print(f"DRY RUN: would keep {len(live)} live, relocate {len(overflow)} to _ARCHIVE/handoffs.md, delete {len(frags)} fragment(s)")
        return 0
    if overflow:
        old = open(arch).read() if os.path.exists(arch) else ""
        os.makedirs(os.path.dirname(arch), exist_ok=True)
        with open(arch, "w") as f:
            f.write("\n\n---\n\n".join(overflow) + "\n\n---\n\n" + old)
        for b in overflow:
            print(f"archived: {b.splitlines()[0]}")
    with open(cm, "w") as f:
        f.write(out)
    for p in frags:
        os.remove(p)
    print(f"handoff_fold: {len(frags)} folded; {len(live)} live in CLAUDE.md. Commit CLAUDE.md, "
          f"_ARCHIVE/handoffs.md and the fragment deletions together.")
    return 0


def self_test():
    import tempfile
    me = os.path.abspath(__file__)
    fails = []

    def check(c, label):
        print(f"  {'PASS' if c else 'FAIL'} {label}")
        if not c:
            fails.append(label)

    with tempfile.TemporaryDirectory() as T:
        run = lambda *a, inp=None: subprocess.run([sys.executable, me, *a], input=inp, capture_output=True, text=True,
                                                  env=dict(os.environ, CLAUDE_PROJECT_DIR=T))
        subprocess.run(["git", "init", "-q", T])
        os.makedirs(os.path.join(T, "_ARCHIVE"))
        claude = ("# Project\n\nrules\n\n---\n\n"
                  "# Handoff — v3.102.0 (2026-10-06)\n\nB102 body\n\n"
                  "# Handoff — v3.101.0 (2026-10-06)\n\nB101 body\n")
        open(os.path.join(T, "CLAUDE.md"), "w").write(claude)
        open(os.path.join(T, "_ARCHIVE", "handoffs.md"), "w").write("# Handoff — v3.99.0 (2026-10-05)\n\nB99\n")

        print("(1) two sessions write fragments at the same moment -> two files, no shared edit")
        r1 = run("new", "--branch", "claude/alpha", inp="> alpha did X\n\n## Open\n1. a\n")
        import time; time.sleep(1.1)
        r2 = run("new", "--branch", "claude/beta", inp="> beta did Y\n")
        check(r1.returncode == 0 and r2.returncode == 0, "both fragments written")
        check(open(os.path.join(T, "CLAUDE.md")).read() == claude, "CLAUDE.md untouched by `new`")
        check(len(fragments(T)) == 2, "two fragment files")

        print("(2) a fragment that names its own version is refused (the collision vector)")
        r = run("new", inp="# Handoff — v3.101.0 (2026-10-06)\n\nx\n")
        check(r.returncode == 2, "titled body refused")

        print("(3) dry run changes nothing")
        r = run("fold", "--dry-run")
        check(r.returncode == 0 and "DRY RUN" in r.stdout and len(fragments(T)) == 2
              and open(os.path.join(T, "CLAUDE.md")).read() == claude, "no writes")

        print("(4) fold: unique sequential versions, newest first, 2 live, overflow archived at top")
        r = run("fold")
        check(r.returncode == 0, "fold exit 0")
        txt = open(os.path.join(T, "CLAUDE.md")).read()
        titles = [l for l in txt.splitlines() if l.startswith("# Handoff")]
        check(titles == ["# Handoff — v3.104.0 (" + titles[0][-11:-1] + ")", "# Handoff — v3.103.0 (" + titles[1][-11:-1] + ")"],
              f"live = v3.104 (beta), v3.103 (alpha): {titles}")
        check("beta did Y" in txt.split("v3.103.0")[0] and "alpha did X" in txt, "beta (newer) above alpha")
        check(txt.startswith("# Project\n\nrules\n\n---\n\n"), "preamble preserved byte-for-byte")
        arch = open(os.path.join(T, "_ARCHIVE", "handoffs.md")).read()
        at = [l for l in arch.splitlines() if l.startswith("# Handoff")]
        check(at == ["# Handoff — v3.102.0 (2026-10-06)", "# Handoff — v3.101.0 (2026-10-06)", "# Handoff — v3.99.0 (2026-10-05)"],
              f"archive newest-first, nothing lost: {at}")
        check("B102 body" in arch and "B101 body" in arch and "B99" in arch, "archived bodies intact")
        check(fragments(T) == [], "fragments deleted after fold")
        check("Folded from `_HANDOFFS/fragments/" in txt, "each block cites its fragment")

        print("(5) fold with nothing to fold is a no-op")
        before = open(os.path.join(T, "CLAUDE.md")).read()
        r = run("fold")
        check(r.returncode == 0 and open(os.path.join(T, "CLAUDE.md")).read() == before, "no-op")

        print("(6) git-level: the old way conflicts, fragments merge clean (the claim, falsifiable)")
        G = os.path.join(T, "g")
        g = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", G, *a], capture_output=True, text=True)
        os.makedirs(G); g("init", "-q", "-b", "main")
        open(os.path.join(G, "CLAUDE.md"), "w").write(claude); g("add", "."); g("commit", "-qm", "base")
        for br, v in (("old-a", "A"), ("old-b", "B")):          # two sessions prepend a block, same base
            g("checkout", "-qb", br, "main")
            open(os.path.join(G, "CLAUDE.md"), "w").write(claude.replace("# Handoff — v3.102.0", f"# Handoff — v3.103.0 (2026-10-06)\n\n{v} body\n\n# Handoff — v3.102.0"))
            g("commit", "-qam", br)
        g("checkout", "-q", "old-a")
        check(g("merge", "-q", "--no-edit", "old-b").returncode != 0, "old way: second session's CLAUDE.md edit CONFLICTS")
        g("merge", "--abort")
        for br in ("frag-a", "frag-b"):                           # two sessions write fragments, same base
            g("checkout", "-qb", br, "main")
            subprocess.run([sys.executable, me, "new", "--branch", br], input=f"{br} body\n", capture_output=True, text=True,
                           env=dict(os.environ, CLAUDE_PROJECT_DIR=G))
            g("add", "."); g("commit", "-qm", br)
            time.sleep(1.1)
        g("checkout", "-q", "frag-a")
        check(g("merge", "-q", "--no-edit", "frag-b").returncode == 0, "fragments: second session merges CLEAN")
        check(len(fragments(G)) == 2, "both fragments present after merge")

        print("(7) usage guard")
        check(run("bogus").returncode == 2, "unknown command exit 2")
        check(run("fold", "--nope").returncode == 2, "unknown flag exit 2")
        check(run("new", inp="").returncode == 2, "empty body exit 2")

    print(f"self-test: {'ALL PASS' if not fails else f'{len(fails)} FAIL'}")
    return 0 if not fails else 1


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    if not argv or argv[0] not in ("new", "list", "fold"):
        sys.stderr.write(__doc__.split("\n\n")[2] + "\n"); return 2
    cmd, rest = argv[0], argv[1:]
    branch, dry, keep, i = None, False, 2, 0
    while i < len(rest):
        a = rest[i]
        if cmd == "new" and a == "--branch" and i + 1 < len(rest):
            branch = rest[i + 1]; i += 2; continue
        if cmd == "fold" and a == "--dry-run":
            dry = True
        elif cmd == "fold" and a == "--keep" and i + 1 < len(rest) and rest[i + 1].isdigit():
            keep = int(rest[i + 1]); i += 2; continue
        else:
            sys.stderr.write(f"handoff_fold: unknown argument {a!r} for {cmd}\n"); return 2
        i += 1
    if cmd == "new":
        return new(ROOT, branch)
    if cmd == "list":
        fr = fragments(ROOT)
        print("\n".join(os.path.relpath(p, ROOT) for p in fr) if fr else "no unfolded fragments")
        return 0
    try:
        return fold(ROOT, dry, keep)
    except ValueError as e:
        sys.stderr.write(f"handoff_fold: REFUSED: {e}\n"); return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
