#!/usr/bin/env python3
"""strata_explorer_build: kit organism 69 (strata explorer) and its embeddable fragment, from the event table.

In:  runtime/specs/shipped-record.json   (scripts/shipped_record_emit.py; every event and link cited there)
     src/ui-kit/strata-explorer/strata.css + strata.js   (the organism's source)
Out: src/ui-kit/specimens/strata-explorer.json  -> scripts/kit_specimen.py -> src/ui-kit/recoil-report/69-strata-explorer.html
     src/ui-kit/strata-explorer/shipped-fragment.html   (style + no-JS floor + data + script, for a page to inline)
     --preview PATH writes the fragment under the kit tokens as a standalone page for page_gate (not committed)

Headline events (fidelity 1): live services, rank-1 milestones, gold-seam reversals, ADRs a reversal led to,
Tao mints that are not the book backfill, and NFTT posts that minted Tao or that a milestone cites.

  python3 scripts/strata_explorer_build.py           write both outputs and rebuild the specimen page
  python3 scripts/strata_explorer_build.py --check   exit 1 if either output is stale
  python3 scripts/strata_explorer_build.py --preview /tmp/strata.html   page for page_gate
  python3 scripts/strata_explorer_build.py --self-test
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
SRC = os.path.join(ROOT, "src/ui-kit/strata-explorer")
SPEC = os.path.join(ROOT, "src/ui-kit/specimens/strata-explorer.json")
FRAG = os.path.join(ROOT, "src/ui-kit/strata-explorer/shipped-fragment.html")
KIT = os.path.join(ROOT, "src/ui-kit/recoil-report")
DAY0 = "2026-04-09"
LANES = [("service", "Live services", "Services"), ("milestone", "Build milestones", "Milestones"),
         ("belief", "Beliefs I reversed", "Beliefs"),
         ("invention", "Decision records (ADRs, architecture decision records) a reversal led to", "Records"),
         ("nftt", "Notes from the Trenches (NFTT), my field-note posts", "Posts"),
         ("tao", "Tao of ARCS proverbs, one-line lessons", "Proverbs")]
# Ledger scope words, in plain English for a reader outside the repo.
SCOPE = {"infra": "an infrastructure", "canon": "a design-canon", "gauntlet": "a pressure-test", "process": "a process",
         "deploy": "a deployment", "security": "a security", "surface": "a public-page", "recoil": "a call-review"}
URLS = {"milestone": "https://status.arcs.care", "belief": "https://status.arcs.care/beliefs"}


def fmt(date):
    d = dt.date.fromisoformat(date)
    return "%d %s %d" % (d.day, d.strftime("%b"), d.year)


def day(date):
    return (dt.date.fromisoformat(date) - dt.date.fromisoformat(DAY0)).days


def payload(rec):
    lane_ix = {k: i for i, (k, _, _) in enumerate(LANES)}
    linked = {l["from"] for l in rec["links"]} | {l["to"] for l in rec["links"]}
    rows, tao_key, tao = [], {}, {}
    for e in rec["events"]:
        if e["lane"] == "tao":  # one dot per mint date; backfill and real mints kept apart
            k = "tao-%s%s" % (e["date"], "-backfill" if e.get("backfill") else "")
            tao_key[e["id"]] = k
            t = tao.setdefault(k, {"date": e["date"], "n": 0, "backfill": e.get("backfill")})
            t["n"] += e["count"]
            continue
        lane = e["lane"]
        head = {"service": 1, "milestone": int(e.get("rank") == 1), "belief": int(bool(e.get("gold"))),
                "invention": 1, "nftt": int(e["id"] in linked)}[lane]
        label = e["label"] if lane != "belief" else "%s: %s belief, reversed" % (e["id"], SCOPE.get(e["scope"], "a"))
        rows.append([e["id"], lane_ix[lane], day(e["date"]), label, int(bool(e.get("gold"))), 1, head,
                     e.get("url") or URLS.get(lane, "")])
    for k, t in tao.items():
        noun = "proverb" if t["n"] == 1 else "proverbs"
        label = ("%d %s backfilled from the Tao book" if t["backfill"] else "%d Tao %s minted") % (t["n"], noun)
        rows.append([k, lane_ix["tao"], day(t["date"]), label, 0, t["n"], int(not t["backfill"]), ""])
    rows.sort(key=lambda r: (r[2], r[1], r[0]))
    links = sorted({(tao_key.get(l["from"], l["from"]), tao_key.get(l["to"], l["to"]), l["kind"]) for l in rec["links"]})
    max_day = max(r[2] for r in rows)
    return {
        "day0": DAY0, "max_day": max_day,
        "lanes": [{"key": k, "label": lab, "short": s} for k, lab, s in LANES],
        "events": rows, "links": [list(l) for l in links],
        "source": "Source: the build record, %s to %s. %d events and %d links, each cited; %d links left out because nothing cites them."
                  % (fmt(DAY0), fmt(rec["events"][-1]["date"]), len(rec["events"]), len(rec["links"]), len(rec["unconfirmed"])),
    }


def floor(p):
    """The no-JS floor: services and rank-1 milestones as a dated list of links."""
    lis = []
    for r in p["events"]:
        if r[1] in (0, 1) and r[6]:
            d = (dt.date.fromisoformat(DAY0) + dt.timedelta(days=r[2])).isoformat()
            lab = '<a href="%s">%s</a>' % (html.escape(r[7]), html.escape(r[3])) if r[7] else html.escape(r[3])
            lis.append('<li><span class="st-meta">%s</span> %s</li>' % (d, lab))
    return '<ul class="st-floor">%s</ul>' % "".join(lis)


def read(name):
    return open(os.path.join(SRC, name), encoding="utf-8").read()


def fragment(p):
    data = json.dumps(p, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return ("<!-- generated by scripts/strata_explorer_build.py from runtime/specs/shipped-record.json; kit organism 69. "
            "Inline after the kit tokens (_tokens.css, _tokens-light.css). Do not hand-edit. -->\n"
            "<style>\n%s</style>\n<div class=\"strata\" data-strata>%s</div>\n"
            "<script type=\"application/json\" data-strata-data>%s</script>\n"
            "<script>\n%s(function(){var h=document.querySelector('[data-strata]'),d=document.querySelector('[data-strata-data]');"
            "if(h&&d)arcsStrata(h,JSON.parse(d.textContent));})();\n</script>\n") % (read("strata.css"), floor(p), data, read("strata.js"))


def preview(frag):
    """A standalone page that inlines the kit tokens and the fragment, so page_gate can judge the fragment itself.
    Inlined, not linked: a linked token file makes file:// requests that page_gate's full matrix counts as errors.
    The token file's own comments carry two em-dashes (its sentinel header); they are CSS comments and never render."""
    tok = "".join(open(os.path.join(KIT, f), encoding="utf-8").read() for f in ("_tokens.css", "_tokens-light.css"))
    return ("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n<title>Shipped this year: strata preview</title>\n"
            "<!-- generated by scripts/strata_explorer_build.py; preview of shipped-fragment.html under the kit tokens -->\n"
            "<style>\n%s\n* { box-sizing: border-box; margin: 0; padding: 0; }\n"
            "body { background: var(--bg); color: var(--text); font-family: var(--ds-font-sans); font-size: var(--fs-body); line-height: 1.6; padding: 32px 16px 64px; }\n"
            "main { max-width: 960px; margin: 0 auto; display: flex; flex-direction: column; gap: 16px; }\n"
            "h1 { font-family: var(--ds-font-display); font-size: var(--fs-headline); font-weight: 500; }\n</style>\n</head>\n<body>\n<main>\n"
            "<h1>Shipped this year</h1>\n%s</main>\n</body>\n</html>\n") % (tok, frag)


def spec(p):
    data = json.dumps(p, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return {
        "number": "69", "name": "Strata Explorer", "slug": "strata-explorer", "layer": "Organism",
        "job": "Walk shipped work since April 2026 as stacked planes: services on top, then milestones, reversed beliefs, the inventions they led to, the posts written up and the proverbs minted, every link cited.",
        "anatomy": [
            {"part": "Planes", "role": "One isometric plane per layer, time running left to right and slightly down", "token": "`surface`, `border`"},
            {"part": "Events", "role": "A dot per cited event in the layer colour; a gold ring marks a reversal that hardened into doctrine", "token": "`cyan`, `text`, `red`, `violet`, `green`, `magenta`, `gold`"},
            {"part": "Threads", "role": "At full fidelity, a curve per cited link; gold when one reversal repaired another", "token": "`cyan`, `gold`"},
            {"part": "Grain band", "role": "A hatched band over the last 30 days of a layer that holds fewer than 3 events, with n printed", "token": "`text-secondary`"},
            {"part": "Controls", "role": "Walk time, Depth and Fidelity as native range inputs, each with its value printed", "token": "`text-secondary`, `cyan`"},
            {"part": "Readout", "role": "A live region listing the 7 days to the scrub point, as links to the evidence", "token": "`text`, `text-secondary`"},
        ],
        "states": [
            {"name": "Today, headline", "args": [p["max_day"], 6, 1, "100%"], "note": "The default: every layer, headline events only."},
            {"name": "Mid-June, every link", "args": [day("2026-06-30"), 6, 2, "100%"], "note": "Walked back in time: thin layers fall to grain and print n."},
            {"name": "Phone, three layers", "args": [p["max_day"], 3, 0, "20rem"], "note": "Counts by month; labels move above each plane under 520px."},
        ],
        "use_when": ["A reader should see how shipped work, being wrong and the writing about it connect over a year.",
                     "Every event and link has a source a reader could check."],
        "avoid_when": ["Do not feed it events without a citation; uncited links belong in the table's unconfirmed list, not on a thread.",
                       "Not for a current-state snapshot such as a risk register: it needs dates to mean anything."],
        "data": [
            {"field": "lanes[]", "type": "{key, label, short}", "required": True, "note": "Top to bottom; Depth shows the first N."},
            {"field": "events[]", "type": "[id, lane, day, label, gold, count, headline, url]", "required": True, "note": "`day` counts from `day0`; `headline` picks fidelity 1."},
            {"field": "links[]", "type": "[from, to, kind]", "required": True, "note": "`repaired-by` draws gold."},
            {"field": "source", "type": "string", "required": True, "note": "Printed under the key."},
        ],
        "access": ["Each control is a native range input with a visible label and its value in an output, so arrow keys, Home and End work.",
                   "The picture has a title that states the date, the event count and the layer count; the readout lists the same week as links.",
                   "Nothing animates, so reduced motion needs no branch. Gold seams also say so in words in the readout.",
                   "Without script the host keeps a dated list of services and headline milestones."],
        "built_from": [{"name": "Kit tokens (atoms)", "href": "_tokens.css"}, {"name": "37 Fidelity Grain", "href": "37-fidelity-grain.html"},
                       {"name": "64 Kintsugi Seam", "href": "64-kintsugi-seam.html"}],
        "used_by": [{"name": "Gravity candidate page, Shipped this year (proposed; wired by its owning session)"}],
        "gates": ["`strata_explorer_build.py --check` (in scripts): the spec and fragment match the event table.",
                  "`shipped_record_emit.py --self-test`: no uncited event or link, no belief text leaked.",
                  "`kit_specimen.py --check` and `kit_primitive_sync.py --check`.",
                  "`artifact_wrap_lint.py` and `page_gate.py` on every page that carries it; sweep 360 to 1440, including 700 to 1000."],
        "links": ["_tokens-light.css", "_kit-sr.css"],
        "css": read("strata.css"),
        "demo": ("var STRATA=%s;\n%s\nfunction sSlot(i){return i===undefined?document.querySelector('[data-stage]'):document.querySelector('[data-state=\"'+i+'\"]');}\n"
                 "arcsStrata(sSlot(),STRATA);\nSTATES.forEach(function(a,i){var b=document.createElement('div');b.style.maxWidth=a[3];sSlot(i).appendChild(b);arcsStrata(b,STRATA,{t:a[0],depth:a[1],fidelity:a[2]});});")
                % (data, read("strata.js")),
    }


def outputs():
    p = payload(json.load(open(REC, encoding="utf-8")))
    frag = fragment(p)
    return {SPEC: json.dumps(spec(p), indent=1, ensure_ascii=False) + "\n", FRAG: frag}, p


def self_test():
    outs, p = outputs()
    ids = {r[0] for r in p["events"]}
    assert all(a in ids and b in ids for a, b, _ in p["links"]), "link to an event the payload dropped"
    assert any(r[0].endswith("-backfill") for r in p["events"]), "Tao backfill not kept apart"
    assert "claim" not in outs[FRAG], "belief claim text in the fragment"
    assert "—" not in outs[FRAG] and "—" not in outs[SPEC], "em-dash"
    assert "<li>" in floor(p), "empty no-JS floor"
    print("strata_explorer_build self-test: OK (%d events, %d links)" % (len(p["events"]), len(p["links"])))
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
            print("✖ stale: %s. fix: python3 scripts/strata_explorer_build.py" % ", ".join(stale), file=sys.stderr)
            return 1
        return 0
    for f, t in outs.items():
        os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f, "w", encoding="utf-8").write(t)
        print("wrote", os.path.relpath(f, ROOT))
    return subprocess.call([sys.executable, os.path.join(ROOT, "scripts/kit_specimen.py"), SPEC])


if __name__ == "__main__":
    sys.exit(main())
