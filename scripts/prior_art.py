#!/usr/bin/env python3
"""prior_art.py — pre-plan lookup: what do we already know about this job?

Run before planning a task. Ranks the existing written learnings against a
plain-language job description so the plan starts from prior lessons instead of
re-deriving them. Read-only, stdlib-only, keyword scoring (no LLM, no embeddings).

Sources (each optional; a missing one is skipped, never an error):
  memory     ~/.claude/projects/-Users-zharris-arcs-v9/memory/*.md (name+description weighted)
  patterns   _PATTERNS/*.md
  adr        _DECISIONS/*.md
  tool       runtime/specs/tool-catalog.json (jtbd lines; reuse-before-invent)

Usage:
  python3 scripts/prior_art.py "add a passcode gate to a new subdomain"
  python3 scripts/prior_art.py --top 3 --json "merge a PR and log a receipt"
"""
import argparse, json, math, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("job", nargs="+", help="plain-language description of the task")
    ap.add_argument("--top", type=int, default=5, help="max hits per source (default 5)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    q = terms(" ".join(a.job))
    if not q:
        sys.exit("prior_art: job has no searchable words")

    docs = []
    docs += md_docs("memory", MEMDIR)
    docs += md_docs("patterns", os.path.join(REPO, "_PATTERNS"), REPO)
    docs += md_docs("adr", os.path.join(REPO, "_DECISIONS"), REPO)
    docs += tool_docs()

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

    if a.json:
        print(json.dumps({k: [{"score": s, "ref": r, "desc": d} for s, r, d in v]
                          for k, v in result.items()}, indent=2))
        return
    if not result:
        print("prior_art: no prior learnings matched. Plan fresh, and capture what you learn.")
        return
    for kind in ("memory", "patterns", "adr", "tool"):
        rows = result.get(kind)
        if not rows:
            continue
        print(f"## {kind}")
        for s, ref, desc in rows:
            print(f"  [{s:>5}] {ref}" + (f" :: {desc[:140]}" if desc else ""))
    print("\nRead the top hits that apply before planning; cite them in the plan.")


if __name__ == "__main__":
    main()
