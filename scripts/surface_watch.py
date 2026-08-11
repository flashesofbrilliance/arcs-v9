#!/usr/bin/env python3
"""Surface watcher — heuristic detector for mini-app / polyform SURFACE candidates (no model, no deps).

Sibling of scripts/adr_dewy_watch.py. Where that one catches ADR/DEWY decision candidates, this catches
moments where an idea gets named as a buildable SURFACE (a mini-app, instrument, ledger, generator, skill,
registry, componentizable thing) AND carries CHARGE (the potency markers where the author lit up). Ranks by
"static charge" = high potential not yet discharged (the spark-plug frame: a gap holding voltage).

NEVER builds anything. It queues surface-candidates for a human to parameterize / formalize / componentize
/ experiment with. Pure stdlib, zero cost.

Usage:
    python3 scripts/surface_watch.py --sessions 7        # sweep Claude Code sessions, last 7 days
    python3 scripts/surface_watch.py --top 20            # ranked by static charge
    python3 scripts/surface_watch.py --self-test
"""
import sys, os, re, json, hashlib, glob, time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LEDGER = os.path.join(_ROOT, "_INBOX", "surface-candidates.jsonl")
_PROJECTS = os.path.expanduser("~/.claude/projects")

# GENESIS: an idea named as a buildable surface.
_GENESIS = [
    r"mini[-\s]?app", r"\bsurface\b", r"\binstrument\b", r"\ba tool\b", r"\bdashboard\b", r"\bledger\b",
    r"componenti[sz]e", r"parameteri[sz]e", r"\bpolyform\b", r"we should build", r"let'?s build",
    r"\bbuild (a|an|this|the)\b", r"this could be", r"this feels like", r"worth building", r"a widget",
    r"\ban app\b", r"a skill (that|for)", r"\bregistry\b", r"a generator", r"\bSSOT\b", r"a page for",
]
# CHARGE: potency / static-charge markers (the author lighting up).
_CHARGE = [
    r"this feels like", r"\bbingo\b", r"\bpotent\b", r"statically charged", r"this is the thing", r"\bwildest\b",
    r"\bobsessed\b", r"\bspice\b", r"flash of brilliance", r"love this", r"\bexactly\b", r"\byes[!,]", r"\bhammer\b",
    r"\bwild\b", r"crack in", r"reverberate", r"resonan",
]
_G = [re.compile(p, re.I) for p in _GENESIS]
_C = [re.compile(p, re.I) for p in _CHARGE]
_SENT = re.compile(r"[^.!?\n]+[.!?]?")


def _norm(s): return " ".join(s.lower().split())
def _title(x):
    w = x.strip().split(); return " ".join(w[:9]) + ("…" if len(w) > 9 else "")


def is_surface(sentence):
    return any(r.search(sentence) for r in _G)


def charge(sentence):
    """Static charge = genesis density + charge markers + co-occurrence bonus, length-sanitized."""
    g = sum(bool(r.search(sentence)) for r in _G)
    c = sum(bool(r.search(sentence)) for r in _C)
    s = g + 2 * c + (2 if (g and c) else 0)
    n = len(sentence)
    if n < 30: s -= 1
    if n > 300: s -= 1
    return s


def scan(text, source="stdin", ts="unstamped"):
    for m in _SENT.finditer(text):
        sent = m.group().strip()
        if len(sent) < 16 or not is_surface(sent):
            continue
        h = hashlib.sha1(_norm(sent).encode()).hexdigest()[:12]
        yield {"ts": ts, "source": source, "excerpt": sent, "charge": charge(sent),
               "proposed_title": _title(sent), "hash": h, "status": "candidate"}


def _session_text(path):
    first = None
    for line in open(path, errors="ignore"):
        line = line.strip()
        if not line:
            continue
        try: d = json.loads(line)
        except Exception: continue
        if first is None and d.get("timestamp"):
            first = d["timestamp"][:10]
        m = d.get("message")
        if not isinstance(m, dict) or m.get("role") not in ("user", "assistant"):
            continue
        ts = (d.get("timestamp") or first or "unstamped")[:10]
        c = m.get("content")
        if isinstance(c, str):
            yield ts, c
        elif isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "text" and b.get("text"):
                    yield ts, b["text"]


def _existing():
    if not os.path.exists(_LEDGER): return set()
    out = set()
    for l in open(_LEDGER):
        l = l.strip()
        if l:
            try: out.add(json.loads(l)["hash"])
            except Exception: pass
    return out


def append(cands):
    os.makedirs(os.path.dirname(_LEDGER), exist_ok=True)
    seen = _existing(); n = 0
    with open(_LEDGER, "a") as f:
        for c in cands:
            if c["hash"] in seen: continue
            seen.add(c["hash"]); f.write(json.dumps(c) + "\n"); n += 1
    return n


def scan_sessions(days=7):
    cutoff = time.time() - days * 86400
    files = [p for p in glob.glob(os.path.join(_PROJECTS, "*", "*.jsonl")) if os.path.getmtime(p) >= cutoff]
    total = 0
    for path in sorted(files):
        src = os.path.basename(os.path.dirname(path)) + "/" + os.path.basename(path)[:8]
        total += append([c for ts, t in _session_text(path) for c in scan(t, source=src, ts=ts)])
    print(f"swept {len(files)} session(s) over last {days}d: {total} new surface-candidate(s) -> "
          f"{os.path.relpath(_LEDGER, _ROOT)}")
    return total


def list_top(n=20):
    if not os.path.exists(_LEDGER):
        print("(no ledger yet)"); return
    rows = [json.loads(l) for l in open(_LEDGER) if l.strip()]
    pend = [r for r in rows if r.get("status") == "candidate"]
    seen, ranked = set(), []
    for r in pend:
        k = _norm(r["excerpt"])[:70]
        if k in seen: continue
        seen.add(k); ranked.append(r)
    ranked.sort(key=lambda r: -r.get("charge", 0))
    print(f"top {min(n, len(ranked))} of {len(ranked)} deduped surface-candidates (by static charge)\n")
    for r in ranked[:n]:
        src = r["source"].split("/")[0].replace("-Users-zharris-arcs-v9--claude-worktrees-", "").replace("-Users-zharris-arcs-v9", "root")
        print(f"  ⚡{r.get('charge',0):>2} {r['ts']}  {r['excerpt'][:92]}")
        print(f"        ↳ {src}")


def _self_test():
    cases = [
        ("this feels like a mini app surface", True),
        ("Bingo, we should build this as an instrument", True),
        ("let's componentize the field-row grammar into one SSOT", True),
        ("the invoice was paid on Tuesday", False),
        ("a one-page conviction ledger that turns the fear into a count", True),
        ("I updated the notification send-to address", False),
    ]
    ok = 0
    for text, exp in cases:
        got = is_surface(text); p = got == exp; ok += p
        print(f"[{'PASS' if p else 'FAIL'}] {str(exp):5} vs {str(got):5} (⚡{charge(text)}) {text[:52]}")
    print(f"\nself-test: {ok}/{len(cases)} passed")
    return ok == len(cases)


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--self-test" in a: sys.exit(0 if _self_test() else 1)
    if "--top" in a:
        i = a.index("--top"); n = int(a[i+1]) if i+1 < len(a) and a[i+1].isdigit() else 20
        list_top(n); sys.exit(0)
    if "--sessions" in a:
        i = a.index("--sessions"); d = int(a[i+1]) if i+1 < len(a) and a[i+1].isdigit() else 7
        scan_sessions(d); sys.exit(0)
    if "--stdin" in a:
        print(f"scanned stdin: {append(scan(sys.stdin.read()))} new"); sys.exit(0)
    print(__doc__)
