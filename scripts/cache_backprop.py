#!/usr/bin/env python3
"""cache_backprop.py — the Metabolic Router's back-propagation organ (ADR-075; build plan 1b).

The cache manifest (scripts/cache_manifest.py) detects a DIRTY slice: files in its provenance
scope changed since it was graded. Back-propagation is the lazy, pull-driven repair — re-grade
ONE (domain, epoch) slice against the current tree and stamp it fresh again. Per the metabolic
split (_SPECS/metabolic-router-v1.md §3) the grading itself is JUDGMENT and is NOT done here:
this script scaffolds and sequences (NOTOMATION), a Curator (an agent, or a human) grades.

    plan                              # list dirty slices worth re-grading (reads the manifest)
    packet   <domain> <epoch> [--out F]   # assemble the Curator work-packet (nodes + current provenance)
    apply    <domain> <epoch> --graded F [--today YYYY-MM-DD]
                                      # write graded statuses back into the digest + stamp THAT slice fresh

Flow: `plan` -> pick a slice -> `packet` -> hand the packet to a Curator -> `apply` its graded
output -> commit the digest + manifest together. The commit is the new grading commit; because
`stamp` now preserves per-slice grades, only the re-graded slice reads fresh, not its siblings
that share the digest file.

A graded file is `{"<node_id>": {"status": "LIVE|LIVE-AS-PROSE|DRIFTED|STALE|UNVERIFIABLE HERE",
"note": "..."}, ...}` — every node in the slice must appear (use --partial to allow a subset).
stdlib only. No network, no model call — grading is external by construction.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cache_manifest as cm  # noqa: E402  (sibling module; reuse its git + slice machinery)

STATUS_VOCAB = ("LIVE", "LIVE-AS-PROSE", "DRIFTED", "STALE", "UNVERIFIABLE HERE")
RUBRIC = {
    "LIVE": "The claim is true of the tree right now; provenance confirms it.",
    "LIVE-AS-PROSE": "True but realized as prose/doc rather than code; provenance is descriptive.",
    "DRIFTED": "Was true, but the provenance has since changed so the claim no longer holds.",
    "STALE": "Superseded or retired; the thing it describes is gone.",
    "UNVERIFIABLE HERE": "Cannot be confirmed from the repo alone (needs a live service / external state).",
}
MAX_PROVENANCE_BYTES = 20_000  # keep a packet bounded; a Curator reads the cited file, not the repo


def load_digest_for(domain: str) -> tuple[dict, str]:
    for d in cm.load_digests():
        if str(d["_domain"]).lower() == domain.lower():
            return d, d["_path"]
    sys.exit(f"cache_backprop: no digest with domain {domain!r} under {cm.ATLAS_DIR}")


def slice_nodes(digest: dict, epoch: str) -> list[dict]:
    out = []
    for n in digest.get("nodes") or []:
        e = n.get("epoch")
        if not isinstance(e, str) or not e:
            e = cm.UNKNOWN_EPOCH
        if e == epoch:
            out.append(n)
    return out


def provenance_files(nodes: list[dict], scope_globs: list[str]) -> list[str]:
    """Distinct tracked files a node cites (the 'file' before any ':line'), intersected with scope."""
    import fnmatch
    tracked = set(cm.git("ls-files").splitlines())
    cited = []
    seen = set()
    for n in nodes:
        prov = str(n.get("provenance") or "").strip()
        if not prov:
            continue
        path = prov.split(":")[0].split("#")[0].strip()
        if path and path in tracked and path not in seen and any(fnmatch.fnmatch(path, g) for g in scope_globs):
            seen.add(path)
            cited.append(path)
    return cited


def cmd_plan(as_json: bool) -> int:
    doc = cm.read_manifest()
    if doc is None:
        print("no manifest — run `cache_manifest.py stamp` first", file=sys.stderr)
        return 1
    head = cm.head_sha()
    slices = [dict(s) for s in doc.get("slices", [])]
    for s in slices:
        s.setdefault("dirty_files", [])
    cm.refresh(slices, head)
    dirty = [s for s in slices if not s["fresh"]]
    if as_json:
        print(json.dumps([{"domain": s["domain"], "epoch": s["epoch"], "node_count": s["node_count"],
                           "dirty_files": s["dirty_files"]} for s in dirty], indent=2))
        return 0
    if not dirty:
        print("no dirty slices — nothing to back-propagate")
        return 0
    print("%d dirty slice(s) to re-grade (pick one, then: packet <domain> <epoch>):" % len(dirty))
    for s in dirty:
        print("  %-9s %-8s %3d nodes  <- %s" % (
            s["domain"], s["epoch"], s["node_count"], ", ".join(s["dirty_files"][:4])))
    return 0


def cmd_packet(domain: str, epoch: str, out: str | None) -> int:
    digest, path = load_digest_for(domain)
    globs = cm.SCOPE_GLOBS.get(domain.lower(), [])
    nodes = slice_nodes(digest, epoch)
    if not nodes:
        sys.exit(f"cache_backprop: slice ({domain}, {epoch}) has no nodes in {path}")
    prov = {}
    for f in provenance_files(nodes, globs):
        try:
            blob = cm.git("show", f"HEAD:{f}")
        except Exception:
            continue
        prov[f] = blob[:MAX_PROVENANCE_BYTES] + ("\n...[truncated]" if len(blob) > MAX_PROVENANCE_BYTES else "")
    packet = {
        "instruction": ("Re-grade each node's `status` against the provenance shown, which is the "
                        "cited file AS IT IS NOW at HEAD. Return ONLY a JSON object mapping node id "
                        "-> {status, note}. Do not invent nodes; grade exactly those given. This is "
                        "judgment: confirm LIVE, or mark DRIFTED/STALE with a one-line why in note."),
        "domain": domain, "epoch": epoch, "graded_against_head": cm.head_sha(),
        "status_vocab": STATUS_VOCAB, "rubric": RUBRIC,
        "nodes": [{"id": n.get("id"), "title": n.get("title"), "current_status": n.get("status"),
                   "claim": n.get("claim"), "provenance": n.get("provenance")} for n in nodes],
        "provenance_files": prov,
    }
    text = json.dumps(packet, indent=2, ensure_ascii=False)
    if out:
        open(out, "w", encoding="utf-8").write(text + "\n")
        print(f"wrote packet for ({domain}, {epoch}): {len(nodes)} nodes, {len(prov)} provenance file(s) -> {out}")
    else:
        print(text)
    return 0


def cmd_apply(domain: str, epoch: str, graded_path: str, today: str, partial: bool) -> int:
    digest, path = load_digest_for(domain)
    nodes = slice_nodes(digest, epoch)
    ids = {n.get("id") for n in nodes}
    try:
        graded = json.load(open(graded_path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"cache_backprop: cannot read graded file {graded_path}: {e}")
    if not isinstance(graded, dict):
        sys.exit("cache_backprop: graded file must be a JSON object {node_id: {status, note?}}")

    # -- validate EVERYTHING before writing anything (a failed apply must never leave a
    #    half-graded digest on disk — finding 1: write-before-validate is a KINTSUGI violation) --
    foreign = [k for k in graded if k not in ids]
    if foreign:
        sys.exit(f"cache_backprop: graded file has ids not in ({domain}, {epoch}): {foreign[:5]}")
    ungraded = [i for i in ids if i not in graded]
    if ungraded and not partial:
        sys.exit(f"cache_backprop: {len(ungraded)} node(s) ungraded (use --partial to allow): {sorted(ungraded)[:5]}")
    bad = [k for k, v in graded.items() if not isinstance(v, dict) or v.get("status") not in STATUS_VOCAB]
    if bad:
        sys.exit(f"cache_backprop: bad/absent status on {bad[:5]} (vocab: {', '.join(STATUS_VOCAB)})")
    # slice-in-manifest is a precondition, checked NOW (before the digest write) so a miss is clean
    head = cm.head_sha()
    doc = cm.read_manifest() or {"slices": []}
    slices = [dict(s) for s in doc.get("slices", [])]
    target = next((s for s in slices if s.get("domain") == domain and s.get("epoch") == epoch), None)
    if target is None:
        sys.exit(f"cache_backprop: ({domain}, {epoch}) not in manifest — run cache_manifest.py stamp first")

    # -- all checks passed; now mutate. (1) write graded statuses into the digest, preserving key
    #    order + all other fields; a "note" key overwrites (empty clears) so a stale rationale never
    #    outlives a status change (finding 3); absent "note" leaves the prior note untouched. --
    changed = 0
    for n in digest.get("nodes") or []:
        g = graded.get(n.get("id"))
        if g is None:
            continue
        if n.get("status") != g["status"]:
            changed += 1
        n["status"] = g["status"]
        if "note" in g:
            if g["note"]:
                n["note"] = g["note"]
            else:
                n.pop("note", None)
    payload = {k: v for k, v in digest.items() if not k.startswith("_")}
    open(os.path.join(cm.REPO, path), "w", encoding="utf-8").write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    # (2) freshness. Only a COMPLETE re-grade earns a fresh stamp: advancing graded_at_sha to HEAD
    #     asserts "the whole slice was graded against HEAD". A --partial grade must not make that
    #     claim (finding 2 — WITNESS honesty), so it advances the digest but leaves the slice dirty
    #     and says so; the manifest never advertises freshness a node did not earn.
    full = not ungraded
    if full:
        target["graded_at_sha"], target["graded_at"] = head, today
    for s in slices:
        s.setdefault("dirty_files", [])
    cm.refresh(slices, head)
    cm.write_manifest(cm.manifest_doc(doc.get("generated", today), head, cm.sort_slices(slices)))

    gs = next(s for s in slices if s["domain"] == domain and s["epoch"] == epoch)
    if full:
        print(f"applied ({domain}, {epoch}): {changed} status change(s) -> {path}; "
              f"slice re-stamped graded_at_sha={head[:12]} graded_at={today}, fresh={gs['fresh']}")
    else:
        print(f"applied ({domain}, {epoch}) PARTIAL: {len(graded)} of {len(ids)} nodes graded "
              f"({changed} status change(s)) -> {path}; slice NOT stamped fresh "
              f"({len(ungraded)} ungraded: {sorted(ungraded)[:5]}) — re-grade the rest to earn freshness.")
    print("next: commit the digest + cache-manifest.json together (that commit is the grading commit).")
    # exit code == "is the slice fresh now": 0 fresh, 2 still dirty (a partial grade is always 2).
    return 0 if gs["fresh"] else 2

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("packet"); p.add_argument("domain"); p.add_argument("epoch"); p.add_argument("--out")
    p = sub.add_parser("apply"); p.add_argument("domain"); p.add_argument("epoch")
    p.add_argument("--graded", required=True); p.add_argument("--today", required=True)
    p.add_argument("--partial", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd in ("apply",) and not cm.DATE_RE.match(a.today):
        ap.error("--today must be YYYY-MM-DD")
    try:
        if a.cmd == "plan":
            return cmd_plan(a.json)
        if a.cmd == "packet":
            return cmd_packet(a.domain, a.epoch, a.out)
        return cmd_apply(a.domain, a.epoch, a.graded, a.today, a.partial)
    except cm.subprocess.CalledProcessError as e:
        print("git failed: %s" % (e.stderr or e).strip(), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
