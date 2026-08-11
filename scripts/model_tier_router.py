#!/usr/bin/env python3
"""Model-tier router — heuristic classifier that RECOMMENDS a Claude tier by reversibility × value (no model, no deps).

Sibling of scripts/surface_watch.py and scripts/adr_dewy_watch.py. Where those catch decision/surface
candidates, this reads a task/prompt and recommends which model tier should carry it:

    HAIKU   — routine / deductive / reversible (rename, format, grep, extract, summarize, boilerplate)
    SONNET  — structured work inside guardrails (implement to spec, refactor, wire, add tests, fix bug)
    OPUS    — abductive / high-value / irreversible (design, architect, novel judgment, ruin-exposed)

It NEVER auto-switches the model (NOTOMATION-safe). It emits a recommendation + rationale; a human
confirms for high-consequence work. Core guardrail: RUIN-EXPOSED / IRREVERSIBLE cues floor the tier at
OPUS and it will never downgrade below what those cues demand — cheapness must never win over survivability.

Usage:
    python3 scripts/model_tier_router.py "rename the helper and fix the typo"     # classify a task string
    echo "design the auth migration and deploy to prod" | python3 scripts/model_tier_router.py --stdin
    python3 scripts/model_tier_router.py --json "refactor compass route per ADR"  # machine-readable
    python3 scripts/model_tier_router.py --sessions 7                              # sweep recent sessions, log recs
    python3 scripts/model_tier_router.py --self-test
"""
import sys, os, re, json, hashlib, glob, time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LEDGER = os.path.join(_ROOT, "_INBOX", "tier-recommendations.jsonl")
_PROJECTS = os.path.expanduser("~/.claude/projects")

# Latest tier -> model id (per global CLAUDE.md: default to latest & most capable).
_MODEL_ID = {
    "HAIKU": "claude-haiku-4-5",
    "SONNET": "claude-sonnet-5",
    "OPUS": "claude-opus-5",
}
_ORDER = ["HAIKU", "SONNET", "OPUS"]  # ascending capability/cost

# ---------------------------------------------------------------------------
# Cue lexicons. Each dimension votes for a tier; the guardrail lexicon can only
# push UP (never down). Regexes are word-boundary-anchored to avoid substring noise.
# ---------------------------------------------------------------------------

# RUIN / IRREVERSIBLE — one-way doors and ruin vectors. Presence FLOORS the tier at OPUS
# and forces human confirmation. Never downgraded, whatever else the task looks like.
_RUIN = [
    r"\birreversibl", r"\bone[-\s]?way door", r"\bcan'?t (be )?undo", r"\bunrecoverabl", r"\bruin\b",
    r"\bexistential\b", r"\bdelete\b", r"\bdrop (table|database|schema)\b", r"\brm\s+-rf\b",
    r"\bforce[-\s]?push\b", r"\bmigrat(e|ion)\b", r"\bdeploy\b", r"\bproduction\b", r"\bprod\b",
    r"\bdrop\b.{0,24}\b(table|database|schema)\b", r"\btruncate\b", r"\boverwrit", r"\bpurge\b",
    r"\bpublish\b", r"\bsend (the |an? )?(email|message|invite|dm)\b", r"\bwire (funds|money|payment)\b",
    r"\bpayment\b", r"\bfinancial\b", r"\btransfer\b", r"\bcredential", r"\bsecret", r"\bapi[-\s]?key",
    r"\btoken\b", r"\bauth(entication)?\b", r"\bsecurity\b", r"\blegal\b", r"\bcontract\b",
    r"\bhigh[-\s]?stakes\b", r"\bhard[-\s]?delete", r"\brotate\b.*\b(key|secret|credential)",
]
# ABDUCTIVE / HIGH-VALUE — open-ended judgment, novel synthesis, wide solution space -> OPUS.
_ABDUCTIVE = [
    r"\bdesign\b", r"\barchitect", r"\bstrateg", r"\bnovel\b", r"\bfrom scratch\b", r"\binvent\b",
    r"\bhypothes", r"\btrade[-\s]?off", r"\bambiguous\b", r"\bopen[-\s]?ended\b", r"\bjudgment\b",
    r"\bnuance", r"\bsynthesi[sz]e\b", r"\broot cause\b", r"\bwhy (does|is|are|did)\b", r"\bdecide\b",
    r"\bfigure out\b", r"\breason about\b", r"\bevaluate the trade", r"\bconceptual", r"\bframework\b",
]
# STRUCTURED / GUARDRAIL — bounded build work with a spec/pattern to follow -> SONNET.
_STRUCTURED = [
    r"\bimplement\b", r"\brefactor\b", r"\bwrite (the )?tests?\b", r"\badd (a |an )?(feature|test|endpoint|route)\b",
    r"\bfix (the )?bug\b", r"\bper (the )?(adr|spec|pattern)\b", r"\bfollow (the )?spec\b", r"\bextend\b",
    r"\bwire (up|it|this|the)\b", r"\bintegrat", r"\bbuild (the |a |an )?(component|route|handler|endpoint)\b",
    r"\bmigrate the code\b", r"\bport\b", r"\breuse the pattern\b", r"\bhook (it|this) up\b",
]
# ROUTINE / DEDUCTIVE / REVERSIBLE — mechanical, single-answer, cheaply reversible -> HAIKU.
_ROUTINE = [
    r"\brename\b", r"\bformat\b", r"\blint\b", r"\btypo\b", r"\breword\b", r"\brephrase\b", r"\blist\b",
    r"\bgrep\b", r"\bfind (the|all|where)\b", r"\block?up\b", r"\bsummari[sz]e\b", r"\bextract\b",
    r"\bboilerplate\b", r"\bmechanical\b", r"\bbump (the )?version\b", r"\badd a comment\b", r"\bcount\b",
    r"\bwhat is the\b", r"\bwhere is\b", r"\bwhich file\b", r"\bcopy[-\s]?edit", r"\bstub\b",
]

_TIER_LEX = {"OPUS": _ABDUCTIVE, "SONNET": _STRUCTURED, "HAIKU": _ROUTINE}
_C = {name: [re.compile(p, re.I) for p in lex] for name, lex in
      {"RUIN": _RUIN, "OPUS": _ABDUCTIVE, "SONNET": _STRUCTURED, "HAIKU": _ROUTINE}.items()}


def _hits(name, text):
    return [r.pattern for r in _C[name] if r.search(text)]


def classify(text):
    """Return a recommendation dict. Guardrail floors at OPUS on any ruin cue; never downgrades below it."""
    text = text or ""
    ruin = _hits("RUIN", text)
    votes = {t: len(_hits(t, text)) for t in _ORDER}

    if ruin:
        tier = "OPUS"
        needs_confirm = True
        rationale = ("ruin-exposed / irreversible cues present — floored at OPUS, never downgraded: "
                     + ", ".join(sorted({p.strip('\\b') for p in ruin}))[:180])
    elif max(votes.values()) == 0:
        # Nothing matched — bias to the safe middle, not the cheap floor. Ambiguity rounds UP.
        tier = "SONNET"
        needs_confirm = False
        rationale = "no strong cues matched — defaulting to SONNET (ambiguity rounds up, never down)."
    else:
        # Highest-voted tier wins; ties break toward the MORE capable tier (index in _ORDER).
        top = max(votes.values())
        tier = max((t for t in _ORDER if votes[t] == top), key=_ORDER.index)
        needs_confirm = tier == "OPUS"
        drivers = ", ".join(sorted({p.strip('\\b') for p in _hits(tier, text)}))[:180]
        rationale = f"{tier} cues dominate (votes {votes}) — driven by: {drivers}."

    return {
        "recommended_tier": tier,
        "model_id": _MODEL_ID[tier],
        "needs_human_confirm": needs_confirm,
        "ruin_exposed": bool(ruin),
        "votes": votes,
        "rationale": rationale,
        "auto_switch": False,  # NOTOMATION: recommend only.
    }


# ---------------------------------------------------------------------------
# Session sweep + ledger (mirrors surface_watch.py). Logs recs for audit; never switches anything.
# ---------------------------------------------------------------------------
_USER_TURN = re.compile(r".")


def _norm(s): return " ".join(s.lower().split())


def _user_prompts(path):
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
        if not isinstance(m, dict) or m.get("role") != "user":
            continue
        ts = (d.get("timestamp") or first or "unstamped")[:10]
        c = m.get("content")
        if isinstance(c, str) and c.strip():
            yield ts, c.strip()
        elif isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip():
                    yield ts, b["text"].strip()


def _existing():
    if not os.path.exists(_LEDGER): return set()
    out = set()
    for l in open(_LEDGER):
        l = l.strip()
        if l:
            try: out.add(json.loads(l)["hash"])
            except Exception: pass
    return out


def _append(recs):
    os.makedirs(os.path.dirname(_LEDGER), exist_ok=True)
    seen = _existing(); n = 0
    with open(_LEDGER, "a") as f:
        for r in recs:
            if r["hash"] in seen: continue
            seen.add(r["hash"]); f.write(json.dumps(r) + "\n"); n += 1
    return n


def scan_sessions(days=7):
    cutoff = time.time() - days * 86400
    files = [p for p in glob.glob(os.path.join(_PROJECTS, "*", "*.jsonl")) if os.path.getmtime(p) >= cutoff]
    recs = []
    for path in sorted(files):
        src = os.path.basename(os.path.dirname(path)) + "/" + os.path.basename(path)[:8]
        for ts, prompt in _user_prompts(path):
            if len(prompt) < 12:
                continue
            rec = classify(prompt)
            rec.update({"ts": ts, "source": src, "excerpt": prompt[:200],
                        "hash": hashlib.sha1(_norm(prompt).encode()).hexdigest()[:12]})
            recs.append(rec)
    n = _append(recs)
    print(f"swept {len(files)} session(s) over last {days}d: {n} new tier-recommendation(s) -> "
          f"{os.path.relpath(_LEDGER, _ROOT)}")
    return n


# ---------------------------------------------------------------------------
def _render(rec):
    icon = {"HAIKU": "○", "SONNET": "◐", "OPUS": "●"}[rec["recommended_tier"]]
    print(f"{icon} recommend: {rec['recommended_tier']}  ({rec['model_id']})")
    if rec["needs_human_confirm"]:
        print("  ⚠ HIGH-CONSEQUENCE — human confirmation required before proceeding.")
    print(f"  why: {rec['rationale']}")
    print("  (recommendation only — NOTOMATION: never auto-switches the model.)")


def _self_test():
    cases = [
        ("rename the helper and fix the typo", "HAIKU"),
        ("summarize this file and list the routes", "HAIKU"),
        ("implement the tier router per the ADR and add tests", "SONNET"),
        ("refactor the compass route and wire up the handler", "SONNET"),
        ("design the new auth architecture from scratch", "OPUS"),
        ("figure out the root cause and decide the trade-off", "OPUS"),
        # Guardrail: routine-looking words but ruin-exposed -> must NOT downgrade to HAIKU.
        ("just rename the column in the prod migration and deploy", "OPUS"),
        ("format the file then drop the old table", "OPUS"),
        ("reword the copy in the payment confirmation email we send", "OPUS"),
        # Ambiguity rounds up to SONNET, not down to HAIKU.
        ("help me with the thing we discussed", "SONNET"),
    ]
    ok = 0
    for text, exp in cases:
        rec = classify(text)
        got = rec["recommended_tier"]
        p = got == exp; ok += p
        flag = "⚠" if rec["needs_human_confirm"] else " "
        print(f"[{'PASS' if p else 'FAIL'}] want {exp:6} got {got:6} {flag} {text[:56]}")
    # Invariant: any ruin-exposed rec is OPUS + needs_confirm.
    inv = classify("delete the production database")
    assert inv["recommended_tier"] == "OPUS" and inv["needs_human_confirm"], "guardrail invariant broken"
    print(f"\nself-test: {ok}/{len(cases)} passed (guardrail invariant: OK)")
    return ok == len(cases)


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--self-test" in a: sys.exit(0 if _self_test() else 1)
    if "--sessions" in a:
        i = a.index("--sessions"); d = int(a[i+1]) if i+1 < len(a) and a[i+1].isdigit() else 7
        scan_sessions(d); sys.exit(0)
    as_json = "--json" in a
    if "--stdin" in a:
        text = sys.stdin.read()
    else:
        text = " ".join(x for x in a if not x.startswith("--"))
    if not text.strip():
        print(__doc__); sys.exit(0)
    rec = classify(text)
    if as_json:
        print(json.dumps(rec, indent=2))
    else:
        _render(rec)
