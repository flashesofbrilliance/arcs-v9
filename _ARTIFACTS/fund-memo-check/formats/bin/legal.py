import os, sys
ENGINE, DOC = sys.argv[1:3]
sys.path.insert(0, os.path.join(ENGINE, "source")); os.environ["MODEL_PROVIDER"] = "mock"
from rfp import answer as A, store, parse as P
db = store.connect(":memory:"); store.ingest(db, P.read_document(DOC), "lpa.txt")
for c in store.all_clauses(db): print("clause", c["clause_id"], "|", c["text"][:150])
cl = store.all_clauses(db)
for line in ["The management fee is 1.75% of commitments.", "Organizational expenses are capped at $2,000,000.",
             "Organizational expenses are capped at $1,500,000.", "Placement fees are shared 50/50 with the fund."]:
    for f in sorted(A.figures(line)):
        hits = [c["clause_id"] for c in cl if A.has_figure(c["text"].lower(), f)]
        print("memo %-52s %-11s found in %s" % (line, f, hits or "nothing"))
r = A.answer(db, "What is the management fee?")
print("engine answer:", r["status"], "|", r["answer"][:120], "| cites", [c["clause_id"] for c in r["citations"]])
