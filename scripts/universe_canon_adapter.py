#!/usr/bin/env python3
"""universe_canon_adapter: thin, READ-ONLY adapter that projects ARCS canon into the `canon` universe.

Follows the corpus-atlas pattern (memory corpus-atlas-pilot-louisville): adapter -> catalog ->
ziggurat atlas -> drift receipt. Same shape as scripts/corpus_adapter_louisville.py. It READS
_CANON/ and _DECISIONS/ and writes only DERIVED files elsewhere; it never edits canon.

Reads   : _CANON/*.md, _CANON/living/*.md, _DECISIONS/ADR-*.md
Writes  : _STATE/job-search/universe/canon.claims.jsonl        (atoms: one per ADR, one per canon H2 section)
          _STATE/job-search/universe/canon.quarantine.jsonl    (atoms refused for naming a counterpart; never loaded)
          _ARTIFACTS/canon-universe-catalog.json               (nodes + declared ADR-NNN cross-reference edges)
          _ARTIFACTS/canon-universe-atlas.html                 (ziggurat atlas: the louisville shell with this catalog swapped in)
          _INBOX/universe-drift.jsonl                          (one drift receipt per run)

Rule enforced here, not by convention: NO COUNTERPART FACT MAY ENTER CANON. Any atom whose text names a
counterpart (registered counterpart universes + registry canon_denied_names_extra) is quarantined and
reported. Edges are declared references only (an explicit 'ADR-NNN' in the text); nothing is inferred.
Stdlib only.   python3 scripts/universe_canon_adapter.py [--dry-run]
"""
import glob, hashlib, json, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import universe_ask as ua

U = ua.ROOT
ADR_RE = re.compile(r"\bADR-(\d{3})\b")
SENT_RE = re.compile(r"(?<=[.!?])\s+")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def first_sentence(lines, cap=240):
    body = " ".join(l.strip() for l in lines if l.strip() and not l.lstrip().startswith(("#", "|", "```", "---", "<")))
    body = re.sub(r"[>*`_]+", "", body).strip()
    return SENT_RE.split(body, maxsplit=1)[0][:cap].strip() if body else ""


def adr_atom(path, today):
    rel = os.path.relpath(path, REPO); lines = open(path, encoding="utf-8").read().splitlines()
    m = re.match(r"#\s*(ADR-\d{3})\s*[—-]\s*(.+)", lines[0]) if lines else None
    if not m:
        return None
    status = next((re.sub(r"[>*]+", "", l).split(":", 1)[1].strip() for l in lines[:12] if "Status:" in l), "")
    status = re.sub(r"\s+", " ", status)[:140]
    return {"id": f"canon/{m.group(1)}", "entity": "adr", "type": "claim",
            "claim": f"{m.group(1)}: {m.group(2).strip()}. Status: {status or 'not stated in header'}",
            "source": f"{rel}:1", "src_sha": sha(path), "grade": "A", "verified_at": today, "ttl_days": 90,
            "tags": ["adr", m.group(1).lower(), (status.split()[0].lower().strip('.,;—') if status else "no-status")], "audience": "internal"}


def canon_atoms(path, today):
    rel = os.path.relpath(path, REPO); lines = open(path, encoding="utf-8").read().splitlines()
    ent = "tao" if "Tao-of-ARCS" in path else "canon-doc"; stem = os.path.splitext(os.path.basename(path))[0]
    heads = [i for i, l in enumerate(lines) if l.startswith("## ")]
    out = []
    for n, i in enumerate(heads):
        end = heads[n + 1] if n + 1 < len(heads) else len(lines)
        fs = first_sentence(lines[i + 1:end])
        if not fs:
            continue
        title = lines[i][3:].strip()
        out.append({"id": f"canon/{stem}#{n + 1}", "entity": ent, "type": "claim", "claim": f"{stem}, {title}: {fs}",
                    "source": f"{rel}:{i + 1}", "src_sha": sha(path), "grade": "A", "verified_at": today, "ttl_days": 90,
                    "tags": ["canon", stem.lower()], "audience": "internal"})
    return out


def main():
    dry = "--dry-run" in sys.argv; today = time.strftime("%Y-%m-%d")
    reg = ua.load_registry(U); deny = ua.counterpart_names(reg)
    if "--deny" in sys.argv:  # test hook: prove the quarantine path fires
        deny = deny + [sys.argv[sys.argv.index("--deny") + 1].lower()]
    adrs = sorted(glob.glob(os.path.join(REPO, "_DECISIONS", "ADR-*.md")))
    docs = sorted(glob.glob(os.path.join(REPO, "_CANON", "*.md")) + glob.glob(os.path.join(REPO, "_CANON", "living", "*.md")))
    atoms, quarantined, nodes, seen_ids, source_hits = [], [], [], {}, {}
    for p in adrs + docs:
        is_adr = p in adrs
        got = [adr_atom(p, today)] if is_adr else canon_atoms(p, today)
        text = open(p, encoding="utf-8").read()
        stem = os.path.splitext(os.path.basename(p))[0]
        nid = stem.split("-")[0] + "-" + stem.split("-")[1] if is_adr else stem
        nodes.append({"id": nid, "file": os.path.relpath(p, REPO), "kind": "adr" if is_adr else "canon", "type": "reference" if is_adr else "project",
                      "section": "Decisions (ADRs)" if is_adr else "Canon documents", "desc": f"{stem} · {len(got)} atom(s)",
                      "age_days": int((time.time() - os.path.getmtime(p)) / 86400), "promoted": False, "versions": 1, "_text": text})
        src_hits = ua.find_names(text, deny)
        if src_hits:
            source_hits[os.path.relpath(p, REPO)] = src_hits
        for a in filter(None, got):
            hit = ua.find_names(ua.atom_text(a), deny)
            if hit:
                a["quarantined_for"] = hit; quarantined.append(a)
            else:
                if a["id"] in seen_ids:
                    a["id"] += "~dup"
                seen_ids[a["id"]] = 1; atoms.append(a)
    ids = {n["id"] for n in nodes}; edges, seen = [], set()
    for n in nodes:
        for m in ADR_RE.finditer(n["_text"]):
            t = f"ADR-{m.group(1)}"
            if t in ids and t != n["id"] and (n["id"], t) not in seen:
                seen.add((n["id"], t)); edges.append({"from": n["id"], "to": t, "rel": "declared-ref"})
    for n in nodes:
        del n["_text"]
    prev = {}
    pp = os.path.join(U, "canon.claims.jsonl")
    if os.path.exists(pp):
        prev = {json.loads(l)["id"]: json.loads(l).get("src_sha") for l in open(pp, encoding="utf-8") if l.strip()}
    changed = sorted(a["id"] for a in atoms if a["id"] in prev and prev[a["id"]] != a["src_sha"])
    new = sorted(a["id"] for a in atoms if a["id"] not in prev) if prev else []
    nums = sorted(int(n["id"][4:7]) for n in nodes if n["kind"] == "adr" and re.match(r"ADR-\d{3}", n["id"]))
    dup_nums = sorted({x for x in nums if nums.count(x) > 1})
    gaps = [x for x in range(nums[0], nums[-1] + 1) if x not in nums] if nums else []
    accepted = set(reg.get("canon_accepted_exposure", {}).get("files", [])) & set(source_hits)
    new_exp = set(source_hits) - accepted  # only a NEW file naming a counterpart is drift; the accepted set is Zach's 2026-10-15 decision
    cat = {"generated": time.strftime("%Y-%m-%d %H:%M"), "corpus": "canon", "nodes": nodes, "edges": edges, "version_dupes": len(dup_nums)}
    receipt = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "type": "canon-adapter-receipt", "nodes": len(nodes), "atoms": len(atoms),
               "declared_edges": len(edges), "quarantined": len(quarantined), "quarantined_ids": [q["id"] for q in quarantined][:40],
               "sources_changed_since_last_run": changed[:40], "new_atoms": len(new), "adr_number_collisions": dup_nums, "adr_number_gaps": gaps[:40],
               "canon_files_naming_counterparts": source_hits, "accepted_exposure": sorted(accepted), "new_exposure": sorted(new_exp),
               "verdict": "DRIFT" if (quarantined or changed or dup_nums or new_exp) else "CLEAN"}
    print(f"canon: {len(nodes)} nodes · {len(atoms)} atoms · {len(edges)} declared ADR refs · quarantined {len(quarantined)} (counterpart names) · "
          f"changed since last run {len(changed)} · ADR number collisions {dup_nums or 'none'} · gaps {len(gaps)}")
    print(f"canon files naming a counterpart: {len(source_hits)} ({len(accepted)} accepted: private repo, Zach 2026-10-15; {len(new_exp)} NEW)")
    for f in sorted(new_exp):
        print(f"  NEW EXPOSURE {f}: {source_hits[f]}")
    for q in quarantined[:12]:
        print(f"  QUARANTINE {q['id']}: names {q['quarantined_for']}")
    if dry:
        return 0
    w = lambda name, rows: open(os.path.join(U, name), "w", encoding="utf-8").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    w("canon.claims.jsonl", atoms); w("canon.quarantine.jsonl", quarantined)
    json.dump(cat, open(os.path.join(REPO, "_ARTIFACTS", "canon-universe-catalog.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    shell = open(os.path.join(REPO, "_ARTIFACTS", "louisville-atlas.html"), encoding="utf-8").read()
    pat = re.compile(r'(<script id="data" type="application/json">)(.*?)(</script>)', re.S)
    open(os.path.join(REPO, "_ARTIFACTS", "canon-universe-atlas.html"), "w", encoding="utf-8").write(pat.sub(lambda m: m.group(1) + json.dumps(cat, ensure_ascii=False) + m.group(3), shell, count=1))
    open(os.path.join(REPO, "_INBOX", "universe-drift.jsonl"), "a", encoding="utf-8").write(json.dumps(receipt) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
