#!/usr/bin/env python3
"""nftt_claim_batch: pilot of the Message Batches API (50% off, async) on the NFTT corpus.

For each routed NFTT post (runtime/specs/nftt-published.json) it asks the `deep` model to run
the claim-check method (.claude/skills/echo-scan/references/claim-check.md) in an OFFLINE form:
atomize the checkable claims, recompute derived numbers, catch internal contradictions, and
list which claims still need a primary record. No web access, so verdicts are limited to
CONFIRMED (recomputed or internally consistent), UNCONFIRMED (needs an outside record),
FALSE (contradicted inside the post) and THIN.

    python3 scripts/nftt_claim_batch.py build            # write requests + cost estimate, no network
    python3 scripts/nftt_claim_batch.py submit           # needs ANTHROPIC_API_KEY
    python3 scripts/nftt_claim_batch.py status <batch_id>
    python3 scripts/nftt_claim_batch.py fetch <batch_id> # writes _STATE/nftt-claim-batch/<date>.{jsonl,md}
Stdlib only. Strict args: unknown verb or extra arg -> exit 2.
Pilot kill condition (pre-registered 2026-10-04): if the FALSE + UNCONFIRMED rows surface
nothing that scripts/provenance_lint.py already flags, Batches do not earn a place.
"""
import datetime, json, os, re, sys, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arcs_models import model  # noqa: E402

OUT = os.path.join(ROOT, "_STATE", "nftt-claim-batch")
API = "https://api.anthropic.com/v1/messages/batches"
# Sonnet 4.x list price per MTok (input, output); batches bill at 50% of this.
PRICE = (3.0, 15.0)
MAX_OUT = 3000

SYSTEM = """You audit one published essay for factual integrity, using the claim-check method below,
in OFFLINE mode: you have no web access. Do not invent sources.

Verdicts allowed offline: CONFIRMED (a number you recomputed, or a claim the essay itself
evidences consistently), UNCONFIRMED (needs an outside primary record you cannot see),
FALSE (contradicted by the essay's own text, dates, or arithmetic), THIN (provenance only).

Return ONLY a JSON object:
{"slug": str, "central_claim": str,
 "claims": [{"claim": str, "verdict": "CONFIRMED|UNCONFIRMED|FALSE|THIN", "evidence": str, "central": bool}],
 "recomputed": [{"what": str, "arithmetic": str, "matches": bool}],
 "contradictions": [str],
 "summary": str}
Keep claim wording short. At most 15 claims: favor numbers, dates, attributions, causal claims.
Private individuals: describe, do not name.

--- claim-check method ---
"""


def strip(html):
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.I | re.S)
    html = re.sub(r"<[^>]+>", " ", html)
    html = re.sub(r"&[a-zA-Z#0-9]+;", " ", html)
    return re.sub(r"\s+", " ", html).strip()


def posts():
    slugs = json.load(open(os.path.join(ROOT, "runtime/specs/nftt-published.json")))["posts"]
    out = []
    for s in slugs:
        p = os.path.join(ROOT, "public", f"blog-nftt-{s}.html")
        if os.path.exists(p):
            out.append((s, strip(open(p, encoding="utf-8").read())))
    return out


def build():
    method = open(os.path.join(ROOT, ".claude/skills/echo-scan/references/claim-check.md")).read()
    system = SYSTEM + method
    reqs = [{"custom_id": s[:64], "params": {
        "model": model("deep"), "max_tokens": MAX_OUT,
        "system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": f"slug: {s}\n\nESSAY TEXT:\n{t}"}]}} for s, t in posts()]
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "requests.json")
    json.dump({"requests": reqs}, open(path, "w"))
    tin = sum(len(r["params"]["messages"][0]["content"]) + len(system) for r in reqs) / 4
    tout = len(reqs) * 1500  # expected, not max
    est = (tin * PRICE[0] + tout * PRICE[1]) / 1e6 * 0.5
    print(f"built {len(reqs)} requests -> {os.path.relpath(path, ROOT)} · model {model('deep')}")
    print(f"estimate: ~{tin/1e3:.0f}K input + ~{tout/1e3:.0f}K output tokens ≈ ${est:.2f} at batch price (cache hits lower it)")
    return reqs


def call(method, url, body=None):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("nftt_claim_batch: ANTHROPIC_API_KEY not set")
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                                          "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode()


def report(rows, day):
    lines = [f"# NFTT claim batch: {day}", "", f"Model `{model('deep')}`, offline claim-check, {len(rows)} posts.", "",
             "| Post | Claims | FALSE | UNCONFIRMED | Contradictions | Summary |", "|---|---|---|---|---|---|"]
    flagged = []
    for slug, r in rows:
        if r is None:
            lines.append(f"| {slug} | error | | | | |")
            continue
        c = r.get("claims", [])
        f = [x for x in c if x.get("verdict") == "FALSE"]
        u = sum(1 for x in c if x.get("verdict") == "UNCONFIRMED")
        lines.append(f"| {slug} | {len(c)} | {len(f)} | {u} | {len(r.get('contradictions', []))} | {r.get('summary', '').replace('|', '/')} |")
        for x in f:
            flagged.append(f"- **{slug}**: {x.get('claim')} ({x.get('evidence')})")
        for x in r.get("contradictions", []):
            flagged.append(f"- **{slug}** (contradiction): {x}")
    lines += ["", "## FALSE claims and contradictions (human review; the model can be wrong)", ""] + (flagged or ["None."])
    return "\n".join(lines) + "\n"


def fetch(bid):
    meta = json.loads(call("GET", f"{API}/{bid}"))
    if meta["processing_status"] != "ended":
        print(f"not ended yet: {meta['processing_status']} {meta['request_counts']}")
        return
    raw = call("GET", meta["results_url"])
    rows = []
    for line in raw.splitlines():
        e = json.loads(line)
        r = None
        if e["result"]["type"] == "succeeded":
            txt = "".join(b.get("text", "") for b in e["result"]["message"]["content"])
            m = re.search(r"\{.*\}", txt, re.S)
            try:
                r = json.loads(m.group(0)) if m else None
            except json.JSONDecodeError:
                r = None
        rows.append((e["custom_id"], r))
    day = datetime.date.today().isoformat()
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, f"{day}.jsonl"), "w").write(raw)
    md = report(sorted(rows), day).replace("—", "-")
    open(os.path.join(OUT, f"{day}.md"), "w").write(md)
    print(f"wrote _STATE/nftt-claim-batch/{day}.md · {meta['request_counts']}")


def main(a):
    if a == ["build"]:
        build()
    elif a == ["submit"]:
        reqs = build()
        res = json.loads(call("POST", API, {"requests": reqs}))
        print(f"submitted batch {res['id']} · status {res['processing_status']}")
    elif len(a) == 2 and a[0] == "status":
        m = json.loads(call("GET", f"{API}/{a[1]}"))
        print(m["processing_status"], m["request_counts"])
    elif len(a) == 2 and a[0] == "fetch":
        fetch(a[1])
    else:
        print("usage: nftt_claim_batch.py build | submit | status <id> | fetch <id>", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
