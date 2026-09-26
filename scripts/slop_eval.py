#!/usr/bin/env python3
"""slop_eval: the JUDGMENT tier of the slop-free system (companion to the mechanical slop_lint).

slop_lint hard-fails the clichés a grep can decide. This grades the tells that need judgment
(binary-contrast, triads, colon reveals, robotic rhythm, specificity) by feeding the surface plus
_PATTERNS/slop-free-rubric.md to Claude and returning a 0-2 score per rubric row. Advisory by
design: it costs money and is non-deterministic, so it is NOT in pre-commit. Run it on demand or
in CI before shipping a customer-facing surface.

Zero new deps: talks to the Anthropic API over stdlib urllib (the repo already carries ANTHROPIC_API_KEY;
the TS SDK powers the compass route, but a Python script should not add the pip SDK).

Usage:
  ANTHROPIC_API_KEY=... python3 scripts/slop_eval.py <file.html|.txt|.md> [...]
  python3 scripts/slop_eval.py --json <file> [...]
  python3 scripts/slop_eval.py --strict <file>     # exit 1 if a surface fails the rubric verdict
No key present -> prints a notice and exits 0 (advisory layer, never blocks the human).
"""
import os, re, sys, json, urllib.request, urllib.error

MODEL = "claude-sonnet-4-6"
RUBRIC_PATH = os.path.join(os.path.dirname(__file__), "..", "_PATTERNS", "slop-free-rubric.md")

def strip_to_text(s: str) -> str:
    s = re.sub(r"<script\b[^>]*>.*?</script>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<style\b[^>]*>.*?</style>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"&[a-zA-Z]+;|&#\d+;", " ", s)
    return re.sub(r"[ \t]+", " ", s).strip()

def rubric_text():
    try:
        return open(RUBRIC_PATH, encoding="utf-8").read()
    except OSError:
        return "(rubric file not found; grade on general AI-slop tells: word clichés, binary contrast, triads, colon reveals, robotic rhythm, and lack of named/measured specificity.)"

PROMPT = """You are grading a customer-facing surface for AI-slop against the rubric below. Score ONLY the judgment rows (B1,B2,B3,B4,C1,D1); the mechanical rows (A*,E*) are handled by a separate linter, so note them but do not let them drive the verdict.

For each judgment row give an integer score 0-2 (0=clean, 1=borderline, 2=slop) and a one-line reason quoting the offending text where possible. Then: total (sum of the judgment rows), fail_rows (any row scored 2), and verdict "SHIP" or "REVISE" (REVISE if total>3 OR any judgment row is 2). Return STRICT JSON only, no prose, shape:
{"rows":{"B1":{"score":0,"why":"..."},"B2":{...},"B3":{...},"B4":{...},"C1":{...},"D1":{...}},"total":0,"fail_rows":[],"verdict":"SHIP"}

=== RUBRIC ===
%s

=== SURFACE TO GRADE ===
%s
"""

def call_claude(text):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None, "no ANTHROPIC_API_KEY in env"
    body = json.dumps({
        "model": os.environ.get("SLOP_EVAL_MODEL", MODEL),
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": PROMPT % (rubric_text(), text[:20000])}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body,
        headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            out = json.load(r)
        txt = "".join(b.get("text", "") for b in out.get("content", []))
        m = re.search(r"\{.*\}", txt, re.S)
        return (json.loads(m.group(0)) if m else None), (None if m else "no JSON in response")
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read()[:200].decode(errors='replace')}"
    except Exception as e:
        return None, str(e)

def main(argv):
    strict = "--strict" in argv
    as_json = "--json" in argv
    files = [a for a in argv if not a.startswith("--")]
    if not files:
        print("usage: slop_eval.py [--json] [--strict] <file> [...]"); return 2
    results, any_revise, skipped = [], False, False
    for path in files:
        text = strip_to_text(open(path, encoding="utf-8", errors="replace").read())
        graded, err = call_claude(text)
        if graded is None:
            skipped = True
            results.append({"file": path, "skipped": err})
            continue
        graded["file"] = path
        results.append(graded)
        any_revise = any_revise or graded.get("verdict") == "REVISE"
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            if "skipped" in r:
                print(f"[SKIP] {r['file']} ({r['skipped']})"); continue
            print(f"[{r.get('verdict','?')}] {r['file']}  total={r.get('total','?')}")
            for row, v in (r.get("rows") or {}).items():
                flag = " <-- FAIL" if v.get("score") == 2 else ""
                print(f"    {row}={v.get('score')}  {v.get('why','')}{flag}")
    if skipped and not as_json:
        print("\n(advisory grader; rows A*/E* are covered by slop_lint + the impeccable detector)")
    return 1 if (strict and any_revise) else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
