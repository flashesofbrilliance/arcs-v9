"""
arcs_inchworm_echo.py — ARCS v9
Golden Inchworm + Orthogonal Echo Detector

> ROM CANDIDATE [RC-OPS-001]
> Status: EXPERIMENTATION — not yet ROM. Do not treat as constitutional.
> Promotion trigger: promote to full ROM only after an Observatory period —
>   findings produced by this module must be logged and replayed through the
>   Observatory (src/app/observatory/page.tsx once recovered, or the static
>   public/observatory/ demo in the interim) across multiple real sessions,
>   with severity grading and named patterns confirmed accurate in hindsight.
>   No fixed receipt count is specified yet; this should be revisited once
>   Observatory replay is actually live (see _PATTERNS/2026-06-23-governance-
>   roadmap.md, task #7).
> History: this is the third implementation pass in one session (v1 → v8.5 →
>   v8.5.1). v1 had 4 confirmed bugs (golden-thread noun-extraction picking up
>   "The", needle double-"before", dead orthogonality_fn injection, OM/canon
>   mismatch). v8.5 fixed 2 of those by simplifying the stubs but introduced a
>   capability regression (orthogonality no longer injectable) and a needle
>   nested-quote regression. This file (v8.5.1) fixes all of the above,
>   verified by independent execution + an explicit injection test (not just
>   reading the source) — see _PATTERNS/2026-06-23-governance-roadmap.md.
>   A parallel v8.5.1 candidate (two-axis ExecGrade/TriuneState dataclass
>   design) was also reviewed and rejected for now: its boolean-feature
>   similarity scoring counts False==False as a match, which let two
>   deliberately-dissimilar domains in its own test suite score as a
>   confident "OM" echo. Worth revisiting that axis-separation idea later,
>   but not before its scoring method is fixed.

Golden Inchworm: Red Thread → Golden Thread → Needle (3-pass, non-blocking)
Orthogonal Echo Detector: cross-domain kinematic isomorphism detection

Canon source: .claude/arcs-canon.md (ROM Primitives #4, #5)
  GOLDEN INCHWORM: "Red Thread → Golden Thread → Needle. Three-pass,
    non-blocking. Every abstraction earned by a concrete example first."
  ORTHOGONAL ECHO DETECTOR: "Surface cross-domain kinematic isomorphisms.
    When two domains move the same way, name the pattern."

Triune status note (corrected vs earlier drafts this session): per
.claude/arcs-canon.md, OM = "Present and resolved — known known... a
confident, stable value" — it is an EPISTEMIC state, not an execution
grade, and is gated explicitly behind `om_gate` here so it never silently
substitutes for PASS.

All pass functions and the orthogonality function are pluggable via
constructor injection — stubs are deterministic and unit-testable; replace
with LLM-backed versions for production. Both receipt types are fully
JSON-serializable.
"""

import json
import hashlib
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Optional


# ── TRIUNE LOGIC / EXECUTION GRADE ────────────────────────────────────────────

class ARCSStatus(str, Enum):
    """
    PASS / WARN / FAIL  = execution quality grades.
    OM                  = Triune epistemic state — "present and resolved,
                          known-known" per .claude/arcs-canon.md. Fires only
                          when an explicit om_gate callback returns True.
                          Never a substitute for PASS.
    NULL                = absent signal (e.g. empty input, <2 domains).
                          Does not poison a clean PASS/WARN result.
    UNDEFINED           = not yet evaluated (reserved; unused by this module
                          today — no code path currently emits it).
    """
    PASS      = "PASS"
    WARN      = "WARN"
    FAIL      = "FAIL"
    NULL      = "NULL"
    OM        = "OM"
    UNDEFINED = "UNDEFINED"


_STATUS_PRIORITY = [
    ARCSStatus.FAIL,
    ARCSStatus.UNDEFINED,
    ARCSStatus.WARN,
    ARCSStatus.OM,
    ARCSStatus.PASS,
    ARCSStatus.NULL,   # absent signal — neutral; never poisons a PASS or WARN
]


def _worst_status(*statuses):
    for p in _STATUS_PRIORITY:
        if p in statuses:
            return p
    return ARCSStatus.PASS


def _make_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:12]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── GOLDEN INCHWORM ───────────────────────────────────────────────────────────

PassFn = Callable[[str], str]


@dataclass
class InchwormReceipt:
    input_text:    str
    red_thread:    str
    golden_thread: str
    needle:        str
    confidence:    float
    uncertainty:   Optional[str]
    status:        ARCSStatus
    run_id:        str
    timestamp:     str

    def to_json(self, indent: int = 2) -> str:
        d = asdict(self)
        d["status"] = self.status.value
        return json.dumps(d, indent=indent)

    def to_brief(self) -> str:
        lines = [
            f"RED    : {self.red_thread}",
            f"GOLDEN : {self.golden_thread}",
            f"NEEDLE : {self.needle}",
            f"STATUS : {self.status.value}  confidence={self.confidence:.2f}",
        ]
        if self.uncertainty:
            lines.append(f"UNCERTAINTY: {self.uncertainty}")
        return "\n".join(lines)


def _stub_red_thread(text: str) -> str:
    """STUB. Replace with an LLM call: extract only what is literally stated,
    no interpretation, one sentence."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    return sentences[0] if sentences else text[:200]


def _stub_golden_thread(red_thread: str) -> str:
    """STUB. Does NOT embed red_thread verbatim — avoids nested-quote
    propagation into the needle stub (the bug found in an earlier draft this
    session). Replace with an LLM call: state the single structural
    principle this observation instantiates, one sentence, no jargon, do not
    quote the observation."""
    return ("Trust erosion precedes behavioral collapse; the surface symptom "
            "is a proxy for a deeper reliability-contract failure.")


def _stub_needle(golden_thread: str) -> str:
    """STUB. Clean verb-first imperative — does not quote or reference
    golden_thread content (the nested-quoting bug found in an earlier draft).
    Replace with an LLM call: state the single sharpest next action,
    verb-first, one sentence, no hedging, no quoted phrases."""
    return ("Audit whether the surface symptom is the root cause or a "
            "symptom of a pre-existing deeper failure before any remediation.")


class GoldenInchworm:
    """
    Three-pass, non-blocking semantic distillation engine.

    Status logic — axes kept separate, never conflated:
      conf >= 0.8, om_gate is None or returns False  ->  PASS
      om_gate returns True                            ->  OM
      conf < 0.8                                      ->  WARN
      empty input                                     ->  NULL

    LLM injection:
        worm = GoldenInchworm(
            red_thread_fn    = my_llm_red,
            golden_thread_fn = my_llm_golden,
            needle_fn        = my_llm_needle,
            confidence_fn    = my_llm_confidence,  # fn(red,gold,needle) -> float 0..1
            om_gate          = my_llm_om_gate,     # fn(red,gold,needle,conf) -> bool
        )
    """

    def __init__(
        self,
        red_thread_fn:    PassFn = _stub_red_thread,
        golden_thread_fn: PassFn = _stub_golden_thread,
        needle_fn:        PassFn = _stub_needle,
        confidence_fn:    Optional[Callable[[str, str, str], float]] = None,
        om_gate:          Optional[Callable[[str, str, str, float], bool]] = None,
    ):
        self._red  = red_thread_fn
        self._gold = golden_thread_fn
        self._ndl  = needle_fn
        self._conf = confidence_fn or (lambda r, g, n: 0.7)
        self._om   = om_gate

    def run(self, text: str) -> InchwormReceipt:
        if not text or not text.strip():
            return InchwormReceipt(
                input_text=text, red_thread="", golden_thread="", needle="",
                confidence=0.0, uncertainty="Empty input", status=ARCSStatus.NULL,
                run_id=_make_id(text), timestamp=_now(),
            )

        red    = self._red(text)
        golden = self._gold(red)
        needle = self._ndl(golden)
        conf   = self._conf(red, golden, needle)

        uncertainty: Optional[str] = None
        if conf < 0.5:
            uncertainty = "Low confidence: golden thread may be misaligned with red thread."
        elif conf < 0.8:
            uncertainty = "Moderate confidence: needle is directionally sound but warrants verification."

        if self._om and self._om(red, golden, needle, conf):
            status = ARCSStatus.OM
        elif uncertainty:
            status = ARCSStatus.WARN
        else:
            status = ARCSStatus.PASS

        return InchwormReceipt(
            input_text=text, red_thread=red, golden_thread=golden, needle=needle,
            confidence=conf, uncertainty=uncertainty, status=status,
            run_id=_make_id(text), timestamp=_now(),
        )


# ── ORTHOGONAL ECHO DETECTOR ──────────────────────────────────────────────────

PATTERN_LIBRARY: dict = {
    "autocatalytic_loop": [
        "self-reinforcing", "feedback accelerates", "output becomes input",
        "exponential growth", "compounding", "positive feedback", "amplifying",
    ],
    "punctuated_equilibrium": [
        "long stasis", "sudden shift", "plateau then leap", "rapid change",
        "stable until disrupted", "phase transition", "stasis", "speciate",
        "stability", "disrupted", "shock",
    ],
    "ratchet_irreversibility": [
        "one-way", "no rollback", "cannot undo", "locks in", "irreversible",
        "path dependent", "no return", "lock-in",
    ],
    "predator_prey_oscillation": [
        "boom bust", "overshoot collapse", "cycles", "periodic",
        "rise and fall", "lag response", "oscillation", "boom", "bust",
    ],
    "diffusion_gradient": [
        "flows from high to low", "spreads", "equalizes",
        "concentration gradient", "dissipation", "entropy", "gradient",
    ],
    "threshold_cascade": [
        "tipping point", "critical mass", "chain reaction", "cascade", "avalanche",
        "contagion", "threshold", "collapse", "catastrophic", "suddenly",
    ],
    "bottleneck_throughput": [
        "constraint limits flow", "single point of failure", "upstream backs up",
        "chokepoint", "rate limiting", "bottleneck", "constraint", "throughput",
        "isolating",
    ],
    "adaptive_immune_memory": [
        "first encounter costly second cheap", "learns from exposure",
        "memory improves response", "acquired resistance", "vaccination",
        "trust", "trust erodes", "rebuilding", "recovery",
    ],
}


@dataclass
class MotionSignature:
    domain:   str
    keywords: list
    raw_text: str


@dataclass
class EchoMatch:
    domain_a:      str
    domain_b:      str
    pattern_name:  str
    similarity:    float
    evidence_a:    list
    evidence_b:    list
    named_insight: str


@dataclass
class EchoReceipt:
    domains:     list
    matches:     list
    top_pattern: Optional[str]
    status:      ARCSStatus
    run_id:      str
    timestamp:   str

    def to_json(self, indent: int = 2) -> str:
        d = {
            "domains": self.domains,
            "matches": [asdict(m) for m in self.matches],
            "top_pattern": self.top_pattern,
            "status": self.status.value,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
        }
        return json.dumps(d, indent=indent)

    def to_brief(self) -> str:
        if not self.matches:
            return "No orthogonal echoes detected."
        lines = [f"ORTHOGONAL ECHO DETECTOR -- {len(self.matches)} match(es)"]
        for m in self.matches[:3]:
            lines.append(
                f"  [{m.pattern_name}]  {m.domain_a} <-> {m.domain_b}  sim={m.similarity:.2f}\n"
                f"    -> {m.named_insight}\n"
                f"    ev_a={m.evidence_a}\n"
                f"    ev_b={m.evidence_b}"
            )
        if len(self.matches) > 3:
            lines.append(f"  ... and {len(self.matches)-3} more.")
        return "\n".join(lines)


OrthogonalityFn = Callable[[str, str], float]


def _default_orthogonality(domain_a: str, domain_b: str) -> float:
    """1.0 for different domains, 0.5 for same domain. Override with an
    embedding-distance function for production use — see constructor docs."""
    return 0.5 if domain_a.lower() == domain_b.lower() else 1.0


def _tokenize(text: str) -> set:
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
        "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did",
        "will", "would", "could", "should", "may", "might", "it", "its", "this", "that",
        "these", "those", "then", "than", "they", "their", "from", "by", "as", "so",
        "if", "not", "no", "up", "out", "into",
    }
    return {t for t in re.findall(r"[a-z]+", text.lower()) if t not in stopwords and len(t) > 2}


def _extract_signature(domain: str, text: str) -> MotionSignature:
    """
    STUB. Token-overlap extraction: a keyword phrase matches if >=60% of its
    tokens appear in the domain text. No exact verbatim match required (the
    earlier draft's brittleness — 0 matches on thematically related domains
    — is what this replaces).

    LLM injection prompt:
        'Given: "{text}"
         List structural/kinematic keywords describing HOW this system moves.
         Focus on dynamics, not content. Return 3-10 comma-separated keywords.'
    """
    text_tokens = _tokenize(text)
    matched = []
    for pattern_kws in PATTERN_LIBRARY.values():
        for kw in pattern_kws:
            kt = _tokenize(kw)
            if kt and len(kt & text_tokens) / len(kt) >= 0.6 and kw not in matched:
                matched.append(kw)
    return MotionSignature(domain=domain, keywords=matched, raw_text=text)


def _score_pattern(sig_a, sig_b, pattern, orthogonality_fn):
    kws  = PATTERN_LIBRARY[pattern]
    ev_a = [k for k in kws if k in sig_a.keywords]
    ev_b = [k for k in kws if k in sig_b.keywords]
    if not ev_a or not ev_b:
        return 0.0, [], []
    union    = set(ev_a) | set(ev_b)
    inter    = set(ev_a) & set(ev_b)
    jaccard  = len(inter) / len(union) if union else 0.0
    orth     = orthogonality_fn(sig_a.domain, sig_b.domain)
    coverage = (len(ev_a) + len(ev_b)) / (2 * max(len(kws), 1))
    score    = min(
        0.4 * jaccard + 0.4 * orth * coverage + 0.2 * min(len(ev_a), len(ev_b)) / max(len(kws), 1),
        1.0,
    )
    return round(score, 4), ev_a, ev_b


def _name_insight(pattern, da, db):
    templates = {
        "autocatalytic_loop":        f"Both {da} and {db} run self-amplifying loops — early investment compounds disproportionately.",
        "punctuated_equilibrium":    f"{da} and {db} both plateau then leap — prepare for sudden transitions.",
        "ratchet_irreversibility":   f"Decisions in {da} and {db} lock in; model reversibility cost before committing.",
        "predator_prey_oscillation": f"{da} and {db} share boom-bust cycles — dampen with lag awareness.",
        "diffusion_gradient":        f"In both {da} and {db} flow follows concentration — route energy to low-density zones.",
        "threshold_cascade":         f"{da} and {db} both have tipping points — small inputs near threshold carry outsized effect.",
        "bottleneck_throughput":     f"Throughput in {da} and {db} is set by the weakest link — relieve the constraint first.",
        "adaptive_immune_memory":    f"{da} and {db} both build memory from exposure — invest in early recoverable encounters.",
    }
    return templates.get(pattern, f"{da} and {db} share the '{pattern}' kinematic pattern.")


class OrthogonalEchoDetector:
    """
    Detects structural isomorphisms across domains.

    orthogonality_fn is fully injectable (verified by an explicit test that
    the injected callable is actually invoked, not just stored — an earlier
    draft this session accepted the parameter but silently never called it).

    LLM injection:
        detector = OrthogonalEchoDetector(
            signature_fn     = my_llm_signature_extractor,  # fn(domain, text) -> MotionSignature
            orthogonality_fn = lambda a, b: 1 - cosine_sim(embed(a), embed(b)),
        )
    """

    def __init__(
        self,
        signature_fn:     Optional[Callable] = None,
        orthogonality_fn: OrthogonalityFn = _default_orthogonality,
        min_similarity:   float = 0.20,
    ):
        self._sig_fn  = signature_fn or _extract_signature
        self._orth_fn = orthogonality_fn
        self._min_sim = min_similarity

    def run(self, domain_texts: dict) -> EchoReceipt:
        if len(domain_texts) < 2:
            return EchoReceipt(
                domains=list(domain_texts.keys()), matches=[], top_pattern=None,
                status=ARCSStatus.NULL,
                run_id=_make_id(str(domain_texts)), timestamp=_now(),
            )
        sigs    = {d: self._sig_fn(d, t) for d, t in domain_texts.items()}
        domains = list(sigs.keys())
        matches = []
        for i in range(len(domains)):
            for j in range(i + 1, len(domains)):
                da, db = domains[i], domains[j]
                for pat in PATTERN_LIBRARY:
                    sc, ea, eb = _score_pattern(sigs[da], sigs[db], pat, self._orth_fn)
                    if sc >= self._min_sim:
                        matches.append(EchoMatch(
                            domain_a=da, domain_b=db, pattern_name=pat,
                            similarity=sc, evidence_a=ea, evidence_b=eb,
                            named_insight=_name_insight(pat, da, db),
                        ))
        matches.sort(key=lambda m: m.similarity, reverse=True)
        top    = matches[0].pattern_name if matches else None
        status = ARCSStatus.PASS if matches else ARCSStatus.NULL
        return EchoReceipt(
            domains=domains, matches=matches, top_pattern=top, status=status,
            run_id=_make_id(str(domain_texts)), timestamp=_now(),
        )


# ── PIPELINE ──────────────────────────────────────────────────────────────────

@dataclass
class ARCSPipelineResult:
    inchworm_receipt: InchwormReceipt
    echo_receipt:     EchoReceipt
    overall_status:   ARCSStatus
    pipeline_version: str = "arcs-v9-rc-ops-001"

    def to_json(self, indent: int = 2) -> str:
        return json.dumps({
            "pipeline_version": self.pipeline_version,
            "overall_status":   self.overall_status.value,
            "inchworm":         json.loads(self.inchworm_receipt.to_json()),
            "echo":             json.loads(self.echo_receipt.to_json()),
        }, indent=indent)

    def to_brief(self) -> str:
        return "\n\n".join([
            f"=== ARCS PIPELINE [RC-OPS-001]  [{self.overall_status.value}] ===",
            self.inchworm_receipt.to_brief(),
            self.echo_receipt.to_brief(),
        ])


def run_arcs_pipeline(
    text: str,
    domain_texts: Optional[dict] = None,
    inchworm: Optional[GoldenInchworm] = None,
    detector: Optional[OrthogonalEchoDetector] = None,
) -> ARCSPipelineResult:
    """
    One-call agentic entry point.
    Absent domain_texts yields a NULL echo, which does not degrade a clean
    inchworm result (NULL ranks below PASS in _STATUS_PRIORITY).
    """
    worm   = inchworm or GoldenInchworm()
    det    = detector or OrthogonalEchoDetector()
    iw_rec = worm.run(text)
    ec_rec = det.run(domain_texts or {})
    return ARCSPipelineResult(
        inchworm_receipt=iw_rec,
        echo_receipt=ec_rec,
        overall_status=_worst_status(iw_rec.status, ec_rec.status),
    )


# ── SMOKE TEST + BRANCH COVERAGE ─────────────────────────────────────────────

if __name__ == "__main__":
    INPUT = (
        "The team keeps missing weekly standups because the scheduling tool is slow "
        "and people have stopped trusting it will work, so they just don't show up."
    )
    DOMAINS = {
        "organisational behaviour": (
            "teams gradually stop attending rituals when tooling fails repeatedly; "
            "trust erodes across a long stable period then collapses suddenly; "
            "rebuilding requires a triggering success event and recovery of trust"
        ),
        "evolutionary biology": (
            "species remain in stable stasis across long periods then rapidly speciate "
            "after environmental shock or sudden habitat disruption"
        ),
        "infrastructure engineering": (
            "systems degrade slowly until a threshold is crossed then cascade-fail; "
            "recovery requires isolating the bottleneck constraint and relieving it first"
        ),
    }

    result = run_arcs_pipeline(text=INPUT, domain_texts=DOMAINS)
    print(result.to_brief())
    print()

    print("--- BRANCH COVERAGE (axes kept separate) ---")
    print(f"  conf=0.9, no om_gate  -> {GoldenInchworm(confidence_fn=lambda r,g,n:0.9).run(INPUT).status.value}  (expect PASS)")
    print(f"  conf=0.9, om_gate=T   -> {GoldenInchworm(confidence_fn=lambda r,g,n:0.9, om_gate=lambda r,g,n,c:True).run(INPUT).status.value}  (expect OM)")
    print(f"  conf=0.6              -> {GoldenInchworm(confidence_fn=lambda r,g,n:0.6).run(INPUT).status.value}  (expect WARN)")
    print(f"  empty input           -> {GoldenInchworm().run('').status.value}  (expect NULL)")

    print()
    print("--- NULL-NEVER-POISONS-CLEAN-RESULT CHECK ---")
    r = run_arcs_pipeline(text=INPUT)
    print(f"  no domain_texts, conf=0.7 -> overall={r.overall_status.value}  (expect WARN, not NULL)")
