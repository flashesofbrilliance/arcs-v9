import sys, os, json
ENGINE, ROOM, MEMO = sys.argv[1:4]
sys.path.insert(0, os.path.join(ENGINE, "source"))
os.environ["MODEL_PROVIDER"] = "mock"
import loader
from rfp import answer as A, store
db = loader.load(ROOM)
clauses = store.all_clauses(db)
print("== topic rule: does the figure's clause share a sentence term beyond the figure?")
for line in open(MEMO).read().strip().splitlines():
    terms = set(A.tokens(line)) - {t for t in A.tokens(line) if any(ch.isdigit() for ch in t)}
    for c in clauses:
        for fig in A.figures(line):
            if A.has_figure(c["text"].lower(), fig):
                shared = sorted(terms & set(A.tokens(c["text"] + " " + (c["section_title"] or ""))))
                print("  %-12s in %-5s shared=%s" % (fig, c["clause_id"], shared))
print("== engine answer() per memo line, mock provider, MOCK_FAULT=%s" % os.environ.get("MOCK_FAULT", "none"))
for line in open(MEMO).read().strip().splitlines():
    r = A.answer(db, line)
    print("  %-62s %-14s gate=%s cites=%s" % (line[:62], r["status"], r.get("gate"), [c["clause_id"] for c in r.get("citations", [])]))
print("== scope refusals on investment questions")
for q in ["Should we invest in Fund II?", "Is a 1.75% fee market for a growth fund?", "Is this a good deal?",
          "Should we commit $25,000,000?", "Give me a go or no-go on this fund", "Draft the IC memo section on fees"]:
    r = A.answer(db, q)
    print("  %-45s %-14s gate=%s" % (q, r["status"], r.get("gate")))
