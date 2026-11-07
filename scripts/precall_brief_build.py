#!/usr/bin/env python3
"""precall_brief_build: render a pre-call brief page from the precall-brief template plus a data file.

The page is rebuilt from three parts, never hand-edited:
  tokens    src/ui-kit/recoil-report/_tokens.css, inlined verbatim (sentinel line kept)
  template  src/ui-kit/precall-brief/page.tpl (renderer + page layer, no counterpart content)
  data      a JSON file valid against src/ui-kit/precall-brief/brief.schema.json

The committed example (_ARTIFACTS/precall-brief/example.json) uses a fictional counterpart. Real briefs
name real people: keep their data and pages in _ARTIFACTS/precall-brief/private/ (gitignored) or the
scratchpad, and publish them as private Artifacts.

  python3 scripts/precall_brief_build.py DATA.json [-o OUT.html]   validate and write the page (default: DATA with .html)
  python3 scripts/precall_brief_build.py DATA.json --gate          also run artifact_wrap_lint + page_gate --matrix full
  python3 scripts/precall_brief_build.py --check                   exit 1 if the example is invalid or its page differs
  python3 scripts/precall_brief_build.py --self-test               prove the validator rejects each bad shape

The written page is a full document (doctype, lang, charset, viewport prepended to the template), so the file the
gates pass is the file that gets published.
Stdlib only.
"""
import argparse, copy, html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS = os.path.join(ROOT, "src/ui-kit/recoil-report/_tokens.css")
TDIR = os.path.join(ROOT, "src/ui-kit/precall-brief")
TEMPLATE = os.path.join(TDIR, "page.tpl")
SCHEMA = os.path.join(TDIR, "brief.schema.json")
EXAMPLE = os.path.join(ROOT, "_ARTIFACTS/precall-brief/example.json")
SKELETON = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>\n'
SECTIONS = ["trip", "ask", "rule", "say"]
LANES = ["before", "opening", "interview", "debrief"]
GATES = ["intake", "before-send", "before-booking", "on-call", "silence"]
TIERS = {"T0": "self-asserted", "T1": "company-published", "T2": "domain-authenticated", "T3": "trusted mutual", "T4": "company-confirmed"}


def _resolve(s, root):
    while "$ref" in s:
        node = root
        for part in s["$ref"].lstrip("#/").split("/"):
            node = node[part]
        s = node
    return s


TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "integer": int, "number": (int, float)}


def _check(v, s, root, path, errs):
    """Validate v against the JSON Schema subset the brief schema uses; append messages to errs."""
    s = _resolve(s, root)
    if "oneOf" in s:
        fits = [b for b in s["oneOf"] if not _errs(v, b, root, path)]
        if len(fits) != 1:
            kind = v.get("type") if isinstance(v, dict) else type(v).__name__
            best = min((_errs(v, b, root, path) for b in s["oneOf"]), key=len)
            errs.extend(best if best else [f"{path}: matches {len(fits)} shapes, want exactly one (type {kind!r})"])
        return
    t = s.get("type")
    if t:
        ok = isinstance(v, TYPES[t]) and not (t in ("integer", "number") and isinstance(v, bool))
        if not ok:
            errs.append(f"{path}: want {t}, got {type(v).__name__}"); return
    if "const" in s and v != s["const"]:
        errs.append(f"{path}: want {s['const']!r}, got {v!r}")
    if "enum" in s and v not in s["enum"]:
        errs.append(f"{path}: {v!r} not in {s['enum']}")
    if isinstance(v, str) and "pattern" in s and not re.search(s["pattern"], v):
        errs.append(f"{path}: {v[:60]!r} does not match {s['pattern']}")
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if "minimum" in s and v < s["minimum"]: errs.append(f"{path}: {v} < {s['minimum']}")
        if "maximum" in s and v > s["maximum"]: errs.append(f"{path}: {v} > {s['maximum']}")
    if isinstance(v, dict):
        for k in s.get("required", []):
            if k not in v: errs.append(f"{path}: missing {k!r}")
        props = s.get("properties", {})
        for k, x in v.items():
            if k in props: _check(x, props[k], root, f"{path}.{k}", errs)
            elif s.get("additionalProperties") is False: errs.append(f"{path}: unknown key {k!r}")
    if isinstance(v, list):
        if "minItems" in s and len(v) < s["minItems"]: errs.append(f"{path}: {len(v)} items < {s['minItems']}")
        if "maxItems" in s and len(v) > s["maxItems"]: errs.append(f"{path}: {len(v)} items > {s['maxItems']}")
        if "items" in s:
            for i, x in enumerate(v): _check(x, s["items"], root, f"{path}[{i}]", errs)


def _errs(v, s, root, path):
    e = []; _check(v, s, root, path, e); return e


def slug(s):
    return "c-" + re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", s.lower()))


def validate(d):
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    errs = _errs(d, schema, schema, "$")
    if errs:
        return errs
    if [s["id"] for s in d["cockpit"]["sections"]] != SECTIONS:
        errs.append(f"cockpit.sections: ids must be {SECTIONS} in that order (stop-loss order)")
    if [l["id"] for l in d["lanes"]] != LANES:
        errs.append(f"lanes: ids must be {LANES} in that order (call order)")
    titles = [c["title"] for l in d["lanes"] for c in l["cards"]]
    seen = {}
    for t in titles:
        if slug(t) in seen: errs.append(f"card titles {seen[slug(t)]!r} and {t!r} share an anchor")
        seen[slug(t)] = t
    for s in d["cockpit"]["sections"]:
        for it in s["items"]:
            if "link" in it and slug(it["link"]) not in seen:
                errs.append(f"cockpit {s['id']}/{it['h']!r}: link {it['link']!r} names no card")
    q = d["qualification"]
    if [c["gate"] for c in q["checks"]] != GATES:
        errs.append(f"qualification.checks: gates must be {GATES} in that order")
    if q["verdict"] == "go" and q["tier"] < "T2":
        errs.append(f"qualification: verdict go needs tier T2 or higher (got {q['tier']}, {TIERS[q['tier']]}); hold until a company-domain email or invite arrives")
    if q["verdict"] == "go" and any(c["status"] == "fail" for c in q["checks"]):
        errs.append("qualification: verdict go with a failed check; a failed gate means hold or stop")
    if not any(c["type"] == "exante" for l in d["lanes"] for c in l["cards"]):
        errs.append("no exante card: the predictions table is required")
    if d["start"] >= d["end"]:
        errs.append("start must be before end")
    raw = json.dumps(d, ensure_ascii=False)
    if "—" in raw:
        errs.append("em-dash in the data (house rule: none; use a colon, comma or period)")
    return errs


def qualification_card(q):
    rows = [["Trust tier", f"{q['tier']}: {TIERS[q['tier']]}"], ["Verdict", q["verdict"].upper()]]
    rows += [[c["gate"], f"{c['status'].upper()}. {c['evidence']}"] for c in q["checks"]]
    return {"type": "kv", "title": "Qualification gate", "chip": "stated", "wide": True, "rows": rows}


def render(d):
    d = copy.deepcopy(d)
    d["lanes"][0]["cards"].insert(0, qualification_card(d.pop("qualification")))
    data = json.dumps(d, ensure_ascii=False, separators=(", ", ": ")).replace("</", "<\\/")
    out = open(TEMPLATE, encoding="utf-8").read()
    out = out.replace("/*@@KIT_TOKENS@@*/", open(TOKENS, encoding="utf-8").read().rstrip("\n"))
    out = out.replace("@@TITLE@@", html.escape(d["title"]))
    return SKELETON + out.replace("@@BRIEF_DATA@@", data) + "</body></html>\n"


def gate(f):
    rc = 0
    for cmd in (["python3", "scripts/artifact_wrap_lint.py", f], ["python3", "scripts/page_gate.py", "--matrix", "full", f]):
        print("$", " ".join(cmd[1:]), flush=True)
        rc |= subprocess.call(cmd, cwd=ROOT)
    return rc


def load(path):
    d = json.load(open(path, encoding="utf-8"))
    errs = validate(d)
    if errs:
        print(f"✖ {os.path.relpath(path, ROOT)} is not a valid brief:", file=sys.stderr)
        for e in errs: print("  " + e, file=sys.stderr)
        sys.exit(1)
    return d


def self_test():
    good = json.load(open(EXAMPLE, encoding="utf-8"))
    assert not validate(good), validate(good)
    def bad(label, mut, needle):
        d = copy.deepcopy(good); mut(d); e = validate(d)
        assert any(needle in x for x in e), f"{label}: expected {needle!r} in {e}"
        print(f"  ok  {label}")
    bad("section order", lambda d: d["cockpit"]["sections"].reverse(), "stop-loss order")
    bad("lane order", lambda d: d["lanes"].reverse(), "call order")
    bad("bad chip", lambda d: d["lanes"][0]["cards"][0].update(chip="likely"), "not in")
    bad("unlabeled basis", lambda d: next(c for l in d["lanes"] for c in l["cards"] if c["type"] == "exante")["items"][0].update(basis="gut feel"), "does not match")
    bad("p out of range", lambda d: next(c for l in d["lanes"] for c in l["cards"] if c["type"] == "exante")["items"][0].update(p=1.4), "> 1")
    bad("dangling link", lambda d: d["cockpit"]["sections"][0]["items"][0].update(link="No such card"), "names no card")
    bad("unknown key", lambda d: d.update(colour="red"), "unknown key")
    bad("em-dash", lambda d: d.update(sub=d["sub"] + " — x"), "em-dash")
    bad("missing tripwires", lambda d: d["cockpit"]["sections"][0].update(items=[]), "items < 1")
    bad("missing qualification", lambda d: d.pop("qualification"), "qualification")
    bad("go below T2", lambda d: d["qualification"].update(tier="T0", verdict="go"), "needs tier T2")
    bad("go with a failed gate", lambda d: d["qualification"]["checks"][0].update(status="fail"), "failed check")
    bad("gate order", lambda d: d["qualification"]["checks"].reverse(), "in that order")
    print("self-test passed")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("data", nargs="?")
    ap.add_argument("-o", "--out")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.check:
        page = render(load(EXAMPLE)); built = EXAMPLE[:-5] + ".html"
        if not os.path.exists(built) or open(built, encoding="utf-8").read() != page:
            print(f"✖ {os.path.relpath(built, ROOT)} differs from its data; run python3 scripts/precall_brief_build.py {os.path.relpath(EXAMPLE, ROOT)}", file=sys.stderr)
            return 1
        print("precall-brief: example valid and current"); return 0
    if not a.data:
        ap.error("give a data file, --check or --self-test")
    page = render(load(a.data))
    out = a.out or re.sub(r"\.json$", "", a.data) + ".html"
    open(out, "w", encoding="utf-8").write(page)
    print(f"wrote {out} ({len(page.encode())} bytes)")
    return gate(os.path.abspath(out)) if a.gate else 0


if __name__ == "__main__":
    sys.exit(main())
