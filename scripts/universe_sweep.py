#!/usr/bin/env python3
"""universe_sweep: night-moves contamination sweep over every registered universe.

Read-only over atoms; appends ONE dated drift receipt to _INBOX/universe-drift.jsonl.
Checks (each is a mechanical grep or count, no model):
  1 cross-universe name grep   an atom names an entity that belongs to ANOTHER universe (or a denied counterpart, for canon)
  2 anti-alias grep            an atom mentions a known look-alike (e.g. 'the wonderful company') without type=collision
  3 shared-line control        memory template-aliasing-shared-boilerplate-fakes-cross-domain-echo: 5-gram echoes across
                               universes, reported raw, then after dropping every line shared verbatim by 2+ universes,
                               plus a word-scramble FP proxy. Only echoes that survive the control are findings.
  4 speaker lint               ADR-033 attribution_provenance_lint over every quote atom (CONTAMINATED / UNSOURCED fail)
  5 air-gap hygiene            atoms without an explicit audience (fail closed to internal), external count per universe
  6 canon                      source changed since the adapter ran, quarantine file non-empty, registered collisions present
Exit 2 on a hard finding (CROSS-NAME, ALIAS-LEAK, CONTAMINATED, UNSOURCED, canon quarantine, missing collision atom).
A leftover echo after the controls is REVIEW (listed, exit 0). Controls: shared-line, template-frequency (3+ atoms in one universe), declared-relation (personal universe and a universe it bridges to).
Stdlib only.   python3 scripts/universe_sweep.py [--no-write] [--self-test]
"""
import collections, json, os, random, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import universe_ask as ua

N = 5


def shingles(text):
    t = re.findall(r"[a-z0-9']+", text.lower())
    return {" ".join(t[i:i + N]) for i in range(len(t) - N + 1)}


def sweep(reg, root, repo=REPO):
    ua.ROOT = root
    rows = {u: ua.load(u, reg, root, repo) for u in reg["universes"] if os.path.exists(os.path.join(root, f"{u}.claims.jsonl"))}
    find = {"cross_name": [], "alias_leak": [], "quote": [], "echo_raw": 0, "echo_after_control": [], "scramble_fp": 0}
    allnames = {u: reg["universes"][u].get("names", []) + reg["universes"][u].get("entities_public", []) for u in rows}
    extra = reg.get("canon_denied_names_extra", [])
    allalias = {u: reg["universes"][u].get("anti_aliases", []) for u in rows}
    owner = {}
    for v, ns in allnames.items():
        for n in ns:
            owner[n] = v
    for u, rs in rows.items():
        personal = reg["universes"][u].get("tier") == "personal"
        foreign = [n for v, ns in allnames.items() if v != u for n in ns] + ([] if personal else extra)  # a person's own receipts may name counterparts who have no universe yet; those are counted, not failed
        if personal:
            for r in rs:
                for n in ua.find_names(ua.atom_text(r), extra):
                    find.setdefault("unregistered_mentions", collections.Counter())[n] += 1
        for r in rs:
            txt = ua.atom_text(r)
            for n in ua.find_names(txt, foreign):
                if owner.get(n) in r.get("bridges", []):
                    find["declared_bridges"] = find.get("declared_bridges", 0) + 1  # declared edge to a counterpart universe, not a leak
                    continue
                find["cross_name"].append({"atom": r["id"], "name": n})
            if r["type"] != "collision":
                for v, als in allalias.items():
                    for n in ua.find_names(txt, als):
                        find["alias_leak"].append({"atom": r["id"], "alias": n, "belongs_to": v})
    # shared-line control
    by_u = {u: [r["claim"] for r in rs] for u, rs in rows.items()}
    def echo(by):
        owners = {}
        for u, claims in by.items():
            for s in set().union(*(shingles(c) for c in claims)) if claims else ():
                owners.setdefault(s, set()).add(u)
        return {s: o for s, o in owners.items() if len(o) > 1}
    raw = echo(by_u)
    find["echo_raw"] = len(raw)
    sent = lambda c: {x.strip().lower() for x in re.split(r"(?<=[.!?])\s+", c) if len(x.split()) >= 6}
    line_owners = {}
    for u, claims in by_u.items():
        for c in claims:
            for x in sent(c):
                line_owners.setdefault(x, set()).add(u)
    shared_lines = {x for x, o in line_owners.items() if len(o) > 1}
    cleaned = {u: [" ".join(x for x in re.split(r"(?<=[.!?])\s+", c) if x.strip().lower() not in shared_lines) for c in claims] for u, claims in by_u.items()}
    after_lines = echo(cleaned)
    # template-frequency control (added 2026-10-18, after the first receipts run): a phrase repeated in 3+ atoms of ONE universe is template wording, not motion
    freq = {}
    for u, claims in cleaned.items():
        cnt = collections.Counter(s for c in claims for s in shingles(c))
        freq[u] = {s for s, k in cnt.items() if k >= 3}
    template = set().union(*freq.values()) if freq else set()
    after_tpl = {s: o for s, o in after_lines.items() if s not in template}
    # declared-relation split: a personal universe and a universe its atoms declare a bridge to describe the same events by design
    bridged = {v for u, rs in rows.items() if reg["universes"][u].get("tier") == "personal" for r in rs for v in r.get("bridges", [])}
    pers = {u for u in rows if reg["universes"][u].get("tier") == "personal"}
    related = {s: o for s, o in after_tpl.items() if len(o) == 2 and (o & pers) and (o - pers) <= bridged}
    hard = {s: o for s, o in after_tpl.items() if s not in related}
    find["echo_after_lines"] = len(after_lines); find["echo_after_template"] = len(after_tpl); find["echo_declared_relation"] = len(related)
    find["echo_after_control"] = [{"shingle": s, "universes": sorted(o)} for s, o in list(hard.items())[:20]]
    find["shared_lines_dropped"] = len(shared_lines)
    rng = random.Random(7)
    def scr(c):
        w = c.split(); rng.shuffle(w); return " ".join(w)
    find["scramble_fp"] = len(echo({u: [scr(c) for c in claims] for u, claims in by_u.items()}))
    for u, rs in rows.items():
        if any(r["type"] == "quote" for r in rs):
            for i, v, det in ua.lint_quotes(u, reg, rs, root):
                find["quote"].append({"atom": i, "verdict": v})
    hyg = {u: {"atoms": len(rs), "no_explicit_audience": sum(1 for r in rs if "audience" not in r), "external": sum(1 for r in rs if ua.audience_of(r, reg, u) == "external")} for u, rs in rows.items()}
    canon = {}
    if "canon" in rows:
        qp = os.path.join(root, "canon.quarantine.jsonl")
        canon = {"source_changed": ua.canon_drift(rows["canon"], repo), "quarantined": sum(1 for _ in open(qp)) if os.path.exists(qp) else 0}
    missing = [c["ref"] for c in reg.get("collisions", []) if not any(c["ref"].lower() in r["claim"].lower() and r["type"] == "collision" for r in rows.get(c["universe"], []))]
    return find, hyg, canon, missing


def verdict(find, canon, missing):
    # Hard failures are mechanical greps and refusals. A leftover echo is evidence to inspect, not proof (REVIEW, exit 0):
    # a receipt that cites an ADR restates the ADR by design. Severity changed 2026-10-18 after the first receipts run.
    hard = bool(find["cross_name"] or find["alias_leak"] or missing
                or any(q["verdict"] in ("CONTAMINATED", "UNSOURCED") for q in find["quote"]) or canon.get("quarantined"))
    if hard:
        return "CONTAMINATED"
    if find["echo_after_control"]:
        return "REVIEW"
    return "DRIFT" if canon.get("source_changed") else "CLEAN"


def self_test():
    import shutil, tempfile
    tmp = tempfile.mkdtemp()
    try:
        reg = {"canon_denied_names_extra": [], "collisions": [{"ref": "row-1", "universe": "a"}], "universes": {
            "a": {"tier": "counterpart", "entities": ["a"], "names": ["alpha co"], "anti_aliases": ["alpha foods"]},
            "b": {"tier": "counterpart", "entities": ["b"], "names": ["beta co"], "anti_aliases": []}}}
        json.dump(reg, open(os.path.join(tmp, "_registry.json"), "w"))
        base = {"type": "claim", "source": "s", "grade": "A", "verified_at": "2026-10-15", "ttl_days": 30, "tags": [], "audience": "internal"}
        boiler = "Every path below was checked to exist on main at cut time."
        W = lambda u, rows: open(os.path.join(tmp, f"{u}.claims.jsonl"), "w").write("".join(json.dumps(r) + "\n" for r in rows))
        W("a", [dict(base, id="a/1", entity="a", claim=f"Alpha Co ships anvils. {boiler}"), dict(base, id="a/2", entity="a", type="collision", claim="row-1 is Alpha Foods, not Alpha Co.")])
        W("b", [dict(base, id="b/1", entity="b", claim=f"Beta Co ships rockets. {boiler}")])
        f, h, c, m = sweep(reg, tmp)
        ok1 = f["echo_raw"] > 0 and not f["echo_after_control"]
        print(("PASS " if ok1 else "FAIL ") + f"shared-line control: raw echoes {f['echo_raw']} from the template line, {len(f['echo_after_control'])} after the control")
        ok2 = not f["cross_name"] and not f["alias_leak"] and not m
        print(("PASS " if ok2 else "FAIL ") + "clean fixture: no cross-name, collision atom may name its alias, collision registered")
        W("b", [dict(base, id="b/1", entity="b", claim="Beta Co met Alpha Co about Alpha Foods.")])
        f, h, c, m = sweep(reg, tmp)
        ok3 = [x["name"] for x in f["cross_name"]] == ["alpha co"] and [x["alias"] for x in f["alias_leak"]] == ["alpha foods"] and verdict(f, c, m) == "CONTAMINATED"
        print(("PASS " if ok3 else "FAIL ") + "seeded contamination: cross-universe name and anti-alias both caught")
        W("b", [dict(base, id="b/1", entity="b", claim="Revenue grows quickly in three regions this year.")])
        W("a", [dict(base, id="a/1", entity="a", claim="Revenue grows quickly in three regions this year.")])
        f, h, c, m = sweep(reg, tmp)
        ok4 = f["echo_raw"] > 0 and f["shared_lines_dropped"] > 0
        print(("PASS " if ok4 else "FAIL ") + f"identical sentence in two universes is dropped by the control (dropped {f['shared_lines_dropped']})")
        return 0 if all((ok1, ok2, ok3, ok4)) else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if "--self-test" in sys.argv:
        return self_test()
    reg = ua.load_registry(ua.ROOT)
    find, hyg, canon, missing = sweep(reg, ua.ROOT)
    v = verdict(find, canon, missing)
    qc = {}
    for q in find["quote"]:
        qc[q["verdict"]] = qc.get(q["verdict"], 0) + 1
    receipt = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "type": "universe-sweep-receipt", "universes": sorted(hyg), "verdict": v,
               "declared_bridges": find.get("declared_bridges", 0), "cross_name": find["cross_name"], "alias_leak": find["alias_leak"], "echo_raw": find["echo_raw"], "shared_lines_dropped": find["shared_lines_dropped"], "echo_after_lines": find["echo_after_lines"], "echo_after_template": find["echo_after_template"], "echo_declared_relation": find["echo_declared_relation"], "unregistered_mentions": dict(find.get("unregistered_mentions", {})),
               "real_echoes_after_template_control": find["echo_after_control"], "scramble_fp_proxy": find["scramble_fp"], "quote_lint": qc,
               "audience_hygiene": hyg, "canon": canon, "collisions_missing_atom": missing}
    print(f"universe sweep {receipt['ts'][:10]}: {v}")
    print("  universes " + ", ".join("%s(%d)" % (u, h["atoms"]) for u, h in hyg.items()))
    print(f"  declared bridges {find.get('declared_bridges', 0)} · cross-universe names {len(find['cross_name'])} · alias leaks {len(find['alias_leak'])} · missing collision atoms {len(missing)}")
    print(f"  echoes raw {find['echo_raw']} -> shared-line {find['echo_after_lines']} -> template-frequency {find['echo_after_template']} -> declared-relation {find['echo_declared_relation']} -> real {len(find['echo_after_control'])} (scramble FP proxy {find['scramble_fp']})")
    if find.get("unregistered_mentions"):
        print("  personal receipts name counterparts with no universe yet: " + ", ".join(f"{n} {k}" for n, k in find["unregistered_mentions"].most_common(8)))
    print(f"  quote lint {qc or 'no quote atoms'} · canon {canon or 'not built'}")
    print("  no explicit audience: " + ", ".join(f"{u} {h['no_explicit_audience']}" for u, h in hyg.items() if h["no_explicit_audience"]) if any(h["no_explicit_audience"] for h in hyg.values()) else "  every atom carries an explicit audience tag")
    for x in find["cross_name"][:10] + find["alias_leak"][:10] + find["echo_after_control"][:8]:
        print("  FINDING", x)
    if "--no-write" not in sys.argv:
        open(os.path.join(REPO, "_INBOX", "universe-drift.jsonl"), "a", encoding="utf-8").write(json.dumps(receipt) + "\n")
    return 2 if v == "CONTAMINATED" else 0


if __name__ == "__main__":
    sys.exit(main())
