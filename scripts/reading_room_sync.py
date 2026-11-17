#!/usr/bin/env python3
"""reading_room_sync.py: one command that keeps app.arcs.care/reading-room and /warroom/surfaces in
step with the repo.

WHY: the Reading Room's three tenants (Almanac, Concordance, Chronicle) and the War Room surface
catalog each have their own renderer, but nothing ran them together and nothing failed when a render
went stale. On 2026-11-11 the Almanac render dated 2026-10-04, the Concordance 2026-09-07, and the
Chronicle failed its own --check, while the surface catalog (the only one wired into pre-commit and
CI) was current. This script is the conductor: it calls the existing renderers in order and adds no
rendering logic of its own (prior_art.py 2026-11-11: no sync tool existed; the full metabolic router
of ADR-075 / build plan Phase 3 is still unbuilt and is NOT this).

WHAT IT DOES
  1. renders   surface_catalog_emit.py, chronicle_render.py, research_render.py (Almanac),
               concordance_render.py, each with its own defaults.
  2. cache     cache_manifest.py check: reports fresh vs dirty slices. NEVER stamps. Only a complete
               re-grade may advance a slice (build plan row 1b; WITNESS honesty).
  3. intake    lists corpus records (ADRs, recoil files, patterns) that exist on disk but appear in no
               digest node. Writes _ARTIFACTS/atlas/intake-queue.json. This is the judgment queue:
               curating a record into a digest (status, claim, links) is a Curator job, not this one.

Usage:
  python3 scripts/reading_room_sync.py                 # render everything, report cache, write queue
  python3 scripts/reading_room_sync.py --check         # exit 1 if any committed render is stale
  python3 scripts/reading_room_sync.py --check --strict-cache   # also exit 2 if any cache slice is dirty
  python3 scripts/reading_room_sync.py --self-test
--check ignores only two moving stamps: the render date the Almanac ("rendered YYYY-MM-DD") and
Concordance ("built YYYY-MM-DD") embed, and the cache-manifest repo_head the Almanac embeds (it
changes with every commit, including the one that commits the render). The cache check runs BEFORE
the renders so the Almanac embeds the current manifest. Stdlib only.
"""
import argparse, datetime, glob, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATLAS = os.path.join(ROOT, "_ARTIFACTS", "atlas")
QUEUE = os.path.join(ATLAS, "intake-queue.json")
DATE_STAMP = re.compile(r"(rendered|built) \d{4}-\d{2}-\d{2}")
HEAD_STAMP = re.compile(r'"repo_head": "[0-9a-f]{7,40}"')  # the Almanac embeds the manifest head; it moves with every commit
INTAKE_SOURCES = [  # (kind, glob, key) key: how a digest would cite the record
    ("adr", "_DECISIONS/ADR-*.md", "adr"),
    ("recoil", "runtime/recoil/generated/*", "stem"),
    ("pattern", "_PATTERNS/*.md", "stem"),
]


def run(args, quiet=False):
    p = subprocess.run([sys.executable] + args, cwd=ROOT, capture_output=True, text=True)
    if not quiet and p.stdout.strip():
        print("   " + p.stdout.strip().splitlines()[-1])
    return p


def digests():
    return sorted(glob.glob(os.path.join(ATLAS, "digest-*.json")))


def normalize(text):
    return HEAD_STAMP.sub('"repo_head": "HEAD"', DATE_STAMP.sub(r"\1 DATE", text))


def same_render(script, committed):
    """Render to a temp file and compare with the committed render, ignoring the date stamp."""
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "r.html")
        p = run([os.path.join("scripts", script), out] + digests(), quiet=True)
        if p.returncode != 0 or not os.path.exists(out):
            return False, f"{script} failed: {(p.stderr or p.stdout).strip()[-200:]}"
        try:
            old = open(committed, encoding="utf-8").read()
        except FileNotFoundError:
            return False, "committed render missing"
        return normalize(open(out, encoding="utf-8").read()) == normalize(old), ""


STEPS = [
    ("surfaces", ["scripts/surface_catalog_emit.py"], lambda: run(["scripts/surface_catalog_emit.py", "--check"], quiet=True).returncode == 0),
    ("chronicle", ["scripts/chronicle_render.py"], lambda: run(["scripts/chronicle_render.py", "--check"], quiet=True).returncode == 0),
    ("almanac", ["scripts/research_render.py"], lambda: same_render("research_render.py", os.path.join(ATLAS, "atlas-almanac.html"))[0]),
    ("concordance", ["scripts/concordance_render.py"], lambda: same_render("concordance_render.py", os.path.join(ATLAS, "concordance.html"))[0]),
]


def cache_report(today, read_only=False):
    """cache_manifest.py check rewrites the manifest (it re-records repo_head). Under --check the
    bytes are snapshotted and restored, so --check writes nothing."""
    man = os.path.join(ATLAS, "cache-manifest.json")
    before = open(man, "rb").read() if read_only and os.path.exists(man) else None
    p = run(["scripts/cache_manifest.py", "--today", today, "--json", "check"], quiet=True)
    if before is not None:
        open(man, "wb").write(before)
    try:
        data = json.loads(p.stdout)
        slices = data.get("slices", data if isinstance(data, list) else [])
        dirty = sum(1 for s in slices if s.get("state", "").upper() != "FRESH" and not s.get("fresh", False))
        epochs = sorted({s.get("epoch", "") for s in slices if re.fullmatch(r"\d{4}-\d{2}", str(s.get("epoch", "")))})
        return {"slices": len(slices), "dirty": dirty, "newest_epoch": epochs[-1] if epochs else "unknown"}
    except (ValueError, AttributeError):
        return {"slices": None, "dirty": None, "newest_epoch": "unknown", "error": (p.stderr or p.stdout).strip()[-200:]}


def digest_text(paths):
    parts = []
    for p in paths:
        try:
            j = json.load(open(p, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for n in (j.get("nodes", []) if isinstance(j, dict) else j):
            parts.append(" ".join(str(n.get(k, "")) for k in ("id", "title", "provenance", "claim", "note")))
    return "\n".join(parts).lower()


def record_key(kind_key, path):
    base = os.path.basename(path)
    if kind_key == "adr":
        m = re.match(r"(ADR-\d+)", base)
        return m.group(1).lower() if m else None
    return os.path.splitext(base)[0].lower()


def added_dates(globs):
    """First-add date per path, one git pass. A file that arrived by rename has no add row -> "unknown (rename)"."""
    p = subprocess.run(["git", "log", "--diff-filter=A", "--name-only", "--format=@%cs", "--"] + globs,
                       cwd=ROOT, capture_output=True, text=True)
    dates, cur = {}, None
    for line in p.stdout.splitlines():
        if line.startswith("@"):
            cur = line[1:]
        elif line.strip():
            dates[line.strip()] = cur  # log is newest first; keep overwriting so the oldest add wins
    return dates


def intake(text):
    dates = added_dates([g for _, g, _ in INTAKE_SOURCES])
    rows = []
    for kind, pattern, key in INTAKE_SOURCES:
        for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
            rel = os.path.relpath(path, ROOT)
            k = record_key(key, rel)
            if not k or k in text:
                continue
            rows.append({"kind": kind, "path": rel, "added": dates.get(rel, "unknown (rename)")})
    rows.sort(key=lambda r: (r["added"], r["path"]), reverse=True)
    return rows


def self_test():
    assert normalize("x rendered 2026-10-04 y built 2026-09-07") == "x rendered DATE y built DATE"
    assert normalize("graded 2026-09-07") == "graded 2026-09-07", "only render stamps are ignored"
    assert normalize('"repo_head": "1b95052"') == '"repo_head": "HEAD"'
    assert record_key("adr", "_DECISIONS/ADR-093-counterpart-citation.md") == "adr-093"
    assert record_key("stem", "runtime/recoil/generated/2026-10-29-gasmi.json") == "2026-10-29-gasmi"
    with tempfile.TemporaryDirectory() as d:
        dg = os.path.join(d, "digest-test.json")
        json.dump({"nodes": [{"id": "x", "provenance": "_DECISIONS/ADR-071-mobius.md"}]}, open(dg, "w"))
        t = digest_text([dg])
        assert "adr-071" in t and "adr-093" not in t
    print("reading_room_sync self-test: ok")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if any committed render is stale; write nothing")
    ap.add_argument("--strict-cache", action="store_true", help="with --check, also exit 2 if any cache slice is dirty")
    ap.add_argument("--today", help="YYYY-MM-DD for the cache check (default: today)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    today = a.today or datetime.date.today().isoformat()

    c = cache_report(today, read_only=a.check)
    print(f"reading_room_sync: cache {c['slices']} slices, {c['dirty']} dirty, newest epoch {c['newest_epoch']} (never stamped here)")

    stale = []
    print("reading_room_sync: renders")
    for name, write_cmd, is_current in STEPS:
        if a.check:
            ok = is_current()
            print(f"  {'ok   ' if ok else 'STALE'} {name}")
            if not ok:
                stale.append(name)
        else:
            print(f"  render {name}")
            p = run(write_cmd)
            if p.returncode != 0:
                print(f"  FAILED {name}: {(p.stderr or p.stdout).strip()[-300:]}", file=sys.stderr)
                return 1


    rows = intake(digest_text(digests()))
    by_kind = {}
    for r in rows:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
    print(f"reading_room_sync: intake {len(rows)} records on disk in no digest " + json.dumps(by_kind, sort_keys=True))
    if not a.check:
        with open(QUEUE, "w", encoding="utf-8") as f:
            json.dump({"spec": "scripts/reading_room_sync.py", "note": "judgment queue: curate into a digest, then re-render",
                       "sources": [g for _, g, _ in INTAKE_SOURCES], "rows": rows}, f, indent=1)
            f.write("\n")
        print(f"   wrote {os.path.relpath(QUEUE, ROOT)}")

    if a.check and stale:
        print(f"stale: {', '.join(stale)}. Fix: python3 scripts/reading_room_sync.py, then stage the renders.", file=sys.stderr)
        return 1
    if a.check and a.strict_cache and c["dirty"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
