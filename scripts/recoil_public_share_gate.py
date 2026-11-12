#!/usr/bin/env python3
"""Gate runtime/recoil/public-shares.json (backlog recoil-public-share-gate, 2026-11-12).

PR 2194 made a signed-out reader of /recoil/2026-10-29-gasmi see the internal war room minus
ten listed lines: the Granola transcript reference, [35:32] quotes, Questions and landmines,
the recruiter's name and the raw redaction_policy JSON. A strip list is not a gate. This one,
for every entry in the file:

  1. the entry must be a valid share (approved + gauntlet run reference), or the page refuses it;
  2. renders the signed-out payload with the REAL projection (src/lib/recoilPublicShare.ts via
     scripts/recoil_public_share_render.mjs), so the scan sees what the page serves;
  3. fails on any leak class: transcript or notetaker name, [m:ss] timestamp, a quote of
     someone on the call, a landmines block, a recruiter name taken from the SSOT, raw
     redaction_policy JSON, or internal-only keys/blocks in the payload;
  4. runs the counterpart voice check (scripts/voice_gate.py, what page_gate.py --counterpart
     adds) over the payload text.

The payload is a superset of the visible page (the client component receives all of it), so
scanning it is stricter than scanning rendered HTML. Layout checks (page_gate.py render) still
need a live page and are not run here.

Usage:
  python3 scripts/recoil_public_share_gate.py [--shares FILE] [--lib FILE.ts] [--staged]
  python3 scripts/recoil_public_share_gate.py --self-test
Exit: 0 clean, 1 leak or invalid entry, 2 cannot check (treated as unsafe).
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARES = "runtime/recoil/public-shares.json"
RENDER = os.path.join(ROOT, "scripts", "recoil_public_share_render.mjs")
LIB = "src/lib/recoilPublicShare.ts"

NOTETAKERS = r"\b(transcripts?|Granola|Fathom|Otter(?:\.ai)?|Fireflies|tl;dv|Gong|Chorus|Read\.ai|Zoom recording|notetaker)\b"
TIMESTAMP = r"\[\d{1,2}:\d{2}(?::\d{2})?\]"
LANDMINE = r"\blandmines?\b"
QUOTE_SPAN = r"[\"“]([^\"“”]{12,})[\"”]"
SPEECH = r"\b(said|says|told|asked|put it|in (?:his|her|their) words|verbatim)\b|\b[A-Z][a-z]+:\s*$"
INTERNAL_KEYS = ("redaction_policy", "_redaction_report", "beliefs", "insights", "next_steps",
                 "kinematic_series", "opportunity", "provenance", "closed_call", "external_sets", "gate")


def strings(v, path="$"):
    if isinstance(v, str):
        yield path, v
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from strings(x, f"{path}[{i}]")
    elif isinstance(v, dict):
        for k, x in v.items():
            yield from strings(x, f"{path}.{k}")


def text_of(s):
    return html.unescape(re.sub(r"<[^>]+>", " ", s))


def recruiter_names(report):
    """Names the SSOT itself tags as the recruiter or their firm."""
    blob = text_of(json.dumps(report, ensure_ascii=False))
    names = set()
    for m in re.finditer(r"[Rr]ecruiter (?:call|screen)[^.;]{0,40}?(?:with\s+|\()([A-Z][a-z]+)(?:[ ,]+\(?([A-Z][A-Za-z]+))?", blob):
        names.update(n for n in m.groups() if n)
    for m in re.finditer(r"\b([A-Z][a-z]+) at ([A-Z][A-Za-z]+)\b[^.]{0,30}\brecruit", blob):
        names.update(m.groups())
    meta = report.get("meta") or {}
    for k in ("recruiter", "recruiter_firm"):
        if isinstance(meta.get(k), str):
            names.add(meta[k])
    return {n for n in names if n not in {"The", "A", "Recruiter"}}


def scan(payload, report, voice=True):
    """Return a list of leak findings for one signed-out payload."""
    out = []
    raw = json.dumps(payload, ensure_ascii=False)
    keys = set()

    def walk(v):
        if isinstance(v, dict):
            keys.update(v)
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
    walk(payload)
    for k in INTERNAL_KEYS:
        if k in keys:
            out.append(f"internal key in payload: {k}")
    if re.search(r'"audience":\s*"internal"', raw):
        out.append("internal-tagged content in payload (audience: internal)")
    names = recruiter_names(report)
    for path, s in strings(payload):
        t = text_of(s)
        for label, rx in (("transcript or notetaker", NOTETAKERS), ("[m:ss] timestamp", TIMESTAMP),
                          ("landmines", LANDMINE)):
            m = re.search(rx, t, re.I if label != "[m:ss] timestamp" else 0)
            if m:
                out.append(f"{label}: {m.group(0)!r} at {path}")
        for m in re.finditer(QUOTE_SPAN, t):
            if len(m.group(1).split()) >= 4 and re.search(SPEECH, t[:m.start()][-60:] + " " + t[m.end():][:40]):
                out.append(f"quote of someone on the call at {path}: {m.group(0)[:60]!r}")
                break
        for n in names:
            if re.search(rf"\b{re.escape(n)}\b", t):
                out.append(f"recruiter name {n!r} at {path}")
    if voice:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import voice_gate
        lines = "\n".join(text_of(s).replace("\n", " ") + (" <!-- joint -->" if 'data-voice="joint"' in s else "")
                          for _, s in strings(payload))
        for line, word, ctx in voice_gate.scan("payload.txt", lines):
            out.append(f"voice: royal {word!r}: {ctx}")
    return out


def render(shares_file, rid, report_file, lib):
    try:
        p = subprocess.run(["node", "--no-warnings", RENDER, shares_file, rid, report_file, lib],
                           cwd=ROOT, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, f"cannot render: {e}"
    if p.returncode == 3:
        return None, "invalid"
    if p.returncode != 0:
        return None, f"cannot render: {p.stderr.strip()[:300]}"
    return json.loads(p.stdout), None


def read(path, staged):
    if staged:
        p = subprocess.run(["git", "show", f":{path}"], cwd=ROOT, capture_output=True, text=True)
        if p.returncode == 0:
            return p.stdout
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return fh.read()


def check(shares_text, lib=LIB, staged=False, voice=True):
    """Return (exit_code, messages) for a public-shares.json body."""
    try:
        shares = json.loads(shares_text)
    except ValueError as e:
        return 2, [f"{SHARES}: not JSON ({e})"]
    msgs, code = [], 0
    with tempfile.TemporaryDirectory() as tmp:
        sf = os.path.join(tmp, "shares.json")
        with open(sf, "w", encoding="utf-8") as fh:
            fh.write(shares_text)
        for rid, entry in shares.items():
            if rid.startswith("_"):
                continue
            rel = f"runtime/recoil/generated/{re.sub(r'[^a-zA-Z0-9_-]', '', rid)}.json"
            try:
                report_text = read(rel, staged)
                report = json.loads(report_text)
            except (OSError, ValueError) as e:
                msgs.append(f"{rid}: cannot read {rel} ({e})")
                code = max(code, 2)
                continue
            rf = os.path.join(tmp, f"{rid}.json")
            with open(rf, "w", encoding="utf-8") as fh:
                fh.write(report_text)
            payload, why = render(sf, rid, rf, lib)
            if why == "invalid":
                msgs.append(f"{rid}: not a valid share: needs approved and gauntlet (the counterpart-gauntlet "
                            "run that cleared this signed-out view); a strip list alone is never a share")
                code = max(code, 1)
                continue
            if why:
                msgs.append(f"{rid}: {why}")
                code = max(code, 2)
                continue
            if isinstance(entry, dict) and "strip_block_types" in entry:
                msgs.append(f"{rid}: strip_block_types is the retired strip-list model; the public view "
                            "shows only audience \"both\" blocks, tag the SSOT instead")
                code = max(code, 1)
            for f in scan(payload, report, voice):
                msgs.append(f"{rid}: {f}")
                code = max(code, 1)
    return code, msgs


def self_test():
    report = {
        "meta": {"counterpart": "Pat Doe", "captured": "Recruiter call with Quinn (Acme Talent), 2026-10-01", "gate": "x"},
        "redaction_policy": {"internal": ["beliefs"]},
        "page": {"header": {"title": "T"}, "tabs": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}], "blocks": [
            {"tab": "a", "audience": "both", "type": "prose", "p": ["I keep a working file before every call."]},
            {"tab": "b", "audience": "internal", "type": "list", "h2": "Questions & landmines",
             "items": ["[35:32] Pat said \"we never ship on Fridays here\" per the Granola transcript; Quinn at Acme"]},
        ]},
    }
    ok_entry = {"approved": "test", "gauntlet": "wf_test"}
    cases = []
    with tempfile.TemporaryDirectory() as tmp:
        gen = os.path.join(tmp, "runtime", "recoil", "generated")
        os.makedirs(gen)
        global ROOT, RENDER
        root0 = ROOT
        RENDER = os.path.join(root0, "scripts", "recoil_public_share_render.mjs")
        ROOT = tmp
        try:
            with open(os.path.join(gen, "t.json"), "w") as fh:
                json.dump(report, fh)
            lib = os.path.join(root0, LIB)
            c, _ = check(json.dumps({"_doc": "x"}), lib, voice=False)
            cases.append(("no entry passes", c == 0))
            c, m = check(json.dumps({"t": ok_entry}), lib, voice=False)
            cases.append(("allow-list render of a mixed report passes", c == 0 and not m))
            c, _ = check(json.dumps({"t": {"approved": "x", "strip_markers": ["landmines"]}}), lib, voice=False)
            cases.append(("entry without a gauntlet fails", c == 1))
            leaked = dict(report)
            leaked["page"] = dict(report["page"], blocks=[dict(b, audience="both") for b in report["page"]["blocks"]])
            payload = dict(leaked)
            found = scan(payload, report, voice=False)
            for label in ("internal key", "transcript or notetaker", "[m:ss] timestamp", "landmines",
                          "quote of someone", "recruiter name"):
                cases.append((f"strip-list-style payload fails on {label}", any(label in f for f in found)))
            cases.append(("royal we fails the voice check",
                          bool(scan({"page": {"blocks": [{"p": ["We will ship our roadmap."]}]}}, {}, voice=True))))
        finally:
            ROOT = root0
    for name, good in cases:
        print(("ok   " if good else "FAIL ") + name)
    return 0 if all(g for _, g in cases) else 1


def main():
    ap = argparse.ArgumentParser(description="Block a public recoil share whose signed-out render leaks.")
    ap.add_argument("--shares", help=f"shares file to check (default: {SHARES})")
    ap.add_argument("--lib", default=LIB, help="projection module (default: the live one)")
    ap.add_argument("--staged", action="store_true", help="read the shares file and reports from the git index")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    text = open(a.shares, encoding="utf-8").read() if a.shares else read(SHARES, a.staged)
    code, msgs = check(text, a.lib, a.staged)
    for m in msgs:
        print(("✖ " if code else "  ") + m, file=sys.stderr if code else sys.stdout)
    if code == 0:
        n = len([k for k in json.loads(text) if not k.startswith("_")])
        print(f"public-share gate: {n} share(s), signed-out render clean")
    return code


if __name__ == "__main__":
    sys.exit(main())
