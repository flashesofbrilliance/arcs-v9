#!/usr/bin/env python3
"""prior_art.py — pre-plan lookup: what do we already know about this job?

Run before planning a task. Ranks the existing written learnings against a
plain-language job description so the plan starts from prior lessons instead of
re-deriving them. Read-only, stdlib-only, keyword scoring (no LLM, no embeddings).

Sources (each optional; a missing one is skipped, never an error):
  memory     ~/.claude/projects/-Users-zharris-arcs-v9/memory/*.md (name+description weighted)
  patterns   _PATTERNS/*.md
  adr        _DECISIONS/*.md
  rules      AGENTS.md, one chunk per section and per numbered gotcha
  tool       runtime/specs/tool-catalog.json (jtbd lines; reuse-before-invent)
  jtbd       the JTBD graph's jtbd(job) assembly (operators/jtbd_query.py lookup): best tool, open
             blockers, dependency closure, last receipts. Its own section, printed first; the five
             sources above are ranked exactly as before. A missing, stale or empty graph falls back
             to the keyword "tool" section and the section says which path answered (--no-jtbd skips it).

A source that cannot be found is reported on stderr, so a partial result never
passes for a complete one.

Usage:
  python3 scripts/prior_art.py "add a passcode gate to a new subdomain"
  python3 scripts/prior_art.py --top 3 --json "merge a PR and log a receipt"
"""
import argparse, json, math, os, re, subprocess, sys

MARKERS = ("AGENTS.md", "_DECISIONS", "_PATTERNS")


def find_repo():
    """The script's own repo; else the git checkout of the cwd. None if neither looks like arcs-v9."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cands = [here]
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True, timeout=5).stdout.strip()
        if top:
            cands.append(top)
    except (OSError, subprocess.SubprocessError):
        pass
    for c in cands:
        if all(os.path.exists(os.path.join(c, m)) for m in MARKERS):
            return c
    return None


REPO = find_repo()
MEMDIR = os.path.expanduser("~/.claude/projects/-Users-zharris-arcs-v9/memory")

STOP = set("""a an and are as at be by for from has have how i in into is it its of on or
our so that the this to use was we what when where which will with without you your
add make new fix do does can should would need want get set""".split())
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
DESC_RE = re.compile(r"^description:\s*(.+)$", re.M)
WORD_RE = re.compile(r"[a-z0-9]+")


def terms(text):
    out = set()
    for w in WORD_RE.findall(text.lower()):
        if len(w) > 2 and w not in STOP:
            out.add(w)
            if w.endswith("s") and len(w) > 4:
                out.add(w[:-1])
    return out


def score(q, idf, head_t, body_t):
    """Rare words weigh more (idf). Head (name/description) hits count 3x body hits."""
    hh = q & head_t
    bb = (q & body_t) - hh
    s = 3 * sum(idf[w] for w in hh) + sum(idf[w] for w in bb)
    return round(s, 1), len(hh), len(hh) + len(bb)


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def md_docs(kind, folder, rel_base=None):
    if not os.path.isdir(folder):
        return
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".md") or name == "MEMORY.md":
            continue
        path = os.path.join(folder, name)
        text = read(path)
        m = FM_RE.match(text)
        desc = ""
        if m:
            d = DESC_RE.search(m.group(1))
            desc = d.group(1).strip() if d else ""
            body = text[m.end():]
        else:
            first = next((l for l in text.splitlines() if l.strip()), "")
            desc = first.lstrip("# ").strip()
            body = text
        shown = os.path.relpath(path, rel_base) if rel_base else name[:-3]
        yield kind, shown, name[:-3].replace("-", " ") + " " + desc, desc, body


GOTCHA_RE = re.compile(r"^(\d+[a-z]?)\. \*\*(.+?)\*\*")


def rule_docs():
    """AGENTS.md split into its ## sections, with each numbered gotcha as its own chunk."""
    text = read(os.path.join(REPO, "AGENTS.md"))
    chunks, head, ref, buf = [], "", "", []

    def flush():
        if head and buf:
            chunks.append(("rules", ref, head, head, "\n".join(buf)))

    for line in text.splitlines():
        g = GOTCHA_RE.match(line)
        if line.startswith("## ") or g:
            flush()
            if g:
                head, ref = g.group(2).strip(" .:"), f"AGENTS.md gotcha {g.group(1)}"
            else:
                head = line[3:].strip()
                ref = f"AGENTS.md § {head}"
            buf = [line]
        else:
            buf.append(line)
    flush()
    # Path-scoped rule files (.claude/rules/*.md) hold content moved out of AGENTS.md so it loads only when
    # relevant; they stay searchable here, one chunk per section, so /prior-art does not lose them.
    rules_dir = os.path.join(REPO, ".claude", "rules")
    if os.path.isdir(rules_dir):
        for fn in sorted(os.listdir(rules_dir)):
            if not fn.endswith(".md"):
                continue
            head, ref, buf = "", "", []
            for line in read(os.path.join(rules_dir, fn)).splitlines():
                if line.startswith("## ") or line.startswith("# "):
                    if head and buf:
                        chunks.append(("rules", ref, head, head, "\n".join(buf)))
                    head = line.lstrip("# ").strip()
                    ref = f".claude/rules/{fn} § {head}"
                    buf = [line]
                elif head:
                    buf.append(line)
            if head and buf:
                chunks.append(("rules", ref, head, head, "\n".join(buf)))
    return chunks


def tool_docs():
    path = os.path.join(REPO, "runtime", "specs", "tool-catalog.json")
    try:
        tools = json.load(open(path, encoding="utf-8")).get("tools", [])
    except (OSError, ValueError):
        return
    for t in tools:
        jtbd = t.get("jtbd") or ""
        label = t.get("invoke") or t.get("path") or t.get("name", "")
        yield "tool", label, t.get("name", "") + " " + jtbd, jtbd, ""


def jtbd_section(job):
    """The graph lookup, or a fallback dict. Never raises: prior-art must still answer without the graph."""
    if not REPO:
        return {"path": "fallback", "reason": "no arcs-v9 checkout", "answer": None}
    try:
        sys.path.insert(0, os.path.join(REPO, "operators"))
        import jtbd_query
        try:
            from arcs_librarian import load_universes
            from pathlib import Path
            recs = load_universes(Path(REPO))
        except Exception:
            recs = None
        return jtbd_query.lookup(job, REPO, MEMDIR, recs)
    except Exception as e:
        return {"path": "fallback", "reason": f"lookup failed ({type(e).__name__})", "answer": None}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("job", nargs="+", help="plain-language description of the task")
    ap.add_argument("--top", type=int, default=5, help="max hits per source (default 5)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-jtbd", action="store_true", help="skip the JTBD graph tool assembly")
    a = ap.parse_args()

    q = terms(" ".join(a.job))
    if not q:
        sys.exit("prior_art: job has no searchable words")

    missing = []
    if not os.path.isdir(MEMDIR):
        missing.append(f"memory ({MEMDIR})")
    docs = list(md_docs("memory", MEMDIR))
    if REPO:
        docs += md_docs("patterns", os.path.join(REPO, "_PATTERNS"), REPO)
        docs += md_docs("adr", os.path.join(REPO, "_DECISIONS"), REPO)
        docs += rule_docs()
        tools = list(tool_docs())
        if not tools:
            missing.append("tool (runtime/specs/tool-catalog.json)")
        docs += tools
    else:
        missing.append("patterns, adr, rules, tool (no arcs-v9 checkout found from the script's "
                       "folder or the current directory; run ./scripts/prior_art.py from a worktree)")
    for m in missing:
        print(f"prior_art: WARNING source not searched: {m}", file=sys.stderr)

    rows = [(k, r, terms(h), d, terms(b[:20000])) for k, r, h, d, b in docs]
    n = len(rows) or 1
    idf = {w: math.log((n + 1) / (1 + sum(1 for x in rows if w in x[2] or w in x[4]))) + 0.1
           for w in q}
    # A hit must touch the head at least once, or match 2+ distinct terms overall.
    floor = 2 if len(q) > 1 else 1
    by_kind = {}
    for kind, ref, head_t, desc, body_t in rows:
        s, h, total = score(q, idf, head_t, body_t)
        if h or total >= floor:
            by_kind.setdefault(kind, []).append((s, ref, desc))
    result = {k: sorted(v, key=lambda r: -r[0])[: a.top] for k, v in by_kind.items()}

    jt = None if a.no_jtbd else jtbd_section(" ".join(a.job))
    if a.json:
        out = {k: [{"score": s, "ref": r, "desc": d} for s, r, d in v] for k, v in result.items()}
        if jt is not None:
            out["jtbd"] = jt
        print(json.dumps(out, indent=2))
        return
    if jt is not None:
        print("## tool assembly (jtbd graph)")
        try:
            import jtbd_query
            print(jtbd_query.render(jt))
        except Exception:
            print(f"answered by: {jt['path']} ({jt['reason']})")
        if jt["path"] != "jtbd-graph":
            print("  -> see the keyword-ranked `## tool` section below")
        print()
    if not result:
        print("prior_art: no prior learnings matched. Plan fresh, and capture what you learn.")
        return
    for kind in ("rules", "memory", "patterns", "adr", "tool"):
        rows = result.get(kind)
        if not rows:
            continue
        print(f"## {kind}")
        for s, ref, desc in rows:
            print(f"  [{s:>5}] {ref}" + (f" :: {desc[:140]}" if desc else ""))
    print("\nRead the top hits that apply before planning; cite them in the plan.")


if __name__ == "__main__":
    main()
