import os, sys
ENGINE, ROOM, CONV = sys.argv[1:4]
sys.path.insert(0, os.path.join(ENGINE, "source")); os.environ["MODEL_PROVIDER"] = "mock"
import loader
from rfp import answer as A, store, parse as P
db = loader.load(ROOM)
print("files in room:", sorted(os.listdir(ROOM)))
print("documents loaded:", [r["filename"] for r in db.execute("select filename from documents")])
r = A.answer(db, "What is the management fee?")
print("answer:", r["status"], "|", r["answer"], "| cites", [c["clause_id"] for c in r["citations"]], "| notes", r.get("notes"))
for f in ["07_lpa_tracked_changes.pandoc-accept.txt", "08_lpa_text.pdftotext.txt"]:
    doc = P.parse(P.read_document(os.path.join(CONV, f)))
    for c in doc.clauses:
        print("%s %s: ...%s" % (f[:22], c.clause_id, c.text[-110:]))
