"""Scratch memo-trace front end over the public engine (no model). Not committed anywhere."""
import json, sys, os
ENGINE = sys.argv[1]; ROOM = sys.argv[2]; MEMO = sys.argv[3]
sys.path.insert(0, os.path.join(ENGINE, "source"))
import loader
from rfp import answer as A, store

db = loader.load(ROOM)
clauses = store.all_clauses(db)
print("ingested clauses:", [c["clause_id"] for c in clauses])
for e in db.execute("SELECT amendment_clause, op, target FROM effects"):
    print("effect:", dict(e))
rows = []
for n, line in enumerate(open(MEMO).read().strip().splitlines(), 1):
    cands = A.expand_with_amendments(db, A.retrieve(clauses, line))
    for fig in sorted(A.figures(line)):
        hit, stale, review = [], [], []
        for c in cands:
            text = c["text"]
            if c["kind"] == "base":
                g = store.governing(db, c["clause_id"])
                unresolved = [e["amendment_clause"] for e in store.effects_on(db, c["clause_id"]) if e["op"] == "unresolved"]
                if unresolved:
                    review.append("%s (amendment %s unclassified)" % (c["clause_id"], ",".join(unresolved)))
                if g and A.has_figure(text.lower(), fig):
                    stale.append("%s -> governed by %s" % (c["clause_id"], g["amendment_clause"]))
                    continue
            if A.has_figure(text.lower(), fig) and not (c["kind"] == "amendment" and ("from " + fig) in text.lower()):
                hit.append(c["clause_id"])
        status = "TRACED" if hit else "STALE" if stale else "NOT COVERED"
        if review and status != "NOT COVERED":
            status += " + NEEDS REVIEW"
        rows.append({"line": n, "figure": fig, "status": status, "clauses": hit, "stale": stale, "review": review})
        print("%d  %-14s %-26s traced=%s stale=%s review=%s" % (n, fig, status, hit, stale, review))
json.dump(rows, open(os.path.join(os.path.dirname(MEMO), "actual.json"), "w"), indent=1)
