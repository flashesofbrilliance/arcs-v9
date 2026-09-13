#!/usr/bin/env python3
"""Orthogonal Echo Detector — cross-tenant shape detection over the recoil/receipt corpus.

Each tenant SSOT is an orthogonal cut from a zero-point problem space. A shape that recurs across
INDEPENDENT tenants is a reinforced invariant (the abductive folksonomy: uncorrelated signals toward
the same horizon reinforce). A shape unique to one tenant is a net-new tributary
([[opposing-abductive-folksonomy-vs-taxonomy-overfit]]).

This is comparative-recoil / the Orthogonal Echo Detector (ROM primitive #5) run over N tenants instead
of 2. FIRST PASS: clusters by the corpus's own canonical IDs (riskFlags[].id, signalThreads[].id) + the
belief-flip direction. Grounded, stdlib-only, no new deps. It SHARPENS once every receipt carries the
provenance envelope (_PATTERNS/receipt-provenance-attestation-contract.md) and a semantic-vector layer
lands (then near-synonym IDs cluster too, not just exact matches).

Watcher-ready: `--json` emits machine output a hook / CI / meta-audit §7 can consume.

Usage:
  python3 scripts/orthogonal_echo.py                 # human report
  python3 scripts/orthogonal_echo.py --json          # machine output (for watchers/hooks)
  python3 scripts/orthogonal_echo.py --min 3         # only shapes recurring across >=3 tenants
"""
import json, glob, os, re, sys, argparse, collections

CORPUS = "runtime/recoil/generated/*.json"


def tenant_name(d, path):
    """One canonical PERSON per tenant, so N surfaces of the same counterpart collapse to one cut."""
    m = d.get("meta") if isinstance(d.get("meta"), dict) else {}
    if m.get("counterpart"):
        return m["counterpart"].strip().split()[0].lower()  # first name = the person
    base = os.path.basename(path).replace(".json", "")
    base = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", base)
    base = re.sub(r"^(precall|pilot-court|warroom)-", "", base)
    base = re.sub(r"-(onedoor|codex|receipt|diamond|recoil|profile|ext|enriched-profile|multicall|serialization|MASTER.*|tidio).*$", "", base)
    return base.split("-")[0].lower() or base


def extract(path):
    try:
        d = json.load(open(path))
    except Exception:
        return None
    if not isinstance(d, dict):
        return None
    name = tenant_name(d, path)
    shapes = []  # (dimension, signature, detail)
    for rf in (d.get("riskFlags") or []):
        if isinstance(rf, dict) and rf.get("id"):
            shapes.append(("risk", str(rf["id"]), str(rf.get("severity", ""))))
    for st in (d.get("signalThreads") or []):
        if isinstance(st, dict) and st.get("id"):
            shapes.append(("signal", str(st["id"]), str(st.get("strength", ""))))
    for b in (d.get("blocks") or []):
        if isinstance(b, dict) and b.get("type") == "story":
            for beat in (b.get("beats") or []):
                if isinstance(beat, dict):
                    shapes.append(("flip", "FLIP_" + str(beat.get("dir", "flip")).upper(), (beat.get("k") or "")[:40]))
    return {"tenant": name, "path": os.path.basename(path), "shapes": shapes}


_STOP = set("not no in with with for to the of and a an is on at by from as be it this that near round low high unclear".split())
_GENERIC = set("arcs call story signal risk flag warm cold read seed step next".split())  # 'step/next' too common to theme alone


def _tokens(sig):
    """Break a canonical ID (NO_NEXT_ACTION, COMP_CEILING_UNCONFIRMED) into significant keywords."""
    out = set()
    for part in re.split(r"[_\W]+", sig):
        for w in re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z]+|[a-z]+", part):
            w = w.lower()
            if len(w) > 2 and w not in _STOP and w not in _GENERIC:
                out.add(w)
    return out


def _semantic_echoes(rows, min_t):
    """Cheap semantic layer: which KEYWORDS (themes) recur across independent tenants. Bridges toward the
    vector layer without a model — catches the near-synonym IDs the exact-match pass cannot."""
    kw = collections.defaultdict(set)
    for r in rows:
        for _dim, sig, _d in r["shapes"]:
            for w in _tokens(sig):
                kw[w].add(r["tenant"])
    return sorted(((w, sorted(ts)) for w, ts in kw.items() if len(ts) >= min_t), key=lambda x: (-len(x[1]), x[0]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--min", type=int, default=2, help="min DISTINCT tenants for a shape to count as recurring")
    ap.add_argument("--corpus", default=CORPUS)
    a = ap.parse_args()

    rows = [t for t in (extract(p) for p in sorted(glob.glob(a.corpus))) if t]
    tenants = sorted({r["tenant"] for r in rows})

    sig_tenants = collections.defaultdict(set)   # signature -> {tenant}
    sig_dim = {}
    for r in rows:
        for dim, sig, _detail in r["shapes"]:
            sig_tenants[sig].add(r["tenant"])
            sig_dim[sig] = dim

    recurring = sorted(((s, sorted(ts)) for s, ts in sig_tenants.items() if len(ts) >= a.min),
                       key=lambda x: (-len(x[1]), x[0]))
    orphans = sorted((s for s, ts in sig_tenants.items() if len(ts) == 1))
    sem = _semantic_echoes(rows, a.min)

    if a.json:
        print(json.dumps({
            "corpus_files": len(rows),
            "distinct_tenants": len(tenants),
            "distinct_shapes": len(sig_tenants),
            "min_tenants": a.min,
            "reinforced_invariants": [
                {"signature": s, "dim": sig_dim[s], "n_tenants": len(ts), "tenants": ts} for s, ts in recurring],
            "net_new_tributaries": [
                {"signature": s, "dim": sig_dim[s], "tenant": next(iter(sig_tenants[s]))} for s in orphans],
            "semantic_echoes": [
                {"keyword": w, "n_tenants": len(ts), "tenants": ts} for w, ts in sem],
        }, indent=2))
        return

    print(f"ORTHOGONAL ECHO  ·  {len(rows)} SSOT files → {len(tenants)} distinct tenants · {len(sig_tenants)} distinct shapes\n")
    print(f"══ REINFORCED INVARIANTS  ·  shape recurs across ≥{a.min} independent tenants ══")
    print("   (a shape surviving orthogonal cuts from different zero-points = a real invariant, not a coincidence)\n")
    if not recurring:
        print("   (none at this threshold)")
    for s, ts in recurring:
        print(f"   [{sig_dim[s]:6}] {s:26} ×{len(ts):<2}  {', '.join(ts)}")
    print(f"\n══ NET-NEW TRIBUTARIES  ·  unique to one tenant  ·  {len(orphans)} total ══")
    print("   (each is a candidate net-new pattern — watch for it to reappear and promote to invariant)\n")
    for s in orphans[:24]:
        print(f"   [{sig_dim[s]:6}] {s:26} {next(iter(sig_tenants[s]))}")
    if len(orphans) > 24:
        print(f"   … +{len(orphans) - 24} more")
    print(f"\n══ SEMANTIC ECHOES  ·  keyword recurs across ≥{a.min} tenants (the near-synonym layer) ══")
    print("   (themes the exact-ID pass can't see: bespoke IDs, shared meaning — this is where a vector layer lives)\n")
    for w, ts in sem[:20]:
        print(f"   {w:16} ×{len(ts):<2}  {', '.join(ts)}")
    if len(sem) > 20:
        print(f"   … +{len(sem) - 20} more")

    print(f"\n(first pass: exact-ID clustering over the pre-envelope corpus. Wire the receipt envelope + a vector")
    print(f" layer and near-synonym shapes cluster too. Feed --json to a watcher to run this on every new tenant.)")


if __name__ == "__main__":
    main()
