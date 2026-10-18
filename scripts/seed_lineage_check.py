#!/usr/bin/env python3
"""seed_lineage_check: can a script walk a seed's ancestry? Read-only gate over _SEEDS/index.jsonl. Stdlib only.

python3 scripts/seed_lineage_check.py --report        # classes, counts, examples
python3 scripts/seed_lineage_check.py --check         # gate: exit 1 on a cycle, or on a NEW seed with no resolvable pointer
python3 scripts/seed_lineage_check.py --baseline-write  # grandfather today's debt (a deliberate human action)
python3 scripts/seed_lineage_check.py --edges         # print the parent edges that were found
python3 scripts/seed_lineage_check.py --self-test     # plant faults, require each to be caught

Invariant (Zach, 2026-10-15): one receipt or seed can sprout new lineage and its ancestry stays traceable. Structurally
that is a DAG: each unit points at a parent, and a real cycle in ancestry is a bug (a spiral in time, not a circle).
Receipts already have a database parent relation; seeds carried free-text provenance, so this reads the pointers out of
that text, and also honours an explicit `parent` / `derived_from` field (a seed id or list of seed ids) for new seeds.

Pointers it recognises in `provenance` (and in the explicit fields):
  seed id      an exact id from the index; a lineage verb ("from", "lineage to", "parent", "derived from", "child of",
               "supersedes", "replaces") before an unknown `seed-...` token makes it a DANGLING pointer
  commit       a 7-40 char hex word with a digit and a letter; must be an ancestor of HEAD (existence is not enough)
  ADR number   ADR-NNN, resolved against _DECISIONS
  repo path    a path with an extension, resolved against the checkout (absolute and ~ paths are machine-specific: skipped)

Classes per seed: ROOTED (at least one resolvable pointer), TEXT_ONLY (provenance with no pointer), ORPHAN (no
provenance and no explicit parent); DANGLING is a flag on top (a pointer that does not resolve). Cycles are searched among
seed-id edges only; `confluence`, `alias` and `conforms_to` are lateral relations, not ancestry, and are ignored.

Ratchet: _SEEDS/lineage-baseline.json lists the seeds that are not ROOTED today. They are grandfathered; a seed outside
the baseline that is TEXT_ONLY, ORPHAN or DANGLING fails the gate. A baselined seed that has since become ROOTED and clean
is reported as ready to graduate.
"""
import argparse
import glob
import inspect
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "_SEEDS", "index.jsonl")
BASELINE = os.path.join(ROOT, "_SEEDS", "lineage-baseline.json")

SEED_TOK = re.compile(r"\bseed-[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\b")
VERB = re.compile(r"(?:\bfrom|\blineage to|\bparent|\bderived from|\bchild of|\bsupersedes|\breplaces)\s+(?:the\s+)?(seed-[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)")
SHA = re.compile(r"\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b")
ADR = re.compile(r"\bADR-(\d{3})\b")
PATH = re.compile(r"(?<![\w/.~-])((?:[\w.-]+/)+[\w.-]+\.[A-Za-z][A-Za-z0-9]{0,4})\b")  # extension starts with a letter: 1.1/1.2 and v1.2 are not paths
URL = re.compile(r"https?://\S+")


class Ctx:
    """Resolvers, injectable so the self-test needs no repository."""

    def __init__(self, ids, sha_exists=None, adr_exists=None, path_exists=None):
        self.ids = ids
        self.sha_exists = sha_exists or self._git_sha
        self.adr_exists = adr_exists or (lambda n: bool(glob.glob(os.path.join(ROOT, "_DECISIONS", "ADR-%s*" % n))))
        self.path_exists = path_exists or (lambda p: os.path.exists(os.path.join(ROOT, p)))

    @staticmethod
    def _git_sha(s):
        # ancestry, not mere existence: a hash that survives only on an old local branch (for example from before the
        # 2026-06-03 history rewrite) would pass here and fail in CI, so it must be an ancestor of HEAD
        return subprocess.run(["git", "-C", ROOT, "merge-base", "--is-ancestor", s, "HEAD"], capture_output=True).returncode == 0


def pointers(row, ctx):
    """Return (resolved, dangling, parents): lists of pointer descriptions, plus the seed-id parents."""
    me = row.get("id")
    text = URL.sub("", str(row.get("provenance") or ""))
    resolved, dangling, parents = [], [], []
    for key in ("parent", "derived_from"):
        v = row.get(key)
        for x in (v if isinstance(v, list) else ([v] if v else [])):
            (resolved if x in ctx.ids else dangling).append("seed:" + str(x))
            if x in ctx.ids and x != me:
                parents.append(x)
    for t in set(SEED_TOK.findall(text)):
        if t in ctx.ids and t != me:
            resolved.append("seed:" + t)
            parents.append(t)
    for m in VERB.finditer(text):
        if m.group(1) not in ctx.ids:
            dangling.append("seed:" + m.group(1))
    for sha in set(SHA.findall(text)):
        (resolved if ctx.sha_exists(sha) else dangling).append("commit:" + sha)
    for n in set(ADR.findall(text)):
        (resolved if ctx.adr_exists(n) else dangling).append("adr:" + n)
    for p in set(PATH.findall(text)):
        if p.startswith(("/", "~")):
            continue
        (resolved if ctx.path_exists(p[2:] if p.startswith("./") else p) else dangling).append("path:" + p)
    return sorted(set(resolved)), sorted(set(dangling)), sorted(set(parents))


def find_cycles(edges):
    """edges: id -> list of parent ids. Return a list of cycles (each a list of ids)."""
    cycles, color, stack = [], {}, []

    def visit(n):
        color[n] = 1
        stack.append(n)
        for m in edges.get(n, []):
            if color.get(m, 0) == 0:
                visit(m)
            elif color.get(m) == 1:
                cycles.append(stack[stack.index(m):] + [m])
        stack.pop()
        color[n] = 2
    for n in list(edges):
        if color.get(n, 0) == 0:
            visit(n)
    return cycles


def analyze(rows, ctx):
    out, edges = {}, {}
    for r in rows:
        res, dang, par = pointers(r, ctx)
        has_text = bool(str(r.get("provenance") or "").strip())
        explicit = bool(r.get("parent") or r.get("derived_from"))
        cls = "ROOTED" if res else ("TEXT_ONLY" if has_text else ("ORPHAN" if not explicit else "ROOTED"))
        out[r["id"]] = {"class": cls, "dangling": dang, "resolved": res, "parents": par}
        edges[r["id"]] = par
    return out, edges, find_cycles(edges)


def load_rows(path=INDEX):
    return [json.loads(l) for l in open(path) if l.strip()]


def load_baseline(path=BASELINE):
    if not os.path.exists(path):
        return {}
    return json.load(open(path)).get("grandfathered", {})


def problems(res, cycles, baseline):
    """Hard problems for --check, and graduation notes."""
    bad, grad = [], []
    for c in cycles:
        bad.append("cycle in ancestry: " + " -> ".join(c))
    for i, r in res.items():
        flagged = r["class"] != "ROOTED" or r["dangling"]
        if flagged and i not in baseline:
            why = r["class"] if r["class"] != "ROOTED" else "DANGLING " + ", ".join(r["dangling"])
            bad.append("%s: %s and not in the baseline (new seeds need a resolvable pointer)" % (i, why))
        if not flagged and i in baseline:
            grad.append(i)
    return bad, grad


def self_test():
    ids = {"seed-a", "seed-b", "seed-c", "seed-d", "seed-e", "seed-f", "seed-g"}
    ctx = Ctx(ids, sha_exists=lambda s: s == "abc1234", adr_exists=lambda n: n == "064", path_exists=lambda p: p in ("src/real.ts", ".claude/hooks/x.sh"))

    def row(i, prov=None, **kw):
        return dict({"id": i, "provenance": prov}, **kw)
    rows = [
        row("seed-a", "germinated from seed-b"),                 # rooted by seed id
        row("seed-b", "minted at abc1234 after review"),         # rooted by commit
        row("seed-c", "grounded in ADR-064"),                    # rooted by ADR
        row("seed-d", "source src/real.ts"),                     # rooted by path
        row("seed-e", "cataloged 2026-08-13"),                   # text only
        row("seed-f", None),                                     # orphan
        row("seed-g", "lineage to seed-ghost and ADR-999, deadb33, src/gone.ts"),  # dangling x4
    ]
    res, edges, cyc = analyze(rows, ctx)
    assert res["seed-a"]["class"] == "ROOTED" and res["seed-a"]["parents"] == ["seed-b"], "seed-id pointer not read"
    assert res["seed-b"]["class"] == "ROOTED", "resolvable commit not accepted"
    assert res["seed-c"]["class"] == "ROOTED", "resolvable ADR not accepted"
    assert res["seed-d"]["class"] == "ROOTED", "resolvable path not accepted"
    assert res["seed-e"]["class"] == "TEXT_ONLY", "free text with no pointer must be TEXT_ONLY"
    assert res["seed-f"]["class"] == "ORPHAN", "missing provenance must be ORPHAN"
    assert len(res["seed-g"]["dangling"]) == 4, "dangling seed, ADR, commit and path not all found: %s" % res["seed-g"]["dangling"]
    assert not cyc, "false cycle on an acyclic graph"
    # self mention is not an edge; dates and plain words are not commits
    r2, _, c2 = analyze([row("seed-a", "seed-a rebuilt 20260813 decade deface")], ctx)
    assert r2["seed-a"]["class"] == "TEXT_ONLY" and not c2 and not r2["seed-a"]["dangling"], "self mention, a date or a hex-looking word counted as a pointer"
    # cycles
    cyc2 = analyze([row("seed-a", "from seed-b"), row("seed-b", "from seed-a")], ctx)[2]
    assert cyc2, "two-seed cycle not found"
    cyc3 = analyze([row("seed-a", "from seed-b"), row("seed-b", "from seed-c"), row("seed-c", "from seed-a")], ctx)[2]
    assert cyc3, "three-seed cycle not found"
    # a leading-dot directory must resolve, and version-like text must not be read as a path
    r5 = analyze([row("seed-a", "see .claude/hooks/x.sh"), row("seed-b", "ratio 1.1/1.2 and rubric-v1.2")], ctx)[0]
    assert r5["seed-a"]["class"] == "ROOTED" and not r5["seed-a"]["dangling"], "a path under a dot directory was mangled"
    assert r5["seed-b"]["class"] == "TEXT_ONLY" and not r5["seed-b"]["dangling"], "version-like text was read as a path"
    # explicit parent field
    r3 = analyze([row("seed-a", None, parent="seed-b"), row("seed-b", None, derived_from=["seed-ghost"])], ctx)[0]
    assert r3["seed-a"]["class"] == "ROOTED" and r3["seed-b"]["dangling"], "explicit parent fields not honoured"
    # lateral fields are not ancestry
    r4 = analyze([row("seed-a", "cataloged", alias="seed-b", confluence="seed-c")], ctx)
    assert r4[0]["seed-a"]["class"] == "TEXT_ONLY" and not r4[2], "alias or confluence treated as ancestry"
    # ratchet
    bad, grad = problems(res, cyc, {})
    assert any("seed-e" in b for b in bad) and any("seed-f" in b for b in bad) and any("seed-g" in b for b in bad), "new debt not flagged"
    bad, grad = problems(res, cyc, {"seed-e": "x", "seed-f": "x", "seed-g": "x", "seed-a": "x"})
    assert not bad, "grandfathered debt was flagged"
    assert grad == ["seed-a"], "a baselined seed that is now clean was not offered for graduation"
    bad, _ = problems(*analyze([row("seed-a", "from seed-b"), row("seed-b", "from seed-a")], ctx)[::2], {"seed-a": "x", "seed-b": "x"})
    assert any("cycle" in b for b in bad), "a cycle was excused by the baseline"
    n = sum(1 for l in inspect.getsource(self_test).splitlines() if l.strip().startswith("assert "))
    print("self-test OK: %d assertion sites behaved (four pointer kinds, text-only, orphan, four dangling kinds, no false cycle, 2- and 3-cycles, self mention, explicit parent, lateral fields, ratchet, graduation, cycles never grandfathered)" % n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--baseline-write", action="store_true")
    ap.add_argument("--edges", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    rows = load_rows()
    res, edges, cyc = analyze(rows, Ctx({r["id"] for r in rows}))
    base = load_baseline()
    from collections import Counter
    c = Counter(v["class"] for v in res.values())
    dang = [i for i, v in res.items() if v["dangling"]]
    if a.edges:
        for i, ps in sorted(edges.items()):
            for p in ps:
                print("%s -> %s" % (i, p))
        return
    if a.baseline_write:
        import datetime
        g = {i: ("%s%s" % (v["class"], " + DANGLING" if v["dangling"] else "")) for i, v in res.items() if v["class"] != "ROOTED" or v["dangling"]}
        json.dump({"_doc": "Seeds grandfathered by scripts/seed_lineage_check.py: not ROOTED, or carrying a dangling pointer, when the ratchet was set. New seeds need a resolvable pointer; fix a seed and it graduates.",
                   "written": str(datetime.date.today()), "grandfathered": g}, open(BASELINE, "w"), indent=1)
        open(BASELINE, "a").write("\n")
        print("wrote %s: %d seeds grandfathered" % (os.path.relpath(BASELINE, ROOT), len(g)))
        return
    print("SEED LINEAGE: %d seeds | ROOTED %d | TEXT_ONLY %d | ORPHAN %d | with a dangling pointer %d | seed-id edges %d | cycles %d" % (
        len(res), c["ROOTED"], c["TEXT_ONLY"], c["ORPHAN"], len(dang), sum(len(v) for v in edges.values()), len(cyc)))
    bad, grad = problems(res, cyc, base)
    if a.report or not a.check:
        for cl in ("TEXT_ONLY", "ORPHAN"):
            ex = [i for i, v in res.items() if v["class"] == cl][:5]
            print("  %-9s e.g. %s" % (cl, ", ".join(ex) or "none"))
        for i in dang[:6]:
            print("  dangling %-34s %s" % (i, ", ".join(res[i]["dangling"])[:90]))
        for cy in cyc:
            print("  CYCLE " + " -> ".join(cy))
    if grad:
        print("  ready to graduate from the baseline: " + ", ".join(grad))
    for b in bad:
        print("  PROBLEM " + b)
    if a.check:
        print("seed lineage gate: %s (baseline %d seeds)" % ("FAIL" if bad else "ok", len(base)))
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
