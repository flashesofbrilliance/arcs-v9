#!/usr/bin/env python3
"""backlog_merge_by_id: resolve a git merge conflict in _QUEUE/induced-backlog.jsonl by row id (stdlib only).

For every row id it takes the base, ours and theirs versions: if only one side changed the row it keeps that side;
if both changed it, it keeps theirs and prints the id for a human to look at. A row added on one side is kept; a row
deleted on one side and untouched on the other stays deleted. Row order follows theirs, then rows only ours has.
Each kept row is written as its original line text, so a merge never reformats rows it did not change.

Modes:
  backlog_merge_by_id.py                      manual: run in a conflicted merge; reads index stages 1/2/3, writes
                                              the merged file; you still `git add` and commit.
  backlog_merge_by_id.py --driver %O %A %B    git merge driver (DRIVER_MODE_V1): writes the merge into %A, exit 0.
                                              Any line that is not a JSON object with a unique id -> falls back to
                                              `git merge-file` (normal conflict markers, exit 1); never drops a line.
  backlog_merge_by_id.py --self-test          two throwaway branches in a temp repo: proves the fixture conflicts
                                              without the driver, merges clean with it, and that a same-row edit
                                              keeps theirs and prints the id.

Wiring: .gitattributes names `merge=backlog-by-id` for the backlog file; .claude/hooks/session-start.sh sets
merge.backlog-by-id.driver (DRIVER_CMD below). Never `merge=union` on this file: rows are edited in place.
Known limit: GitHub's server-side mergeability ignores local drivers, so a PR still shows CONFLICTING until the
owner runs `git merge origin/main`; the driver removes the hand resolution, not that round trip.
"""
import json, os, subprocess, sys, tempfile

F = "_QUEUE/induced-backlog.jsonl"
# The driver command the session-start hook arms. The sh guard runs the driver only when the checked-out copy of
# this script has driver mode; an older copy (a branch cut before this change) gets a plain text merge with
# conflict markers instead of the manual mode, which would ignore %A and silently keep ours.
DRIVER_CMD = ("sh -c 'f=scripts/backlog_merge_by_id.py; if grep -q DRIVER_MODE_V1 \"$f\" 2>/dev/null; "
              "then exec python3 \"$f\" --driver \"$1\" \"$2\" \"$3\"; fi; "
              "git merge-file -L ours -L base -L theirs \"$2\" \"$1\" \"$3\"' backlog-by-id %O %A %B")


class Unparsable(Exception):
    pass


def parse(text, strict):
    """Return ({id: (row, raw_line)}, [ids in order])."""
    d, order = {}, []
    for n, l in enumerate(text.split("\n"), 1):
        if not l.strip():
            continue
        try:
            r = json.loads(l)
        except Exception:
            if strict: raise Unparsable("line %d is not JSON" % n)
            continue
        k = r.get("id") if isinstance(r, dict) else None
        if not k:
            if strict: raise Unparsable("line %d has no id" % n)
            continue
        if strict and k in d:
            raise Unparsable("duplicate id %s" % k)
        d[k] = (r, l)
        order.append(k)
    return d, order


def merge(base, ours, theirs, strict=False):
    """Return (merged_text, ids_changed_on_both_sides)."""
    b, _ = parse(base, strict)
    o, oo = parse(ours, strict)
    t, to = parse(theirs, strict)
    out, both = [], []
    for k in list(to) + [k for k in oo if k not in t]:
        bs, ou, th = (b.get(k) or (None,))[0], o.get(k), t.get(k)
        ov, tv = (ou or (None,))[0], (th or (None,))[0]
        if th is None:  # theirs lacks it: kept by ours, or deleted by theirs
            r = None if (bs is not None and ov == bs) else ou
        elif ou is None:  # ours lacks it: added by theirs, or deleted by ours
            r = None if (bs is not None and tv == bs) else th
        elif ov == tv or bs == ov: r = th
        elif bs == tv: r = ou
        else: r = th; both.append(k)
        if r is not None:
            out.append(r[1])
    return "".join(l + "\n" for l in out), both


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def driver(o_path, a_path, b_path):
    try:
        text, both = merge(read(o_path), read(a_path), read(b_path), strict=True)
    except Unparsable as e:
        print("backlog-by-id: %s; falling back to a text merge with conflict markers" % e, file=sys.stderr)
        return 1 if subprocess.run(["git", "merge-file", "-L", "ours", "-L", "base", "-L", "theirs",
                                    a_path, o_path, b_path]).returncode else 0
    with open(a_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("backlog-by-id: %d rows; changed on both sides (theirs kept): %s"
          % (text.count("\n"), ", ".join(both) or "none"), file=sys.stderr)
    return 0


def manual():
    def stage(n):
        return subprocess.run(["git", "show", ":%d:%s" % (n, F)], capture_output=True, text=True).stdout
    text, both = merge(stage(1), stage(2), stage(3))
    with open(F, "w", encoding="utf-8") as f:
        f.write(text)
    print("rows %d, changed on both sides (theirs kept): %s" % (text.count("\n"), both or "none"))
    return 0


def self_test():
    import os as _os  # a pre-commit hook exports GIT_DIR / GIT_INDEX_FILE; left set, the scratch git below writes to the REAL repo
    for _k in [k for k in _os.environ if k.startswith("GIT_")]:
        del _os.environ[_k]
    here = os.path.dirname(os.path.abspath(__file__))
    fails = []

    def check(name, ok):
        print("%s %s" % ("ok  " if ok else "FAIL", name))
        if not ok: fails.append(name)

    def row(i, note):
        # ensure_ascii=False and a non-ASCII char: the driver must keep each line's own text, never re-serialize it
        return json.dumps({"id": "r%d" % i, "state": "OPEN", "status_note": note + " →"}, ensure_ascii=False)

    with tempfile.TemporaryDirectory() as d:
        # a pre-commit hook exports GIT_DIR and GIT_INDEX_FILE; drop them so the temp repo is its own repo
        env = {k: v for k, v in os.environ.items() if k not in (
            "GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE", "GIT_PREFIX", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY")}
        env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0")

        def git(*a):
            return subprocess.run(["git", "-C", d] + list(a), capture_output=True, text=True, env=env)

        def write(lines):
            with open(os.path.join(d, F), "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

        def commit(msg):
            git("add", "-A"); git("commit", "-qm", msg)

        os.makedirs(os.path.join(d, "_QUEUE")); os.makedirs(os.path.join(d, "scripts"))
        with open(os.path.join(d, "scripts", "backlog_merge_by_id.py"), "w") as f:
            f.write(read(os.path.abspath(__file__)))
        git("init", "-q", "-b", "main"); git("config", "user.email", "t@t"); git("config", "user.name", "t")
        git("config", "commit.gpgsign", "false"); git("config", "core.hooksPath", "/dev/null")
        # the repo's real .gitattributes line for this file
        ga = os.path.join(here, "..", ".gitattributes")
        attrs = [l for l in read(ga).splitlines() if l.startswith(F + " ")] if os.path.exists(ga) else []
        check(".gitattributes names merge=backlog-by-id for the backlog (and never union)",
              len(attrs) == 1 and "merge=backlog-by-id" in attrs[0] and "union" not in attrs[0])
        with open(os.path.join(d, ".gitattributes"), "w") as f:
            f.write("\n".join(attrs) + "\n")
        base = [row(i, "base") for i in range(1, 6)]
        write(base); commit("base")

        # different rows on two branches, adjacent lines: a line merge conflicts here
        git("checkout", "-qb", "ours"); write([base[0], row(2, "ours edit")] + base[2:]); commit("ours r2")
        git("checkout", "-q", "main"); git("checkout", "-qb", "theirs")
        write(base[:2] + [row(3, "theirs edit")] + base[3:] + [row(6, "theirs new")]); commit("theirs r3 + r6")

        def try_merge(branch, other):
            git("checkout", "-qf", branch); git("reset", "-q", "--hard")
            r = git("merge", "--no-edit", other)
            body = read(os.path.join(d, F))
            git("merge", "--abort")
            git("reset", "-q", "--hard", branch)
            return r, body

        # red: no driver configured -> git falls back to its text merge and conflicts
        r, body = try_merge("ours", "theirs")
        check("without the driver: different-row edits conflict (fixture is real)",
              r.returncode != 0 and "<<<<<<<" in body)

        # green: driver armed exactly as the session-start hook arms it
        git("config", "merge.backlog-by-id.driver", DRIVER_CMD)
        r, body = try_merge("ours", "theirs")
        clean = r.returncode == 0 and "<<<<<<<" not in body
        check("with the driver: different rows merge clean, no conflict markers", clean)
        want = [base[0], row(2, "ours edit"), row(3, "theirs edit")] + base[3:] + [row(6, "theirs new")]
        check("with the driver: both edits and the new row survive, every line byte-identical to its source",
              clean and body.splitlines() == want)

        # same row on both sides -> theirs kept, id printed
        git("checkout", "-qb", "ours2", "main"); write([base[0], row(2, "ours take")] + base[2:]); commit("ours2")
        git("checkout", "-qb", "theirs2", "main"); write([base[0], row(2, "theirs take")] + base[2:]); commit("theirs2")
        r, body = try_merge("ours2", "theirs2")
        check("same row on both sides: merge completes and keeps theirs",
              r.returncode == 0 and "theirs take" in body and "<<<<<<<" not in body)
        check("same row on both sides: the id is printed", "theirs kept): r2" in (r.stderr + r.stdout))

        # deletion on one side, untouched on the other, stays deleted
        git("checkout", "-qb", "ours3", "main"); write(base[:3] + base[4:]); commit("ours3 drops r4")
        git("checkout", "-qb", "theirs3", "main"); write([row(1, "theirs edit")] + base[1:]); commit("theirs3")
        r, body = try_merge("ours3", "theirs3")
        check("a row deleted on one side stays deleted", r.returncode == 0 and '"r4"' not in body and "theirs edit" in body)

        # a non-JSON line falls back to conflict markers, never drops the line
        git("checkout", "-qb", "ours4", "main"); write([base[0], "not json"] + base[2:]); commit("ours4 bad")
        git("checkout", "-qb", "theirs4", "main"); write(base[:2] + [row(3, "t")] + base[3:]); commit("theirs4")
        r, body = try_merge("ours4", "theirs4")
        check("an unparsable line falls back to a marked conflict", r.returncode != 0 and "not json" in body)

        # an old copy of the script (no driver mode) gets a text merge, not the manual mode
        git("checkout", "-qb", "old", "main")
        with open(os.path.join(d, "scripts", "backlog_merge_by_id.py"), "w") as f:
            f.write("print('old manual mode')\n")
        write([base[0], row(2, "old edit")] + base[2:]); commit("old script")
        r, body = try_merge("old", "theirs")
        check("an old script copy gets conflict markers, never a silent keep-ours",
              r.returncode != 0 and "<<<<<<<" in body)

    print("self-test: %s" % ("PASS" if not fails else "FAIL (%d)" % len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--self-test"]:
        sys.exit(self_test())
    if len(a) == 4 and a[0] == "--driver":
        sys.exit(driver(*a[1:]))
    if not a:
        sys.exit(manual())
    print(__doc__, file=sys.stderr)
    sys.exit(2)
