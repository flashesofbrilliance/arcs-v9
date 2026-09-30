#!/usr/bin/env python3
"""
arcs_verb_eval.py - the five-verb print-schedule evals (ADR-068), stdlib only.

    Analysis by ARCS        -> fate: sourced | unsourced
    Assessment by ARCS      -> fate: verified | gap | unresolved (per claim) ; run: pass | fail
    Evaluation by ARCS      -> fate: pass | conditional pass | fail
    Synthesis by ARCS       -> fate: ship | hold
    Recapitulation by ARCS  -> fate: parked (a tool never sends; a human does)

Each verb has two halves:
  mechanical  hard gates; any failed gate exits 1 and sets the failing fate.
  judgment    rubric rows scored 0-2 by a human or model judge. The tool emits them
              pre-filled with evidence and score=null; pass --scores to fill them.
              The tool never grades judgment itself.

Lineage: each verb reads the previous verb's JSON print via --upstream, which is how
"verified must be sourced", "no new claims", and "note claims resolve" are checked
mechanically instead of on trust.

Anti-sycophancy: the Operator 25 Shavasana check (scripts/shavasana_handoff.py:76,
runtime/specs/operator-25-shavasana-v0.md component 5), same markers and thresholds,
re-stated here so the tool stays standalone. Report-only at analysis/assessment/synthesis;
blocking (RETURN fails) at evaluation and recapitulation.

Artifact conventions (the teardown_eval.py claim-span convention, extended):
  HTML claim   <span class="claim" data-id="c1" data-src="https://a,https://b"
                     data-stakes="high" data-verdict="gap" data-severity="high"
                     data-render="degraded">text</span>
  Assessment   <... data-summary="36/2/3"> verified/gap/unresolved counts, must match rows
  Gauntlet     JSON {"lenses":[{"name","result":"pass|fail|dissent","reason"}],
                     "verdict":"pass|conditional pass|fail",
                     "conditions":[{"id","claim","action":"drop|degrade","text"}]}
  Note (md)    front matter lines  status: DRAFT / ex_ante: <path> / gauntlet: <path>
               claims cited inline as [claim:c1]

Usage: see ./arcs-verb-eval (the shell runner) or --help.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from urllib.parse import urlparse

VERBS = ("analysis", "assessment", "evaluation", "synthesis", "recapitulation")
VERDICTS = ("verified", "gap", "unresolved")
SEVERITIES = ("low", "medium", "high")
MIN_LENSES = 4
EMDASH = "\u2014"

# ---- anti-sycophancy (Operator 25, component 5) --------------------------------------
DISSENT_RE = re.compile(r"\b(FALSIFIED|falsif|blocked|STOP:|refused|corrected|premise correction|deceipt|retract|red X|does not exist|not evidence|wrong|dissent|fail(ed|s)?)\b", re.I)
UNCONFIRMED_RE = re.compile(r"\b(unconfirmed|not verified|not checked|unverified|unresolved|assum(e|ed|ption))\b", re.I)
AGREE_RE = re.compile(r"\b(merged|shipped|done|complete|green|verified|confirmed|landed|agree[sd]?|pass(ed|es)?)\b", re.I)


def sycophancy(text: str, blocking: bool) -> dict:
    agree = len(AGREE_RE.findall(text))
    dissent = len(DISSENT_RE.findall(text)) + len(UNCONFIRMED_RE.findall(text))
    ratio = agree / (dissent + 1)
    if agree >= 5 and dissent == 0:
        verdict = "RETURN"
    elif ratio > 4:
        verdict = "THIN"
    else:
        verdict = "OK"
    return {"agreement": agree, "dissent": dissent, "ratio": round(ratio, 2),
            "verdict": verdict, "blocking": blocking}


# ---- artifact parsing ------------------------------------------------------------------
class _ClaimParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.claims, self.meta, self._stack, self.summary = [], [], [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "data-summary" in a:
            self.summary = a["data-summary"]
        if tag == "meta":
            self.meta.append(a)
        if "claim" in (a.get("class") or "").split():
            self._stack.append({"attrs": a, "text": [], "depth": 0})
        elif self._stack:
            self._stack[-1]["depth"] += 1

    def handle_endtag(self, tag):
        if not self._stack:
            return
        top = self._stack[-1]
        if top["depth"]:
            top["depth"] -= 1
            return
        self._stack.pop()
        a = top["attrs"]
        src = [s.strip() for s in (a.get("data-src") or "").split(",") if s.strip()]
        self.claims.append({
            "id": a.get("data-id") or f"auto{len(self.claims) + 1}",
            "text": " ".join("".join(top["text"]).split()),
            "src": src,
            "stakes": a.get("data-stakes", "normal"),
            "verdict": a.get("data-verdict"),
            "severity": a.get("data-severity"),
            "render": a.get("data-render"),
            "evidence": a.get("data-evidence"),
        })

    def handle_data(self, data):
        for s in self._stack:
            s["text"].append(data)


def parse_html(text: str) -> _ClaimParser:
    p = _ClaimParser()
    p.feed(text)
    p.close()
    return p


def visible_text(html: str) -> str:
    html = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", html)
    return re.sub(r"<[^>]+>", " ", html)


def load_json(path):
    return json.loads(Path(path).read_text()) if path else None


def load_ledger(path) -> set:
    keys = set()
    if not path:
        return keys
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        for k in ("source", "url", "src", "id"):
            if row.get(k):
                keys.add(str(row[k]))
    return keys


def host(s: str) -> str:
    return urlparse(s).netloc or s


def digest(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()[:12]


# ---- report plumbing -------------------------------------------------------------------
class Run:
    def __init__(self, verb: str):
        import time
        self._clock = time.perf_counter
        self._last = self._clock()
        self.verb, self.gates, self.rubric = verb, [], []

    def gate(self, gid: str, ok: bool, evidence: str):
        now = self._clock()
        self.gates.append({"id": gid, "ok": bool(ok), "evidence": evidence, "ms": round((now - self._last) * 1000, 3)})
        self._last = now

    def row(self, rid: str, label: str, evidence: str = ""):
        self.rubric.append({"row": rid, "label": label, "evidence": evidence, "score": None, "judge": "pending"})

    @property
    def ok(self) -> bool:
        return all(g["ok"] for g in self.gates)

    def failed(self):
        return [g["id"] for g in self.gates if not g["ok"]]


def apply_scores(run: Run, scores: dict | None):
    if not scores:
        return
    for r in run.rubric:
        if r["row"] in scores:
            v = scores[r["row"]]
            if v not in (0, 1, 2):
                raise SystemExit(f"score for {r['row']} must be 0, 1 or 2, got {v!r}")
            r["score"], r["judge"] = v, scores.get("_judge", "human")


# ---- the five verbs --------------------------------------------------------------------
def analysis(text: str, ledger: set | None = None, **_) -> tuple[Run, dict]:
    run = Run("analysis")
    p = parse_html(text)
    cl = p.claims
    run.gate("has-claims", len(cl) > 0, f"{len(cl)} claim spans")
    unsourced = [c["id"] for c in cl if not c["src"]]
    run.gate("every-claim-sourced", not unsourced, f"{len(cl) - len(unsourced)}/{len(cl)} sourced" + (f"; unsourced: {', '.join(unsourced)}" if unsourced else ""))
    thin = [c["id"] for c in cl if c["stakes"] == "high" and len({host(s) for s in c["src"]}) < 2]
    run.gate("high-stakes-two-sources", not thin, f"{sum(c['stakes'] == 'high' for c in cl)} high-stakes" + (f"; under 2 hosts: {', '.join(thin)}" if thin else ""))
    if ledger is not None and ledger:
        orphan = sorted({s for c in cl for s in c["src"] if s not in ledger})
        run.gate("sources-in-ledger", not orphan, f"{len(orphan)} orphan" + (f": {', '.join(orphan[:5])}" if orphan else ""))
    hosts = {host(s) for c in cl for s in c["src"]}
    run.row("coverage", "Coverage: the obvious records were pulled", f"{len(hosts)} source hosts")
    run.row("primary", "Primary source over a summary of it")
    run.row("open-question", "The question stays open; no conclusion slipped in")
    run.row("anomalies", "Anomalies logged, not dropped")
    fate = "sourced" if run.ok else "unsourced"
    return run, {"fate": fate, "claims": [{k: c[k] for k in ("id", "text", "src", "stakes")} for c in cl]}


def assessment(text: str, upstream: dict | None = None, **_) -> tuple[Run, dict]:
    run = Run("assessment")
    p = parse_html(text)
    cl = p.claims
    run.gate("has-claims", len(cl) > 0, f"{len(cl)} claim spans")
    bad = [c["id"] for c in cl if c["verdict"] not in VERDICTS or c["severity"] not in SEVERITIES]
    run.gate("verdict-and-severity", not bad, f"{len(cl) - len(bad)}/{len(cl)} rows complete" + (f"; incomplete: {', '.join(bad)}" if bad else ""))
    if upstream is not None:
        sourced = {c["id"] for c in upstream.get("claims", []) if c.get("src")}
        rogue = [c["id"] for c in cl if c["verdict"] == "verified" and c["id"] not in sourced]
        run.gate("verified-was-sourced", not rogue, f"{sum(c['verdict'] == 'verified' for c in cl) - len(rogue)} verified resolve upstream" + (f"; not sourced upstream: {', '.join(rogue)}" if rogue else ""))
    with_ev = [c for c in cl if c["verdict"] == "verified" and c.get("evidence")]
    if with_ev:
        num = re.compile(r"(?<![\w.])\d+(?:\.\d+)?")
        drift = [c["id"] for c in with_ev if not set(num.findall(c["text"])) & set(num.findall(c["evidence"]))]
        run.gate("verified-numbers-in-evidence", not drift, f"{len(with_ev) - len(drift)}/{len(with_ev)} verified claims share a number with their evidence" + (f"; drifted: {', '.join(drift)}" if drift else ""))
    counts = [sum(c["verdict"] == v for c in cl) for v in VERDICTS]
    actual = "/".join(map(str, counts))
    run.gate("summary-matches-rows", p.summary == actual, f"header {p.summary or 'missing'} vs rows {actual}")
    run.row("severity-calibrated", "Severity calibrated to consequence")
    run.row("gaps-plain", "Gaps stated as plainly as wins", f"{counts[1]} gap rows")
    run.row("no-hedge-inflation", "No hedge inflation")
    run.row("objection-table", "Objection table present")
    fate = "pass" if run.ok else "fail"
    return run, {"fate": fate, "counts": dict(zip(VERDICTS, counts)),
                 "claims": [{k: c[k] for k in ("id", "text", "src", "verdict", "severity")} for c in cl]}


def evaluation(text: str, upstream: dict | None = None, min_lenses: int = MIN_LENSES, **_) -> tuple[Run, dict]:
    run = Run("evaluation")
    min_lenses = int(min_lenses)
    g = json.loads(text)
    lenses = g.get("lenses", [])
    run.gate("min-lenses", len(lenses) >= min_lenses, f"{len(lenses)} lenses (min {min_lenses}): " + ", ".join(l.get("name", "?") for l in lenses))
    incomplete = [l.get("name", "?") for l in lenses if l.get("result") not in ("pass", "fail", "dissent") or not (l.get("reason") or "").strip()]
    run.gate("lens-result-and-reason", not incomplete, f"{len(lenses) - len(incomplete)}/{len(lenses)} complete" + (f"; incomplete: {', '.join(incomplete)}" if incomplete else ""))
    dissenters = [l.get("name", "?") for l in lenses if l.get("result") in ("fail", "dissent")]
    run.gate("dissent-floor", bool(dissenters), f"{len(dissenters)} dissent: {', '.join(dissenters)}" if dissenters else "no lens dissented; a gauntlet nothing could fail is not a gauntlet")
    verdict, conds = g.get("verdict"), g.get("conditions", [])
    fails = [l for l in lenses if l.get("result") == "fail"]
    consistent = (verdict == "fail") or (verdict == "conditional pass" and bool(conds)) or (verdict == "pass" and not fails and not conds)
    run.gate("verdict-follows", verdict in ("pass", "conditional pass", "fail") and consistent,
             f"verdict {verdict!r} · {len(fails)} fail lenses · {len(conds)} conditions")
    if upstream is not None:
        ids = {c["id"] for c in upstream.get("claims", [])}
        dangling = [c.get("id", "?") for c in conds if c.get("claim") and c["claim"] not in ids]
        run.gate("conditions-cite-claims", not dangling, f"{len(conds)} conditions" + (f"; dangling: {', '.join(dangling)}" if dangling else ""))
    syc = sycophancy(" ".join(f"{l.get('result', '')} {l.get('reason', '')}" for l in lenses), blocking=True)
    run.gate("sycophancy", syc["verdict"] != "RETURN", f"{syc['verdict']} · agreement {syc['agreement']} · dissent {syc['dissent']}")
    run.row("dissent-real", "Strongest dissent is real, not a straw man")
    run.row("product-truth", "Product truth argued")
    run.row("proof-truth", "Proof truth argued")
    run.row("conditions-concrete", "Conditions on the pass are concrete", f"{len(conds)} conditions")
    fate = verdict if run.ok else "fail"
    carried = (upstream or {}).get("claims", [])
    return run, {"fate": fate, "verdict": verdict, "conditions": conds, "claims": carried, "_syc": syc}


def synthesis(text: str, upstream: dict | None = None, public: bool = False, slop: bool = True, slop_lint: str | None = None, slop_args: list | None = None, **_) -> tuple[Run, dict]:
    run = Run("synthesis")
    p = parse_html(text)
    cl = p.claims
    up_claims = {c["id"]: c for c in (upstream or {}).get("claims", [])}
    if upstream is not None:
        new = [c["id"] for c in cl if c["id"] not in up_claims]
        run.gate("no-new-claims", not new, f"{len(cl) - len(new)}/{len(cl)} resolve upstream" + (f"; new: {', '.join(new)}" if new else ""))
        present = {c["id"]: c for c in cl}
        open_c = []
        for cond in upstream.get("conditions", []):
            cid, act = cond.get("claim"), cond.get("action")
            if cid in present and (act == "drop" or (act == "degrade" and present[cid]["render"] in (None, "sharp"))):
                open_c.append(f"{cond.get('id', '?')} ({act} {cid})")
        run.gate("conditions-honored", not open_c, "all closed" if not open_c else "open: " + ", ".join(open_c))
        oversharp = [c["id"] for c in cl if up_claims.get(c["id"], {}).get("verdict") in ("gap", "unresolved") and c["render"] in (None, "sharp")]
        run.gate("render-matches-verdict", not oversharp, "earned fidelity holds" if not oversharp else "gap/unresolved rendered sharp: " + ", ".join(oversharp))
    n_dash = visible_text(text).count(EMDASH)
    run.gate("em-dash-zero", n_dash == 0, f"{n_dash} em-dashes in visible text")
    if not public:
        noindex = any(m.get("name") == "robots" and "noindex" in (m.get("content") or "") for m in p.meta)
        run.gate("noindex", noindex, "robots noindex present" if noindex else "missing <meta name=robots content=noindex> (pass --public to waive)")
    if slop:
        lint = Path(slop_lint) if slop_lint else find_repo_script("slop_lint.py")
        if lint:
            with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as fh:
                fh.write(text)
            r = subprocess.run([sys.executable, str(lint), *(slop_args or []), fh.name], capture_output=True, text=True)
            Path(fh.name).unlink(missing_ok=True)
            tail = (r.stdout.strip().splitlines() or ["clean"])[-1][:160]
            run.gate("slop-lint", r.returncode == 0, tail)
    words_out = len(visible_text(text).split())
    run.row("A-word", "Slop-free rubric A: word level")
    run.row("B-structure", "Slop-free rubric B: structure")
    run.row("C-rhythm", "Slop-free rubric C: rhythm")
    run.row("D-specificity", "Slop-free rubric D: specificity, the positive test")
    run.row("compression", "Compression holds near 1:5", f"{words_out} words out")
    fate = "ship" if run.ok else "hold"
    carried = [c for c in cl if c["id"] in up_claims] if upstream is not None else cl
    return run, {"fate": fate, "claims": [{"id": c["id"], "text": c["text"]} for c in carried]}


FM_RE = re.compile(r"^(status|ex_ante|gauntlet)\s*:\s*(.+?)\s*$", re.M | re.I)
CITE_RE = re.compile(r"\[claim:([\w.-]+)\]")


def recapitulation(text: str, upstream: dict | None = None, base: Path | None = None, **_) -> tuple[Run, dict]:
    run = Run("recapitulation")
    fm = {k.lower(): v for k, v in FM_RE.findall(text)}
    run.gate("draft-marker", fm.get("status", "").upper() == "DRAFT", f"status: {fm.get('status', 'missing')}")
    base = base or Path.cwd()
    for key, gid in (("ex_ante", "ex-ante-receipt"), ("gauntlet", "pre-send-gauntlet")):
        ref = fm.get(key)
        ok = bool(ref) and (base / ref).exists()
        run.gate(gid, ok, f"{ref} resolves" if ok else f"{key}: {ref or 'missing'} does not resolve")
    cites = CITE_RE.findall(text)
    if upstream is not None:
        ids = {c["id"] for c in upstream.get("claims", [])}
        rogue = [c for c in cites if c not in ids]
        run.gate("note-claims-resolve", not rogue, f"{len(cites) - len(rogue)}/{len(cites)} resolve to synthesis" + (f"; unknown: {', '.join(rogue)}" if rogue else ""))
    syc = sycophancy(text, blocking=True)
    run.gate("sycophancy", syc["verdict"] != "RETURN", f"{syc['verdict']} · agreement {syc['agreement']} · dissent {syc['dissent']}")
    run.row("register-fit", "Register fits the counterpart")
    run.row("release-honest", "Released and kept claims honest in both directions")
    run.row("ask-concrete", "The ask is concrete")
    run.row("close-loop", "Close-loop obligation logged")
    fate = "parked" if run.ok else "blocked"
    return run, {"fate": fate, "claims_cited": cites, "_syc": syc}


VERB_FN = {"analysis": analysis, "assessment": assessment, "evaluation": evaluation,
           "synthesis": synthesis, "recapitulation": recapitulation}


def find_repo_script(name: str) -> Path | None:
    for d in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents]:
        if (d / "scripts" / name).exists():
            return d / "scripts" / name
    return None


def evaluate(verb: str, text: str, upstream: dict | None = None, scores: dict | None = None, **opts) -> dict:
    """Importable entry point. Returns the print (a JSON-serialisable dict)."""
    if verb not in VERB_FN:
        raise ValueError(f"unknown verb {verb!r}; one of {', '.join(VERBS)}")
    skip = set(opts.pop("skip_gates", None) or [])
    run, carry = VERB_FN[verb](text, upstream=upstream, **opts)
    for g in run.gates:
        if g["id"] in skip:
            g.update(ok=True, skipped=True, evidence="SKIPPED by config: " + g["evidence"])
    if skip and carry.get("fate") in ("unsourced", "fail", "hold", "blocked") and run.ok:
        carry["fate"] = {"analysis": "sourced", "assessment": "pass", "synthesis": "ship",
                         "recapitulation": "parked", "evaluation": carry.get("verdict")}.get(verb, carry["fate"])
    apply_scores(run, scores)
    syc = carry.pop("_syc", None) or sycophancy(visible_text(text), blocking=False)
    out = {"verb": verb, "tool": f"{verb.capitalize()} by ARCS", "fate": carry.pop("fate"),
           "ok": run.ok, "failed": run.failed(), "artifact": digest(text),
           "upstream": (upstream or {}).get("artifact"), "gates": run.gates,
           "rubric": run.rubric, "sycophancy": syc}
    out.update(carry)
    out["trace"] = trace_events(out)
    return out


# ---- trace: which lane decided what ---------------------------------------------------
# lane "rules": a fixed check; same input, same answer; decides go/stop.
# lane "judge": a rubric question for a person or a model. The tool never sends it; the event
# carries the exact prompt that WOULD be sent, and sent=false. Judge scores never change fate.
JUDGE_PROMPT = ("You are scoring one row of the {tool} rubric.\n"
                "Question: {label}\n"
                "Score 0, 1 or 2. Reply with the number and one sentence of reason.\n"
                "Machine-check evidence for this step:\n{evidence}\n"
                "Artifact: {artifact}")


def judge_prompt(rep: dict, row: dict) -> str:
    ev = "\n".join(f"- {g['id']}: {'pass' if g['ok'] else 'fail'} ({g['evidence']})" for g in rep["gates"])
    if row.get("evidence"):
        ev += f"\n- row hint: {row['evidence']}"
    return JUDGE_PROMPT.format(tool=rep["tool"], label=row["label"], evidence=ev, artifact=rep["artifact"])


def trace_events(rep: dict) -> list[dict]:
    ev = [{"lane": "rules", "verb": rep["verb"], "id": g["id"], "ok": g["ok"], "ms": g.get("ms"),
           "evidence": g["evidence"], "skipped": bool(g.get("skipped"))} for g in rep["gates"]]
    for r in rep["rubric"]:
        ev.append({"lane": "judge", "verb": rep["verb"], "id": r["row"], "label": r["label"],
                   "sent": False, "score": r["score"], "judge": r["judge"], "prompt": judge_prompt(rep, r)})
    ev.append({"lane": "summary", "verb": rep["verb"], "rules": len(rep["gates"]), "llm_calls": 0,
               "judge_pending": sum(r["score"] is None for r in rep["rubric"]), "fate": rep["fate"],
               "decided_by": "rules"})
    return ev


def write_trace(rep: dict, dest: str | None):
    if not dest:
        return
    lines = "".join(json.dumps(e) + "\n" for e in rep["trace"])
    if dest == "-":
        sys.stderr.write(lines)
    else:
        with open(dest, "a") as fh:
            fh.write(lines)


# ---- rendering -------------------------------------------------------------------------
def human(rep: dict) -> str:
    lines = [f"{rep['tool']}  ->  fate: {rep['fate'].upper()}", ""]
    for g in rep["gates"]:
        tag = "SKIP" if g.get("skipped") else ("PASS" if g["ok"] else "FAIL")
        lines.append(f"  {tag}  {g['id']:<26} {g['evidence']}")
    s = rep["sycophancy"]
    lines.append(f"  {'----' if not s['blocking'] else 'GATE'}  sycophancy {s['verdict']:<15} agreement {s['agreement']} · dissent {s['dissent']} · ratio {s['ratio']}")
    lines += ["", "  judgment (0-2, scored by a judge, never by this tool):"]
    for r in rep["rubric"]:
        sc = "--" if r["score"] is None else f"{r['score']}/2"
        lines.append(f"    [{sc}] {r['label']}" + (f"  ({r['evidence']})" if r["evidence"] else ""))
        if r.get("reason"):
            lines.append(f"          {r['judge']}: {r['reason']}")
    calls = rep.get("judge_calls")
    summ = rep["trace"][-1] if rep.get("trace") else {}
    n_llm = summ.get("llm_calls", 0)
    lines.append(f"\n  lanes: {len(rep['gates'])} rule checks decided the stamp · {n_llm} LLM calls" + (" (scores only)" if n_llm else "")
                 + (f" · {summ['llm_errors']} judge errors" if summ.get("llm_errors") else ""))
    return "\n".join(lines)


# ---- self-test: fails-on-bad AND passes-on-good, per verb, chained ---------------------
GOOD = {
    "analysis": """<html><body>
<span class="claim" data-id="c1" data-src="https://a.example/demo">Onboarding takes under 10 minutes.</span>
<span class="claim" data-id="c2" data-stakes="high" data-src="https://a.example/deck,https://b.example/cases">The deck says 40 customers.</span>
<span class="claim" data-id="c3" data-src="https://c.example/trust">No SOC 2 report was found.</span>
</body></html>""",
    "assessment": """<html><body><div data-summary="1/1/1">
<span class="claim" data-id="c1" data-verdict="verified" data-severity="low">Onboarding under 10 minutes.</span>
<span class="claim" data-id="c2" data-verdict="gap" data-severity="high">Deck says 40; case page lists 12.</span>
<span class="claim" data-id="c3" data-verdict="unresolved" data-severity="medium">SOC 2 status unknown.</span>
</div></body></html>""",
    "evaluation": json.dumps({"lenses": [
        {"name": "LAB", "result": "pass", "reason": "claims trace to records"},
        {"name": "BAR", "result": "dissent", "reason": "ruin path if the 40 figure is wrong"},
        {"name": "Loki", "result": "dissent", "reason": "the SOC 2 gap was assumed away in the deck"},
        {"name": "dual bar-raiser", "result": "pass", "reason": "product truth holds, proof truth thin"}],
        "verdict": "conditional pass",
        "conditions": [{"id": "k1", "claim": "c2", "action": "degrade", "text": "degrade the 40 figure"}]}),
    "synthesis": """<html><head><meta name="robots" content="noindex"></head><body>
<p><span class="claim" data-id="c1" data-render="sharp">Setup is quick: under ten minutes on the demo.</span>
<span class="claim" data-id="c2" data-render="degraded">Customer count is contested: the deck says 40, the case page lists 12.</span>
<span class="claim" data-id="c3" data-render="grain">SOC 2 status could not be confirmed.</span></p>
</body></html>""",
    "recapitulation": """status: DRAFT
ex_ante: ex-ante.json
gauntlet: gauntlet.json

Thanks for the time today. Setup looked quick [claim:c1]. One thing I could not square:
the customer count [claim:c2]. Could you point me to the source for 40? SOC 2 is still
unconfirmed on my side [claim:c3].
""",
}

# each bad case: (verb, mutate(good_text) -> bad_text, gate that must fail)
BAD = [
    ("analysis", lambda t: t.replace(' data-src="https://c.example/trust"', ""), "every-claim-sourced"),
    ("analysis", lambda t: t.replace("https://a.example/deck,https://b.example/cases", "https://a.example/deck"), "high-stakes-two-sources"),
    ("assessment", lambda t: t.replace('data-summary="1/1/1"', 'data-summary="2/1/0"'), "summary-matches-rows"),
    ("assessment", lambda t: t.replace('data-verdict="unresolved" data-severity="medium"', 'data-verdict="maybe" data-severity="medium"'), "verdict-and-severity"),
    ("assessment", lambda t: t.replace('data-id="c1"', 'data-id="c9"'), "verified-was-sourced"),
    ("evaluation", lambda t: t.replace('"dissent"', '"pass"'), "dissent-floor"),
    ("evaluation", lambda t: json.dumps({**json.loads(t), "lenses": json.loads(t)["lenses"][:2]}), "min-lenses"),
    ("evaluation", lambda t: t.replace('"conditional pass"', '"pass"'), "verdict-follows"),
    ("evaluation", lambda t: json.dumps({"verdict": "pass", "conditions": [], "lenses": [
        {"name": n, "result": "pass", "reason": "verified, confirmed, shipped, green, done"} for n in ("A", "B", "C", "D")]}), "sycophancy"),
    ("synthesis", lambda t: t.replace("</p>", '<span class="claim" data-id="c7">Trusted by 50+ teams.</span></p>'), "no-new-claims"),
    ("synthesis", lambda t: t.replace('data-id="c2" data-render="degraded"', 'data-id="c2" data-render="sharp"'), "conditions-honored"),
    ("synthesis", lambda t: t.replace('data-id="c3" data-render="grain"', 'data-id="c3"'), "render-matches-verdict"),
    ("synthesis", lambda t: t.replace("contested: the", "contested " + EMDASH + " the"), "em-dash-zero"),
    ("synthesis", lambda t: t.replace('<meta name="robots" content="noindex">', ""), "noindex"),
    ("recapitulation", lambda t: t.replace("status: DRAFT", "status: SENT"), "draft-marker"),
    ("recapitulation", lambda t: t.replace("ex_ante: ex-ante.json", "ex_ante: missing.json"), "ex-ante-receipt"),
    ("recapitulation", lambda t: t.replace("[claim:c3]", "[claim:c8]"), "note-claims-resolve"),
    ("recapitulation", lambda t: "status: DRAFT\nex_ante: ex-ante.json\ngauntlet: gauntlet.json\n\nAll verified, confirmed, shipped, green and done. Agreed.\n", "sycophancy"),
]


def self_test() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="arcs-verb-eval-"))
    (tmp / "ex-ante.json").write_text("{}")
    (tmp / "gauntlet.json").write_text("{}")
    opts = {"base": tmp, "slop": False}
    passed = failed = 0

    def check(cond, msg):
        nonlocal passed, failed
        passed, failed = passed + bool(cond), failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'}  {msg}")

    print("pass-on-good (chained through --upstream):")
    prints, up = {}, None
    for v in VERBS:
        rep = evaluate(v, GOOD[v], upstream=up, **opts)
        check(rep["ok"], f"{v:<15} good fixture passes -> {rep['fate']}" + ("" if rep["ok"] else f"  failed: {rep['failed']}"))
        prints[v], up = rep, rep
    print("fails-on-bad (each gate proven to fire on its own mutation):")
    for v, mut, gate in BAD:
        up = prints[VERBS[VERBS.index(v) - 1]] if v != "analysis" else None
        rep = evaluate(v, mut(GOOD[v]), upstream=up, **opts)
        check(gate in rep["failed"], f"{v:<15} {gate:<26} fires" + ("" if gate in rep["failed"] else f"  (failed: {rep['failed']})"))
    tr = prints["synthesis"]["trace"]
    check(all(e["sent"] is False for e in tr if e["lane"] == "judge") and tr[-1]["llm_calls"] == 0,
          "trace: judge lane never sends; llm_calls is 0")
    check(all(e["lane"] == "rules" for e in tr if e.get("ok") is not None) and tr[-1]["decided_by"] == "rules",
          "trace: every go/stop decision comes from the rules lane")
    covered = {g for _, _, g in BAD}
    all_gates = {g["id"] for r in prints.values() for g in r["gates"]} - {"has-claims", "lens-result-and-reason", "conditions-cite-claims", "pre-send-gauntlet", "sources-in-ledger", "slop-lint"}
    check(all_gates <= covered, f"every gate that can fail has a bad fixture (uncovered: {sorted(all_gates - covered) or 'none'})")
    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


# ---- optional HTTP surface (stdlib) ----------------------------------------------------
def serve(port: int):
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            verb = self.path.rstrip("/").rsplit("/", 1)[-1]
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                rep = evaluate(verb, body["artifact"], upstream=body.get("upstream"),
                               scores=body.get("scores"), public=body.get("public", False), slop=False)
                code, payload = 200, rep
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                code, payload = 400, {"error": str(e)}
            data = json.dumps(payload).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    print(f"arcs-verb-eval listening on http://127.0.0.1:{port}/eval/<verb>")
    HTTPServer(("127.0.0.1", port), H).serve_forever()


# ---- componentized CLI: config -> env -> --set, then per-verb opts --------------------
# Precedence (lowest to highest): built-in defaults < config file < ARCS_VERB_EVAL_* env < --set.
# Config shape (JSON, or TOML on python >= 3.11):
#   {"defaults": {"slop": true},
#    "analysis": {"ledger": "evidence.jsonl"},
#    "evaluation": {"min_lenses": 6, "skip_gates": []},
#    "synthesis": {"public": false, "slop_lint": "scripts/slop_lint.py", "slop_args": []},
#    "pipeline": {"analysis": "teardown.html", ..., "outdir": "prints"}}
ENV_PREFIX = "ARCS_VERB_EVAL_"


def load_config(path: str | None) -> dict:
    if not path:
        return {}
    p = Path(path)
    if p.suffix == ".toml":
        import tomllib  # stdlib on 3.11+
        return tomllib.loads(p.read_text())
    return json.loads(p.read_text())


def coerce(v: str):
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    try:
        return json.loads(v)
    except json.JSONDecodeError:
        return v


def resolve_opts(verb: str, cfg: dict, sets: list[str]) -> dict:
    import os
    opts = dict(cfg.get("defaults", {}))
    opts.update(cfg.get(verb, {}))
    for k, v in os.environ.items():
        if k.startswith(ENV_PREFIX) and k != ENV_PREFIX + "CONFIG":
            key = k[len(ENV_PREFIX):].lower()
            scope, _, name = key.partition("__")
            if name and scope == verb:
                opts[name] = coerce(v)
            elif not name:
                opts[key] = coerce(v)
    for kv in sets:
        k, _, v = kv.partition("=")
        scope, _, name = k.partition(".")
        if name and scope == verb:
            opts[name] = coerce(v)
        elif not name:
            opts[k] = coerce(v)
    return opts


def run_one(verb: str, artifact: str, opts: dict, upstream: dict | None, scores: dict | None) -> dict:
    path = None if artifact == "-" else Path(artifact)
    text = sys.stdin.read() if path is None else path.read_text()
    opts = dict(opts)
    ledger = opts.pop("ledger", None)
    opts.setdefault("base", path.parent if path else Path.cwd())
    return evaluate(verb, text, upstream=upstream, scores=scores,
                    ledger=load_ledger(ledger) if ledger else None, **opts)


def env_report(cfg: dict, sets: list[str]) -> dict:
    import platform
    lint = find_repo_script("slop_lint.py")
    return {"runtime": {"python": sys.executable, "version": platform.python_version(),
                        "toml_config": sys.version_info >= (3, 11)},
            "deps": {"third_party": [], "stdlib": ["argparse", "html.parser", "json", "re", "hashlib", "http.server", "subprocess"]},
            "srcs": {"engine": str(Path(__file__).resolve()), "slop_lint": str(lint) if lint else None},
            "effective_opts": {v: {k: str(x) for k, x in resolve_opts(v, cfg, sets).items()} for v in VERBS}}


def main(argv=None) -> int:
    import os
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config", default=os.environ.get(ENV_PREFIX + "CONFIG"), help="JSON or TOML config (also $ARCS_VERB_EVAL_CONFIG)")
    common.add_argument("--set", action="append", default=[], metavar="K=V", help="pass-through override; verb-scoped as verb.key=value (repeatable)")
    common.add_argument("--skip-gate", action="append", default=[], metavar="ID", help="waive a gate by id; recorded as SKIPPED in the print")
    common.add_argument("--json", action="store_true", help="print JSON instead of the human report")
    common.add_argument("--judge", action="store_true", help="score the rubric with Claude (needs the anthropic SDK + ANTHROPIC_API_KEY); never changes go/stop")
    common.add_argument("--judge-model", default=None, help="judge model (default claude-opus-5-5)")
    common.add_argument("--trace", metavar="FILE", help="append one JSON event per check (lane rules|judge|summary); - for stderr")

    ap = argparse.ArgumentParser(prog="arcs-verb-eval", description="Five-verb print-schedule evals (ADR-068).", parents=[common])
    ap.add_argument("--self-test", action="store_true", help="prove fails-on-bad and passes-on-good for every gate")
    sub = ap.add_subparsers(dest="cmd")
    for v in VERBS:
        sp = sub.add_parser(v, parents=[common], help=f"{v.capitalize()} by ARCS")
        sp.add_argument("artifact", help="artifact file, or - for stdin")
        sp.add_argument("--upstream", help="previous verb's JSON print")
        sp.add_argument("--ledger", help="evidence.jsonl (analysis)")
        sp.add_argument("--scores", help="JSON {row_id: 0|1|2, _judge: name}")
        sp.add_argument("--out", help="write the JSON print here")
        sp.add_argument("--public", action="store_true", help="synthesis: waive noindex")
        sp.add_argument("--no-slop", action="store_true", help="synthesis: skip slop_lint.py")
        sp.add_argument("--slop-arg", action="append", default=[], help="pass-through arg to slop_lint.py (repeatable)")
    pp = sub.add_parser("pipeline", parents=[common], help="run the whole arc, chaining each print into the next")
    for v in VERBS:
        pp.add_argument(f"--{v}", help=f"{v} artifact")
    pp.add_argument("--outdir", default=None, help="where to write <verb>.json prints")
    pp.add_argument("--keep-going", action="store_true", help="continue past a failing verb")
    ig = sub.add_parser("ingest", parents=[common], help="data in: notebook (.ipynb) or claims table (.csv/.jsonl) -> artifacts")
    ig.add_argument("source")
    ig.add_argument("--outdir", required=True)
    ig.add_argument("--format", choices=("ipynb", "table"))
    ig.add_argument("--mutate", type=int, default=0, help="also write N corrupted negative fixtures")
    ex = sub.add_parser("export", parents=[common], help="data out: prints dir -> jsonl | csv | md | junit | receipt")
    ex.add_argument("prints_dir")
    ex.add_argument("--format", required=True, choices=("jsonl", "csv", "md", "junit", "receipt"))
    ex.add_argument("--question", default="")
    ex.add_argument("--out", help="file to write (default stdout)")
    sub.add_parser("env", parents=[common], help="show runtime, deps, resolved srcs, effective opts")
    sv = sub.add_parser("serve", parents=[common], help="stdlib HTTP: POST /eval/<verb>")
    sv.add_argument("--port", type=int, default=8787)

    a = ap.parse_args(argv)
    if a.self_test:
        import arcs_verb_eval_io as vio
        print("== core ==")
        rc = self_test()
        print("\n== io ==")
        rc = rc or vio.self_test()
        import arcs_verb_eval_judge as vj
        print("\n== judge (offline, fake client) ==")
        return rc or vj.self_test()
    cfg = load_config(a.config)
    if a.cmd == "ingest":
        import arcs_verb_eval_io as vio
        print(json.dumps(vio.ingest(a.source, a.outdir, a.format, a.mutate), indent=2))
        return 0
    if a.cmd == "export":
        import arcs_verb_eval_io as vio
        text = vio.export(a.prints_dir, a.format, a.question)
        if a.out:
            Path(a.out).parent.mkdir(parents=True, exist_ok=True)
            Path(a.out).write_text(text)
        else:
            sys.stdout.write(text)
        return 0
    if a.cmd == "env":
        print(json.dumps(env_report(cfg, a.set), indent=2))
        return 0
    if a.cmd == "serve":
        serve(a.port)
        return 0
    if a.cmd in VERBS:
        opts = resolve_opts(a.cmd, cfg, a.set)
        if a.ledger: opts["ledger"] = a.ledger
        if a.public: opts["public"] = True
        if a.no_slop: opts["slop"] = False
        if a.slop_arg: opts["slop_args"] = a.slop_arg
        if a.skip_gate: opts["skip_gates"] = opts.get("skip_gates", []) + a.skip_gate
        rep = run_one(a.cmd, a.artifact, opts, load_json(a.upstream), load_json(a.scores))
        if a.judge:
            import arcs_verb_eval_judge as vj
            art = sys.stdin.read() if a.artifact == "-" else Path(a.artifact).read_text()
            rep = vj.judge(rep, art, model=a.judge_model or vj.DEFAULT_MODEL)
        write_trace(rep, a.trace)
        if a.out:
            Path(a.out).parent.mkdir(parents=True, exist_ok=True)
            Path(a.out).write_text(json.dumps(rep, indent=2) + "\n")
        print(json.dumps(rep, indent=2) if a.json else human(rep))
        return 0 if rep["ok"] else 1
    if a.cmd == "pipeline":
        pcfg = cfg.get("pipeline", {})
        outdir = Path(a.outdir or pcfg.get("outdir", "prints"))
        outdir.mkdir(parents=True, exist_ok=True)
        up, code, summary = None, 0, []
        for v in VERBS:
            art = getattr(a, v) or pcfg.get(v)
            if not art:
                summary.append({"verb": v, "fate": "not run"})
                continue
            opts = resolve_opts(v, cfg, a.set)
            if a.skip_gate: opts["skip_gates"] = opts.get("skip_gates", []) + a.skip_gate
            rep = run_one(v, art, opts, up, None)
            if a.judge:
                import arcs_verb_eval_judge as vj
                rep = vj.judge(rep, Path(art).read_text(), model=a.judge_model or vj.DEFAULT_MODEL)
            write_trace(rep, a.trace)
            (outdir / f"{v}.json").write_text(json.dumps(rep, indent=2) + "\n")
            summary.append({"verb": v, "fate": rep["fate"], "failed": rep["failed"]})
            if not a.json:
                print(human(rep) + "\n")
            up = rep
            if not rep["ok"]:
                code = 1
                if not a.keep_going:
                    break
        line = "  ->  ".join(f"{s['verb']}:{s['fate']}" for s in summary)
        print(json.dumps(summary, indent=2) if a.json else f"arc: {line}\nprints: {outdir}/")
        return code
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
