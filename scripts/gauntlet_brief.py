#!/usr/bin/env python3
"""gauntlet_brief.py: one page shape for every counterpart gauntlet.

The counterpart-gauntlet workflow (.claude/workflows/counterpart-gauntlet.js) returns
{counterpart, facet_count, raw_findings, synthesis:{verified, rejected_overflags, keep_dont_touch, verdict}}.
This script turns that result into tabbed-brief data (scripts/tabbed_brief_build.py renders it with the kit),
saves the run in the repo, and adds a row to the gauntlet ledger so the run is not lost.

  python3 scripts/gauntlet_brief.py ingest OUTPUT --slug SLUG [--run-id wf_...] [--context CTX.json] [--subject TEXT]
      OUTPUT: the workflow's task output file, or a saved result JSON.
      Writes _ARTIFACTS/gauntlets/<date>-<slug>/{gauntlet.json, brief.json}, appends one row to
      _STATE/gauntlet-runs.jsonl (skipped if the run_id is already there), then prints the render command.
  python3 scripts/gauntlet_brief.py brief RESULT.json [--context CTX.json] -o BRIEF.json
      Data only: no save, no ledger row.
  python3 scripts/gauntlet_brief.py --self-test

Render (internal; counterpart findings never go to public/):
  python3 scripts/tabbed_brief_build.py _ARTIFACTS/gauntlets/<dir>/brief.json --artifact OUT.html

CTX.json (all optional): run_id, ts, subject, headline [2 lines], lede [lines], meta {prepared_for, from},
  status {"<rank>": "Fixed" | "Kept out" | "Open" | ...}, sections [extra overview folds, placed after the verdict],
  tabs [extra tabs, placed before Findings], findings_lede.
Status "Fixed" or "Kept out" renders cyan (a fact you can check); open breaks render gold (judgment); the rest plain.
Stdlib only.
"""
import argparse, datetime, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "_STATE", "gauntlet-runs.jsonl")
OUTDIR = os.path.join(ROOT, "_ARTIFACTS", "gauntlets")
SEV_GROUPS = [("Pathogens and breaks, before any send", ("pathogen", "break")), ("Cracks", ("crack",)), ("Nits", ("nit",))]
CHECKED = ("Fixed", "Kept out")


def clean(s):
    """No em-dashes on ARCS pages; no markdown bold inside chips and cells."""
    return re.sub(r"\s*—\s*", ", ", s or "").replace("**", "").strip()


def short(s, n):
    s = clean(s)
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "..."


def load_result(path):
    """Accept the workflow task output (text with a JSON envelope), the envelope, or the bare result."""
    t = open(path, encoding="utf-8").read()
    d = json.loads(t[t.find("{"):t.rfind("}") + 1])
    d = d.get("result", d)
    if "synthesis" not in d:
        raise SystemExit("gauntlet_brief: %s has no synthesis; is it a counterpart-gauntlet result?" % path)
    return d


def finding_row(f, status):
    st = status.get(str(f.get("rank")))
    chip = "#%s %s" % (f.get("rank"), st) if st else "#%s" % f.get("rank")
    tone = "cyan" if st in CHECKED else ("gold" if f.get("severity") in ("pathogen", "break") else "plain")
    signal = short(clean(f.get("surface")).split(":")[0].split(" (")[0], 64)
    text = "%s Fix: %s" % (clean(f.get("issue")), clean(f.get("fix")))
    q = clean(f.get("quote")).split()
    if q:  # quotes stay short: the counterpart's words are evidence, not content to republish
        text = '"%s%s" %s' % (" ".join(q[:14]), "..." if len(q) > 14 else "", text)
    return {"chip": chip, "tone": tone, "signal": signal or "Finding", "text": text}


def brief(res, ctx=None):
    ctx = ctx or {}
    syn = res["synthesis"]
    V = syn.get("verified", [])
    status = {str(k): v for k, v in (ctx.get("status") or {}).items()}
    groups = []
    for label, sevs in SEV_GROUPS:
        rows = [finding_row(f, status) for f in V if f.get("severity") in sevs]
        if rows:
            groups.append({"label": label, "judgment": True, "rows": rows})
    who = clean(res.get("counterpart", "the counterpart")).split(" (")[0]
    fixed = sum(1 for v in status.values() if v in CHECKED)
    keep, rej = syn.get("keep_dont_touch", []), syn.get("rejected_overflags", [])
    sections = [{"id": "verdict", "title": "Verdict", "tagline": "What %s would conclude." % who, "open": True,
                 "blocks": [{"type": "callout", "lead": "Read", "text": clean(syn.get("verdict"))}]}]
    sections += ctx.get("sections", [])
    if keep:
        sections.append({"id": "keep", "title": "Keep as is", "tagline": "Lines the gauntlet says already land.", "open": False,
                         "blocks": [{"type": "list", "items": [clean(k) for k in keep]}]})
    if rej:
        sections.append({"id": "rejected", "title": "Rejected over-flags", "tagline": "Claims the verify pass threw out.", "open": False,
                         "blocks": [{"type": "table", "head": ["Claim", "Why rejected"], "rows": [[clean(r.get("claim")), clean(r.get("why_rejected"))] for r in rej]}]})
    findings_tab = {"id": "findings", "label": "Findings", "name": "%d facets read the work as %s" % (res.get("facet_count", 0), who),
                    "tagline": "%d findings" % len(V), "headline": "Ranked findings, with what has been fixed.",
                    "lede": ctx.get("findings_lede") or "Ranked by the verify pass. Cyan rows are fixed or kept out; gold rows are open breaks; plain rows are open cracks and nits.",
                    "units": [{"title": "Findings", "blocks": [{"type": "ledger", "groups": groups}]}] if groups else [{"title": "Findings", "blocks": [{"type": "p", "text": "No finding survived verification."}]}]}
    slug = re.sub(r"[^a-z0-9]+", "-", who.lower()).strip("-") or "gauntlet"
    return {
        "id": "gauntlet-" + slug, "doc_title": ctx.get("doc_title") or "Gauntlet: %s" % who, "storage_key": "gauntletTheme",
        "analytics": False, "horizons": [30, 90, 180], "pages": False, "default_theme": "light",
        "meta": ctx.get("meta") or {"prepared_for": "Zach Harris (internal)", "from": "Gauntlet run %s, %s" % (ctx.get("run_id", "?"), ctx.get("ts", "?"))},
        "overview": {
            "label": "Overview",
            "headline": ctx.get("headline") or ["%s read the work." % who, "Here is what held and what broke."],
            "byline": "Internal read, %s. Not for send." % ctx.get("ts", "undated"),
            "lede": ctx.get("lede") or ["Counterpart gauntlet: %d facets read the work as %s, then a verify pass rejected over-flags and ranked the rest." % (res.get("facet_count", 0), who)],
            "tiles": [
                {"v": str(res.get("facet_count", 0)), "k": "Facets", "note": "Versions of %s that read it" % who},
                {"v": str(len(V)), "k": "Findings verified", "note": "%d over-flags rejected" % len(rej)},
                {"v": str(fixed), "k": "Fixed or kept out", "note": "of %d findings" % len(V)},
                {"v": str(len(keep)), "k": "Keep as is", "note": "Lines not to touch"}],
            "sections": sections},
        "tabs": list(ctx.get("tabs", [])) + [findings_tab]}


def ledger_row(res, ctx, path):
    V = res["synthesis"].get("verified", [])
    sev = {}
    for f in V:
        sev[f.get("severity", "?")] = sev.get(f.get("severity", "?"), 0) + 1
    counts = ", ".join("%d %s" % (sev[k], k) for k in ("pathogen", "break", "crack", "nit") if k in sev)
    return {"run_id": ctx["run_id"], "kind": "counterpart-gauntlet", "ts": ctx["ts"], "subject": ctx.get("subject", ""),
            "counterpart": clean(res.get("counterpart", "")), "agents": res.get("facet_count", 0) + 1,
            "gates": "%d persona facets -> adversarial verify + synthesis" % res.get("facet_count", 0),
            "finding": "%d verified (%s), %d over-flags rejected." % (len(V), counts, len(res["synthesis"].get("rejected_overflags", []))),
            "brief": os.path.relpath(path, ROOT)}


def ingest(a):
    res = load_result(a.output)
    ctx = json.load(open(a.context, encoding="utf-8")) if a.context else {}
    ctx.setdefault("ts", datetime.date.today().isoformat())
    m = re.search(r"wf_[a-z0-9-]{6,}", open(a.output, encoding="utf-8").read())
    ctx.setdefault("run_id", m.group(0) if m else "manual-" + a.slug)
    if a.run_id:
        ctx["run_id"] = a.run_id
    if a.subject:
        ctx["subject"] = a.subject
    d = os.path.join(OUTDIR, "%s-%s" % (ctx["ts"], a.slug))
    os.makedirs(d, exist_ok=True)
    json.dump(res, open(os.path.join(d, "gauntlet.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if a.context:
        json.dump(ctx, open(os.path.join(d, "context.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    bp = os.path.join(d, "brief.json")
    json.dump(brief(res, ctx), open(bp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    seen = set()
    if os.path.exists(LEDGER):
        for line in open(LEDGER, encoding="utf-8"):
            if line.strip():
                seen.add(json.loads(line).get("run_id"))
    if ctx["run_id"] in seen:
        print("ledger: %s already logged; row not added" % ctx["run_id"])
    else:
        with open(LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps(ledger_row(res, ctx, bp), ensure_ascii=False) + "\n")
        print("ledger: appended %s to %s" % (ctx["run_id"], os.path.relpath(LEDGER, ROOT)))
    print("saved: %s" % os.path.relpath(d, ROOT))
    print("render: python3 scripts/tabbed_brief_build.py %s --artifact OUT.html" % os.path.relpath(bp, ROOT))
    print("then: python3 scripts/gauntlet_log_emit.py && python3 scripts/warroom_board.py  (refresh the two ledger views)")


def self_test():
    res = {"counterpart": "Ada Example (CTO, Acme)", "facet_count": 3, "raw_findings": [], "synthesis": {
        "verified": [
            {"rank": 1, "severity": "break", "surface": "Hero: the headline", "quote": "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen",
             "issue": "Claims too much — really.", "fix": "Say less.", "basis": "x"},
            {"rank": 2, "severity": "crack", "surface": "Footer", "issue": "Small.", "fix": "Trim.", "basis": "y"},
            {"rank": 3, "severity": "nit", "surface": "Tile (left)", "issue": "Tiny.", "fix": "Nudge.", "basis": "z"}],
        "rejected_overflags": [{"claim": "c", "why_rejected": "w"}], "keep_dont_touch": ["k1"], "verdict": "Holds, mostly."}}
    d = brief(res, {"status": {"1": "Fixed"}, "run_id": "wf_test", "ts": "2026-01-01"})
    rows = d["tabs"][-1]["units"][0]["blocks"][0]["groups"]
    assert [g["label"] for g in rows] == [x[0] for x in SEV_GROUPS], rows
    r1 = rows[0]["rows"][0]
    assert r1["chip"] == "#1 Fixed" and r1["tone"] == "cyan", r1
    assert "..." in r1["text"] and "sixteen" not in r1["text"], "quote not trimmed to 14 words"
    assert "—" not in json.dumps(d, ensure_ascii=False), "em-dash leaked"
    assert rows[1]["rows"][0]["tone"] == "plain" and d["overview"]["tiles"][2]["v"] == "1"
    assert d["default_theme"] == "light" and d["analytics"] is False
    row = ledger_row(res, {"run_id": "wf_test", "ts": "2026-01-01"}, os.path.join(OUTDIR, "x", "brief.json"))
    assert row["finding"].startswith("3 verified (1 break, 1 crack, 1 nit)") and row["kind"] == "counterpart-gauntlet", row
    print("gauntlet_brief self-test: OK")


def main():
    if "--self-test" in sys.argv:
        return self_test()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    i = sp.add_parser("ingest"); i.add_argument("output"); i.add_argument("--slug", required=True); i.add_argument("--context"); i.add_argument("--subject"); i.add_argument("--run-id", help="the workflow Run ID (wf_...); found in OUTPUT when present")
    b = sp.add_parser("brief"); b.add_argument("result"); b.add_argument("--context"); b.add_argument("-o", required=True)
    a = ap.parse_args()
    if a.cmd == "ingest":
        return ingest(a)
    ctx = json.load(open(a.context, encoding="utf-8")) if a.context else {}
    json.dump(brief(load_result(a.result), ctx), open(a.o, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %s" % a.o)


if __name__ == "__main__":
    main()
