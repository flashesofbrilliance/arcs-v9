#!/usr/bin/env python3
"""
event_rules.py — declarative rule engine for the ARCS Observatory.

Turns the hardcoded, arcs-specific classify() heuristic into a USER-EDITABLE
ruleset. Given a normalized signal (a commit / PR / release / workflow-run mapped
to a common dict) and a rules config, it produces Observatory `event` / `risk`
objects in the exact schema the Observatory payload consumes.

This is the "custom events people set up" surface: edit scripts/event-rules.json,
re-run the ingester, swap the dataset. No code change.

Signal shape (the common denominator the ingester normalizes everything into):
  { kind: "commit"|"pr"|"release"|"workflow",
    sha: "abc1234", date: "YYYY-MM-DD", subject: "feat(x): ...", body: "...",
    author: "login", labels: ["..."], status: "success"|"failure"|None,
    extra: {...} }

Rule match predicates (all must hold; omitted = ignored):
  subject_matches : regex (search) over subject
  body_matches    : regex over body
  prefix_in       : conventional-commit type ∈ list   (feat/fix/docs/chore/…)
  scope_in        : conventional-commit scope ∈ list
  author_in       : author ∈ list
  label_in        : any label ∈ list
  kind_in         : signal kind ∈ list
  status_in       : status ∈ list

Rule `set` fields (what the matched signal becomes):
  type, alt (L1–L5), conf (int), peak (bool)         → for event rules
  sev (RUIN/HIGH/MED), status (AVERTED/MITIGATED/OPEN), how, note → for risk rules
  label defaults to the cleaned subject if not set.

Order matters: the FIRST matching rule wins. No match → `default` (kept only if
default.keep is true). `drop` short-circuits to nothing (housekeeping noise).
"""
from __future__ import annotations
import json, os, re

DEFAULT_RULES_PATH = os.path.join(os.path.dirname(__file__), "event-rules.json")


def load_rules(path: str | None = None) -> dict:
    with open(path or DEFAULT_RULES_PATH) as f:
        return json.load(f)


def parse_conventional(subject: str):
    """feat(scope): subject  ->  ('feat', 'scope').  Best-effort; ('','') if none."""
    m = re.match(r"^([a-zA-Z]+)(?:\(([^)]+)\))?\s*!?:", subject or "")
    if not m:
        return "", ""
    return (m.group(1) or "").lower(), (m.group(2) or "").lower()


def clean_subject(subject: str) -> str:
    s = (subject or "").strip()
    # strip a trailing [NCI:xx] tag — arcs convention noise, harmless elsewhere
    return re.sub(r"\s*\[NCI:[^\]]*\]\s*$", "", s).strip()


def _matches(when: dict, sig: dict, prefix: str, scope: str) -> bool:
    if not when:
        return True
    subj = sig.get("subject", "") or ""
    body = sig.get("body", "") or ""
    if "subject_matches" in when and not re.search(when["subject_matches"], subj):
        return False
    if "body_matches" in when and not re.search(when["body_matches"], body):
        return False
    if "prefix_in" in when and prefix not in [p.lower() for p in when["prefix_in"]]:
        return False
    if "scope_in" in when and scope not in [s.lower() for s in when["scope_in"]]:
        return False
    if "author_in" in when and (sig.get("author") or "") not in when["author_in"]:
        return False
    if "kind_in" in when and (sig.get("kind") or "commit") not in when["kind_in"]:
        return False
    if "status_in" in when and (sig.get("status") or None) not in when["status_in"]:
        return False
    if "label_in" in when:
        labels = set(sig.get("labels") or [])
        if labels.isdisjoint(set(when["label_in"])):
            return False
    return True


def classify_event(sig: dict, rules: dict, first: bool = False) -> dict | None:
    """Apply event_rules to a signal → an Observatory event dict, or None to drop."""
    subj = sig.get("subject", "") or ""
    prefix, scope = parse_conventional(subj)

    drop = rules.get("drop")
    if drop and not first and _matches(drop, sig, prefix, scope):
        return None

    chosen = None
    for rule in rules.get("event_rules", []):
        if _matches(rule.get("when", {}), sig, prefix, scope):
            chosen = rule.get("set", {})
            break
    if chosen is None:
        d = rules.get("default", {})
        if not d.get("keep"):
            return None
        chosen = d

    ev = {
        "id": f"ev-{sig.get('sha', '')[:7]}",
        "date": sig.get("date"),
        "alt": chosen.get("alt", "L1"),
        "type": chosen.get("type", "feat"),
        "label": chosen.get("label") or clean_subject(subj),
        "sha": (sig.get("sha") or "")[:7],
        "desc": sig.get("body", "").strip() or clean_subject(subj),
        "conf": int(chosen.get("conf", 82)),
    }
    if first or chosen.get("peak"):
        ev["peak"] = True
    return ev


def classify_risk(sig: dict, rules: dict) -> dict | None:
    """Apply risk_rules to a signal → an Observatory risk dict, or None."""
    subj = sig.get("subject", "") or ""
    prefix, scope = parse_conventional(subj)
    for rule in rules.get("risk_rules", []):
        if _matches(rule.get("when", {}), sig, prefix, scope):
            st = rule.get("set", {})
            return {
                "id": f"risk-{sig.get('sha', '')[:7]}",
                "date": sig.get("date"),
                "risk": st.get("risk") or clean_subject(subj),
                "sev": st.get("sev", "MED"),
                "status": st.get("status", "MITIGATED"),
                "sha": (sig.get("sha") or "")[:7] or None,
                "how": st.get("how", "see commit"),
                "note": st.get("note") or clean_subject(subj),
            }
    return None


# ── self-test: run `python3 scripts/event_rules.py` to validate the engine offline ──
if __name__ == "__main__":
    rules = load_rules()
    fixtures = [
        {"kind": "commit", "sha": "aaaaaaa", "date": "2026-06-01", "subject": "feat(auth): RLS deny-all policies", "body": ""},
        {"kind": "commit", "sha": "bbbbbbb", "date": "2026-06-02", "subject": "feat(ui): Button component", "body": ""},
        {"kind": "commit", "sha": "ccccccc", "date": "2026-06-03", "subject": "fix(deploy): vercel adapter", "body": ""},
        {"kind": "commit", "sha": "ddddddd", "date": "2026-06-04", "subject": "chore(handoff): snapshot v2", "body": ""},
        {"kind": "commit", "sha": "eeeeeee", "date": "2026-06-05", "subject": "revert: bad migration", "body": ""},
    ]
    print("EVENTS:")
    for f in fixtures:
        e = classify_event(f, rules)
        print(f"  {f['subject'][:40]:42} -> {e and (e['type'], e['alt'], e['conf'], e.get('peak', False))}")
    print("RISKS:")
    for f in fixtures:
        r = classify_risk(f, rules)
        if r:
            print(f"  {f['subject'][:40]:42} -> {(r['sev'], r['status'])}")
