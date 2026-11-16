#!/usr/bin/env python3
"""Layer 1 projection metrics from Granola transcripts. Counted, no judgment.
Usage: python3 projection.py projection-data/raw_exact/*.txt  -> prints per-call metrics + prediction verdicts, writes metrics.json"""
import json, re, sys, statistics as st
from pathlib import Path

LINE = re.compile(r"^(?:\[(\d+):(\d\d)\]\s+)?(Microphone|System audio(?: \([^)]*\))?):\s*(.*)$")  # fixed 2026-11-16: named labels + untimed older transcripts were dropped
STOP = set("""about above after again against also because been before being below between both could does doing down during
each from further have having here into just like more most much myself once only other ought over same should some such than
that their theirs them then there these they this those through under until very what when where which while whom with would
your yours yeah yes okay right know mean think thing things kind sort really actually basically gonna want going said says
well good great cool totally sure stuff because people little bit maybe even still""".split())
INSIDER = set("""arcs kintsugi kairos primitive primitives manifold hyperstition provenance orthogonal notomation receipt receipts
operator operators compass ontology ontological epistemic isomorphism isomorphisms telemetry agentic orchestration substrate
recoil cartography fidelity lattice canon heuristic heuristics instantiate composable composability""".split())
BACKCH = re.compile(r"^(mm+-?hmm+|mhm+|uh-?huh|yeah|yep|right|okay|ok|sure|wow|nice|totally|exactly|got it|cool)[.!,]?(\s|$)", re.I)

def syl(w):
    w = w.lower(); g = re.findall(r"[aeiouy]+", w)
    n = len(g) - (1 if w.endswith("e") and len(g) > 1 else 0)
    return max(1, n)

def words(t): return re.findall(r"[A-Za-z']+", t)
def content(t): return {w.lower() for w in words(t) if len(w) >= 4 and w.lower() not in STOP}

def turns(path):
    blocks = []
    for ln in Path(path).read_text().splitlines():
        m = LINE.match(ln)
        if m: blocks.append(("Z" if m[3] == "Microphone" else "C", (int(m[1]) * 60 + int(m[2]) if m[1] else 0), m[4]))
    out, backch = [], 0
    for who, t, txt in blocks:
        short = len(words(txt)) <= 3
        if out and out[-1]["who"] == "Z" and who == "C" and short:
            backch += 1; out[-1]["backch"] += 1; continue   # listener noise does not end Zach's turn
        if out and out[-1]["who"] == who:
            out[-1]["text"] += " " + txt; out[-1]["end"] = t
        else:
            out.append({"who": who, "start": t, "end": t, "text": txt, "backch": 0})
    return out, backch

def score(path):
    T, backch = turns(path)
    zw = sum(len(words(x["text"])) for x in T if x["who"] == "Z"); cw = sum(len(words(x["text"])) for x in T if x["who"] == "C")
    rows = []
    for i, x in enumerate(T):
        if x["who"] != "Z": continue
        w = words(x["text"]); n = len(w)
        if n == 0: continue
        nxt = next((y for y in T[i + 1:] if y["who"] == "C" and len(words(y["text"])) > 3), None)
        hard = sum(1 for v in w if syl(v) >= 3) / n
        ins = sum(1 for v in w if v.lower() in INSIDER)
        rows.append({"start": x["start"], "words": n, "q": "?" in x["text"], "hard": round(hard, 3), "insider": ins,
                     "laconic": n >= 150, "grug": hard > 0.15 or ins >= 2,
                     "uptake": len(content(x["text"]) & content(nxt["text"])) if nxt else None,
                     "reply_words": len(words(nxt["text"])) if nxt else None})
    for r in rows: r["midcurve"] = r["laconic"] and r["grug"]
    # POST-HOC (added 2026-11-16 after the smoke test showed raw uptake scales with turn length):
    # lift = echo of THIS turn in the reply minus mean echo of Zach's other turns of similar length (0.5x to 2x words).
    zt = [x for x in T if x["who"] == "Z" and words(x["text"])]
    for k, r in enumerate(rows):
        r["lift"] = None
        if r["reply_words"] is None: continue
        i = T.index(zt[k]); rep = next(y for y in T[i + 1:] if y["who"] == "C" and len(words(y["text"])) > 3)
        peers = [z for j, z in enumerate(zt) if j != k and 0.5 * r["words"] <= len(words(z["text"])) <= 2 * r["words"]]
        if len(peers) >= 2:
            base = st.mean(len(content(z["text"]) & content(rep["text"])) for z in peers)
            r["lift"] = round(r["uptake"] - base, 2)
    zq = sum(x["text"].count("?") for x in T if x["who"] == "Z"); cq = sum(x["text"].count("?") for x in T if x["who"] == "C")
    longest = max((r["words"] for r in rows), default=0)
    return {"call": Path(path).stem, "zach_share": round(zw / max(1, zw + cw), 3), "zach_words": zw, "other_words": cw,
            "zach_turns": len(rows), "longest_turn_words": longest, "zach_questions": zq, "other_questions": cq,
            "backchannels_during_zach": backch, "laconic_trips": sum(r["laconic"] for r in rows),
            "grug_trips": sum(r["grug"] for r in rows), "midcurve": sum(r["midcurve"] for r in rows), "rows": rows}

def mean(xs): xs = [x for x in xs if x is not None]; return round(st.mean(xs), 2) if xs else None

def verdicts(calls):
    R = [r for c in calls for r in c["rows"]]
    out = {}
    out["P1 talk share >55% in >=2 calls"] = sum(c["zach_share"] > .55 for c in calls) >= 2
    ws = sorted(r["words"] for r in R); q3 = ws[int(.75 * (len(ws) - 1))] if ws else 0; med = st.median(ws) if ws else 0
    lo, hi = mean([r["uptake"] for r in R if r["words"] <= med]), mean([r["uptake"] for r in R if r["words"] >= q3])
    out["P2 uptake lower after long turns (top quartile %s+ words: %s) than short (<=%s: %s)" % (q3, hi, med, lo)] = None if None in (lo, hi) else hi < lo
    a, b = mean([r["reply_words"] for r in R if r["q"]]), mean([r["reply_words"] for r in R if not r["q"]])
    out["P3 reply longer after question (%s) than statement (%s)" % (a, b)] = None if None in (a, b) else a > b
    out["P4 Zach asks fewer questions in every call"] = all(c["zach_questions"] < c["other_questions"] for c in calls)
    L = [r for r in R if r["laconic"]]; g, ng = [r for r in L if r["grug"]], [r for r in L if not r["grug"]]
    a, b = mean([r["uptake"] for r in g]), mean([r["uptake"] for r in ng])
    out["P5 long+dense uptake (%s, n=%d) < long+plain (%s, n=%d)" % (a, len(g), b, len(ng))] = None if None in (a, b) or min(len(g), len(ng)) < 3 else a < b
    lo, hi = mean([r["lift"] for r in R if r["words"] <= med]), mean([r["lift"] for r in R if r["words"] >= q3])
    out["P2b POST-HOC lift lower after long turns (%s) than short (%s)" % (hi, lo)] = None if None in (lo, hi) else hi < lo
    a, b = mean([r["lift"] for r in g]), mean([r["lift"] for r in ng])
    ga, nb = len([r for r in g if r["lift"] is not None]), len([r for r in ng if r["lift"] is not None])
    out["P5b POST-HOC long+dense lift (%s, n=%d) < long+plain lift (%s, n=%d)" % (a, ga, b, nb)] = None if None in (a, b) or min(ga, nb) < 3 else a < b
    return out

if __name__ == "__main__":
    calls = [score(p) for p in sys.argv[1:]]
    for c in calls: print({k: v for k, v in c.items() if k != "rows"})
    for k, v in verdicts(calls).items(): print("TRUE " if v else ("FALSE" if v is False else "CAN'T TELL (n<3 or no data)"), k)
    Path(Path(sys.argv[0]).parent / "projection-data" / "metrics.json").write_text(json.dumps(calls, indent=1))
