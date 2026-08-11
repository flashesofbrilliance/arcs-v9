#!/usr/bin/env python3
"""ADR / DEWY candidate watcher — heuristic detector (no model, no deps).

Scans a text blob (a session transcript, a git diff, or free text) for decision-cue language, classifies
each hit as an ADR candidate (a durable rule / architecture choice) and/or a DEWY candidate (a bet under
uncertainty with priors to check later), and appends deduped candidates to an append-only ledger:

    _INBOX/adr-dewy-candidates.jsonl

It NEVER writes an ADR or a receipt. Detection queues a candidate; a human promotes it (see the design at
_PATTERNS/adr-dewy-candidate-watcher.md). Cheapest layer of the watcher: pure stdlib, zero cost.

Usage:
    python3 scripts/adr_dewy_watch.py --scan transcript.txt      # scan a file, append candidates
    cat blob | python3 scripts/adr_dewy_watch.py --stdin         # scan stdin
    python3 scripts/adr_dewy_watch.py --sessions 7               # sweep all Claude Code sessions, last 7 days
    python3 scripts/adr_dewy_watch.py --list                     # show pending candidates
    python3 scripts/adr_dewy_watch.py --self-test                # verify the classifier
"""
import sys, os, re, json, hashlib, glob, time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LEDGER = os.path.join(_ROOT, "_INBOX", "adr-dewy-candidates.jsonl")

# Cue language. Word-boundary, case-insensitive. Kept deliberately high-precision (a missed candidate is
# cheap — L1 reflex + the next scan catch it; a false candidate wastes a human review).
_ADR_CUES = [
    r"chose\s+\w[\w\s]{0,40}?\s+over\s+\w", r"\bwe chose\b", r"\bgoing with\b", r"\bwent with\b",
    r"\bdecided to\b", r"\bfrom now on\b", r"\bstandardi[sz]e\b", r"\bdefault to\b", r"\bdeprecate[ds]?\b",
    r"\bsupersede[ds]?\b", r"\binstead of\b", r"\bthe tradeoff\b", r"\bpivot(?:ing|ed)? to\b",
    r"\bwe(?:'ll| will)? adopt\b", r"\bthe rule is\b", r"\brather than\b.{0,40}\bbecause\b",
]
_DEWY_CUES = [
    r"\bmy read is\b", r"\bi(?:'m| am) betting\b", r"\bbet(?:ting)? that\b", r"\bconviction\b",
    r"\bi expect\b", r"\bex[-\s]?ante\b", r"\bupdate (?:my |our )?priors?\b", r"\bwe(?:'ll| will) see if\b",
    r"\bhypothesi[sz]e?d?\b", r"\bmy prior\b", r"\by[-\s]?gate\b", r"\b(?:green|yellow|red)-?leaning\b",
    r"\blikely (?:that|to)\b",
]
_ADR_RE = [re.compile(p, re.I) for p in _ADR_CUES]
_DEWY_RE = [re.compile(p, re.I) for p in _DEWY_CUES]

# Split into sentence-ish units so an excerpt is one claim, not a paragraph.
_SENT = re.compile(r"[^.!?\n]+[.!?]?")


def _norm(s):
    return " ".join(s.lower().split())


def _title(excerpt):
    words = excerpt.strip().split()
    return " ".join(words[:9]) + ("…" if len(words) > 9 else "")


def classify(sentence):
    """Return 'adr' | 'dewy' | 'both' | None for one sentence."""
    adr = any(r.search(sentence) for r in _ADR_RE)
    dewy = any(r.search(sentence) for r in _DEWY_RE)
    if adr and dewy:
        return "both"
    if adr:
        return "adr"
    if dewy:
        return "dewy"
    return None


def scan(text, source="stdin", ts="unstamped"):
    """Yield candidate dicts for each decision-cue sentence in text."""
    for m in _SENT.finditer(text):
        s = m.group().strip()
        if len(s) < 12:
            continue
        kind = classify(s)
        if not kind:
            continue
        h = hashlib.sha1(_norm(s).encode()).hexdigest()[:12]
        yield {"ts": ts, "source": source, "excerpt": s, "type": kind,
               "proposed_title": _title(s), "hash": h, "status": "candidate"}


_RATIONALE = [r"\bbecause\b", r"\binstead of\b", r"\brather than\b", r"\btradeoff\b", r"\bso that\b", r"\s+over\s+"]
_DECISIVE = [r"\bchose\b", r"\bdecided\b", r"\bgoing with\b", r"\bwent with\b", r"\bstandardi[sz]e\b",
             r"\bdefault to\b", r"\bdeprecate", r"\bsupersede", r"\bpivot"]
_CONVICTION = [r"\bconviction\b", r"\bmy read is\b", r"\bbet(?:ting)? that\b", r"\bex[-\s]?ante\b",
               r"\bupdate (?:my |our )?priors?\b", r"\by[-\s]?gate\b"]
_RAT_RE = [re.compile(p, re.I) for p in _RATIONALE]
_DEC_RE = [re.compile(p, re.I) for p in _DECISIVE]
_CONV_RE = [re.compile(p, re.I) for p in _CONVICTION]


def score(excerpt, kind="adr"):
    """Rank a candidate: rationale + decisiveness + conviction, penalize too-short/too-long. Pure fn of text."""
    s = 0
    s += 2 * sum(bool(r.search(excerpt)) for r in _RAT_RE)
    s += 1 * sum(bool(r.search(excerpt)) for r in _DEC_RE)
    s += 2 * sum(bool(r.search(excerpt)) for r in _CONV_RE)
    if kind == "both":
        s += 1
    n = len(excerpt)
    if n < 40:
        s -= 1
    if n > 320:
        s -= 1
    return s


def _existing_hashes():
    if not os.path.exists(_LEDGER):
        return set()
    out = set()
    for line in open(_LEDGER):
        line = line.strip()
        if line:
            try:
                out.add(json.loads(line)["hash"])
            except Exception:
                pass
    return out


def append(candidates):
    """Append new (deduped) candidates to the ledger. Returns count written."""
    os.makedirs(os.path.dirname(_LEDGER), exist_ok=True)
    seen = _existing_hashes()
    n = 0
    with open(_LEDGER, "a") as f:
        for c in candidates:
            if c["hash"] in seen:
                continue
            seen.add(c["hash"])
            f.write(json.dumps(c) + "\n")
            n += 1
    return n


def list_pending():
    if not os.path.exists(_LEDGER):
        print("(no ledger yet)")
        return
    rows = [json.loads(l) for l in open(_LEDGER) if l.strip()]
    pend = [r for r in rows if r.get("status") == "candidate"]
    print(f"{len(pend)} pending / {len(rows)} total\n")
    for r in pend:
        print(f"  [{r['type']:4}] {r['hash']}  {r['proposed_title']}")


_PROJECTS = os.path.expanduser("~/.claude/projects")


def _session_text(path):
    """Yield (ts, text) for each user/assistant text block in a Claude Code transcript .jsonl.
    Skips thinking / tool_use / tool_result / image — decisions are stated in prose, and tool noise
    produces false candidates."""
    first_ts = None
    for line in open(path, errors="ignore"):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        if first_ts is None and d.get("timestamp"):
            first_ts = d["timestamp"][:10]
        m = d.get("message")
        if not isinstance(m, dict) or m.get("role") not in ("user", "assistant"):
            continue
        c = m.get("content")
        ts = (d.get("timestamp") or first_ts or "unstamped")[:10]
        if isinstance(c, str):
            yield ts, c
        elif isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "text" and b.get("text"):
                    yield ts, b["text"]


def scan_sessions(days=7):
    """Sweep every Claude Code session transcript modified in the last `days` days, harvest
    ADR/DEWY candidates into the ledger. Pure heuristic, no model. Returns (files, written)."""
    cutoff = time.time() - days * 86400
    files = [p for p in glob.glob(os.path.join(_PROJECTS, "*", "*.jsonl")) if os.path.getmtime(p) >= cutoff]
    total = 0
    per_session = []
    for path in sorted(files):
        proj = os.path.basename(os.path.dirname(path))
        sid = os.path.basename(path)[:8]
        src = f"{proj}/{sid}"
        cands = []
        for ts, text in _session_text(path):
            for c in scan(text, source=src, ts=ts):
                cands.append(c)
        wrote = append(cands)
        total += wrote
        if wrote:
            per_session.append((src, wrote))
    print(f"swept {len(files)} session(s) over last {days}d: {total} new candidate(s) "
          f"-> {os.path.relpath(_LEDGER, _ROOT)}\n")
    for src, w in sorted(per_session, key=lambda x: -x[1]):
        print(f"  +{w:3}  {src}")
    return len(files), total


def list_top(n=25):
    """Rank pending candidates by score, dedup near-duplicates, print the top n. The reconciliation view."""
    if not os.path.exists(_LEDGER):
        print("(no ledger yet)")
        return
    rows = [json.loads(l) for l in open(_LEDGER) if l.strip()]
    pend = [r for r in rows if r.get("status") == "candidate"]
    seen, ranked = set(), []
    for r in pend:
        key = _norm(r["excerpt"])[:70]
        if key in seen:
            continue
        seen.add(key)
        ranked.append((score(r["excerpt"], r["type"]), r))
    ranked.sort(key=lambda x: -x[0])
    print(f"top {min(n, len(ranked))} of {len(ranked)} deduped candidates ({len(pend)} raw pending)\n")
    for sc, r in ranked[:n]:
        src = r["source"].split("/")[0].replace("-Users-zharris-arcs-v9--claude-worktrees-", "").replace("-Users-zharris-arcs-v9", "root")
        print(f"  {sc:>2} [{r['type']:4}] {r['ts']}  {r['excerpt'][:88]}")
        print(f"       ↳ {src}")


def _self_test():
    cases = [
        ("we went with Akismet over the PHP snippet because there is no safe code host", "adr"),
        ("From now on, deploy the client deck from the main worktree only.", "adr"),
        ("My read is this call is green-leaning and we should let him drive.", "dewy"),
        ("Adaptive rhetorical resonance: I'm betting we standardize tuning delivery to their register.", "both"),
        ("The forms are protected by honeypot, speed check, and Akismet.", None),
        ("Todd paid the invoice today and the sandbox is pending.", None),
        ("We default to plus-addressing for test leads.", "adr"),
        ("I expect the funds are still pending on the new-account hold.", "dewy"),
    ]
    ok = 0
    for text, exp in cases:
        got = classify(text)
        p = got == exp
        ok += p
        print(f"[{'PASS' if p else 'FAIL'}] {str(exp):5} vs {str(got):5}  {text[:58]}")
    print(f"\nself-test: {ok}/{len(cases)} passed")
    return ok == len(cases)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--self-test" in args:
        sys.exit(0 if _self_test() else 1)
    if "--list" in args:
        list_pending()
        sys.exit(0)
    if "--top" in args:
        i = args.index("--top")
        n = int(args[i + 1]) if i + 1 < len(args) and args[i + 1].isdigit() else 25
        list_top(n)
        sys.exit(0)
    if "--sessions" in args:
        i = args.index("--sessions")
        days = int(args[i + 1]) if i + 1 < len(args) and args[i + 1].isdigit() else 7
        scan_sessions(days)
        sys.exit(0)
    if "--scan" in args:
        path = args[args.index("--scan") + 1]
        text = open(path).read()
        ts = "unstamped"  # caller stamps; Date.now-free by design
        n = append(scan(text, source=os.path.basename(path), ts=ts))
        print(f"scanned {path}: {n} new candidate(s) -> {os.path.relpath(_LEDGER, _ROOT)}")
        sys.exit(0)
    if "--stdin" in args:
        n = append(scan(sys.stdin.read(), source="stdin"))
        print(f"scanned stdin: {n} new candidate(s) -> {os.path.relpath(_LEDGER, _ROOT)}")
        sys.exit(0)
    print(__doc__)
