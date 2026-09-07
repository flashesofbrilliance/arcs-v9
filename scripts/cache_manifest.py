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


def build_slices(digests: list[dict], head: str, today: str) -> list[OrderedDict]:
    slices = []
    for d in digests:
        domain = str(d["_domain"]).lower()
        # graded_at_sha = the sha the digest records, else the digest FILE's own last commit
        # (the closest honest proxy for "when it was graded"); HEAD only when untracked, and
        # then the slice is marked dirty rather than silently fresh.
        untracked = False
        sha = digest_sha(d)
        if not sha:
            sha = file_last_commit(d["_path"])
        if not sha:
            sha, untracked = head, True
        graded_at = digest_generated(d, today)
        globs = SCOPE_GLOBS.get(domain)
        markers = []
        if globs is None:
            globs = []
            markers.append("<unknown domain %s: no scope>" % domain)
        if untracked:
            markers.append("<untracked digest %s>" % d["_path"])
        counts: dict[str, int] = {}
        for node in d.get("nodes") or []:
            epoch = node.get("epoch")
            if not isinstance(epoch, str) or not epoch:
                epoch = UNKNOWN_EPOCH
            counts[epoch] = counts.get(epoch, 0) + 1
        for epoch in sorted(counts):
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
    slices = build_slices(digests, head, today)
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


def reconcile(doc: dict, today: str, head: str) -> list:
    """The manifest's slices reconciled against the digests AS THEY ARE NOW, with
    fresh/dirty recomputed against ``head``. Shared by ``check`` (report) and
    ``backprop`` (which needs the same freshness truth to find its target slice).

    A ``(domain, epoch)`` in a digest but not the manifest is MISSING; a manifest
    slice with no digest behind it is an ORPHAN. Both are dirty. This mutates and
    returns a fresh slice list; it does not read or write the manifest file.
    """
    slices = sort_slices([OrderedDict(s) for s in doc.get("slices", [])])
    for s in slices:
        s.setdefault("dirty_files", [])
    current = {(c["domain"], c["epoch"]): c for c in build_slices(load_digests(), head, today)}
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
    return slices


def cmd_check(today: str, as_json: bool) -> int:
    head = head_sha()
    doc = read_manifest()
    if doc is None:
        msg = "no manifest at %s — run `stamp` first (consumers treat this as freshness=unknown)"
        print(msg % os.path.relpath(MANIFEST_PATH, REPO), file=sys.stderr)
        return 1
    for s in doc.get("slices", []):
        for k in ("graded_at_sha", "scope_globs", "domain", "epoch"):
            if k not in s:
                print("manifest slice missing %r: %s" % (k, json.dumps(s)[:120]), file=sys.stderr)
                return 1
    slices = reconcile(doc, today, head)
    # `generated` is the stamp date; check rewrites fresh/dirty/node_count + repo_head only.
    out = manifest_doc(doc.get("generated", today), head, slices)
    write_manifest(out)
    dirty = [s for s in slices if not s["fresh"]]
    if as_json:
        print(json.dumps(out, indent=2))
    else:
        print_table(slices, head)
    # Back-propagation (the v1 seam, now wired): a dirty slice is re-graded lazily,
    # on read, by `backprop --slice <domain>/<epoch>` — a TARGETED Curator over
    # exactly that (domain, epoch), never a full re-audit. `check` only reports; it
    # never re-grades (grading is judgment, metabolic-router §3). See cmd_backprop.
    return 2 if dirty else 0


# ---------------------------------------------------------------- back-propagation
# Lazy, pull-driven re-grading of ONE dirty/missing slice (spec §"Request / back-propagate
# flow"). Two phases, both mechanical here; the judgment (the grading itself) happens in the
# Curator subagent between them:
#
#   emit-packet  read-only. Refuse if the slice is already fresh (nothing to do — this is the
#                "a fresh slice does NOT re-grade" guard). Otherwise emit exactly this slice's
#                current nodes + the tracked files in its scope, for a TARGETED Curator run.
#   apply        take the Curator's re-graded nodes for THIS slice, validate every node really
#                belongs to (domain, epoch), replace ONLY this slice's nodes in the digest, and
#                re-stamp ONLY this slice's manifest row to graded_at_sha = HEAD (-> fresh).
#
# What this deliberately never does: touch any other slice, re-stamp the whole manifest, or
# write nodes it did not verify belong to the slice. Those are the three failure modes the
# peer review gates on.
BACKPROP_INSTRUCTIONS = (
    "TARGETED Curator re-grade of ONE cache slice. Re-grade ONLY the nodes for this exact "
    "(domain, epoch) against the files listed in scope_files (read them at HEAD). Do NOT audit "
    "any other slice, domain, or epoch. Output JSON {\"nodes\": [...]} where EVERY node has "
    "domain == this domain and epoch == this epoch, using the node schema "
    "{id, title, domain, cluster, status, claim, provenance, links[], note, epoch}. Status "
    "vocabulary: LIVE, LIVE-AS-PROSE, DRIFTED, STALE, UNVERIFIED. Keep node ids stable where a "
    "node still corresponds to a prior one; drop nodes whose subject no longer exists; add nodes "
    "for new records in scope. current_nodes is what the slice held when last graded."
)


def parse_slice(spec: str) -> tuple[str, str]:
    if "/" not in spec:
        raise DigestError("bad --slice %r: want DOMAIN/EPOCH (e.g. product/2026-08)" % spec)
    dom, _, epoch = spec.partition("/")
    dom, epoch = dom.strip().lower(), epoch.strip()
    if not dom or not epoch:
        raise DigestError("bad --slice %r: want DOMAIN/EPOCH (e.g. product/2026-08)" % spec)
    return dom, epoch


def digest_path_for(domain: str) -> str:
    return os.path.join(ATLAS_DIR, "digest-%s.json" % domain)


def find_slice(slices: list, dom: str, epoch: str):
    for s in slices:
        if s["domain"] == dom and s["epoch"] == epoch:
            return s
    return None


def tracked_scope_files(globs: list) -> list:
    return match_scope(git("ls-files").splitlines(), globs) if globs else []


def cmd_backprop_emit(today: str, dom: str, epoch: str, packet_path: str) -> int:
    head = head_sha()
    doc = read_manifest()
    if doc is None:
        print("no manifest — run `stamp` first", file=sys.stderr)
        return 1
    slices = reconcile(doc, today, head)
    s = find_slice(slices, dom, epoch)
    if s is None:
        print("no slice (%s, %s) in manifest or digests — nothing to grade" % (dom, epoch), file=sys.stderr)
        return 1
    if s["fresh"]:
        # The guard: back-prop is for dirty/missing slices only. A fresh slice is a cache
        # HIT and must never re-grade.
        print("slice (%s, %s) is fresh (graded_at_sha=%s == scope unchanged) — no re-grade"
              % (dom, epoch, s["graded_at_sha"][:12]))
        return 0
    globs = SCOPE_GLOBS.get(dom, [])
    digest = {}
    dp = digest_path_for(dom)
    if os.path.exists(dp):
        with open(dp, encoding="utf-8") as fh:
            digest = json.load(fh)
    current_nodes = [n for n in (digest.get("nodes") or [])
                     if (n.get("epoch") or UNKNOWN_EPOCH) == epoch]
    packet = OrderedDict([
        ("slice", "%s/%s" % (dom, epoch)),
        ("domain", dom), ("epoch", epoch),
        ("head_sha", head),
        ("dirty_files", s.get("dirty_files", [])),
        ("scope_globs", globs),
        ("scope_files", tracked_scope_files(globs)),
        ("instructions", BACKPROP_INSTRUCTIONS),
        ("current_nodes", current_nodes),
    ])
    with open(packet_path, "w", encoding="utf-8") as fh:
        json.dump(packet, fh, indent=2)
        fh.write("\n")
    print("emitted Curator packet for (%s, %s): %d node(s), %d scope file(s) -> %s"
          % (dom, epoch, len(current_nodes), len(packet["scope_files"]), packet_path))
    return 0


def cmd_backprop_apply(today: str, dom: str, epoch: str, regraded_path: str) -> int:
    head = head_sha()
    doc = read_manifest()
    if doc is None:
        print("no manifest — run `stamp` first", file=sys.stderr)
        return 1
    with open(regraded_path, encoding="utf-8") as fh:
        regraded = json.load(fh)
    nodes = regraded.get("nodes") if isinstance(regraded, dict) else regraded
    if not isinstance(nodes, list):
        print("regraded file %s: want {\"nodes\": [...]}" % regraded_path, file=sys.stderr)
        return 1
    # VALIDATE before any write: every re-graded node must belong to THIS slice. A node with a
    # foreign domain/epoch means the Curator strayed out of scope; refuse and write nothing.
    clean = []
    for i, n in enumerate(nodes):
        if not isinstance(n, dict):
            print("regraded node %d is not an object" % i, file=sys.stderr)
            return 1
        nd = (n.get("domain") or dom)
        ne = (n.get("epoch") or epoch)
        if nd != dom or ne != epoch:
            print("regraded node %r is (%s, %s), not the requested slice (%s, %s) — refusing"
                  % (n.get("id") or i, nd, ne, dom, epoch), file=sys.stderr)
            return 1
        n = dict(n); n["domain"] = dom; n["epoch"] = epoch
        clean.append(n)
    # Merge: replace ONLY this slice's nodes in the digest; every other epoch is untouched.
    dp = digest_path_for(dom)
    if os.path.exists(dp):
        with open(dp, encoding="utf-8") as fh:
            digest = json.load(fh)
    else:
        digest = OrderedDict([("domain", dom), ("generated", today), ("nodes", [])])
    kept = [n for n in (digest.get("nodes") or []) if (n.get("epoch") or UNKNOWN_EPOCH) != epoch]
    digest["nodes"] = kept + clean
    digest["generated"] = today
    with open(dp, "w", encoding="utf-8") as fh:
        json.dump(digest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    # Re-stamp ONLY this slice's manifest row: graded_at_sha = HEAD. Other rows keep their old
    # graded_at_sha, so they stay exactly as dirty/fresh as they were (no whole-manifest stamp).
    slices = [OrderedDict(s) for s in doc.get("slices", [])]
    row = find_slice(slices, dom, epoch)
    if row is None:
        row = OrderedDict([("domain", dom), ("epoch", epoch)])
        slices.append(row)
    row["node_count"] = len(clean)
    row["graded_at_sha"] = head
    row["graded_at"] = today
    row["scope_globs"] = list(SCOPE_GLOBS.get(dom, []))
    slices = sort_slices(slices)
    refresh([row], head)  # graded_at_sha == HEAD -> empty diff -> fresh
    doc_out = manifest_doc(doc.get("generated", today), head, slices)
    write_manifest(doc_out)
    state = "fresh" if row["fresh"] else "DIRTY(%s)" % ", ".join(row["dirty_files"])
    print("back-propagated (%s, %s): %d node(s) regraded, digest %s updated, slice re-stamped to %s -> %s"
          % (dom, epoch, len(clean), os.path.relpath(dp, REPO), head[:12], state))
    return 0 if row["fresh"] else 1


def cmd_backprop(today: str, slice_spec: str, emit_packet: str | None, apply_path: str | None) -> int:
    dom, epoch = parse_slice(slice_spec)
    if bool(emit_packet) == bool(apply_path):
        print("backprop: pass exactly one of --emit-packet or --apply", file=sys.stderr)
        return 1
    if emit_packet:
        return cmd_backprop_emit(today, dom, epoch, emit_packet)
    return cmd_backprop_apply(today, dom, epoch, apply_path)


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
    ap.add_argument("command", choices=["stamp", "check", "backprop"])
    ap.add_argument("--slice", metavar="DOMAIN/EPOCH",
                    help="backprop only: the one slice to re-grade, e.g. product/2026-08")
    ap.add_argument("--emit-packet", metavar="PATH",
                    help="backprop only: write the targeted-Curator packet for --slice to PATH")
    ap.add_argument("--apply", metavar="PATH", dest="apply_path",
                    help="backprop only: merge the Curator's re-graded nodes for --slice from PATH")
    args = ap.parse_args(argv)
    if not DATE_RE.match(args.today):
        ap.error("--today must be YYYY-MM-DD")
    if args.command == "backprop" and not args.slice:
        ap.error("backprop requires --slice DOMAIN/EPOCH")
    if args.command != "backprop" and (args.slice or args.emit_packet or args.apply_path):
        ap.error("--slice/--emit-packet/--apply are only valid with the backprop command")
    try:
        if args.command == "stamp":
            return cmd_stamp(args.today, args.json)
        if args.command == "backprop":
            return cmd_backprop(args.today, args.slice, args.emit_packet, args.apply_path)
        return cmd_check(args.today, args.json)
    except subprocess.CalledProcessError as e:
        print("git failed: %s" % (e.stderr or e).strip(), file=sys.stderr)
        return 1
    except DigestError as e:
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
