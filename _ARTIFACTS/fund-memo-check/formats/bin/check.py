"""Run each test file (raw) and each conversion through the public engine's own reader and parser."""
import os, sys, shutil, tempfile, json
ENGINE, FILES, CONV = sys.argv[1:4]
sys.path.insert(0, os.path.join(ENGINE, "source"))
import loader
from rfp import parse as P, store, answer as A
LEAKS = {"comment 1.50%": "1.50%", "footnote 1.25%": "1.25%", "header": "confidential", "page no.": "page 4", "struck $1,500,000": "$1,500,000"}
out = []
print("== A. raw files dropped into the data folder, one per folder (what loader.load does)")
for f in sorted(os.listdir(FILES)):
    d = tempfile.mkdtemp(); shutil.copy(os.path.join(FILES, f), d)
    try:
        db = loader.load(d); n = len(store.all_clauses(db))
        res = "loaded, %d clauses" % n if n else "SKIPPED SILENTLY (0 documents, no error)" if not db.execute("select count(*) from documents").fetchone()[0] else "loaded, 0 clauses"
    except Exception as e:
        res = "REFUSED: %s" % str(e).split(":")[0] + ": " + type(e).__name__
    print("  %-32s %s" % (f, res)); out.append({"stage": "raw", "file": f, "result": res})
print("== A2. raw bytes forced through read_document + ingest (as if renamed .txt)")
for f in sorted(os.listdir(FILES)):
    if f.endswith((".txt", ".md")): continue
    db = store.connect(":memory:")
    try:
        doc, _ = store.ingest(db, P.read_document(os.path.join(FILES, f)), f + ".txt"); res = "%d clauses" % len(doc.clauses)
    except Exception as e:
        res = "REFUSED (%s)" % type(e).__name__
    print("  %-32s %s" % (f, res)); out.append({"stage": "forced", "file": f, "result": res})
print("== B. conversions parsed by the engine: clause ids, then what clause 8.1 / 8.3 say")
srcs = [os.path.join(FILES, f) for f in sorted(os.listdir(FILES)) if f.endswith((".txt", ".md"))] + \
       [os.path.join(CONV, f) for f in sorted(os.listdir(CONV))]
for p in srcs:
    raw = P.read_document(p); doc = P.parse(raw); ids = [c.clause_id for c in doc.clauses]
    by = {c.clause_id: c.text for c in doc.clauses}
    t81, t83 = by.get("8.1", "").lower(), by.get("8.3", "").lower()
    figs81 = sorted(A.figures(t81) & {"2.0%", "1.75%", "1.50%", "1.25%"})
    leaks = [k for k, v in LEAKS.items() if v in " ".join(by.values()).lower() and not (k.startswith("struck") and "1,500,000" in t83 and "2,000,000" not in t83)]
    try:
        db = store.connect(":memory:"); store.ingest(db, raw, os.path.basename(p) + ".txt"); ing = "ok"
    except Exception as e:
        ing = "REFUSED (%s)" % type(e).__name__
    row = {"stage": "converted", "file": os.path.basename(p), "ingest": ing, "clauses": ids, "8.1 fee figures": figs81, "8.3": t83[-80:], "leaks": leaks}
    out.append(row)
    print("  %-46s ingest=%-24s ids=%s\n      8.1 fee figures=%s  leaks=%s" % (row["file"], ing, ids, figs81, leaks))
json.dump(out, open(os.path.join(os.path.dirname(CONV), "results.json"), "w"), indent=1)
