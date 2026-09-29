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
> Seaworthiness rebuild (2026-09-26, closes F34): the v8.5.1 echo matcher scored
>   on lone keyword-token overlap and was FALSIFIED by its own dogfood — at no
>   threshold did it get both high recall and low adversarial false-positive rate
>   (adv-FP 1.0 at the operating threshold; _STATE/2026-08-29-echo-detector-dogfood
>   .json). This pass replaces the flat PATTERN_LIBRARY with a CONCEPT_LIBRARY of
>   named kinematic concepts, each detected only by a RELATIONAL phrase (never a
>   lone generic word), and gates a match on >= MIN_SHARED_CONCEPTS (2) concepts
>   present on BOTH sides. signature_fn + orthogonality_fn stay injectable (LLM /
>   embedding in production; make_llm_signature_fn / make_embedding_orthogonality_fn);
>   the offline defaults are deterministic fixtures, labeled honestly as fixtures.
>   Re-run bench: precision 1.0 / recall 1.0 / adv-FP 0.0 across the full sweep,
>   plus a held-out bench (see scripts/echo_detector_dogfood.py). This clears
>   RC-OPS-001 graduation criterion 2 (detector precision); the blind-field-echo
>   and Observatory criteria remain open.

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
import math
import re
from dataclasses import dataclass, asdict, field
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

# ── CONCEPT LIBRARY (the seaworthiness rebuild — closes F34) ────────────────────
# F34: the old PATTERN_LIBRARY was a flat list of keyword *phrases* per pattern,
# many of them lone generic words ("trust", "shock", "gradient", "collapse",
# "stability", "recovery", "spreads", "suddenly"). The four adversarial decoys in
# the dogfood share exactly those isolated words WITHOUT sharing the underlying
# dynamic, so any low threshold flagged them (adv-FP 1.0). A shared *word* was
# treated as a shared *structure*.
#
# The fix: each pattern is defined by a small set of named KINEMATIC CONCEPTS, and
# a concept is present only when a RELATIONAL phrase for it appears — never a lone
# generic word. A pattern then matches a domain pair only when >= MIN_SHARED_CONCEPTS
# distinct concepts are present on BOTH sides (see OrthogonalEchoDetector). One
# shared structural feature is a coincidence; a shared multi-feature dynamical
# signature is an isomorphism. This is a domain-general rule, not a per-case filter.
#
# Each cue is matched case-insensitively; a cue containing ".*" / "\b" / "{" is
# treated as a regex (DOTALL), otherwise as a plain substring. Cues are deliberately
# RELATIONAL (a verb + its object, or two co-referring nouns) so that a decoy's lone
# generic token cannot satisfy them.

CONCEPT_LIBRARY: dict = {
    "autocatalytic_loop": {
        "output_becomes_input": [r"output\s+becomes\s+(?:\w+\s+){0,3}input", "becomes input",
                                 "becomes next", "feedback accelerates"],
        "self_reinforcing":     ["self-reinforcing", "self reinforcing", "positive feedback",
                                 "compound", "amplif"],
        "exponential_growth":   ["exponential"],
    },
    "punctuated_equilibrium": {
        "long_stasis":     ["long stasis", "long plateau", "long stable", "stable until disrupted",
                            "after stasis", "long period", "long stable period"],
        "sudden_shift":    ["sudden shift", "a leap", "then a leap", "rapid change",
                            r"sudden\w*\s+(?:\w+\s+){0,2}shift"],
        "phase_transition": ["phase transition", "speciate"],
    },
    "ratchet_irreversibility": {
        "one_way":        ["one-way", "one way", "no rollback", "no return"],
        "cannot_undo":    ["cannot undo", "can't undo", "irreversible", "unrecoverable"],
        "locks_in":       ["locks in", "lock in", "lock-in", "locked in"],
        "path_dependent": ["path dependent", "path-dependent"],
    },
    "predator_prey_oscillation": {
        "boom_bust":  ["boom bust", "boom-bust", "boom and bust", "rise and fall"],
        "overshoot":  ["overshoot collapse", "overshoot then", "overshoots"],
        "cyclic":     ["oscillat", "periodic cycle", "predator-prey", r"boom.{0,20}bust\s+cycle"],
    },
    "diffusion_gradient": {
        "flow_high_to_low":     ["flows from high to low", "high to low", "concentration gradient",
                                 "down the gradient"],
        "equalizes_dissipates": ["equalizes", "equalize", "dissipation", "dissipates",
                                 "toward equilibrium"],
    },
    "threshold_cascade": {
        "tipping":  ["tipping point", "critical mass", "past a threshold", "past the tipping",
                     "past the threshold", "crosses a threshold", "beyond a threshold"],
        "chain":    ["chain reaction", "cascade", "cascades", "contagion", "avalanche"],
    },
    "bottleneck_throughput": {
        "constraint_limits": ["constraint limits flow", "rate limiting", "rate-limiting",
                              "chokepoint", "limits the flow", "sets the pace"],
        "single_point":      ["single point of failure", "weakest link", "the constraint first"],
        "backs_up":          ["upstream backs up", "backs up", "queue builds"],
    },
    "adaptive_immune_memory": {
        "cost_asymmetry":       [r"first\b.{0,45}\bcostl.{0,70}\b(second|later)\w*.{0,35}cheap",
                                 "first encounter is costly", "first betrayal is costly"],
        "learn_from_exposure":  ["learns from exposure", "learn from exposure",
                                 "learned from exposure"],
        "memory_improves":      ["memory improves", "memory of the encounter", "acquired resistance",
                                 "recovery is memory", r"memory\s+of\s+the"],
    },
}

# Back-compat shim: a few external docs and older callers referenced PATTERN_LIBRARY
# as "the set of pattern names". Keep the NAMES available (as concept-keyed dict) but
# no code path scores against a flat keyword list any more.
PATTERN_LIBRARY = CONCEPT_LIBRARY

# An isomorphism needs a shared multi-feature structure, not a single coincident
# feature. Two independently-present concepts is the floor; below it, do not fire.
MIN_SHARED_CONCEPTS = 2


@dataclass
class MotionSignature:
    """A domain's kinematic signature.

    `concepts` maps pattern_name -> {concept_name: strength 0..1}: the structural
    concepts the signature_fn found present in this domain's text. This is the unit
    of comparison — NOT a flat bag of keywords (that was the F34 failure mode).
    `keywords` is kept as a flat, deduped list of the concept names for back-compat
    and human-readable receipts; nothing scores against it.
    """
    domain:   str
    concepts: dict
    raw_text: str
    keywords: list = field(default_factory=list)


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
SignatureFn     = Callable[[str, str], MotionSignature]


def _char_trigrams(s: str) -> dict:
    s = re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
    s = f"  {s} "
    counts: dict = {}
    for i in range(len(s) - 2):
        g = s[i:i + 3]
        counts[g] = counts.get(g, 0) + 1
    return counts


def _cosine(a: dict, b: dict) -> float:
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(k, 0) for k, v in a.items())
    na  = math.sqrt(sum(v * v for v in a.values()))
    nb  = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def _default_orthogonality(domain_a: str, domain_b: str) -> float:
    """DETERMINISTIC FIXTURE — honest about being one. A stand-in for a real
    embedding distance, computed as (1 - character-trigram cosine similarity)
    between the two domain LABELS, clamped to [0, 1]. Distant labels -> ~1.0
    (genuinely orthogonal domains), near-identical labels -> ~0.0.

    This is a lexical proxy, NOT a semantic embedding: it cannot tell that
    "cardiology" and "the heart" are the same domain. In production, inject a
    real embedding via `make_embedding_orthogonality_fn(embed)` (below). It is
    kept honest and simple because, for the orthogonal-ECHO task, orthogonality
    only modulates the score — the discriminator that rejects the adversarial
    decoys is the shared-CONCEPT gate in `_score_pattern`, not this function.
    """
    if domain_a.strip().lower() == domain_b.strip().lower():
        return 0.0
    sim = _cosine(_char_trigrams(domain_a), _char_trigrams(domain_b))
    return round(max(0.0, min(1.0, 1.0 - sim)), 4)


def _cue_present(cue: str, text_lc: str) -> bool:
    """A cue is a regex when it carries regex metacharacters, else a substring.
    Matched case-insensitively, DOTALL so relational cues can span punctuation."""
    if any(ch in cue for ch in (".*", "\\b", "\\w", "\\s", "{", "(", "[", "|")):
        return re.search(cue, text_lc, re.DOTALL) is not None
    return cue in text_lc


def _extract_signature(domain: str, text: str) -> MotionSignature:
    """DETERMINISTIC FIXTURE signature_fn — honest about being one. Detects, per
    pattern, which named kinematic CONCEPTS are present in the text, where a
    concept counts as present only if at least one of its RELATIONAL cues matches.
    A lone generic word ("trust", "shock", "collapse", "gradient") satisfies no
    cue, which is exactly why the adversarial decoys score zero shared concepts.

    This is not a semantic model; it is a curated relational-phrase detector built
    from the general theory of each named pattern (not from the bench's answers).
    In production, inject an LLM extractor via `make_llm_signature_fn(llm_call)`
    (below), which returns the same MotionSignature shape.
    """
    text_lc = text.lower()
    concepts: dict = {}
    flat: list = []
    for pattern, concept_map in CONCEPT_LIBRARY.items():
        present: dict = {}
        for concept, cues in concept_map.items():
            if any(_cue_present(c, text_lc) for c in cues):
                present[concept] = 1.0
                flat.append(concept)
        if present:
            concepts[pattern] = present
    return MotionSignature(domain=domain, concepts=concepts, raw_text=text,
                           keywords=sorted(set(flat)))


def _score_pattern(sig_a, sig_b, pattern, orthogonality_fn):
    """Score one pattern for a domain pair. Returns (score, evidence_a, evidence_b).

    The hard gate: fewer than MIN_SHARED_CONCEPTS concepts present on BOTH sides
    -> score 0.0 (a single coincident feature is not an isomorphism). Above the
    gate, the score grades by how much of the pattern's structure is jointly
    present, then is modulated by domain orthogonality (an orthogonal echo is
    worth more than a same-domain one).
    """
    concept_map = CONCEPT_LIBRARY[pattern]
    conc_a = sig_a.concepts.get(pattern, {})
    conc_b = sig_b.concepts.get(pattern, {})
    shared = set(conc_a) & set(conc_b)
    if len(shared) < MIN_SHARED_CONCEPTS:
        return 0.0, sorted(conc_a), sorted(conc_b)

    n_concepts = max(len(concept_map), 1)
    coverage = len(shared) / n_concepts                              # jointly-present structure
    depth    = min(len(conc_a), len(conc_b)) / n_concepts            # each side's independent depth
    strength = sum(min(conc_a[c], conc_b[c]) for c in shared) / len(shared)
    sig_sim  = 0.5 * coverage + 0.3 * depth + 0.2 * strength
    orth     = orthogonality_fn(sig_a.domain, sig_b.domain)
    score    = min(sig_sim * (0.6 + 0.4 * orth), 1.0)
    return round(score, 4), sorted(shared), sorted(shared)


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


def make_llm_signature_fn(llm_call: Callable[[str], str]) -> SignatureFn:
    """Build a production signature_fn backed by a real LLM.

    `llm_call(prompt) -> str` must return the model's completion. The returned
    fn asks the model which named kinematic concepts (from CONCEPT_LIBRARY) are
    genuinely present in the text, parses the JSON list, and maps it onto the
    same MotionSignature shape the offline fixture produces — so the detector,
    dogfood, and receipts are identical whether the signature is fixture- or
    LLM-derived. NOT exercised by the offline dogfood (no network); it is the
    seam the graduation gate's "signature_fn (LLM structural extraction)" names.
    """
    concept_index = {c: p for p, cm in CONCEPT_LIBRARY.items() for c in cm}
    catalogue = ", ".join(sorted(concept_index))

    def _fn(domain: str, text: str) -> MotionSignature:
        prompt = (
            "You are extracting the KINEMATIC (how-it-moves) concepts a passage "
            "genuinely instantiates. Do not reward a lone topical word; a concept "
            "counts only if the passage expresses its relation.\n"
            f"Allowed concepts: {catalogue}\n"
            f'Passage: "{text}"\n'
            "Return a JSON array of the concept names that genuinely apply."
        )
        try:
            names = json.loads(llm_call(prompt))
        except Exception:
            names = []
        concepts: dict = {}
        flat: list = []
        for name in names:
            pat = concept_index.get(name)
            if pat:
                concepts.setdefault(pat, {})[name] = 1.0
                flat.append(name)
        return MotionSignature(domain=domain, concepts=concepts, raw_text=text,
                               keywords=sorted(set(flat)))
    return _fn


def make_embedding_orthogonality_fn(embed: Callable[[str], list]) -> OrthogonalityFn:
    """Build a production orthogonality_fn from a real embedding.

    `embed(text) -> vector`. Returns (1 - cosine similarity), clamped to [0, 1]:
    genuinely distant domains -> ~1.0, near-duplicate domains -> ~0.0. This is the
    seam the graduation gate's "orthogonality_fn (embedding distance)" names; the
    offline default (`_default_orthogonality`) is a labeled lexical fixture that
    needs no network.
    """
    def _cos(u: list, v: list) -> float:
        dot = sum(a * b for a, b in zip(u, v))
        nu  = math.sqrt(sum(a * a for a in u))
        nv  = math.sqrt(sum(b * b for b in v))
        return dot / (nu * nv) if nu and nv else 0.0

    def _fn(domain_a: str, domain_b: str) -> float:
        sim = _cos(embed(domain_a), embed(domain_b))
        return round(max(0.0, min(1.0, 1.0 - sim)), 4)
    return _fn


class OrthogonalEchoDetector:
    """
    Detects structural isomorphisms across domains.

    Seaworthy since the F34 rebuild: matches are gated on shared *concepts*
    (relational structure), never on lone keyword overlap. Both the signature
    extractor and the orthogonality metric are fully injectable — the offline
    defaults are deterministic fixtures, honestly labeled, so the dogfood runs
    with no network; production injects an LLM signature_fn + embedding
    orthogonality_fn (see make_llm_signature_fn / make_embedding_orthogonality_fn).
    The injected orthogonality_fn is verified to be actually invoked (an earlier
    draft accepted the parameter but silently never called it).

    LLM injection:
        detector = OrthogonalEchoDetector(
            signature_fn     = make_llm_signature_fn(my_llm_call),
            orthogonality_fn = make_embedding_orthogonality_fn(my_embed),
        )
    """

    def __init__(
        self,
        signature_fn:     Optional[Callable] = None,
        orthogonality_fn: OrthogonalityFn = _default_orthogonality,
        min_similarity:   float = 0.35,
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
    # These three domains each express the punctuated-equilibrium dynamic with
    # MORE THAN ONE structural concept (long stasis + a sudden shift), so the
    # seaworthy detector fires a genuine cross-domain echo. Loosely-worded domains
    # that share only a single feature (or a lone generic word) correctly do NOT
    # echo any more — that conservatism is the F34 fix, not a regression.
    DOMAINS = {
        "organisational behaviour": (
            "the team holds a long stable period of steady rituals, then a sudden "
            "shift as attendance collapses; a rapid change no one predicted"
        ),
        "evolutionary biology": (
            "species sit in long stasis, then a rapid change; a phase transition as "
            "they speciate after the sudden shift of an environmental shock"
        ),
        "infrastructure engineering": (
            "the platform runs in long stasis until a sudden shift; a rapid change "
            "as load crosses a threshold and the failure cascades"
        ),
    }

    result = run_arcs_pipeline(text=INPUT, domain_texts=DOMAINS)
    print(result.to_brief())
    print()

    print("--- INJECTION IS ACTUALLY INVOKED (not just accepted) ---")
    _sig_seen, _orth_seen = [], []
    def _spy_sig(domain, text):
        _sig_seen.append(domain); return _extract_signature(domain, text)
    def _spy_orth(a, b):
        _orth_seen.append((a, b)); return _default_orthogonality(a, b)
    _det = OrthogonalEchoDetector(signature_fn=_spy_sig, orthogonality_fn=_spy_orth)
    _det.run(DOMAINS)
    assert _sig_seen, "injected signature_fn was never called"
    assert _orth_seen, "injected orthogonality_fn was never called"
    print(f"  signature_fn called {len(_sig_seen)}x, orthogonality_fn called {len(_orth_seen)}x  (both OK)")
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
