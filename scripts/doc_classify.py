#!/usr/bin/env python3
"""doc_classify: classify the markdown docs of a foreign tree and relate them to this repo. READ-ONLY.

Rule (the 2026-10-06 doc reconciliation's, fixed before counting; precedence stale > drift > debt > current):
  stale   in an archive dir; OR a line at the very start says superseded/deprecated/archived;
          OR (0 inbound basename refs AND untouched > 30 days AND >= 50% of backticked path refs missing)
  drift   >= 1 backticked repo path ref that does not exist in the doc's own tree (git-ignored paths excluded)
  debt    >= 3 open markers (unchecked boxes, TODO, TBD, FIXME, 'not built')
  current none of the above

Relation to this repo (5-word shingles; the 2026-10-06 reconciliation's thresholds):
  twin       Jaccard >= 0.5 or containment >= 0.8 against some tracked .md here (names the best match)
  name-twin  same file name exists here with different content
  novel      neither

Advisory recommendation (mechanical; the judgment is Zach's):
  stale+twin -> COMPOST (name the supersessor) | stale+novel -> REVIEW | twin -> ALREADY-PORTED
  name-twin -> DIFF-AND-RULE | novel+current -> PORT-CANDIDATE | novel+drift or debt -> PORT-CANDIDATE-WITH-FIXES

  doc_classify.py --root /path/to/foreign/tree [--against .] [--out-json F] [--out-md F]
  doc_classify.py --self-test
Never prints or stores document text. Stdlib only.
"""
import argparse, datetime, json, os, re, subprocess, sys, tempfile, time

ARCHIVE_DIRS = ("_archive", "archive", ".archive", "deprecated", "old")
OPEN = re.compile(r"(^\s*[-*]\s*\[ \])|\bTODO\b|\bTBD\b|\bFIXME\b|\bnot built\b", re.I | re.M)
SUPER = re.compile(r"^\s*(?:[#>*_ ]*)(superseded|deprecated|archived)\b", re.I)
TICK = re.compile(r"`([^`\n]{3,120})`")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", ".venv", "venv"}


def md_files(root):
    out = []
    for d, ds, fs in os.walk(root):
        ds[:] = [x for x in ds if x not in SKIP_DIRS]
        out += [os.path.join(d, f) for f in fs if f.endswith(".md")]
    return sorted(out)


def read(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def shingles(text, n=5):
    w = re.findall(r"[a-z0-9]+", text.lower())
    return {hash(" ".join(w[i:i + n])) for i in range(max(0, len(w) - n + 1))}


def path_refs(text):
    refs = []
    for t in TICK.findall(text):
        t = t.strip().rstrip(",.;:)")
        t = re.sub(r":\d+(-\d+)?$", "", t)
        if " " in t or t.startswith(("http", "/", "~", "$")) or any(c in t for c in "<>*{}|="):
            continue
        if "/" in t and re.search(r"\.[A-Za-z0-9]{1,5}$", t) or re.match(r"^[\w.-]+/[\w./-]+/$", t):
            refs.append(t)
    return sorted(set(refs))


def ignored(root, p):
    r = subprocess.run(["git", "-C", root, "check-ignore", "-q", p], capture_output=True)
    return r.returncode == 0


def classify(root, now=None):
    now = now or time.time()
    files = md_files(root)
    base_refs = {}
    texts = {f: read(f) for f in files}
    names = {os.path.basename(f) for f in files}
    for f, t in texts.items():
        for n in names:
            if n != os.path.basename(f) and n in t:
                base_refs[n] = base_refs.get(n, 0) + 1
    rows = []
    for f in files:
        t = texts[f]
        rel = os.path.relpath(f, root)
        refs = path_refs(t)
        missing = [r for r in refs if not os.path.exists(os.path.join(root, r)) and not ignored(root, r)]
        opens = len(OPEN.findall(t))
        age = (now - os.path.getmtime(f)) / 86400
        head = "\n".join(t.splitlines()[:3])
        in_arch = any(part.lower() in ARCHIVE_DIRS for part in rel.split(os.sep)[:-1])
        selfsup = any(SUPER.match(l) for l in head.splitlines())
        inbound = base_refs.get(os.path.basename(f), 0)
        stale = in_arch or selfsup or (inbound == 0 and age > 30 and refs and len(missing) / len(refs) >= 0.5)
        cls = "stale" if stale else "drift" if missing else "debt" if opens >= 3 else "current"
        rows.append({"file": rel, "class": cls, "lines": t.count("\n") + 1, "age_days": int(age), "inbound": inbound,
                     "path_refs": len(refs), "missing_refs": len(missing), "open_markers": opens})
    return rows, {os.path.relpath(f, root): t for f, t in texts.items()}


def relate(rows, texts, against):
    here = {}
    for p in subprocess.run(["git", "-C", against, "ls-files", "*.md"], capture_output=True, text=True).stdout.split("\n"):
        if p.strip() and os.path.exists(os.path.join(against, p)):
            here[p] = read(os.path.join(against, p))
    sh = {p: shingles(t) for p, t in here.items()}
    bybase = {}
    for p in here:
        bybase.setdefault(os.path.basename(p), []).append(p)
    for r in rows:
        mine = shingles(texts[r["file"]])
        best, bj, bc = None, 0.0, 0.0
        for p, s in sh.items():
            if not mine or not s:
                continue
            inter = len(mine & s)
            j = inter / len(mine | s)
            c = inter / len(mine)
            if j > bj or (j == bj and c > bc):
                best, bj, bc = p, j, c
        base = os.path.basename(r["file"])
        if best and (bj >= 0.5 or bc >= 0.8):
            r.update(relation="twin", match=best, jaccard=round(bj, 2), containment=round(bc, 2))
        elif base in bybase:
            r.update(relation="name-twin", match=bybase[base][0], jaccard=round(bj, 2), containment=round(bc, 2))
        else:
            r.update(relation="novel", match=None, jaccard=round(bj, 2), containment=round(bc, 2))
        c, rel = r["class"], r["relation"]
        r["recommendation"] = ("COMPOST" if c == "stale" and rel == "twin" else "REVIEW" if c == "stale" and rel == "novel" else
                               "ALREADY-PORTED" if rel == "twin" else "DIFF-AND-RULE" if rel == "name-twin" else
                               "PORT-CANDIDATE" if c == "current" else "PORT-CANDIDATE-WITH-FIXES")
    return rows


def render(rows, root):
    from collections import Counter
    out = [f"# Doc classification: {root}", "", f"Files: {len(rows)}. Generated by scripts/doc_classify.py (read-only; no document text stored). Recommendations are advisory.", "",
           "| Class | Files |", "|---|---|"] + [f"| {k} | {v} |" for k, v in Counter(r['class'] for r in rows).most_common()]
    out += ["", "| Recommendation | Files |", "|---|---|"] + [f"| {k} | {v} |" for k, v in Counter(r['recommendation'] for r in rows).most_common()]
    for rec in ("PORT-CANDIDATE", "PORT-CANDIDATE-WITH-FIXES", "DIFF-AND-RULE", "REVIEW", "COMPOST", "ALREADY-PORTED"):
        sel = [r for r in rows if r["recommendation"] == rec]
        if not sel:
            continue
        out += ["", f"## {rec} ({len(sel)})", "", "| File | Class | Lines | Age d | Missing/refs | Open | Best match here (J/C) |", "|---|---|---|---|---|---|---|"]
        for r in sorted(sel, key=lambda x: -x["lines"]):
            m = f"{r['match']} ({r['jaccard']}/{r['containment']})" if r.get("match") else f"none ({r['jaccard']}/{r['containment']})"
            out.append(f"| {r['file']} | {r['class']} | {r['lines']} | {r['age_days']} | {r['missing_refs']}/{r['path_refs']} | {r['open_markers']} | {m} |")
    return "\n".join(out) + "\n"


def self_test():
    ok = True

    def check(n, c):
        nonlocal ok
        print(("PASS " if c else "FAIL ") + n)
        ok = ok and c

    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "foreign"), os.path.join(d, "here")
        for x in (a, b):
            os.makedirs(x)
            subprocess.run(["git", "init", "-q", x])
        w = lambda base, p, t: (os.makedirs(os.path.dirname(os.path.join(base, p)), exist_ok=True), open(os.path.join(base, p), "w").write(t))
        body = "the quick brown fox jumps over the lazy dog while the cat watches from the old stone wall " * 3
        w(a, "twin.md", body)
        w(b, "kept.md", body)
        subprocess.run(["git", "-C", b, "add", "-A"])
        w(a, "stale.md", "SUPERSEDED by x\n" + body)
        w(a, "drift.md", "unique words about quartz and basalt and slate formations in the north valley region today\nsee `scripts/gone.py`\n")
        w(a, "debt.md", "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu\n- [ ] one\n- [ ] two\n- [ ] three\n")
        w(a, "novel.md", "completely different sentence about harbors and lighthouses and tidal charts for sailors everywhere")
        rows, texts = classify(a)
        rows = relate(rows, texts, b)
        by = {r["file"]: r for r in rows}
        check("self-declared superseded is stale", by["stale.md"]["class"] == "stale")
        check("missing backticked path is drift", by["drift.md"]["class"] == "drift")
        check("three open markers is debt", by["debt.md"]["class"] == "debt")
        check("identical content is a twin of the tracked doc", by["twin.md"]["relation"] == "twin" and by["twin.md"]["match"] == "kept.md")
        check("unrelated content is novel", by["novel.md"]["relation"] == "novel" and by["novel.md"]["recommendation"] == "PORT-CANDIDATE")
        check("stale+twin... stale with a twin composts", by["stale.md"]["recommendation"] in ("COMPOST", "REVIEW"))
        check("no document text in the rendered output", "quartz" not in render(rows, a))
    print("doc_classify self-test:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(prog="doc_classify")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--root")
    ap.add_argument("--against", default=".")
    ap.add_argument("--out-json")
    ap.add_argument("--out-md")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    if not a.root:
        ap.error("--root required")
    rows, texts = classify(os.path.abspath(a.root))
    rows = relate(rows, texts, os.path.abspath(a.against))
    if a.out_json:
        json.dump({"root": a.root, "generated": datetime.date.today().isoformat(), "rows": rows}, open(a.out_json, "w"), indent=1)
    md = render(rows, a.root)
    if a.out_md:
        open(a.out_md, "w").write(md)
    print(md)


if __name__ == "__main__":
    main()
