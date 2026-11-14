#!/usr/bin/env python3
"""braided_lanes_build: kit organism 72 (braided lanes) and the fragment status.arcs.care/beliefs inlines.

In:  runtime/specs/shipped-record.json   (scripts/shipped_record_emit.py; beliefs, repaired-by links, weekly tempo)
     src/ui-kit/braided-lanes/braid.css + braid.js   (the organism's source)
Out: src/ui-kit/specimens/braided-lanes.json -> scripts/kit_specimen.py -> src/ui-kit/recoil-report/72-braided-lanes.html
     src/ui-kit/braided-lanes/belief-fragment.html   (style + no-JS floor + data + script; scripts/belief_log_emit.py
     inlines it into public/belief-log.html)
     --preview PATH writes the fragment under the kit tokens as a standalone page for page_gate (not committed)

Public shape only: a belief carries id, scope, date and the gold flag. Claim text never enters the payload.

  python3 scripts/braided_lanes_build.py           write both outputs, rebuild the specimen page and the belief log
  python3 scripts/braided_lanes_build.py --check   exit 1 if either output is stale
  python3 scripts/braided_lanes_build.py --preview /tmp/braid.html
  python3 scripts/braided_lanes_build.py --self-test
Stdlib only.
"""
import datetime as dt
import html
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(ROOT, "runtime/specs/shipped-record.json")
SRC = os.path.join(ROOT, "src/ui-kit/braided-lanes")
SPEC = os.path.join(ROOT, "src/ui-kit/specimens/braided-lanes.json")
FRAG = os.path.join(SRC, "belief-fragment.html")
KIT = os.path.join(ROOT, "src/ui-kit/recoil-report")
GRAIN_N = 3
# Plain-English name and meaning of each ledger scope (names as the belief-log page has always used; meanings without pronouns).
PLAIN = {
    "canon": ("Rulebook", "The written principles the work is built and decided by."),
    "infra": ("Infrastructure", "The machinery underneath: servers, databases, and builds."),
    "process": ("How we work", "Working habits: reviews, checks, and when something counts as done."),
    "gauntlet": ("Stress tests", "The review panels work goes through, and what they cost to run."),
    "deploy": ("Shipping", "How a change gets from the desk to the live site."),
    "security": ("Security", "Keeping private things private, and automated access in check."),
    "recoil": ("Client reads", "Judgment calls about real outside engagements."),
    "surface": ("Public pages", "The pages anyone can see, including this one."),
}


def monday(d):
    return d - dt.timedelta(days=d.weekday())


def fmt(date):
    d = dt.date.fromisoformat(date) if isinstance(date, str) else date
    return "%d %s %d" % (d.day, d.strftime("%b"), d.year)


def payload(rec):
    tempo = rec["tempo"]
    beliefs = [e for e in rec["events"] if e["lane"] == "belief"]
    commits = {w["week"]: w["n"] for w in tempo["commits"]}
    receipts = {w["week"]: w["n"] for w in tempo["receipts"]}
    start = dt.date.fromisoformat(min(commits))
    as_of = dt.date.fromisoformat(tempo["commits_as_of"])
    weeks = (monday(as_of) - start).days // 7 + 1
    wk = [(start + dt.timedelta(weeks=i)).isoformat() for i in range(weeks)]
    first_r = min(receipts)
    r_as_of = monday(dt.date.fromisoformat(tempo["receipts_as_of"])).isoformat()
    counts = {}
    for b in beliefs:
        counts[b["scope"]] = counts.get(b["scope"], 0) + 1
    order = sorted(counts, key=lambda k: (-counts[k], k))
    ix = {k: i for i, k in enumerate(order)}
    ids = {b["id"] for b in beliefs}
    links = sorted([l["from"], l["to"]] for l in rec["links"] if l["kind"] == "repaired-by" and l["from"] in ids and l["to"] in ids)
    first_belief = min(b["date"] for b in beliefs)
    return {
        "start": start.isoformat(), "weeks": weeks, "as_of": as_of.isoformat(),
        "first_receipt_week": wk.index(first_r),
        "default": [wk.index(monday(dt.date.fromisoformat(first_belief)).isoformat()), weeks - 1],
        "commits": [commits.get(w, 0) for w in wk],
        # null, never 0, for weeks the receipt ledger did not exist yet or the snapshot had not reached.
        "receipts": [None if w < first_r or w > r_as_of else receipts.get(w, 0) for w in wk],
        "lanes": [{"key": k, "label": PLAIN.get(k, (k, ""))[0], "def": PLAIN.get(k, (k, ""))[1], "n": counts[k]} for k in order],
        "events": [[b["id"], ix[b["scope"]], (dt.date.fromisoformat(b["date"]) - start).days, int(bool(b.get("gold")))]
                   for b in sorted(beliefs, key=lambda b: (b["date"], b["id"]))],
        "links": links,
        "source": ("Source: the falsification ledger, %d reversals from %s to %s; %d repaired-by links, each cited in the ledger. "
                   "Commits: every commit on main, merges included, to %s. Receipts: the decision-receipt ledger, snapshot of %s; it begins the week of %s."
                   % (len(beliefs), fmt(first_belief), fmt(max(b["date"] for b in beliefs)), len(links),
                      fmt(as_of), fmt(tempo["receipts_as_of"]), fmt(first_r))),
    }


def floor(p):
    """The no-JS floor: each domain with its count and how many of its reversals changed the rulebook."""
    gold = {}
    for e in p["events"]:
        gold[e[1]] = gold.get(e[1], 0) + e[3]
    lis = ['<li>%s <span class="bl-fmeta">n=%d%s, %d changed the rulebook</span></li>'
           % (html.escape(l["label"]), l["n"], " · grain" if l["n"] < GRAIN_N else "", gold.get(i, 0))
           for i, l in enumerate(p["lanes"])]
    return '<ul class="bl-floor">%s</ul>' % "".join(lis)


def read(name):
    return open(os.path.join(SRC, name), encoding="utf-8").read()


def fragment(p):
    data = json.dumps(p, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return ("<!-- generated by scripts/braided_lanes_build.py from runtime/specs/shipped-record.json; kit organism 72. "
            "Inline after the kit tokens (_tokens.css). Do not hand-edit. -->\n"
            "<style>\n%s</style>\n<div class=\"braid\" data-braid>%s</div>\n"
            "<script type=\"application/json\" data-braid-data>%s</script>\n"
            "<script>\n%s(function(){var h=document.querySelector('[data-braid]'),d=document.querySelector('[data-braid-data]');"
            "if(h&&d){var p=JSON.parse(d.textContent);arcsBraid(h,p,{w0:p.default[0],w1:p.default[1]});}})();\n</script>\n"
            ) % (read("braid.css"), floor(p), data, read("braid.js"))


def preview(frag):
    """A standalone page that inlines the kit tokens and the fragment, so page_gate can judge the fragment itself."""
    tok = "".join(open(os.path.join(KIT, f), encoding="utf-8").read() for f in ("_tokens.css", "_tokens-light.css"))
    return ("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n<title>Belief lanes: preview</title>\n"
            "<!-- generated by scripts/braided_lanes_build.py; preview of belief-fragment.html under the kit tokens -->\n"
            "<style>\n%s\n* { box-sizing: border-box; margin: 0; padding: 0; }\n"
            "body { background: var(--bg); color: var(--text); font-family: var(--ds-font-sans); font-size: var(--fs-body); line-height: 1.6; padding: 32px 16px 64px; }\n"
            "main { max-width: 1000px; margin: 0 auto; display: flex; flex-direction: column; gap: 16px; }\n"
            "h1 { font-family: var(--ds-font-display); font-size: var(--fs-headline); font-weight: 500; }\n</style>\n</head>\n<body>\n<main>\n"
            "<h1>Every reversal, plotted in time</h1>\n%s</main>\n</body>\n</html>\n") % (tok, frag)


def spec(p):
    data = json.dumps(p, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    w = p["weeks"] - 1
    aug = (dt.date(2026, 8, 10) - dt.date.fromisoformat(p["start"])).days // 7
    return {
        "number": "72", "name": "Braided Lanes", "slug": "braided-lanes", "layer": "Organism",
        "job": "Read every reversed belief as one flat lane per domain over time, see which reversals repaired others and which hardened into rules, against the weekly pace of work.",
        "anatomy": [
            {"part": "Activity ribbon", "role": "Two sparkline rows, commits and decision receipts per week, each scaled to its own peak in the window; weeks with no count are hatched, never drawn as zero", "token": "`cyan`, `green`, `border`"},
            {"part": "Lanes", "role": "One flat lane per domain, sorted by count, n printed at the right", "token": "`border`, `text-secondary`"},
            {"part": "Events", "role": "A dot per reversal in its domain colour; a gold ring when the fix became a standing rule", "token": "`cyan`, `green`, `red`, `violet`, `magenta`, `orange`, `text-secondary`, `gold`"},
            {"part": "Braids", "role": "A curve from a reversal to the later one that repaired it, cited in the ledger", "token": "`text`"},
            {"part": "Thin evidence", "role": "Lanes with under 3 events in all sit below a divider; any lane under 3 in the window renders as grain and prints n", "token": "`surface`, `text-secondary`"},
            {"part": "Window", "role": "Two native range inputs set the first and last week; the dates print beside them", "token": "`text-secondary`, `cyan`"},
            {"part": "Readout", "role": "A live region that reads the focused or pointed dot in words", "token": "`text`, `surface`"},
        ],
        "states": [
            {"name": "Default window", "args": [p["default"][0], w, "100%"], "note": "From the first reversal to the record's date."},
            {"name": "The repair chain", "args": [aug, aug + 8, "100%"], "note": "Mid-August to early October: two braids in the window, and most lanes fall to grain."},
            {"name": "Phone", "args": [p["default"][0], w, "20rem"], "note": "Under 520px the names move above each lane and the plot takes the full width."},
        ],
        "use_when": ["A reader should see how often and where a record changed its mind, which reversals repaired others, and how that sits against the pace of work.",
                     "Every event and link has a source a reader could check."],
        "avoid_when": ["Do not put the belief itself on the page: the public shape is id, domain, date and the gold flag.",
                       "Not for a single domain or a handful of events: with one lane it is a timeline, use one."],
        "data": [
            {"field": "start, weeks, as_of", "type": "ISO date, int, ISO date", "required": True, "note": "Week 0 is the Monday of `start`."},
            {"field": "commits[], receipts[]", "type": "int per week; receipts may be null", "required": True, "note": "`null` means not recorded, rendered hatched."},
            {"field": "lanes[]", "type": "{key, label, def, n}", "required": True, "note": "Top to bottom; `key` picks the colour class."},
            {"field": "events[]", "type": "[id, lane, day, gold]", "required": True, "note": "`day` counts from `start`."},
            {"field": "links[]", "type": "[from, to]", "required": True, "note": "Repaired-by only; drawn when both ends are in the window."},
            {"field": "source", "type": "string", "required": True, "note": "Printed under the readout."},
        ],
        "access": ["The window is two native range inputs with labels; arrow keys, Home and End move a week at a time, and the dates print in an output.",
                   "Every dot is focusable with a label that states the domain, the belief number, the date and whether it changed the rulebook; focus also fills the readout.",
                   "Colour is never the only signal: lanes are named, gold rings are also said in words, grain prints n.",
                   "Nothing animates, so reduced motion needs no branch. Without script the host keeps a list of domains with their counts."],
        "built_from": [{"name": "Kit tokens (atoms)", "href": "_tokens.css"}, {"name": "37 Fidelity Grain", "href": "37-fidelity-grain.html"},
                       {"name": "64 Kintsugi Seam", "href": "64-kintsugi-seam.html"}, {"name": "69 Strata Explorer", "href": "69-strata-explorer.html"}],
        "used_by": [{"name": "status.arcs.care/beliefs, the belief-change log (public/belief-log.html via scripts/belief_log_emit.py)"}],
        "gates": ["`braided_lanes_build.py --check` (in scripts): the spec and fragment match the record.",
                  "`shipped_record_emit.py --self-test`: no uncited event or link, no belief text leaked, tempo carries its as-of dates.",
                  "`belief_log_emit.py --check`: the page carries the current fragment, and its reversal count matches the ledger.",
                  "`kit_specimen.py --check` and `kit_primitive_sync.py --check`.",
                  "`artifact_wrap_lint.py` and `page_gate.py` on every page that carries it; sweep 360 to 1440, including 700 to 1000."],
        "links": ["_tokens-light.css", "_kit-sr.css"],
        "css": read("braid.css"),
        "demo": ("var BRAID=%s;\n%s\nfunction bSlot(i){return i===undefined?document.querySelector('[data-stage]'):document.querySelector('[data-state=\"'+i+'\"]');}\n"
                 "arcsBraid(bSlot(),BRAID,{w0:BRAID.default[0],w1:BRAID.default[1]});\n"
                 "STATES.forEach(function(a,i){var b=document.createElement('div');b.style.maxWidth=a[2];bSlot(i).appendChild(b);arcsBraid(b,BRAID,{w0:a[0],w1:a[1]});});") % (data, read("braid.js")),
    }


def outputs():
    p = payload(json.load(open(REC, encoding="utf-8")))
    return {SPEC: json.dumps(spec(p), indent=1, ensure_ascii=False) + "\n", FRAG: fragment(p)}, p


def self_test():
    outs, p = outputs()
    ids = {e[0] for e in p["events"]}
    assert all(a in ids and b in ids for a, b in p["links"]), "braid to a belief the payload dropped"
    assert len(p["commits"]) == len(p["receipts"]) == p["weeks"], "tempo arrays off the week grid"
    assert p["receipts"][0] is None and p["receipts"][p["first_receipt_week"]] is not None, "pre-ledger weeks drawn as counts"
    assert all(len(e) == 4 for e in p["events"]) and '"claim"' not in outs[FRAG], "belief text in the fragment"
    assert "—" not in outs[FRAG] and "—" not in outs[SPEC], "em-dash"
    assert "<li>" in floor(p), "empty no-JS floor"
    print("braided_lanes_build self-test: OK (%d beliefs, %d braids, %d weeks)" % (len(p["events"]), len(p["links"]), p["weeks"]))
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    outs, _ = outputs()
    if "--preview" in sys.argv:
        path = sys.argv[sys.argv.index("--preview") + 1]
        open(path, "w", encoding="utf-8").write(preview(outs[FRAG]))
        print("wrote", path)
        return 0
    if "--check" in sys.argv:
        stale = [os.path.relpath(f, ROOT) for f, t in outs.items() if not os.path.exists(f) or open(f, encoding="utf-8").read() != t]
        if stale:
            print("✖ stale: %s. fix: python3 scripts/braided_lanes_build.py" % ", ".join(stale), file=sys.stderr)
            return 1
        return 0
    for f, t in outs.items():
        open(f, "w", encoding="utf-8").write(t)
        print("wrote", os.path.relpath(f, ROOT))
    rc = subprocess.call([sys.executable, os.path.join(ROOT, "scripts/kit_specimen.py"), SPEC])
    return rc or subprocess.call([sys.executable, os.path.join(ROOT, "scripts/belief_log_emit.py")])


if __name__ == "__main__":
    sys.exit(main())
