#!/usr/bin/env python3
"""forecast_base_rates: empirical base rates for the three peer follow-up forecasts the recoil pages make.

Backlog row forecast-base-rates (R10), spec _PROPOSALS/2026-11-11-recoil-call-service-arc-weld.md section 4.3.
Stdlib only. Read-only: reads runtime/recoil/generated/*.json and the local export of public.decision_receipt
(_STATE/job-search/universe/sources/decision-receipts.json, refreshed by `scripts/receipt_coverage.py --export`,
a SELECT only). Writes one file: runtime/specs/forecast-base-rates.json.

COUNTING RULE (written before counting; edit it here, not in the output)
Three outcomes (kind):
  times  the counterpart sends meeting times or availability
  call   a follow-up call between the two parties is held
  tool   the counterpart tries the tool (the card, demo, skill, pilot or trial)
A CASE is one source row that states the ask or plan for a kind: its text matches that kind's ASK regex.
  Source A  one line of an SSOT's next_steps[] or close.status_note / close.net_new[].update (runtime/recoil/generated).
            Forecast text (scenarios, beliefs, callWalk) is NOT evidence: a forecast cannot resolve itself.
  Source B  one decision_receipt row (question + what_confirmed + what_unconfirmed) matching the ASK regex AND naming a
            counterpart (COUNTERPART regex). Added after the first run: without it, PR-merge receipts matched "test ... page"
            and "pilot" in code context and counted as peer outcomes. That was a rule bug, not a result I disliked.
A case is a SUCCESS when the same row also matches that kind's DONE regex AND (Source A) the line starts with "DONE"
or (Source B) the match sits in what_confirmed.
A case is a FAILURE ("lapsed") when it is not a success and its date is more than LAPSE_DAYS (14) before today.
A case younger than LAPSE_DAYS is OPEN and left out of n.
The row date is the YYYY-MM-DD in the SSOT filename (Source A) or event_at (Source B); a "DONE YYYY-MM-DD" stamp
in the line overrides it for recency only.
n = successes + lapsed failures. rate = successes / n. Any rate with n < 3 is labelled grain and prints no sharp number.
Known bias, printed with every run: Source A lines are written by the operator after the fact, so a lapsed ask that
nobody wrote down never enters the count (survivorship toward done work); treat every rate as an upper-leaning
estimate, a basis rather than a forecast. Cases from the same engagement are not independent; the table prints
distinct engagements next to n.

  python3 scripts/forecast_base_rates.py            # print table, write runtime/specs/forecast-base-rates.json
  python3 scripts/forecast_base_rates.py --no-write
  python3 scripts/forecast_base_rates.py --self-test
"""
import datetime, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
SSOT_GLOB = os.path.join(REPO, "runtime/recoil/generated/*.json")
RECEIPTS = os.path.join(REPO, "_STATE/job-search/universe/sources/decision-receipts.json")
OUT = os.path.join(REPO, "runtime/specs/forecast-base-rates.json")
LAPSE_DAYS = 14
GRAIN_BELOW = 3

I = re.I
KINDS = {
    "times": {
        "label": "counterpart sends times within N days",
        "ask": re.compile(r"\b(send|sends|sent|share|propose|offer)\w*\b[^.]{0,40}\b(times|slots|availability)\b|\b(times|availability)\b[^.]{0,30}\b(send|sends|sent|share)", I),
        "done": re.compile(r"\b(sent|sends|offered|shared|proposed)\b[^.]{0,40}\b(times|slots|availability)\b|\b(times|slots|availability)\b[^.]{0,30}\b(sent|came|arrived|received)", I),
    },
    "call": {
        "label": "a follow-up call happens within N days",
        "ask": re.compile(r"follow-?\s?up call|second call|part[- ]two|next call|schedule the [^.]{0,30}(call|follow-?up)|20-minute [^.]{0,20}call", I),
        "done": re.compile(r"(follow-?\s?up|second|next|update)[^.]{0,30}\b(call|meeting)\b[^.]{0,20}\b(held|took|happened|done)\b|\b(held|took)\b[^.]{0,30}(follow-?\s?up|second|update)[^.]{0,15}(call|meeting)|follow-?\s?up call held", I),
    },
    "tool": {
        "label": "counterpart tries the tool",
        "ask": re.compile(r"\b(try|tries|trial|pilot|test)\b[^.]{0,30}\b(card|demo|skill|tool|page|arcs)\b|\b(card|demo|skill|tool|page)\b[^.]{0,30}\b(trial|pilot)\b", I),
        "done": re.compile(r"\b(tried|opened|used|ran|reading it in real time|looking at it right now)\b[^.]{0,40}\b(card|demo|skill|tool|page|it)\b", I),
    },
}
COUNTERPART = re.compile(r"\b(counterpart|recruiter|prospect|founder|hiring manager|champion|client)\b", I)
DATE_IN_NAME = re.compile(r"(\d{4}-\d{2}-\d{2})")


def to_date(s):
    try:
        return datetime.date.fromisoformat(s[:10])
    except Exception:
        return None


def ssot_lines(d):
    """Yield (text) lines from next_steps and close only."""
    for s in d.get("next_steps") or []:
        yield s.get("text", "") if isinstance(s, dict) else str(s)
    c = d.get("close")
    if isinstance(c, dict):
        if isinstance(c.get("status_note"), str):
            yield c["status_note"]
        for n in c.get("net_new") or []:
            if isinstance(n, dict) and isinstance(n.get("update"), str):
                yield n["update"]


def classify(text, done_in_confirmed, row_date, today):
    """Return (kind, outcome) pairs for one row. outcome in success|lapsed|open."""
    out = []
    for k, r in KINDS.items():
        if not r["ask"].search(text) and not (done_in_confirmed is not None and r["done"].search(done_in_confirmed)):
            continue
        ok = bool(r["done"].search(done_in_confirmed if done_in_confirmed is not None else text))
        if done_in_confirmed is None:
            ok = ok and text.lstrip().upper().startswith("DONE")
        if ok:
            out.append((k, "success"))
        elif row_date and (today - row_date).days > LAPSE_DAYS:
            out.append((k, "lapsed"))
        else:
            out.append((k, "open"))
    return out


def collect(today, ssot_files=None, receipts=None):
    cases = []  # dicts: kind, outcome, source, engagement, row
    for f in sorted(ssot_files if ssot_files is not None else glob.glob(SSOT_GLOB)):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        base = os.path.basename(f)
        m = DATE_IN_NAME.match(base)
        fdate = to_date(m.group(1)) if m else None
        for i, t in enumerate(ssot_lines(d)):
            if not t:
                continue
            dm = re.search(r"DONE (\d{4}-\d{2}-\d{2})", t)
            rd = to_date(dm.group(1)) if dm else fdate
            for k, o in classify(t, None, rd, today):
                cases.append({"kind": k, "outcome": o, "source": "ssot", "engagement": base, "row": "%s#%d" % (base, i), "excerpt": t[:140]})
    if receipts is None and os.path.exists(RECEIPTS):
        receipts = json.load(open(RECEIPTS))
    for r in receipts or []:
        conf = " ".join(r.get("what_confirmed") or [])
        unc = " ".join(r.get("what_unconfirmed") or [])
        text = " ".join([r.get("question") or "", conf, unc])
        if not COUNTERPART.search(text):
            continue
        for k, o in classify(text, conf, to_date(r.get("event_at") or ""), today):
            cases.append({"kind": k, "outcome": o, "source": "receipt", "engagement": r.get("receipt_id"), "row": r.get("receipt_id"), "excerpt": text[:140]})
    return cases


def summarize(cases):
    res = {}
    for k, r in KINDS.items():
        rows = [c for c in cases if c["kind"] == k and c["outcome"] != "open"]
        succ = [c for c in rows if c["outcome"] == "success"]
        n = len(rows)
        res[k] = {
            "label": r["label"], "n": n, "successes": len(succ),
            "open_excluded": len([c for c in cases if c["kind"] == k and c["outcome"] == "open"]),
            "distinct_engagements": len({c["engagement"] for c in rows}),
            "rate": round(len(succ) / n, 3) if n >= GRAIN_BELOW else None,
            "fidelity": "grain" if n < GRAIN_BELOW else "counted",
            "source_rows": [{"row": c["row"], "source": c["source"], "outcome": c["outcome"], "excerpt": c["excerpt"]} for c in rows],
        }
    return res


def table(res):
    lines = ["%-42s %4s %5s %5s  %s" % ("forecast", "n", "succ", "eng", "rate")]
    for k, v in res.items():
        rate = "grain (n = %d)" % v["n"] if v["fidelity"] == "grain" else "%d%% (n = %d)" % (round(v["rate"] * 100), v["n"])
        lines.append("%-42s %4d %5d %5d  %s" % (v["label"], v["n"], v["successes"], v["distinct_engagements"], rate))
    return "\n".join(lines)


def self_test():
    t = datetime.date(2026, 11, 11)
    ss = [("2026-09-01-x.json", {"next_steps": [{"text": "DONE 2026-09-17: follow-up call held."}, {"text": "Schedule the follow-up call."}, {"text": "Schedule the follow-up call with Y."}]})]
    import tempfile
    tmp = tempfile.mkdtemp(); fs = []
    for n, d in ss:
        p = os.path.join(tmp, n); json.dump(d, open(p, "w")); fs.append(p)
    cs = collect(t, ssot_files=fs, receipts=[])
    got = sorted((c["kind"], c["outcome"]) for c in cs)
    assert got == [("call", "lapsed"), ("call", "lapsed"), ("call", "success")], got
    s = summarize(cs)["call"]
    assert s["n"] == 3 and s["successes"] == 1 and s["rate"] == 0.333
    assert summarize(cs)["times"]["fidelity"] == "grain" and summarize(cs)["times"]["rate"] is None
    print("self-test ok")


def main():
    if "--self-test" in sys.argv:
        return self_test()
    today = datetime.date.today()
    cases = collect(today)
    res = summarize(cases)
    print(table(res))
    print("\nRows counted (outcome, source, row):")
    for k, v in res.items():
        print("\n[%s] %s" % (k, v["label"]))
        for c in v["source_rows"]:
            print("  %-7s %-7s %s" % (c["outcome"], c["source"], c["row"]))
        print("  open, excluded (< %d d old): %d" % (LAPSE_DAYS, v["open_excluded"]))
    print("\nBias: operator-written rows over-represent done work; Source A rows from one engagement are not independent.")
    if "--no-write" not in sys.argv:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump({"generated": today.isoformat(), "rule": "see scripts/forecast_base_rates.py header", "lapse_days": LAPSE_DAYS,
                   "grain_below_n": GRAIN_BELOW, "rates": res}, open(OUT, "w"), indent=1, ensure_ascii=False)
        print("wrote", os.path.relpath(OUT, REPO))


if __name__ == "__main__":
    main()
