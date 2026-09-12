#!/usr/bin/env python3
"""cache_manifest.py — the Almanac cache manifest (Reading Room build plan row 1b).

A *slice* is one ``(domain, epoch)`` bucket of already-graded digest nodes — the atom
of the corpus cache — stamped with the commit it was graded against and the file globs
whose changes could invalidate it. The manifest is the index over those slices: a slice
is *fresh* while nothing in its ``scope_globs`` changed between ``graded_at_sha`` and
``HEAD``, and *dirty* (a cache miss waiting to happen) otherwise.

Spec: ``_ARTIFACTS/atlas/cache-manifest.spec.md``. Mechanical/judgment split per
``_SPECS/metabolic-router-v1.md`` §3: everything in this file is mechanical (group,
diff, stamp, invalidate). The judgment half — re-grading a dirty slice via a targeted
Curator run — is deliberately NOT implemented here (see the TODO seam in ``main``).

Usage:
    python3 scripts/cache_manifest.py --today YYYY-MM-DD stamp
    python3 scripts/cache_manifest.py --today YYYY-MM-DD check
    python3 scripts/cache_manifest.py --today YYYY-MM-DD --json check

``--today`` is required (no ``datetime.now``) so two runs on the same tree are
byte-identical. ``check`` exits 2 if any slice is dirty (including MISSING / ORPHAN /
unknown-domain / untracked-digest markers), 0 otherwise, 1 on any error or usage mistake.
stdlib only.
"""
from __future__ import annotations

import argparse
import fnmatch
import glob
import json
import os
import re
import subprocess
import sys
from collections import OrderedDict

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ATLAS_DIR = os.path.join(REPO, "_ARTIFACTS", "atlas")
MANIFEST_PATH = os.path.join(ATLAS_DIR, "cache-manifest.json")
DIGEST_GLOB = os.path.join(ATLAS_DIR, "digest-*.json")

# Fixed provenance scope per auditor domain (spec §cache-manifest.json).
# Scope = what the digest was graded FROM, not what the spec first guessed. The memory corpus
# is not vendored into the repo, so memories freshness is index-level (MEMORY.md + archive);
# recoil nodes cite the recoil SSOTs, the memory index, and the gate/proxy code they describe.
SCOPE_GLOBS = {
    "memories": ["_MEMORY/*.md", "MEMORY.md", "_ARCHIVE/memory-archive.md"],
    "product": ["_DECISIONS/*", "_SEEDS/*", "WORLD.md", "AGENTS.md"],
    "handoffs": ["CLAUDE.md", "_ARCHIVE/handoffs.md"],
    "recoil": ["runtime/recoil/**", "MEMORY.md", "_PATTERNS/counterpart-*.md",
               "src/proxy.ts", "src/lib/admin.ts", "src/lib/ammo-gate.ts"],
}
DOMAIN_ORDER = ["memories", "handoffs", "product", "recoil"]
UNKNOWN_EPOCH = "unknown"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
# Keys a digest may use to record the sha it was graded against (none do yet).
DIGEST_SHA_KEYS = ("graded_at_sha", "repo_head", "sha", "git_sha", "head_sha")


# ---------------------------------------------------------------- git helpers
def git(*args: str) -> str:
    out = subprocess.run(
        ["git", "-C", REPO, *args], capture_output=True, text=True, check=True
    )
    return out.stdout.strip()


def head_sha() -> str:
    return git("rev-parse", "HEAD")


def file_last_commit(relpath: str) -> str | None:
    """Last commit that touched <relpath>, or None if untracked / never committed."""
    out = git("log", "-1", "--format=%H", "--", relpath)
    return out or None


class DigestError(Exception):
    pass


def changed_files_since(sha: str, head: str) -> list[str] | None:
    """``git diff --name-only <sha> <head>``; None if <sha> is unknown to this clone."""
    try:
        out = git("diff", "--name-only", sha, head)
    except subprocess.CalledProcessError:
        return None
    return [ln for ln in out.splitlines() if ln]


def match_scope(files: list[str], globs: list[str]) -> list[str]:
    """fnmatch each changed path against the slice's scope globs.

    ``fnmatch`` treats ``*`` as matching ``/`` too, so ``runtime/recoil/**`` and
    ``_DECISIONS/*`` both cover nested paths — the intended (conservative) reading.
    """
    hits = set()
    for f in files:
        for g in globs:
            if fnmatch.fnmatch(f, g):
                hits.add(f)
                break
    return sorted(hits)


# ---------------------------------------------------------------- digests
def load_digests() -> list[dict]:
    digests = []
    for path in sorted(glob.glob(DIGEST_GLOB)):
        try:
            with open(path, encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, json.JSONDecodeError) as e:
            raise DigestError("bad digest %s: %s" % (os.path.relpath(path, REPO), e))
        if not isinstance(d, dict):
            raise DigestError("bad digest %s: top level is not an object" % os.path.relpath(path, REPO))
        domain = d.get("domain") or os.path.basename(path)[len("digest-"):-len(".json")]
        d["_domain"] = domain
        d["_path"] = os.path.relpath(path, REPO)
        digests.append(d)
    return digests


def digest_sha(d: dict) -> str | None:
    for k in DIGEST_SHA_KEYS:
        v = d.get(k)
        if isinstance(v, str) and SHA_RE.match(v):
            return v
    return None


def digest_generated(d: dict, fallback: str) -> str:
    v = d.get("generated")
    return v if isinstance(v, str) and DATE_RE.match(v) else fallback


def build_slices(digests: list[dict], head: str, today: str, prior: dict | None = None) -> list[OrderedDict]:
    """Group digest nodes into (domain, epoch) slices.

    `prior` maps (domain, epoch) -> {graded_at_sha, graded_at} from an existing manifest. When a
    slice is already recorded there, its grade is PRESERVED — the manifest is the source of truth
    for WHEN each slice was graded, so a per-slice back-propagation (cache_backprop.py re-grading
    one slice) is never clobbered by the whole-file heuristic below. The file's last commit only
    BOOTSTRAPS a brand-new slice that no manifest has recorded yet.
    """
    prior = prior or {}
    slices = []
    for d in digests:
        domain = str(d["_domain"]).lower()
        # Bootstrap sha for slices this digest introduces: the sha the digest records, else the
        # digest FILE's own last commit; HEAD only when untracked, and then marked dirty.
        untracked = False
        boot = digest_sha(d)
        if not boot:
            boot = file_last_commit(d["_path"])
        if not boot:
            boot, untracked = head, True
        boot_at = digest_generated(d, today)
        globs = SCOPE_GLOBS.get(domain)
        base_markers = []
        if globs is None:
            globs = []
            base_markers.append("<unknown domain %s: no scope>" % domain)
        counts: dict[str, int] = {}
        for node in d.get("nodes") or []:
            epoch = node.get("epoch")
            if not isinstance(epoch, str) or not epoch:
                epoch = UNKNOWN_EPOCH
            counts[epoch] = counts.get(epoch, 0) + 1
        for epoch in sorted(counts):
            rec = prior.get((domain, epoch))
            markers = list(base_markers)
            if rec and rec.get("graded_at_sha"):
                sha, graded_at = rec["graded_at_sha"], rec.get("graded_at") or boot_at
            else:
                sha, graded_at = boot, boot_at
                if untracked:
                    markers.append("<untracked digest %s>" % d["_path"])
            slices.append(OrderedDict([
                ("domain", domain),
                ("epoch", epoch),
                ("node_count", counts[epoch]),
                ("graded_at_sha", sha),
                ("graded_at", graded_at),
                ("scope_globs", list(globs)),
                ("fresh", not markers),
                ("dirty_files", list(markers)),
            ]))
    return sort_slices(slices)


def prior_grades(doc: dict | None) -> dict:
    """{(domain, epoch): {graded_at_sha, graded_at}} from an existing manifest, for preservation."""
    out = {}
    for s in ((doc or {}).get("slices") or []):
        if isinstance(s, dict) and s.get("domain") and s.get("epoch"):
            out[(s["domain"], s["epoch"])] = {"graded_at_sha": s.get("graded_at_sha"), "graded_at": s.get("graded_at")}
    return out


def sort_slices(slices: list) -> list:
    def key(s):
        dom = s["domain"]
        di = DOMAIN_ORDER.index(dom) if dom in DOMAIN_ORDER else len(DOMAIN_ORDER)
        return (di, dom, s["epoch"])
    return sorted(slices, key=key)


# ---------------------------------------------------------------- freshness
def refresh(slices: list, head: str) -> None:
    """Recompute fresh/dirty in place. One git diff per distinct graded_at_sha."""
    diffs: dict[str, list[str] | None] = {}
    for s in slices:
        sha = s["graded_at_sha"]
        if sha not in diffs:
            diffs[sha] = [] if sha == head else changed_files_since(sha, head)
    for s in slices:
        # Structural markers (unknown domain / untracked digest / missing / orphan) are not
        # git-derived; they persist across refresh and always mean dirty.
        markers = [f for f in s.get("dirty_files", []) if isinstance(f, str) and f.startswith("<") and "graded_at_sha" not in f]
        if not s.get("scope_globs") and not any("unknown domain" in m for m in markers):
            markers.append("<unknown domain %s: no scope>" % s["domain"])
        changed = diffs[s["graded_at_sha"]]
        if changed is None:
            # Unknown sha (unfetched / rewritten history): cannot prove freshness.
            s["fresh"] = False
            s["dirty_files"] = ["<unknown graded_at_sha %s>" % s["graded_at_sha"]]
            continue
        dirty = match_scope(changed, s["scope_globs"]) + markers
        s["fresh"] = not dirty
        s["dirty_files"] = dirty


def warn_dead_scopes(tracked: list[str]) -> list[str]:
    """A domain whose globs match no tracked file can never go dirty: say so, loudly."""
    dead = [dom for dom, globs in SCOPE_GLOBS.items() if not match_scope(tracked, globs)]
    for dom in dead:
        print("WARN: scope for domain %r matches no tracked file (%s) — it can never invalidate"
              % (dom, ", ".join(SCOPE_GLOBS[dom])), file=sys.stderr)
    return dead


# ---------------------------------------------------------------- manifest io
def read_manifest() -> dict | None:
    if not os.path.exists(MANIFEST_PATH):
        return None
    with open(MANIFEST_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def manifest_doc(generated: str, head: str, slices: list) -> OrderedDict:
    """One shape for the file AND for --json, from both commands."""
    dirty = sum(1 for s in slices if not s["fresh"])
    return OrderedDict([("generated", generated), ("repo_head", head),
                        ("dirty_count", dirty), ("slices", slices)])


def write_manifest(doc: OrderedDict) -> None:
    os.makedirs(ATLAS_DIR, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)
        fh.write("\n")


def print_table(slices: list, head: str) -> None:
    print("cache-manifest  repo_head=%s  slices=%d" % (head[:12], len(slices)))
    print("%-9s %-8s %5s  %-12s %-10s %-5s %s" % (
        "domain", "epoch", "nodes", "graded_sha", "graded_at", "state", "dirty_files"))
    for s in slices:
        state = "fresh" if s["fresh"] else "DIRTY"
        print("%-9s %-8s %5d  %-12s %-10s %-5s %s" % (
            s["domain"], s["epoch"], s["node_count"], s["graded_at_sha"][:12],
            s["graded_at"], state, ", ".join(s["dirty_files"])))
    dirty = sum(1 for s in slices if not s["fresh"])
    print("%d fresh / %d dirty" % (len(slices) - dirty, dirty))


# ---------------------------------------------------------------- commands
def cmd_stamp(today: str, as_json: bool) -> int:
    head = head_sha()
    digests = load_digests()
    if not digests:
        print("no digests found under %s" % ATLAS_DIR, file=sys.stderr)
        return 1
    # Preserve per-slice grades already recorded (so a re-stamp never resurrects a slice that
    # back-propagation graded, nor bumps un-re-graded slices via the shared digest's last commit).
    slices = build_slices(digests, head, today, prior=prior_grades(read_manifest()))
    refresh(slices, head)
    warn_dead_scopes(git("ls-files").splitlines())
    doc = manifest_doc(today, head, slices)
    write_manifest(doc)
    if as_json:
        print(json.dumps(doc, indent=2))
    else:
        print_table(slices, head)
        print("wrote %s" % os.path.relpath(MANIFEST_PATH, REPO))
    return 0


def cmd_check(today: str, as_json: bool) -> int:
    head = head_sha()
    doc = read_manifest()
    if doc is None:
        msg = "no manifest at %s — run `stamp` first (consumers treat this as freshness=unknown)"
        print(msg % os.path.relpath(MANIFEST_PATH, REPO), file=sys.stderr)
        return 1
    slices = sort_slices([OrderedDict(s) for s in doc.get("slices", [])])
    for s in slices:
        s.setdefault("dirty_files", [])
        for k in ("graded_at_sha", "scope_globs", "domain", "epoch"):
            if k not in s:
                print("manifest slice missing %r: %s" % (k, json.dumps(s)[:120]), file=sys.stderr)
                return 1
    # Reconcile with the digests as they are NOW: a (domain, epoch) that exists in a digest
    # but not in the manifest is MISSING (a re-curation or new epoch since stamp); a manifest
    # slice with no digest behind it is an ORPHAN. Both are dirty; node_count is refreshed.
    current = {(c["domain"], c["epoch"]): c for c in build_slices(load_digests(), head, today, prior=prior_grades(doc))}
    have = {(s["domain"], s["epoch"]) for s in slices}
    for key, c in current.items():
        if key not in have:
            c["fresh"] = False
            c["dirty_files"] = ["<missing: (%s, %s) not in manifest, re-stamp>" % key] + c["dirty_files"]
            slices.append(c)
    for s in slices:
        key = (s["domain"], s["epoch"])
        if key in current:
            s["node_count"] = current[key]["node_count"]
        elif not any(str(f).startswith("<orphan") for f in s["dirty_files"]):
            s["dirty_files"] = ["<orphan: no digest has (%s, %s)>" % key] + list(s["dirty_files"])
    slices = sort_slices(slices)
    refresh(slices, head)
    # keep structural markers refresh() cannot derive from git
    for s in slices:
        key = (s["domain"], s["epoch"])
        if key not in current and not any(str(f).startswith("<orphan") for f in s["dirty_files"]):
            s["dirty_files"].insert(0, "<orphan: no digest has (%s, %s)>" % key); s["fresh"] = False
        if key in current and key not in have and not any(str(f).startswith("<missing") for f in s["dirty_files"]):
            s["dirty_files"].insert(0, "<missing: (%s, %s) not in manifest, re-stamp>" % key); s["fresh"] = False
    # `generated` is the stamp date; check rewrites fresh/dirty/node_count + repo_head only.
    out = manifest_doc(doc.get("generated", today), head, slices)
    write_manifest(out)
    dirty = [s for s in slices if not s["fresh"]]
    if as_json:
        print(json.dumps(out, indent=2))
    else:
        print_table(slices, head)
    # TODO(back-propagation, v1 seam — NOT built): for each dirty slice, run a
    # targeted Curator over exactly that (domain, epoch), rewrite its nodes in
    # digest-<domain>.json, then re-`stamp` so graded_at_sha = HEAD. That step is
    # judgment (metabolic-router §3) and is deliberately left out of this script.
    return 2 if dirty else 0


class _Parser(argparse.ArgumentParser):
    # Usage errors exit 1, never 2: exit 2 is reserved for "manifest is dirty".
    def error(self, message):
        self.print_usage(sys.stderr)
        print("%s: error: %s" % (self.prog, message), file=sys.stderr)
        sys.exit(1)


def main(argv: list[str] | None = None) -> int:
    ap = _Parser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--today", required=True, metavar="YYYY-MM-DD",
                    help="stamp date (required; no clock reads, for reproducible runs)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("command", choices=["stamp", "check"])
    args = ap.parse_args(argv)
    if not DATE_RE.match(args.today):
        ap.error("--today must be YYYY-MM-DD")
    try:
        if args.command == "stamp":
            return cmd_stamp(args.today, args.json)
        return cmd_check(args.today, args.json)
    except subprocess.CalledProcessError as e:
        print("git failed: %s" % (e.stderr or e).strip(), file=sys.stderr)
        return 1
    except DigestError as e:
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
