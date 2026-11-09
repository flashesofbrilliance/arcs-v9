#!/usr/bin/env python3
"""proposal_lint.py: the honest-proposals checks over one engagement's text and rendered outputs.

Runs on every engagement whose record is schema engagement-record-v1 (v0 records are skipped).
Spec: runtime/specs/engagement-record-v0.md, section "v1: honest proposals". Four lints, plus a send gate:

  1. figures   no money, percent or "N hours/days/weeks" figure typed into a template or record text;
               every figure comes from a cite, so it has a source.
  2. sharing   no sharing-ban phrase in a client output; the agreement says "not legal" advice and "as is".
  3. leak      while the first step is unpaid, no figure at or above leak.ceiling_usd and no task-level
               bid sheet (three or more table rows carrying a price or hours) in a client output.
  4. voice     no em-dash, no first person plural (we, our, us) in a client output.
  send gate    (--send-ready) all of the above, outputs fresh, and counsel_review, gauntlet (0 open)
               and ex_ante set in the record.
  cap warning  any engagement (v0 or v1) whose investment.json shows unpaid hours past its cap gets a
               warning line (scripts/engagement_hours.py). It never fails the lint: free work is a choice.

  python3 scripts/proposal_lint.py                      # every v1 engagement
  python3 scripts/proposal_lint.py --dir <slug-dir>
  python3 scripts/proposal_lint.py --send-ready --dir <slug-dir>
  python3 scripts/proposal_lint.py --self-test

Read-only. Stdlib only. Client outputs are every out/*.md plus exported out/*.json; proposal.html is the
internal page and is not linted for voice or leak.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engagement_render as er  # noqa: E402

ROOT = er.ROOT
FIGURE = re.compile(r"\$\s?\d[\d,]*(\.\d+)?|\b\d+(\.\d+)?\s?%|\b\d+\s?(hours?|hrs?|days?|weeks?|months?)\b", re.I)
MONEY = re.compile(r"\$\s?(\d[\d,]*)(\.\d+)?")
HOURS = re.compile(r"\b\d+(\.\d+)?\s?(hours?|hrs?|h)\b", re.I)
BAN = re.compile(r"\b(may not|must not|do not|don't|cannot|can't|not to)\s+(be\s+)?(share|shared|forward|forwarded|"
                 r"distribute|distributed|disclose|disclosed|show|shown)\b", re.I)
PLURAL = re.compile(r"\b(we|We|our|Our|ours|Ours|us|we're|We're|we'll|We'll|we've|We've|let's|Let's)\b")
TEXT_KEYS = ("terms", "lists", "phases", "scenarios", "cold_read", "altitudes", "not_proven", "assumptions")


def load(eng_dir):
    with open(os.path.join(eng_dir, "engagement.json"), encoding="utf-8") as fh:
        return json.load(fh)


def client_outputs(eng_dir):
    out = {}
    for p in sorted(glob.glob(os.path.join(eng_dir, "out", "*.md")) + glob.glob(os.path.join(eng_dir, "out", "*.json"))):
        name = os.path.basename(p)
        if name == er.LOCK:
            continue
        text = open(p, encoding="utf-8").read()
        out[name] = re.sub(r"<!--.*?-->", "", text, flags=re.S)  # internal header comments are not client text
    return out


def strings(v, path):
    if isinstance(v, str):
        yield path, v
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from strings(x, f"{path}[{i}]")
    elif isinstance(v, dict):
        for k, x in v.items():
            if k in ("source", "test_that_would_decide", "status", "watch", "guard", "id"):
                continue
            yield from strings(x, f"{path}.{k}")


def lint_figures(eng_dir, rec):
    probs = []
    srcs = [(f"templates/{os.path.basename(t)}", open(t, encoding="utf-8").read())
            for t in sorted(glob.glob(os.path.join(eng_dir, "templates", "*.md.tpl")))]
    for key in TEXT_KEYS:
        srcs += list(strings(rec.get(key), key))
    for where, text in srcs:
        bare = er.CITE.sub("", text)
        for m in FIGURE.finditer(bare):
            probs.append(f"figures: {where}: {m.group(0)!r} is typed in; put it in a field with a source and cite it")
    return probs


def lint_sharing(outs):
    probs = []
    for name, text in outs.items():
        for m in BAN.finditer(text):
            probs.append(f"sharing: {name}: {m.group(0)!r} reads as a sharing ban; use the reliance term instead")
    agr = outs.get("agreement.md")
    if agr is None:
        probs.append("sharing: no out/agreement.md")
    else:
        low = agr.lower()
        if "not legal" not in low:
            probs.append("sharing: agreement.md does not say the work is opinion, not legal or compliance advice")
        if "as is" not in low:
            probs.append("sharing: agreement.md does not say delivered code or setup is provided as is")
    return probs


def lint_leak(rec, outs):
    phases = rec.get("phases") or [{}]
    if phases[0].get("paid"):
        return []
    ceiling = rec["leak"]["ceiling_usd"]
    probs = []
    for name, text in outs.items():
        big = sorted({m.group(0) for m in MONEY.finditer(text) if float(m.group(1).replace(",", "")) >= ceiling})
        if big:
            probs.append(f"leak: {name}: {', '.join(big)} at or above the {ceiling:,} ceiling before the first step is paid")
        rows = [ln for ln in text.splitlines() if ln.lstrip().startswith("|") and not re.fullmatch(r"\s*\|[\s|:-]*\|?\s*", ln)
                and (MONEY.search(ln) or HOURS.search(ln))]
        if len(rows) >= 3:
            probs.append(f"leak: {name}: {len(rows)} table rows carry a price or hours; that is a task-level bid sheet before the paid step")
    return probs


def lint_voice(outs):
    probs = []
    for name, text in outs.items():
        if "\u2014" in text:
            probs.append(f"voice: {name}: em-dash")
        words = sorted({m.group(0) for m in PLURAL.finditer(text)})
        if words:
            probs.append(f"voice: {name}: first person plural {', '.join(words)}; write as I, to you")
    return probs


def send_gate(eng_dir, rec):
    probs = [f"send: {p.strip()}" for p in er.check(eng_dir) if not p.startswith("  fix:")]
    if not rec.get("counsel_review"):
        probs.append("send: counsel_review not set; a lawyer reads the agreement template once before it goes out")
    g = rec.get("gauntlet")
    if not g:
        probs.append("send: gauntlet not run (counterpart-gauntlet, proposal seats)")
    elif g.get("open_findings"):
        probs.append(f"send: gauntlet has {g['open_findings']} open finding(s)")
    if not rec.get("ex_ante"):
        probs.append("send: ex_ante not written; predict the reply, with odds and their basis, before sending")
    return probs


def cap_warning(eng_dir):
    """A warning line when unpaid hours pass the engagement's discovery cap, else None."""
    if not os.path.exists(os.path.join(eng_dir, "investment.json")):
        return None
    import engagement_hours as eh
    text, over = eh.report(eng_dir)
    return f"warn: {text.splitlines()[0]}; free work past the cap is a choice, make it on purpose" if over else None


def lint(eng_dir, send_ready=False):
    rec = load(eng_dir)
    if rec.get("schema") != er.SCHEMA_V1:
        return None
    errs = er.validate(rec)
    if errs:
        return [f"record: {e}" for e in errs]
    outs = client_outputs(eng_dir)
    probs = lint_figures(eng_dir, rec) + lint_sharing(outs) + lint_leak(rec, outs) + lint_voice(outs)
    if send_ready:
        probs += send_gate(eng_dir, rec)
    return probs


# ---------------------------------------------------------------- self-test

EXAMPLE = os.path.join(ROOT, "_ARTIFACTS", "engagements", "example-fictional")


def self_test() -> int:
    tmp = tempfile.mkdtemp(prefix="proposal-lint-")
    eng = os.path.join(tmp, "eng")
    try:
        shutil.copytree(EXAMPLE, eng)
        recp = os.path.join(eng, "engagement.json")
        base = json.load(open(recp, encoding="utf-8"))

        def reset(fn=None, render=True):
            r = json.loads(json.dumps(base))
            if fn:
                fn(r)
            json.dump(r, open(recp, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
            if render:
                er.write(eng)

        def tpl_append(name, line):
            with open(os.path.join(eng, "templates", name), "a", encoding="utf-8") as fh:
                fh.write(line)

        reset()
        assert lint(eng) == [], f"the example must pass: {lint(eng)}"
        assert any("counsel_review" in p for p in lint(eng, send_ready=True)), "the example is not send-ready until counsel reads it"

        cases = []
        def case(label, want, fn=None, tpl=None):
            cases.append((label, want, fn, tpl))
        case("typed figure", "figures:", tpl=("reply.md.tpl", "\nIt costs $500 more.\n"))
        case("sharing ban", "sharing ban", tpl=("reply.md.tpl", "\nThis may not be shared outside your team.\n"))
        case("leak ceiling", "ceiling", tpl=("reply.md.tpl", "\nThe full build is about {{leak_probe}}.\n"),
             fn=lambda r: r["fields"].update(leak_probe={"kind": "money", "label": "probe", "value": 40000, "history": [],
                                                          "source": {"kind": "judgment", "ref": "self-test", "date": "2026-11-08"}}))
        case("bid sheet", "bid sheet", tpl=("exhibit-a.md.tpl", "\n| Task | Hours |\n|---|---|\n| a | {{hours_step1}} hours |\n| b | {{hours_step1}} hours |\n| c | {{hours_step1}} hours |\n"))
        case("plural voice", "first person plural", tpl=("reply.md.tpl", "\nWe can start soon.\n"))
        case("no as-is", "as is", fn=lambda r: [t.update(title=t["title"].replace("as is", "with care"), body=t["body"].replace("as is", "with care")) for t in r["terms"]])
        case("quote, not range", "money_range", fn=lambda r: r["phases"][1].update(fee="{{fee_step1}}"))
        case("range, no assumption", "assumptions[]", fn=lambda r: r["phases"][1].update(assumptions=[]))
        case("empty not_proven", "not_proven", fn=lambda r: r.update(not_proven=[]))
        case("no reliance term", "reliance", fn=lambda r: r.update(terms=[t for t in r["terms"] if t["id"] != "reliance"]))
        case("close before ex_ante", "close without ex_ante",
             fn=lambda r: (r.pop("ex_ante", None), r.update(close={"what_happened": "x", "held": True, "date": "2026-11-09"})))
        for label, want, fn, tpl in cases:
            shutil.rmtree(eng)
            shutil.copytree(EXAMPLE, eng)
            if tpl:
                tpl_append(*tpl)
            try:
                reset(fn)
            except er.RecordError:
                pass  # an invalid record refuses to render; lint() reports why
            p = lint(eng)
            assert p and any(want in x for x in p), (label, want, p)
        shutil.rmtree(eng)
        shutil.copytree(EXAMPLE, eng)
        tpl_append("reply.md.tpl", "\nThe full build is about {{leak_probe}}.\n")
        def paid(r):
            cases[2][2](r)
            r["phases"][0].update(paid=True)
        reset(paid)
        assert not any(x.startswith("leak") for x in lint(eng)), "after the first step is paid the leak check stands down"
        capd = os.path.join(tmp, "capcase")
        os.makedirs(capd)
        json.dump({"cap_hours": 1, "paid_from": None, "work_paths": ["no/such/path"],
                   "calls": [{"date": "2026-11-01", "minutes": 120, "source": "t", "basis": "measured"}]},
                  open(os.path.join(capd, "investment.json"), "w"))
        assert (cap_warning(capd) or "").startswith("warn: capcase: unpaid 2.0"), cap_warning(capd)
        assert cap_warning(EXAMPLE) is None, "no investment.json, no warning"
        print(f"proposal_lint self-test: OK (example passes, not send-ready without counsel, {len(cases)} bad cases each refused, leak stands down once paid, cap warning fires past the cap)")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dir", help="one engagement folder (default: every v1 engagement)")
    ap.add_argument("--send-ready", action="store_true", help="also require fresh outputs, counsel review, a clean gauntlet and an ex-ante")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    dirs = [os.path.abspath(a.dir)] if a.dir else sorted(os.path.dirname(p) for p in glob.glob(er.ENG_GLOB))
    bad, ran = 0, 0
    for d in dirs:
        w = cap_warning(d)
        if w:
            print(f"{os.path.relpath(d, ROOT)}: {w}", file=sys.stderr)
        probs = lint(d, a.send_ready)
        if probs is None:
            continue
        ran += 1
        rel = os.path.relpath(d, ROOT)
        for p in probs:
            print(f"{rel}: {p}", file=sys.stderr)
        bad += bool(probs)
    word = "send-ready" if a.send_ready else "clean"
    print(f"proposal_lint: {ran - bad}/{ran} v1 engagement(s) {word}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
