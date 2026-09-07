#!/usr/bin/env python3
"""gauntlet_prepass.py — the mechanical half of the counterpart gauntlet.

Runs the DETERMINISTIC defect classes over a counterpart artifact family ONCE,
before any agent is spawned, and emits a machine-readable baseline that
`.claude/workflows/counterpart-gauntlet.js` injects into every facet + the synth.

Why this exists (ADR-075, the metabolic router; _SPECS/gauntlet-cba-v1.md):
the gauntlet spends 6 persona agents + a synth re-reading the whole corpus, and
a large share of what they hunt is mechanically scorable — a grep, a diff, a
count. Those classes are cheaper AND more reliable as a script: caught every
run, deterministically, instead of probabilistically by whichever agent looked.
Correctness goes UP; the agents keep their judgment work (tone, situation,
respect, resonance) untouched.

This does NOT replace `scripts/leak_check.sh` — that is the repo-wide air-gap
CI gate and stays the source of truth for the internal-marker denylist. The
prepass COMPOSES it (runs it, folds its verdict in) and adds the gauntlet-only
classes leak_check does not cover.

Classes covered here (each maps to a facet's mechanical residue):
  - banned_lexicon      → skeptic facet: oversell / "words they'd never say"
  - cross_surface_dup   → bitesize facet: same span repeated across surfaces
  - false_precision     → builder facet (mechanical half): suspiciously exact numbers
  - employer_overexpose → air-gap policy: employer named more than once on a surface

Every finding is a CANDIDATE: the gauntlet's synth still verifies against the
transcript and rejects over-flags. The prepass never blocks — it informs.

Stdlib only. Usage:
    python3 scripts/gauntlet_prepass.py \
        --surface public/yuri.html --surface public/yuri-ext.html \
        --employer "Acme" --banned runtime/recoil/generated/yuri-banned.txt \
        --out _STATE/gauntlet/yuri-mechanical-baseline.json
    # --banned file: one term per line (the register card's don't-say list).
    # --employer: the current employer name air-gap policy allows named once.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from html.parser import HTMLParser

# Default oversell lexicon — generic hype a hype-allergic reader would never say
# at dinner. Conservative on purpose; a real run SHOULD pass --banned with the
# counterpart's register-card don't-say list, which is the judgment layer.
DEFAULT_BANNED = [
    "revolutionary", "game-chang", "game chang", "synerg", "supercharge",
    "seamless", "cutting-edge", "best-in-class", "world-class", "paradigm shift",
    "disrupt", "10x ", "unlock value", "north star", "move the needle",
    "at the end of the day", "circle back", "low-hanging fruit",
]


class _Text(HTMLParser):
    """Extract visible text from HTML (drop <script>/<style> bodies)."""
    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)

    def text(self):
        return re.sub(r"\s+", " ", " ".join(self.parts)).strip()


def visible_text(path):
    try:
        raw = open(path, encoding="utf-8", errors="replace").read()
    except OSError as e:
        return None, f"cannot read: {e}"
    p = _Text()
    p.feed(raw)
    return p.text(), None


def sentences(text):
    # crude but deterministic sentence split for cross-surface dup detection
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) >= 40]


def check_banned(label, text, banned):
    out = []
    low = text.lower()
    for term in banned:
        start = 0
        while True:
            i = low.find(term.lower(), start)
            if i < 0:
                break
            ctx = text[max(0, i - 30):i + len(term) + 30]
            out.append({"class": "banned_lexicon", "surface": label,
                        "evidence": term, "context": ctx.strip(), "confidence": "medium"})
            start = i + len(term)
    return out


def check_false_precision(label, text):
    # numbers a reader would hover on: >=3 sig-fig percents, exact-to-the-dollar
    # large amounts, decimal multipliers. Heuristic → medium/low confidence.
    out = []
    for m in re.finditer(r"\b\d{1,3}\.\d+%|\$\s?\d{1,3}(?:,\d{3})+(?:\.\d+)?|\b\d+\.\d+x\b", text):
        ctx = text[max(0, m.start() - 30):m.end() + 30]
        out.append({"class": "false_precision", "surface": label,
                    "evidence": m.group(0), "context": ctx.strip(), "confidence": "low"})
    return out


def check_employer(label, text, employer):
    if not employer:
        return []
    n = len(re.findall(re.escape(employer), text, flags=re.I))
    if n > 1:
        return [{"class": "employer_overexpose", "surface": label,
                 "evidence": f"{employer!r} appears {n}x (air-gap policy: once)",
                 "context": "", "confidence": "high"}]
    return []


def check_cross_surface_dup(texts):
    # a span (>=40 chars) appearing verbatim on 2+ surfaces = cross-surface repetition
    seen = {}
    for label, t in texts.items():
        for s in set(sentences(t)):
            seen.setdefault(s, []).append(label)
    out = []
    for s, labels in seen.items():
        if len(labels) >= 2:
            out.append({"class": "cross_surface_dup", "surface": ", ".join(sorted(labels)),
                        "evidence": s[:120] + ("…" if len(s) > 120 else ""),
                        "context": "", "confidence": "high"})
    return out


def run_leak_check(repo_root):
    """Compose the repo-wide air-gap gate. Returns (verdict, detail)."""
    script = os.path.join(repo_root, "scripts", "leak_check.sh")
    if not os.path.isfile(script):
        return "skipped", "scripts/leak_check.sh not found"
    try:
        r = subprocess.run(["bash", script], cwd=repo_root,
                           capture_output=True, text=True, timeout=120)
    except (subprocess.SubprocessError, OSError) as e:
        return "error", str(e)
    verdict = {0: "clean", 1: "leak", 2: "cannot-scan"}.get(r.returncode, f"exit{r.returncode}")
    tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-8:])
    return verdict, tail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--surface", action="append", default=[], metavar="PATH",
                    help="a surface HTML under review; repeat per surface")
    ap.add_argument("--employer", default="", help="current employer (air-gap: named once)")
    ap.add_argument("--banned", default="", help="file of don't-say terms, one per line (register card)")
    ap.add_argument("--repo-root", default=".", help="repo root for leak_check.sh")
    ap.add_argument("--out", default="", help="write baseline JSON here (default: stdout)")
    ap.add_argument("--no-leak-check", action="store_true", help="skip composing leak_check.sh")
    a = ap.parse_args()

    if not a.surface:
        ap.error("at least one --surface is required")

    banned = list(DEFAULT_BANNED)
    if a.banned:
        try:
            banned += [ln.strip() for ln in open(a.banned, encoding="utf-8") if ln.strip()]
        except OSError as e:
            print(f"warn: cannot read --banned {a.banned}: {e}", file=sys.stderr)

    findings, texts, unreadable = [], {}, []
    for path in a.surface:
        label = os.path.basename(path)
        text, err = visible_text(path)
        if err:
            unreadable.append({"surface": label, "error": err})
            continue
        texts[label] = text
        findings += check_banned(label, text, banned)
        findings += check_false_precision(label, text)
        findings += check_employer(label, text, a.employer)
    findings += check_cross_surface_dup(texts)

    leak_verdict, leak_detail = ("skipped", "")
    if not a.no_leak_check:
        leak_verdict, leak_detail = run_leak_check(a.repo_root)

    by_class = {}
    for f in findings:
        by_class[f["class"]] = by_class.get(f["class"], 0) + 1

    baseline = {
        "kind": "gauntlet-mechanical-baseline",
        "version": "v1",
        "surfaces": list(texts.keys()),
        "unreadable": unreadable,
        "leak_check": {"verdict": leak_verdict, "detail": leak_detail},
        "counts_by_class": by_class,
        "findings": findings,
        "note": ("These classes were checked DETERMINISTICALLY. Facets: do NOT "
                 "re-hunt them. Synth: dedupe agent findings against these and treat "
                 "a repeat as already-caught, not a new flag. Each is a candidate — "
                 "verify against the transcript before prescribing a fix."),
    }
    out = json.dumps(baseline, indent=2)
    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(out + "\n")
        print(f"wrote {a.out}  ·  {len(findings)} candidate finding(s) "
              f"across {len(texts)} surface(s)  ·  leak_check={leak_verdict}")
    else:
        print(out)

    # Never blocks — informs. The gauntlet is family-scoped; leak_check's
    # repo-wide verdict is folded into the baseline (and shouted below) for the
    # synth to escalate, but the HARD air-gap gate stays in CI (leak_check.sh
    # itself), not here. Always exit 0.
    if leak_verdict == "leak":
        print("  ⚠ leak_check reports a repo-wide air-gap LEAK — see baseline.leak_check; "
              "run `bash scripts/leak_check.sh` to locate. (Not blocking the gauntlet.)",
              file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
