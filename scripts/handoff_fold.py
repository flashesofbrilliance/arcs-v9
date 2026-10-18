#!/usr/bin/env python3
"""handoff_fold — fragments are raw material; molt turns them into ONE cold-moltable arc. ADR-085 (d).

Why: every /handoff used to edit the same lines of CLAUDE.md, and two sessions collided (#893 and
#894 both shipped "v3.101.0" on 2026-10-06). Fragments (one new file per session) fixed the write
collision, but `fold` still turned each fragment into its own CLAUDE.md block and computed the
version itself (highest+1), so the result was shards and bookends, not an arc a cold session could
resume from. Now:

  - `new` stays cheap and append-only: one file per session, warns (never blocks) on missing fields.
  - `molt` synthesizes ALL unfolded fragments into ONE block with fixed sections, takes its version
    from `scripts/oracle.py next handoff` (git non-fast-forward is the lock), and refuses a bookend.

  handoff_fold.py new [--branch B] [--session S] < body.md
        write _HANDOFFS/fragments/<utc-ts>--<branch>.md (body = headed sections, no '# Handoff' title)
  handoff_fold.py list                     unfolded fragments, oldest first
  handoff_fold.py molt [--input F|-] [--dry-run] [--keep 1]
        synthesize every fragment (+ optional summary/override sections from F or stdin) into one
        block, gate it, allocate the version from the oracle, prepend to CLAUDE.md, relocate
        overflow (chosen by VERSION, not position) to the top of _ARCHIVE/handoffs.md, delete the
        molted fragments. Commit CLAUDE.md, _ARCHIVE/handoffs.md, _HANDOFFS/fragments/ and
        _SEEDS/_oracle.json together; a non-ff push rejection means someone took the number:
        reset to origin/main, keep your fragments, molt again.
  handoff_fold.py archive [--keep 1] [--dry-run]
        relocate live blocks beyond --keep (newest by VERSION kept) to the top of _ARCHIVE/handoffs.md, with
        no new block and no oracle number. Same relocation `molt` does; use it to trim CLAUDE.md between molts.
        Default keep is 1: CLAUDE.md is always-on context, /handoff-pickup reads only the highest version, and
        older arcs stay in _ARCHIVE/handoffs.md and git (2026-10-17, WS1 slice 2).
  handoff_fold.py fold ...                 DEPRECATED alias of molt (prints a notice)
  handoff_fold.py --self-test              throwaway dirs; touches nothing else

Fragment schema (headed sections; front matter is written by `new`):
  ## Changed      merged PRs (#NNN) and decision-receipt ids        (molt: union)
  ## State        what is true now                                  (molt: newest wins)
  ## Decisions    decisions made this session                       (molt: union)
  ## Open         numbered open items; mark Zach's with "Zach:"     (molt: union, renumbered)
  ## Next action  ONE next action                                   (molt: newest wins)
  ## Cold-start   files/commands/tracker view a no-context session needs (molt: newest wins)
  ## Goal         optional; the arc's true north                    (molt: input, else newest)
  anything else (## Lessons ...) is carried under "Notes" verbatim.
Molt input (--input) uses the same headings plus `## Summary` (one-paragraph arc summary, written by
the human or the calling LLM; this script never calls a paid API). An input section overrides the
assembled one.

Root: $CLAUDE_PROJECT_DIR, else cwd. Stdlib only. Exit 0 ok, 1 refused, 2 usage.
"""
import datetime, os, re, subprocess, sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
TITLE = re.compile(r"^# Handoff — v(\d+)\.(\d+)\.(\d+) \((\d{4}-\d{2}-\d{2})\)\s*$", re.M)
ORACLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oracle.py")
TRACKER = "https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm"
# fragment heading -> canonical key (prefix match, case-insensitive)
KEYS = [("changed", "changed"), ("what changed", "changed"), ("done", "changed"), ("shipped", "changed"),
        ("prs", "changed"), ("state", "state"), ("current state", "state"), ("decisions", "decisions"),
        ("open", "open"), ("next action", "next"), ("next", "next"), ("cold-start", "cold"),
        ("cold start", "cold"), ("goal", "goal"), ("true north", "goal"), ("summary", "summary")]
REQUIRED = ("changed", "state", "decisions", "open", "next", "cold")
EVIDENCE = re.compile(r"#\d{2,}\b|\b\d{4}-\d{2}-\d{2}--[\w.-]+--[A-Z]{2,}\b")


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
        raise ValueError(f"{p}: fragment carries its own '# Handoff — vX' title; molt assigns the version")
    return meta, body.strip("\n")


def canon(heading):
    h = heading.strip().lower()
    for prefix, key in KEYS:
        if h.startswith(prefix):
            return key
    return None


def sections(body):
    """-> (lead text before the first '## ', {key: text}, [(heading, text) unrecognized])."""
    parts = re.split(r"^## +(.+?)\s*$", body, flags=re.M)
    lead, out, other = parts[0].strip(), {}, []
    for h, t in zip(parts[1::2], parts[2::2]):
        k, t = canon(h), t.strip()
        if k and t:
            out[k] = (out[k] + "\n" + t) if k in out else t
        elif t:
            other.append((h.strip(), t))
    return lead, out, other


def items(text):
    """Split '- x' / '1. x' lists into items (continuation lines kept); prose -> one item."""
    out, cur = [], None
    for line in text.splitlines():
        m = re.match(r"^\s*(?:[-*]|\d+\.)\s+(.*)$", line)
        if m:
            if cur is not None:
                out.append(cur)
            cur = m.group(1).rstrip()
        elif line.strip() and cur is not None:
            cur += "\n   " + line.strip()
        elif line.strip():
            cur = line.strip() if cur is None else cur
    if cur is not None:
        out.append(cur)
    return out


def new(root, branch, session):
    body = sys.stdin.read().strip("\n")
    if not body:
        sys.stderr.write("handoff_fold: empty body on stdin\n"); return 2
    if TITLE.search(body):
        sys.stderr.write("handoff_fold: drop the '# Handoff — vX' title; molt assigns the version\n"); return 2
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
        f.write(f"<!--\nsession: {session or slug(branch)}\nbranch: {branch}\nhead: {head}\n"
                f"created_at: {now:%Y-%m-%dT%H:%M:%SZ}\n-->\n{body}\n")
    _, sec, _ = sections(body)
    missing = [k for k in REQUIRED if k not in sec]
    if missing:
        sys.stderr.write(f"handoff_fold: WARN fragment missing section(s): {', '.join(missing)} "
                         f"(written anyway; molt will need them from another fragment or --input)\n")
    if "changed" in sec and not EVIDENCE.search(sec["changed"]):
        sys.stderr.write("handoff_fold: WARN '## Changed' cites no PR (#NNN) or receipt id\n")
    print(os.path.relpath(p, root))
    return 0


def split_blocks(text):
    """-> (preamble, [blocks]); a block runs from its '# Handoff' title to the next."""
    starts = [m.start() for m in TITLE.finditer(text)]
    if not starts:
        return text, []
    pre = text[:starts[0]]
    blocks = [text[a:b].rstrip("\n") for a, b in zip(starts, starts[1:] + [len(text)])]
    return pre, blocks


def block_version(block):
    """-> (major, minor, patch) parsed from a block's '# Handoff — vX.Y.Z' title."""
    return tuple(map(int, TITLE.match(block).groups()[:3]))


def assemble(frags, inp):
    """frags: [(path, meta, body)] oldest first; inp: molt input text. -> (sections dict, notes, sources)."""
    parsed = [(p, m) + sections(b) for p, m, b in frags]
    ilead, isec, _ = sections(inp or "")
    if ilead and "summary" not in isec:
        isec["summary"] = ilead
    out = {}
    for k in ("changed", "decisions", "open"):
        seen, acc = set(), []
        for *_, sec, _o in parsed:
            for it in items(sec.get(k, "")):
                if it not in seen:
                    seen.add(it); acc.append(it)
        out[k] = acc
    for k in ("state", "next", "cold", "goal"):
        out[k] = next((s[k] for *_, s, _o in reversed(parsed) if k in s), "")
    out["summary"] = "\n\n".join(l for _, _, l, _, _ in parsed if l)
    for k, v in isec.items():   # input overrides assembly
        out[k] = items(v) if k in ("changed", "decisions", "open") else v
    notes = [(h, t) for _, _, _, _, o in parsed for h, t in o]
    if "summary" in isec:  # the supplied summary replaces the fragment leads; keep them, never drop raw material
        notes = [(f"lead of {os.path.basename(p)}", l) for p, _, l, _, _ in parsed if l] + notes
    return out, notes


def gate(sec):
    """-> list of reasons the arc is refused (empty = accepted)."""
    why = []
    if not sec.get("goal", "").strip():
        why.append("no Goal / true north (add '## Goal' to a fragment or --input)")
    if not any(EVIDENCE.search(i) for i in sec.get("changed", [])):
        why.append("bookend: 'What changed' cites no merged PR (#NNN) or receipt id")
    nxt = sec.get("next", "").strip()
    if not nxt:
        why.append("no Next action")
    elif len(items(nxt)) != 1 or "\n\n" in nxt:
        why.append(f"Next action must be exactly ONE action, got {len(items(nxt))}")
    if not sec.get("cold", "").strip():
        why.append("no Cold-start recipe (files, commands, tracker view)")
    return why


def render(version, date, sec, notes, sources):
    zach = [i for i in sec["open"] if re.match(r"\**zach\b", i, re.I)]
    rest = [i for i in sec["open"] if i not in zach]
    num = lambda xs: "\n".join(f"{n}. {x}" for n, x in enumerate(xs, 1)) or "None."
    bul = lambda xs: "\n".join(f"- {x}" for x in xs) or "- None."
    out = [f"# Handoff — {version} ({date})", ""]
    if sec.get("summary"):
        out += ["\n".join("> " + l if l else ">" for l in sec["summary"].splitlines()), ""]
    out += ["## Goal / true north", sec["goal"].strip(), "",
            "## What changed", bul(sec["changed"]), "",
            "## Current state", sec.get("state", "").strip() or "Unchanged.", "",
            "## Decisions made", bul(sec["decisions"]), "",
            "## Open decisions (waiting on Zach)", num(zach), ""]
    if rest:
        out += ["## Open (other)", num(rest), ""]
    out += ["## Next action", sec["next"].strip().lstrip("-*0123456789. ").strip(), "",
            "## Cold-start recipe", sec["cold"].strip(), "",
            f"Debt lives in the tracker ({TRACKER}, `debt` collection); not restated here.", ""]
    for h, t in notes:
        out += [f"### Notes: {h}", t, ""]
    out.append("> Molted from " + "; ".join(sources) + ".")
    return "\n".join(out)


def oracle(root, dry):
    r = subprocess.run([sys.executable, ORACLE, "next", "handoff"] + (["--dry-run"] if dry else []),
                       capture_output=True, text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=root))
    if r.returncode != 0 or not r.stdout.strip().isdigit():
        raise RuntimeError(f"oracle next handoff failed: {r.stderr.strip()}")
    return int(r.stdout.strip())


DEFAULT_KEEP = 1


def archive(root, dry, keep):
    """Relocate blocks beyond `keep` (newest by version kept) to the archive. Anything after the last block's
    title (a stray trailing section) travels with that block, exactly as in molt."""
    cm, arch, _ = paths(root)
    pre, blocks = split_blocks(open(cm).read())
    blocks = sorted(blocks, key=block_version, reverse=True)
    live, overflow = blocks[:keep], blocks[keep:]
    if not overflow:
        print(f"handoff_fold: {len(live)} live block(s), keep {keep}: nothing to archive"); return 0
    if dry:
        print(f"DRY RUN: would keep {len(live)} live and relocate {len(overflow)}:")
        for b in overflow:
            print(f"  {b.splitlines()[0]} ({len(b.encode())} bytes)")
        return 0
    old = open(arch).read() if os.path.exists(arch) else ""
    os.makedirs(os.path.dirname(arch), exist_ok=True)
    with open(arch, "w") as f:
        f.write("\n\n---\n\n".join(overflow) + "\n\n---\n\n" + old)
    for b in overflow:
        print(f"archived: {b.splitlines()[0]}")
    with open(cm, "w") as f:
        f.write(pre + "\n\n".join(live) + "\n")
    print("handoff_fold: archived. Commit CLAUDE.md and _ARCHIVE/handoffs.md together.")
    return 0


def molt(root, dry, keep, inp):
    cm, arch, _ = paths(root)
    fps = fragments(root)
    if not fps:
        print("handoff_fold: no fragments to molt"); return 0
    frags = [(p,) + parse_fragment(p) for p in fps]
    sec, notes = assemble(frags, inp)
    why = gate(sec)
    if why:
        sys.stderr.write("handoff_fold: REFUSED (not a cold-moltable arc):\n" + "".join(f"  - {w}\n" for w in why))
        return 1
    n = oracle(root, dry)          # gate first, so a refused molt never burns a number
    version = f"v3.{n}.0"
    date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    sources = [f"`{os.path.relpath(p, root)}` (branch `{m.get('branch', '?')}`, head `{m.get('head', '?')}`)" for p, m, _ in frags]
    block = render(version, date, sec, notes, sources)
    pre, blocks = split_blocks(open(cm).read())
    # newest first BY VERSION: a hand-edited CLAUDE.md can carry blocks out of order (v3.104.0 below
    # v3.103.0 on 2026-10-06), and archiving by position then relocated the newer one (#919)
    blocks = sorted([block] + blocks, key=block_version, reverse=True)
    live, overflow = blocks[:keep], blocks[keep:]
    if dry:
        print(block)
        print(f"\nDRY RUN: would write {version} from {len(frags)} fragment(s), keep {len(live)} live, "
              f"relocate {len(overflow)}. Nothing written (oracle not advanced).")
        return 0
    if overflow:
        old = open(arch).read() if os.path.exists(arch) else ""
        os.makedirs(os.path.dirname(arch), exist_ok=True)
        with open(arch, "w") as f:
            f.write("\n\n---\n\n".join(overflow) + "\n\n---\n\n" + old)
        for b in overflow:
            print(f"archived: {b.splitlines()[0]}")
    with open(cm, "w") as f:
        f.write(pre + "\n\n".join(live) + "\n")
    for p in fps:
        os.remove(p)
    print(f"handoff_fold: molted {len(frags)} fragment(s) into {version}. Commit CLAUDE.md, _ARCHIVE/handoffs.md, "
          f"_HANDOFFS/fragments/ and _SEEDS/_oracle.json together.")
    return 0


FULL = ("## Goal\nOne cold-moltable arc per molt.\n\n## Changed\n- #950 merged; receipt 2026-10-06--x-pr950--ZH\n\n"
        "## State\nmolt live.\n\n## Decisions\n- molt replaces fold\n\n## Open\n1. Zach: approve merge\n2. score rows\n\n"
        "## Next action\nRun the 10-07 check.\n\n## Cold-start\nRead CLAUDE.md latest block; run `scripts/handoff_fold.py list`.\n")


def self_test():
    import tempfile, time
    me = os.path.abspath(__file__)
    fails = []

    def check(c, label):
        print(f"  {'PASS' if c else 'FAIL'} {label}")
        if not c:
            fails.append(label)

    def runner(root):
        return lambda *a, inp=None: subprocess.run([sys.executable, me, *a], input=inp, capture_output=True, text=True,
                                                   env=dict(os.environ, CLAUDE_PROJECT_DIR=root))

    def counter(root):
        import json
        p = os.path.join(root, "_SEEDS", "_oracle.json")
        return json.load(open(p)).get("handoff") if os.path.exists(p) else None

    with tempfile.TemporaryDirectory() as T:
        run = runner(T)
        subprocess.run(["git", "init", "-q", T])
        os.makedirs(os.path.join(T, "_ARCHIVE"))
        # out of order on purpose: v3.101.0 sits ABOVE v3.102.0
        claude = ("# Project\n\nrules\n\n---\n\n"
                  "# Handoff — v3.101.0 (2026-10-06)\n\nB101 body\n\n"
                  "# Handoff — v3.102.0 (2026-10-06)\n\nB102 body\n")
        open(os.path.join(T, "CLAUDE.md"), "w").write(claude)
        open(os.path.join(T, "_ARCHIVE", "handoffs.md"), "w").write("# Handoff — v3.99.0 (2026-10-05)\n\nB99\n")

        print("(1) new: cheap, append-only, warns (never blocks) on missing fields")
        r = run("new", "--branch", "claude/alpha", inp="> alpha did X\n\n## Open\n1. a\n")
        check(r.returncode == 0 and "WARN" in r.stderr and "cold" in r.stderr, "partial fragment written WITH a warning")
        check(open(os.path.join(T, "CLAUDE.md")).read() == claude, "CLAUDE.md untouched by `new`")
        r = run("new", inp="# Handoff — v3.101.0 (2026-10-06)\n\nx\n")
        check(r.returncode == 2, "titled body refused")

        print("(2) gate rejects a bookend (fail-on-bad); nothing written, oracle not advanced")
        r = run("molt")
        check(r.returncode == 1 and "bookend" in r.stderr and "Cold-start" in r.stderr, f"bookend refused: {r.stderr.strip()[:120]}")
        check(open(os.path.join(T, "CLAUDE.md")).read() == claude and len(fragments(T)) == 1, "no writes, fragment kept")
        check(counter(T) is None, "refused molt burns no oracle number")
        r = run("molt", "--input", "-", inp=FULL.replace("Run the 10-07 check.", "- one\n- two"))
        check(r.returncode == 1 and "exactly ONE" in r.stderr, "two next actions refused")

        print("(3) dry run prints the arc, writes nothing")
        time.sleep(1.1)
        run("new", "--branch", "claude/beta", inp=FULL)
        r = run("molt", "--dry-run")
        check(r.returncode == 0 and "# Handoff — v3.103.0" in r.stdout and len(fragments(T)) == 2
              and counter(T) is None, "dry run: v3.103.0 previewed, no writes")

        print("(4) full arc accepted (pass-on-good): ONE block, oracle version, version-sorted archive")
        r = run("molt", "--keep", "2", "--input", "-", inp="## Summary\nTwo sessions, one arc.\n")
        check(r.returncode == 0, f"molt exit 0 {r.stderr.strip()[:120]}")
        txt = open(os.path.join(T, "CLAUDE.md")).read()
        titles = [l.split(" (")[0] for l in txt.splitlines() if l.startswith("# Handoff")]
        check(titles == ["# Handoff — v3.103.0", "# Handoff — v3.102.0"], f"live = v3.103 (molt), v3.102 (by version): {titles}")
        check(counter(T) == 103, "version came from the oracle counter")
        check(txt.count("# Handoff — v3.103.0") == 1 and "alpha did X" in txt and "#950" in txt, "two fragments -> one block")
        for h in ("## Goal / true north", "## What changed", "## Current state", "## Decisions made",
                  "## Open decisions (waiting on Zach)", "## Next action", "## Cold-start recipe", TRACKER):
            check(h in txt, f"block has {h}")
        check(txt.startswith("# Project\n\nrules\n\n---\n\n"), "preamble preserved byte-for-byte")
        arch = open(os.path.join(T, "_ARCHIVE", "handoffs.md")).read()
        at = [l for l in arch.splitlines() if l.startswith("# Handoff")]
        check(at == ["# Handoff — v3.101.0 (2026-10-06)", "# Handoff — v3.99.0 (2026-10-05)"],
              f"out-of-order v3.101.0 archived, v3.102.0 kept: {at}")
        check(fragments(T) == [], "fragments deleted after molt")

        print("(5) oracle race: two molts on the same base, one wins, the loser re-molts to the next number")
        O = os.path.join(T, "origin.git")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", O])
        gi = lambda d, *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", d, *a],
                                          capture_output=True, text=True)
        S = os.path.join(T, "seed"); subprocess.run(["git", "clone", "-q", O, S], capture_output=True)
        gi(S, "checkout", "-qb", "main")
        open(os.path.join(S, "CLAUDE.md"), "w").write("# P\n\n# Handoff — v3.110.0 (2026-10-06)\n\nB110\n")
        gi(S, "add", "."); gi(S, "commit", "-qm", "base"); gi(S, "push", "-q", "origin", "main")
        res = {}
        for who in ("A", "B"):
            D = os.path.join(T, who); subprocess.run(["git", "clone", "-q", O, D], capture_output=True)
            runner(D)("new", "--branch", f"claude/{who}", inp=FULL)
            r = runner(D)("molt", "--keep", "2")
            gi(D, "add", "-A"); gi(D, "commit", "-qm", f"molt {who}")
            res[who] = (r.returncode, counter(D))
        check(res["A"] == (0, 111) and res["B"] == (0, 111), f"both sessions allocate v3.111.0 locally: {res}")
        check(gi(os.path.join(T, "A"), "push", "-q", "origin", "main").returncode == 0, "A pushes first: wins")
        B = os.path.join(T, "B")
        check(gi(B, "push", "-q", "origin", "main").returncode != 0, "B's push is non-ff REJECTED (git is the lock)")
        # B's loser recovery: reset to the winner's main, re-write its fragment, molt again
        gi(B, "fetch", "-q"); gi(B, "reset", "-q", "--hard", "origin/main")
        runner(B)("new", "--branch", "claude/B", inp=FULL)
        r = runner(B)("molt", "--keep", "2"); gi(B, "add", "-A"); gi(B, "commit", "-qm", "re-molt B")
        bt = [l.split(" (")[0] for l in open(os.path.join(B, "CLAUDE.md")).read().splitlines() if l.startswith("# Handoff")]
        check(r.returncode == 0 and counter(B) == 112 and bt[:2] == ["# Handoff — v3.112.0", "# Handoff — v3.111.0"],
              f"B re-molts on fresh main to v3.112.0, no duplicate: {bt}")
        check(gi(B, "push", "-q", "origin", "main").returncode == 0, "B's second push lands")

        print("(6) fold is a deprecated alias of molt")
        F = os.path.join(T, "f"); os.makedirs(F); open(os.path.join(F, "CLAUDE.md"), "w").write("# P\n")
        runner(F)("new", "--branch", "claude/f", inp=FULL)
        r = runner(F)("fold")
        check(r.returncode == 0 and "deprecated" in r.stderr.lower() and "v3.1.0" in open(os.path.join(F, "CLAUDE.md")).read(),
              "fold -> molt with a notice")

        print("(8) archive: trim CLAUDE.md between molts (WS1 slice 2), default keep is 1")
        A8 = os.path.join(T, "a8"); os.makedirs(os.path.join(A8, "_ARCHIVE"))
        blk = lambda v: f"# Handoff — v3.{v}.0 (2026-10-1{v % 10})\n\n## Goal / true north\nG{v}\n"
        open(os.path.join(A8, "CLAUDE.md"), "w").write("# Project\n\nrules\n\n---\n\n" + blk(7) + "\n" + blk(9) + "\n" + blk(8) + "\n# Stray tail section\n\nkeep with the last block\n")
        open(os.path.join(A8, "_ARCHIVE", "handoffs.md"), "w").write("# Handoff — v3.5.0 (2026-10-01)\n\nold\n")
        r8 = runner(A8)
        before = open(os.path.join(A8, "CLAUDE.md")).read()
        d = r8("archive", "--dry-run")
        check(d.returncode == 0 and open(os.path.join(A8, "CLAUDE.md")).read() == before, "dry run changes nothing")
        r = r8("archive")
        cm8 = open(os.path.join(A8, "CLAUDE.md")).read()
        ar8 = open(os.path.join(A8, "_ARCHIVE", "handoffs.md")).read()
        live8 = [l.split(" (")[0] for l in cm8.splitlines() if l.startswith("# Handoff")]
        arch8 = [l.split(" (")[0] for l in ar8.splitlines() if l.startswith("# Handoff")]
        check(r.returncode == 0 and live8 == ["# Handoff — v3.9.0"], f"keeps only the highest version (not the topmost): {live8}")
        check(arch8 == ["# Handoff — v3.8.0", "# Handoff — v3.7.0", "# Handoff — v3.5.0"], f"others archived newest first above the old archive: {arch8}")
        check(cm8.startswith("# Project\n\nrules\n\n---\n\n") and "G9" in cm8 and "G8" not in cm8, "preamble kept, newest body kept, older bodies gone from CLAUDE.md")
        check("Stray tail section" in ar8 and "Stray tail section" not in cm8, "a trailing section travels with the last block it follows")
        again = r8("archive")
        check(again.returncode == 0 and "nothing to archive" in again.stdout and open(os.path.join(A8, "CLAUDE.md")).read() == cm8, "second run is a no-op (idempotent)")
        check(r8("archive", "--keep", "2").returncode == 0, "explicit --keep is accepted")
        check(r8("archive", "--nope").returncode == 2, "archive rejects an unknown flag")

        print("(7) usage guard")
        check(run("bogus").returncode == 2, "unknown command exit 2")
        check(run("molt", "--nope").returncode == 2, "unknown flag exit 2")
        check(run("new", inp="").returncode == 2, "empty body exit 2")

    print(f"self-test: {'ALL PASS' if not fails else f'{len(fails)} FAIL'}")
    return 0 if not fails else 1


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    if not argv or argv[0] not in ("new", "list", "molt", "fold", "archive"):
        sys.stderr.write(__doc__.split("\n\n")[3] + "\n"); return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "fold":
        sys.stderr.write("handoff_fold: `fold` is DEPRECATED; it now runs `molt` (one arc from all fragments).\n")
        cmd = "molt"
    branch = session = inp_path = None
    dry, keep, i = False, DEFAULT_KEEP, 0
    while i < len(rest):
        a = rest[i]
        val = rest[i + 1] if i + 1 < len(rest) else None
        if cmd == "new" and a == "--branch" and val:
            branch = val; i += 2; continue
        if cmd == "new" and a == "--session" and val:
            session = val; i += 2; continue
        if cmd == "molt" and a == "--input" and val:
            inp_path = val; i += 2; continue
        if cmd in ("molt", "archive") and a == "--keep" and val and val.isdigit():
            keep = int(val); i += 2; continue
        if cmd in ("molt", "archive") and a == "--dry-run":
            dry = True; i += 1; continue
        sys.stderr.write(f"handoff_fold: unknown argument {a!r} for {cmd}\n"); return 2
    if cmd == "new":
        return new(ROOT, branch, session)
    if cmd == "list":
        fr = fragments(ROOT)
        print("\n".join(os.path.relpath(p, ROOT) for p in fr) if fr else "no unfolded fragments")
        return 0
    if cmd == "archive":
        return archive(ROOT, dry, keep)
    inp = None
    if inp_path:
        inp = sys.stdin.read() if inp_path == "-" else open(inp_path).read()
    try:
        return molt(ROOT, dry, keep, inp)
    except (ValueError, RuntimeError) as e:
        sys.stderr.write(f"handoff_fold: REFUSED: {e}\n"); return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
