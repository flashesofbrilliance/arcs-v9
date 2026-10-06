#!/usr/bin/env python3
"""handoff_cluster — deterministic domain clustering of excavated handoff units (no LLM).

Fallback for Op20/Op21 (2026-10-06): both are READY and ran via the bridge, but Op20's 54-dim seed is
receipt-shaped (nci/somatic/axiom) so 150 handoff blocks collapsed to ONE cluster, and Op21 ranks its
own corpus, not a passed-in one. So: split each canonical block (latest variant per version) into
units (bullet or paragraph, with its section heading), score each unit against a keyword lexicon per
domain, assign the top domain (ties and zero-hit units -> "unsorted"), and mark units under
Open/Next/Blocked headings as open loops.

  handoff_cluster.py [--in _STATE/handoff-excavation/<date>.jsonl] [--outdir same-dir]
Writes <outdir>/units.jsonl and prints per-domain counts. Stdlib only.
"""
import collections, datetime, json, os, re, sys

LEX = {
    "jobs": r"job factory|\bjobs?\b|intake|recruit|resume|candidac|interview|schriner|oxenham|vico|blacksmith|"
            r"gosquad|squad|application|missed-pile|swipe|hiring|role\b|success academy|fanatics|lycett",
    "recoil": r"recoil|war-?room|counterpart|\bforge\b|codex|\bprl\b|todd|sugar|ahmed|\bwing\b|teardown|omakase|"
              r"gauntlet|pre-?call|louisville|brooks|jeben|yuri|robin|kam\b|polyform|ex-ante",
    "infra": r"\bci\b|workflow|github actions|vercel|deploy|worktree|\bhook|cruft|migrate|supabase|billing|"
             r"api key|anthropic key|secret|pre-commit|domain|alias|preview|squash|merge commit|cron|bundle|eslint|"
             r"security-review|outage|env\b|\.env|dns|proxy\.ts",
    "compass": r"compass|receipt page|/receipt|brief|y-?gate|dewy|auth|magic.?link|idor|share token|dashboard|"
               r"field landing|observatory|prep ?session|outcome|nci_score|tributar|userid|sign-in|prisma schema",
    "canon": r"canon|memory|\badr-?\d|\bseed|oracle|handoff|molt|fragment|\btao\b|operator|periodic|librarian|"
             r"folksonomy|ledger|backlog|induced|witness|drift|lattice|kintsugi|inchworm|catalog|claude\.md|"
             r"debt tracker|tracker",
    "outward": r"good\.arcs|nftt|\bblog|linkedin|brand|icon|m[öo]bius|reading room|chronicle|almanac|zachharris\.xyz|"
               r"newsletter|post\b|essay|showcase|og image|share card|status page|tribes|lede|wrap-lint|artifact",
}
LEXC = {k: re.compile(v, re.I) for k, v in LEX.items()}
OPEN_H = re.compile(r"open|next|todo|blocked|pending|follow|carry|unresolved|zach'?s? (move|action)|waiting", re.I)
DEC_H = re.compile(r"decision|decided|locked|lesson|learn|principle|rule", re.I)


def units(body):
    sec = ""
    buf = []
    for line in body.split("\n")[1:]:
        h = re.match(r"^#{2,4} (.+)", line)
        if h:
            if buf: yield sec, "\n".join(buf).strip(); buf = []
            sec = h.group(1).strip()
            continue
        starts = re.match(r"^\s{0,1}(?:[-*]|\d+[.)]) ", line) or (not line.strip())
        if starts and buf:
            yield sec, "\n".join(buf).strip(); buf = []
        if line.strip():
            buf.append(line)
    if buf:
        yield sec, "\n".join(buf).strip()


def main():
    a = sys.argv
    inp = a[a.index("--in") + 1] if "--in" in a else f"_STATE/handoff-excavation/{datetime.date.today()}.jsonl"
    outdir = a[a.index("--outdir") + 1] if "--outdir" in a else os.path.dirname(inp)
    canon = {}
    for l in open(inp):
        r = json.loads(l)
        canon[r["version"] or r["hash"]] = r          # latest variant per version wins
    out, cnt, opn = [], collections.Counter(), collections.Counter()
    for key, r in canon.items():
        for sec, u in units(r["body"]):
            if len(u) < 25:
                continue
            sc = {k: len(c.findall(u)) + 0.5 * len(c.findall(sec)) for k, c in LEXC.items()}
            best = max(sc.values())
            top = [k for k, v in sc.items() if v == best]
            dom = top[0] if best > 0 and len(top) == 1 else ("unsorted" if best == 0 else "+".join(sorted(top)))
            kind = "open" if OPEN_H.search(sec) else "decision" if DEC_H.search(sec) else "fact"
            row = {"block": key, "date": r["date"], "section": sec, "domain": dom, "kind": kind,
                   "prs": sorted({int(x) for x in re.findall(r"(?<![\w/])#(\d{2,4})\b", u)}), "text": u}
            out.append(row); cnt[dom] += 1
            if kind == "open": opn[dom] += 1
    p = os.path.join(outdir, "units.jsonl")
    with open(p, "w") as fh:
        for row in out:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"{len(out)} units from {len(canon)} blocks -> {p}")
    for d, n in cnt.most_common():
        print(f"  {d:28} {n:5}  open={opn[d]}")


if __name__ == "__main__":
    main()
