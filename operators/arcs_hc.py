"""
arcs_hc.py — ARCS Hemisphere Checker (HC)
==========================================
Pre-transmission sender cognitive health diagnostic.

Implements the 5-axis feature manifold defined in the HC Feature Set Spec
(ARCS-CIS-SPEC-v1.0, Gap Closure Addendum v1.0).

Pipeline position: fires BEFORE LTE Intake.
Gate: CSS < 0.65 halts LTE or forces mandatory seam.

Axes:
  ER  — Epistemic Register        (certainty vs uncertainty ratio)
  EAS — Evidence Anchoring Score  (external evidence vs self-referential)
  PEI — Pattern Extrapolation     (how far claims exceed sample base)
  JSD — JTBD Semantic Distance    (cosine drift from session JTBD anchor)
  NCS — Narrative Coherence Score (story structure presence)

Engine Scores:
  myth_engine_score    = f(ER, EAS, NCS, exception_density)
  pattern_engine_score = f(PEI, EAS, exception_density, causal_ratio)
  temporal_drift_score = f(JSD, UI, self_referential_density)

CSS Composite:
  css = 1.0 - (0.45*myth + 0.30*pattern + 0.25*temporal_drift)
  CSS = 1.0 → fully healthy sender
  CSS < 0.65 → LTE gate triggers
"""

from __future__ import annotations

import re
import math
import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional


# ─── Constants ────────────────────────────────────────────────────────────────

CSS_GATE_THRESHOLD = 0.65       # below this: LTE halts or mandatory seam
CSS_SEAM_WARNING   = 0.75       # below this: elevated seam (soft warning)
CSS_HEALTHY        = 0.85       # above this: confidence stamp elevated

MYTH_WEIGHT        = 0.45
PATTERN_WEIGHT     = 0.30
TEMPORAL_WEIGHT    = 0.25


# ─── CognitiveSafetyScore — LOCKED INTERFACE ─────────────────────────────────
# This dataclass is the contract between HC output and every downstream LTE stage.
# It is LOCKED before Sprint 0. Changes require a new decision receipt.
# Spec source: CIS Product Spec v1.0 / "What Needs to Happen Before Sprint 0 Starts"

@dataclass
class CognitiveSafetyScore:
    """
    Emitted by HC. Injected into all downstream LTE stages.
    This interface is LOCKED before Sprint 0.

    Gate threshold: overall < 0.65 → block or warn before translation.
    """
    overall: float                    # 0–1. Gate threshold: 0.65
    myth_engine: float                # premature schema / narrative lock
    pattern_engine: float             # overfitting / false signal
    temporal_drift: float             # distance from JTBD anchor
    urgency_modifier: float           # multiplied into Altitude Detector urgency_index
    invariant_confidence_floor: float # minimum IPS threshold for this signal
    bandwagon_suppress: bool          # if True, RRE suppresses social proof amplification
    seam_string: str                  # visible in Recomp: "Note: sender state [X]"
    gate_pass: bool                   # overall < 0.65 → False

    @classmethod
    def from_csr(cls, csr: "CognitiveStateRegister") -> "CognitiveSafetyScore":
        """Build from a CognitiveStateRegister (the HC's internal output)."""
        gate_pass = csr.css >= CSS_GATE_THRESHOLD
        # urgency_modifier: scale down urgency when myth is active
        urgency_modifier = max(0.3, 1.0 - csr.myth_engine_score * 0.8)
        # invariant_confidence_floor: higher distortion → lower floor
        invariant_confidence_floor = max(0.50, csr.css * 0.95)
        # bandwagon suppress: engage when pattern engine is hot
        bandwagon_suppress = csr.pattern_engine_score >= 0.55
        # seam_string
        if not gate_pass:
            seam = f"⚠ Sender state: CSS {csr.css:.2f} — translation held."
        elif csr.css < CSS_SEAM_WARNING:
            seam = f"Note: sender state {csr.css:.2f} — elevated distortion risk."
        else:
            seam = f"Sender state: {csr.css:.2f} — healthy."
        return cls(
            overall=csr.css,
            myth_engine=csr.myth_engine_score,
            pattern_engine=csr.pattern_engine_score,
            temporal_drift=csr.temporal_drift_score,
            urgency_modifier=urgency_modifier,
            invariant_confidence_floor=invariant_confidence_floor,
            bandwagon_suppress=bandwagon_suppress,
            seam_string=seam,
            gate_pass=gate_pass,
        )


# ─── Lexical Feature Banks ────────────────────────────────────────────────────

_CERTAINTY_MARKERS = re.compile(
    r"\b(is|are|will|must|always|never|definitely|clearly|obviously|"
    r"certainly|undoubtedly|without doubt|the fact is|it is clear|"
    r"everyone knows|it follows that|this proves|this means|this shows)\b",
    re.IGNORECASE,
)

_UNCERTAINTY_MARKERS = re.compile(
    r"\b(might|could|may|seems|appears|suggests|probably|perhaps|"
    r"possibly|I think|I believe|I wonder|it seems|it appears|"
    r"arguably|potentially|likely|unlikely|not sure|unsure)\b",
    re.IGNORECASE,
)

_ANCHORING_MARKERS = re.compile(
    r"\b(because|per|according to|based on|data shows|research shows|"
    r"studies show|I observed|I measured|I found|I tested|I saw|I noted|"
    r"n=|sample|evidence|source|cited|documented|recorded|reported|"
    r"published|demonstrated|from the data|the numbers show|"
    r"in practice|in our experience|we found|we measured|we tested)\b"
    r"|\b\d+(?:\.\d+)?%"             # numeric percentages (no trailing \b — % is non-word)
    r"|\b\d{4}\b",                    # years (external reference)
    re.IGNORECASE,
)

_SELF_REFERENTIAL_MARKERS = re.compile(
    r"\b(I believe|it makes sense that|logically|it follows that|"
    r"obviously|everyone knows|intuitively|common sense|it's clear|"
    r"naturally|of course|as we know|as everyone knows|it's obvious)\b",
    re.IGNORECASE,
)

_EXTRAPOLATION_MARKERS = re.compile(
    r"\b(always|never|in general|as a rule|people tend to|"
    r"the pattern is|this means that|X always|universally|"
    r"invariably|without exception|every time|all cases)\b",
    re.IGNORECASE,
)

_BOUNDING_MARKERS = re.compile(
    r"\b(in this case|for this instance|I've seen this|based on these|"
    r"so far|in my experience|in this context|for now|at least in|"
    r"this specific|these particular|limited to|only when)\b",
    re.IGNORECASE,
)

_EXCEPTION_MARKERS = re.compile(
    r"\b(but|except|unless|however|although|though|yet|whereas|"
    r"despite|notwithstanding|on the other hand|that said|"
    r"with the caveat|with the exception)\b",
    re.IGNORECASE,
)

_CAUSAL_MARKERS = re.compile(
    r"\b(causes|caused by|leads to|results in|produces|generates|"
    r"triggers|drives|creates|because of|due to|as a result of|"
    r"therefore|thus|hence|consequently|so that)\b",
    re.IGNORECASE,
)

_TEMPORAL_MARKERS = re.compile(
    r"\b(urgent|immediately|now|asap|critical|emergency|deadline|"
    r"by tomorrow|today|this week|no time|running out|must act|"
    r"time sensitive|time-sensitive|can't wait)\b",
    re.IGNORECASE,
)

# Narrative structure: agent + action verb + resolution language
_NARRATIVE_RESOLUTION = re.compile(
    r"\b(so|therefore|which means|and that's why|the result was|"
    r"this led to|consequently|in conclusion|the outcome|"
    r"this resulted in|the impact was|ultimately)\b",
    re.IGNORECASE,
)

_ACTION_VERBS = re.compile(
    r"\b(decided|built|shipped|launched|created|delivered|solved|"
    r"fixed|grew|achieved|completed|executed|drove|led|managed)\b",
    re.IGNORECASE,
)


# ─── Low-Level Feature Extractors ─────────────────────────────────────────────

def _token_count(text: str) -> int:
    return max(1, len(text.split()))


def _sentence_count(text: str) -> int:
    sentences = re.split(r'[.!?]+', text)
    return max(1, len([s for s in sentences if s.strip()]))


def _count_matches(pattern: re.Pattern, text: str) -> int:
    return len(pattern.findall(text))


def _density_per_100(count: int, token_count: int) -> float:
    """Normalize a count to per-100-tokens frequency."""
    return (count / token_count) * 100


# ─── Axis 1: Epistemic Register (ER) ──────────────────────────────────────────

def score_epistemic_register(text: str) -> float:
    """
    ER: ratio of certainty-dominant language to (certainty + uncertainty).
    Range: 0.0 (pure hedge) → 1.0 (pure assertion)

    Alone means nothing. Distortion signal when EAS is also low.
    """
    tokens = _token_count(text)
    certainty = _count_matches(_CERTAINTY_MARKERS, text)
    uncertainty = _count_matches(_UNCERTAINTY_MARKERS, text)
    total = certainty + uncertainty
    if total == 0:
        return 0.50  # neutral prior when no signal
    return certainty / total


# ─── Axis 2: Evidence Anchoring Score (EAS) ───────────────────────────────────

def score_evidence_anchoring(text: str) -> float:
    """
    EAS: how often the text cites external, verifiable evidence
    vs self-referential logic.
    Range: 0.0 (no anchoring) → 1.0 (fully evidence-grounded)

    Myth Engine fires when ER high AND EAS low.
    """
    tokens = _token_count(text)
    anchoring  = _density_per_100(_count_matches(_ANCHORING_MARKERS, text), tokens)
    self_ref   = _density_per_100(_count_matches(_SELF_REFERENTIAL_MARKERS, text), tokens)

    # Anchor score: sigmoid-like squeeze into 0-1
    raw = anchoring / max(1.0, anchoring + self_ref + 1.0)
    return float(min(1.0, max(0.0, raw)))


# ─── Axis 3: Pattern Extrapolation Index (PEI) ────────────────────────────────

def score_pattern_extrapolation(text: str) -> float:
    """
    PEI: how far claims extend beyond their observed sample base.
    Range: 0.0 (conservative, well-bounded) → 1.0 (heavily overfit)

    Pattern Engine fires when PEI high AND EAS low.
    """
    tokens = _token_count(text)
    extrap  = _density_per_100(_count_matches(_EXTRAPOLATION_MARKERS, text), tokens)
    bounding = _density_per_100(_count_matches(_BOUNDING_MARKERS, text), tokens)

    # High extrapolation, low bounding = high PEI
    raw = extrap / max(1.0, extrap + bounding + 1.0)
    return float(min(1.0, max(0.0, raw)))


# ─── Axis 4: JTBD Semantic Distance (JSD) ─────────────────────────────────────

def score_jtbd_distance(
    text: str,
    jtbd_anchor: Optional[str],
    use_embeddings: bool = False,
) -> float:
    """
    JSD: cosine distance between current signal and JTBD anchor.
    Range: 0.0 (perfectly on JTBD) → 1.0 (completely orthogonal)

    Temporal Drift fires when JSD high AND UI low (drifted + no urgency).

    v1.0: lexical overlap fallback (top-N noun/keyword overlap).
    Future: sentence-transformer embedding when use_embeddings=True.
    """
    if jtbd_anchor is None:
        return 0.0  # no anchor = no drift signal

    if use_embeddings:
        return _jsd_embedding(text, jtbd_anchor)
    else:
        return _jsd_lexical(text, jtbd_anchor)


def _jsd_lexical(text: str, jtbd_anchor: str) -> float:
    """
    Lexical JSD: keyword coverage of JTBD anchor terms in the signal.
    Uses anchor-keyword coverage rather than full Jaccard — Jaccard collapses
    on short JTBD anchors (2-4 content words) giving spuriously high distance.

    Coverage = fraction of anchor keywords found anywhere in signal.
    JSD = 1 - coverage.
    Accuracy ~0.62 — use only as cold-start stub until embeddings are available.
    """
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "i", "we", "you", "he", "she", "it", "they", "my", "our",
        "this", "that", "these", "those", "and", "or", "but", "in",
        "on", "at", "to", "for", "of", "with", "by", "from", "as",
        "if", "not", "do", "did", "have", "has", "had", "will", "would",
        "can", "could", "should", "may", "might", "must", "shall",
    }

    def content_words(t: str) -> list[str]:
        words = re.findall(r"\b[a-z]{3,}\b", t.lower())
        return [w for w in words if w not in stopwords]

    anchor_words = set(content_words(jtbd_anchor))
    if not anchor_words:
        return 0.0

    signal_lower = text.lower()
    # Count how many anchor keywords appear at least once in signal
    found = sum(1 for w in anchor_words if re.search(rf"\b{re.escape(w)}\b", signal_lower))
    coverage = found / len(anchor_words)

    # Penalize more if the signal introduces a large volume of off-anchor vocabulary
    signal_words = set(content_words(text))
    off_anchor_ratio = len(signal_words - anchor_words) / max(1, len(signal_words))

    # JSD blends coverage miss + off-anchor ratio, anchor coverage weighted higher
    jsd = (0.70 * (1.0 - coverage)) + (0.30 * off_anchor_ratio * (1.0 - coverage))
    return float(min(1.0, max(0.0, jsd)))


def _jsd_embedding(text: str, jtbd_anchor: str) -> float:
    """
    Embedding-based JSD using sentence-transformers (MiniLM-L6-v2).
    Falls back to lexical if import fails.
    """
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
        model = SentenceTransformer("all-MiniLM-L6-v2")
        vecs = model.encode([text, jtbd_anchor])
        cos_sim = float(
            np.dot(vecs[0], vecs[1]) /
            (np.linalg.norm(vecs[0]) * np.linalg.norm(vecs[1]) + 1e-9)
        )
        return float(1.0 - max(0.0, min(1.0, cos_sim)))
    except ImportError:
        return _jsd_lexical(text, jtbd_anchor)


# ─── Axis 5: Narrative Coherence Score (NCS) ──────────────────────────────────

def score_narrative_coherence(text: str) -> float:
    """
    NCS: whether the text has story structure (agent → action → outcome arc).
    Range: 0.0 (pure data dump) → 1.0 (complete narrative arc)

    NCS alone is healthy. Distortion signal only as cross-product with ER and (1-EAS):
    NCS * ER * (1 - EAS) = story + certainty + no evidence = Myth Engine max danger.
    """
    tokens = _token_count(text)
    resolution = _density_per_100(_count_matches(_NARRATIVE_RESOLUTION, text), tokens)
    action_verbs = _density_per_100(_count_matches(_ACTION_VERBS, text), tokens)

    # NCS is a gentle score — narrative is common and mostly healthy
    raw = (resolution * 0.60 + action_verbs * 0.40) / 5.0  # normalize: ~5 per 100 is high
    return float(min(1.0, max(0.0, raw)))


# ─── Derived Feature: Urgency Index (UI) ──────────────────────────────────────

def score_urgency_index(text: str) -> float:
    """
    UI: ratio of imperative/temporal language density.
    Borrowed from Altitude Detector — also used in temporal drift scoring.
    Range: 0.0 (long-horizon deliberation) → 1.0 (crisis/action-now)
    """
    tokens = _token_count(text)
    temporal = _density_per_100(_count_matches(_TEMPORAL_MARKERS, text), tokens)
    raw = temporal / max(1.0, temporal + 3.0)   # 3.0 floor prevents noise spikes
    return float(min(1.0, max(0.0, raw)))


# ─── Engine Scoring Functions ─────────────────────────────────────────────────

def compute_myth_engine_score(
    er: float,
    eas: float,
    ncs: float,
    exception_density: float,
) -> float:
    """
    Myth Engine fires when: high certainty (ER↑) + thin evidence (EAS↓)
    The story-hardening cross-product NCS*ER*(1-EAS) captures the most dangerous form:
    a polished narrative asserted with certainty backed by nothing.

    myth_engine_score = 0.35*ER + 0.30*(1-EAS) + 0.25*(NCS*ER*(1-EAS)) + 0.10*(1-exception_density)
    """
    cross_product = ncs * er * (1.0 - eas)  # the story-hardening term
    score = (
        0.35 * er +
        0.30 * (1.0 - eas) +
        0.25 * cross_product +
        0.10 * (1.0 - exception_density)
    )
    return float(min(1.0, max(0.0, score)))


def compute_pattern_engine_score(
    pei: float,
    eas: float,
    exception_density: float,
    causal_ratio: float,
) -> float:
    """
    Pattern Engine fires when: heavy extrapolation (PEI↑) + thin evidence (EAS↓)
    Causal language (X causes Y vs X preceded Y) amplifies overfit pattern claims.

    pattern_engine_score = 0.40*PEI + 0.30*(1-EAS) + 0.20*(1-exception_density) + 0.10*causal_ratio
    """
    score = (
        0.40 * pei +
        0.30 * (1.0 - eas) +
        0.20 * (1.0 - exception_density) +
        0.10 * causal_ratio
    )
    return float(min(1.0, max(0.0, score)))


def compute_temporal_drift_score(
    jsd: float,
    ui: float,
    self_referential_density: float,
) -> float:
    """
    Temporal Drift fires when: high semantic distance from JTBD (JSD↑) + low urgency (UI↓)
    You've drifted AND stopped feeling the decision pressure.
    Increasing self-reference (spiral inward) amplifies drift signal.

    temporal_drift_score = 0.60*JSD + 0.25*(1-UI) + 0.15*self_referential_density
    """
    score = (
        0.60 * jsd +
        0.25 * (1.0 - ui) +
        0.15 * self_referential_density
    )
    return float(min(1.0, max(0.0, score)))


def compute_css(
    myth: float,
    pattern: float,
    temporal_drift: float,
) -> float:
    """
    CSS (Cognitive State Score): composite sender health.
    CSS = 1.0 → fully healthy sender
    CSS < 0.75 → elevated seam warning
    CSS < 0.60 → LTE gate (halt or mandatory seam)

    Myth engine weighted highest — a losslessly transmitted myth is the worst failure mode.
    css = 1.0 - (0.45*myth + 0.30*pattern + 0.25*temporal_drift)
    """
    distortion = (
        MYTH_WEIGHT    * myth +
        PATTERN_WEIGHT * pattern +
        TEMPORAL_WEIGHT * temporal_drift
    )
    return float(min(1.0, max(0.0, 1.0 - distortion)))


# ─── Cognitive State Register ─────────────────────────────────────────────────

@dataclass
class CognitiveStateRegister:
    """
    Full output of one HC scan. Injected into every LTE pipeline stage.
    Also used as the CSR (Channel State Register) update payload.
    """
    # Altitude Detector axes (existing, carried forward)
    abstraction_index:     float = 0.0
    density_index:         float = 0.0
    urgency_index:         float = 0.0   # UI — also borrowed by temporal drift

    # HC-specific axes
    epistemic_register:        float = 0.0   # ER
    evidence_anchoring:        float = 0.0   # EAS
    pattern_extrapolation:     float = 0.0   # PEI
    jtbd_distance:             float = 0.0   # JSD — requires session JTBD anchor
    narrative_coherence:       float = 0.0   # NCS

    # Derived features (intermediate, exposed for debugging)
    exception_density:         float = 0.0
    causal_ratio:              float = 0.0
    self_referential_density:  float = 0.0

    # Engine scores
    myth_engine_score:         float = 0.0
    pattern_engine_score:      float = 0.0
    temporal_drift_score:      float = 0.0

    # Composite output
    css: float = 1.0

    # Distortion flags (human-readable)
    active_distortions: list = field(default_factory=list)

    # Gate state
    gate_status: str = "pass"           # "pass" | "warn" | "halt"
    recommended_action: str = ""
    seam_text: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# ─── Distortion Flag Logic ────────────────────────────────────────────────────

def _compute_distortion_flags(csr: CognitiveStateRegister) -> list[str]:
    flags = []

    if csr.myth_engine_score >= 0.65:
        flags.append("MYTH_ENGINE: high certainty + thin evidence detected — story may be hardening into law")

    if csr.myth_engine_score >= 0.50 and csr.narrative_coherence > 0.5:
        flags.append("MYTH_ENGINE_NARRATIVE: polished story structure with low evidence base — check for hero narrative")

    if csr.pattern_engine_score >= 0.65:
        flags.append("PATTERN_ENGINE: claims extrapolating far beyond observed sample — check for overfit")

    if csr.temporal_drift_score >= 0.60:
        flags.append("TEMPORAL_DRIFT: signal has diverged from session JTBD anchor — check for scope creep")

    if csr.urgency_index >= 0.70:
        flags.append("URGENCY_INFLATION: high temporal urgency markers detected — validate if urgency is real")

    return flags


def _compute_gate_state(css: float) -> tuple[str, str, str]:
    """Returns (gate_status, recommended_action, seam_text)."""
    if css < CSS_GATE_THRESHOLD:
        return (
            "halt",
            "CSS below 0.65 — LTE halted. Review signal for distortion before retransmitting.",
            f"⚠ Sender cognitive confidence: {css:.2f}. Translation held pending review.",
        )
    elif css < CSS_SEAM_WARNING:
        return (
            "warn",
            "CSS below 0.75 — LTE proceeding with elevated seam. Flag active distortions in receipt.",
            f"Note: Sender cognitive confidence: {css:.2f}. {'; '.join(['See active distortions'])}",
        )
    else:
        return (
            "pass",
            "CSS healthy — LTE proceeds with standard seam.",
            "",
        )


# ─── Main HC Scan ─────────────────────────────────────────────────────────────

def run_hc_scan(
    text: str,
    jtbd_anchor: Optional[str] = None,
    use_embeddings: bool = False,
    abstraction_index: float = 0.0,   # pass-through from Altitude Detector if available
    density_index: float = 0.0,
) -> CognitiveStateRegister:
    """
    Full HC scan. Returns a populated CognitiveStateRegister.

    Args:
        text:              The raw signal to scan (sender's text).
        jtbd_anchor:       Session JTBD anchor string. Required for JSD.
                           If None, temporal drift scoring is weakened.
        use_embeddings:    Use sentence-transformer for JSD (default: lexical fallback).
        abstraction_index: Pass-through from Altitude Detector if already computed.
        density_index:     Pass-through from Altitude Detector if already computed.

    Returns:
        CognitiveStateRegister with all axes scored, engines computed, CSS set, gate evaluated.
    """
    tokens = _token_count(text)

    # ── 5 Axis Scores ──
    er  = score_epistemic_register(text)
    eas = score_evidence_anchoring(text)
    pei = score_pattern_extrapolation(text)
    jsd = score_jtbd_distance(text, jtbd_anchor, use_embeddings)
    ncs = score_narrative_coherence(text)
    ui  = score_urgency_index(text)

    # ── Derived Features ──
    exception_density = min(
        1.0,
        _density_per_100(_count_matches(_EXCEPTION_MARKERS, text), tokens) / 10.0
    )
    causal_ratio = min(
        1.0,
        _density_per_100(_count_matches(_CAUSAL_MARKERS, text), tokens) / 10.0
    )
    self_ref_density = min(
        1.0,
        _density_per_100(_count_matches(_SELF_REFERENTIAL_MARKERS, text), tokens) / 5.0
    )

    # ── Engine Scores ──
    myth    = compute_myth_engine_score(er, eas, ncs, exception_density)
    pattern = compute_pattern_engine_score(pei, eas, exception_density, causal_ratio)
    drift   = compute_temporal_drift_score(jsd, ui, self_ref_density)

    # ── CSS ──
    css = compute_css(myth, pattern, drift)

    # ── Build CSR ──
    csr = CognitiveStateRegister(
        abstraction_index     = abstraction_index,
        density_index         = density_index,
        urgency_index         = ui,
        epistemic_register    = er,
        evidence_anchoring    = eas,
        pattern_extrapolation = pei,
        jtbd_distance         = jsd,
        narrative_coherence   = ncs,
        exception_density     = exception_density,
        causal_ratio          = causal_ratio,
        self_referential_density = self_ref_density,
        myth_engine_score     = myth,
        pattern_engine_score  = pattern,
        temporal_drift_score  = drift,
        css                   = css,
    )

    # ── Flags + Gate ──
    csr.active_distortions = _compute_distortion_flags(csr)
    csr.gate_status, csr.recommended_action, csr.seam_text = _compute_gate_state(css)

    return csr


# ─── G2: Archetype Cold-Start Detection (Gap Closure v1.0) ───────────────────

ARCHETYPE_LEXICAL_FINGERPRINTS = {
    "QUANT":           {"patterns": [r"\d+%", r"\bp[<=>]\d", r"\bbaseline\b", r"\bstatistically\b", r"\bsignificant\b", r"\bcorrelation\b", r"\bn=\b", r"\bR²\b"], "weight": 2.5},
    "EXECUTOR":        {"patterns": [r"\bship\b", r"\bbuild\b", r"\bdeadline\b", r"\blaunch\b", r"\bsprint\b", r"\bblock\b", r"\bowner\b", r"\bdeliver\b"], "weight": 2.0},
    "ARCHITECT":       {"patterns": [r"\bsystem\b", r"\barchitecture\b", r"\bmodular\b", r"\binterface\b", r"\bscaffold\b", r"\bpipeline\b", r"\bschema\b"], "weight": 2.0},
    "INSTITUTIONALIST":{"patterns": [r"\bcompliance\b", r"\bpolicy\b", r"\brisk\b", r"\bregulat\b", r"\bstakeholder\b", r"\bgovernance\b", r"\bprocess\b"], "weight": 1.8},
    "CONNECTOR":       {"patterns": [r"\brelationship\b", r"\btrust\b", r"\bteam\b", r"\bpeople\b", r"\bculture\b", r"\balign\b", r"\bvibe\b"], "weight": 1.5},
    "PATTERN_MATCHER": {"patterns": [r"\bpattern\b", r"\belegant\b", r"\bfractal\b", r"\brecursi\b", r"\bunified\b", r"\btheory\b", r"\bprinciple\b"], "weight": 1.5},
    "PHILOSOPHER":     {"patterns": [r"\bmeaning\b", r"\bpurpose\b", r"\bwhy\b", r"\bidentity\b", r"\bvalue\b", r"\bbecoming\b", r"\bnarrative\b"], "weight": 1.3},
}

# Quadrant → archetype prior mapping (from hemisphere checker scores)
QUADRANT_ARCHETYPE_PRIORS: dict[str, dict[str, float]] = {
    "lf": {"ARCHITECT": 0.40, "PATTERN_MATCHER": 0.30, "INSTITUTIONALIST": 0.15, "EXECUTOR": 0.10, "CONNECTOR": 0.05},
    "rf": {"CONNECTOR": 0.35, "PHILOSOPHER": 0.30, "PATTERN_MATCHER": 0.20, "ARCHITECT": 0.10, "EXECUTOR": 0.05},
    "ln": {"QUANT": 0.40, "INSTITUTIONALIST": 0.30, "ARCHITECT": 0.15, "EXECUTOR": 0.10, "PATTERN_MATCHER": 0.05},
    "rn": {"EXECUTOR": 0.35, "CONNECTOR": 0.30, "PHILOSOPHER": 0.20, "QUANT": 0.10, "PATTERN_MATCHER": 0.05},
}


def lexical_archetype_scan(signal_text: str) -> dict[str, float]:
    """
    Naive fingerprint scan for archetype cold-start.
    Accuracy ~0.62 on clean business prose.
    Use only as cold-start fallback; CSR overrides within 3 turns.
    """
    scores: dict[str, float] = {a: 0.0 for a in ARCHETYPE_LEXICAL_FINGERPRINTS}
    text_lower = signal_text.lower()
    for archetype, config in ARCHETYPE_LEXICAL_FINGERPRINTS.items():
        for pattern in config["patterns"]:
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            scores[archetype] += matches * config["weight"]
    total = sum(scores.values()) or 1.0
    uniform = 1.0 / len(scores)
    smoothed = {k: (v/total * 0.80) + (uniform * 0.20) for k, v in scores.items()}
    return dict(sorted(smoothed.items(), key=lambda x: -x[1]))


def cold_start_archetype_prior(hemisphere_scores: dict[str, int]) -> dict[str, float]:
    """
    Given hemisphere checker scores {lf, rf, ln, rn}, return weighted
    prior over archetypes by blending the quadrant-archetype maps.
    """
    total = sum(hemisphere_scores.values()) or 1
    blended: dict[str, float] = {}
    for quadrant, raw_score in hemisphere_scores.items():
        weight = raw_score / total
        for archetype, prior in QUADRANT_ARCHETYPE_PRIORS.get(quadrant, {}).items():
            blended[archetype] = blended.get(archetype, 0.0) + weight * prior
    total_prob = sum(blended.values()) or 1
    return {k: v / total_prob for k, v in sorted(blended.items(), key=lambda x: -x[1])}


# ─── Session JTBD Anchor Management ───────────────────────────────────────────

class HCSession:
    """
    Manages session-level state for HC: JTBD anchor, CSS history,
    turn count, and running trust calibration.

    Usage:
        session = HCSession(jtbd="Should we hire a head of sales now?")
        csr = session.scan("Here's my thinking on the hire...")
        print(csr.css, csr.active_distortions)
    """

    def __init__(
        self,
        jtbd: Optional[str] = None,
        use_embeddings: bool = False,
    ):
        self.jtbd = jtbd
        self.use_embeddings = use_embeddings
        self.turn_count = 0
        self.css_history: list[float] = []
        self.distortion_history: list[list[str]] = []

    def scan(
        self,
        text: str,
        abstraction_index: float = 0.0,
        density_index: float = 0.0,
    ) -> CognitiveStateRegister:
        """Run a full HC scan for one turn."""
        csr = run_hc_scan(
            text=text,
            jtbd_anchor=self.jtbd,
            use_embeddings=self.use_embeddings,
            abstraction_index=abstraction_index,
            density_index=density_index,
        )
        self.turn_count += 1
        self.css_history.append(csr.css)
        self.distortion_history.append(csr.active_distortions)
        return csr

    @property
    def avg_css(self) -> float:
        if not self.css_history:
            return 1.0
        return sum(self.css_history) / len(self.css_history)

    @property
    def trust_calibration_score(self) -> float:
        """
        Long-run sender reliability: avg CSS weighted toward recent turns.
        Converges after ~5 turns.
        """
        if not self.css_history:
            return 1.0
        n = len(self.css_history)
        weights = [math.exp(0.3 * i) for i in range(n)]
        w_sum = sum(weights)
        return sum(c * w for c, w in zip(self.css_history, weights)) / w_sum

    @property
    def is_stable(self) -> bool:
        """Session is cognitively stable if avg CSS ≥ 0.75 over last 3 turns."""
        recent = self.css_history[-3:] if len(self.css_history) >= 3 else self.css_history
        return bool(recent) and (sum(recent) / len(recent)) >= CSS_SEAM_WARNING

    def summary(self) -> dict:
        return {
            "jtbd": self.jtbd,
            "turn_count": self.turn_count,
            "avg_css": round(self.avg_css, 3),
            "trust_calibration_score": round(self.trust_calibration_score, 3),
            "is_stable": self.is_stable,
            "css_history": [round(c, 3) for c in self.css_history],
        }


# ─── CLI Smoke Test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("ARCS HC — Smoke Test")
    print("=" * 60)

    test_cases = [
        {
            "label": "HEALTHY — measured, evidence-grounded",
            "jtbd": "Should we expand to enterprise sales?",
            "text": (
                "Based on the last three deals, which all came through warm intros, "
                "our close rate on enterprise seems to be around 30%. That might suggest "
                "a structured outbound motion could work, but I'd want to validate with "
                "at least five more data points before committing headcount. The risk is "
                "that we hire too early and the pipeline dries up."
            ),
        },
        {
            "label": "MYTH ENGINE — certainty + no evidence + narrative arc",
            "jtbd": "Should we expand to enterprise sales?",
            "text": (
                "This is clearly the right moment to go enterprise. The market is obviously "
                "ready. Everyone in our space is doing it. It will definitely unlock the "
                "growth we need. The story writes itself: we started scrappy, we proved the "
                "model, and now we scale. This is how every great B2B company has done it. "
                "We need to move now."
            ),
        },
        {
            "label": "PATTERN ENGINE — extrapolation far beyond sample",
            "jtbd": "Should we expand to enterprise sales?",
            "text": (
                "Enterprise always beats SMB in B2B SaaS. The data universally shows that "
                "net revenue retention is higher in enterprise. As a rule, companies that "
                "move upmarket earlier always outperform. This pattern is consistent across "
                "every category I've ever seen. It always works this way."
            ),
        },
        {
            "label": "TEMPORAL DRIFT — off JTBD, low urgency",
            "jtbd": "Should we expand to enterprise sales?",
            "text": (
                "I've been thinking about our brand positioning and the long-term narrative "
                "of what we're building. There's something about the way we tell our story "
                "that might not resonate with the kind of founders we want to attract as "
                "advisors. The community angle feels underexplored. I wonder if we should "
                "invest more in thought leadership."
            ),
        },
    ]

    for case in test_cases:
        print(f"\n{'─' * 50}")
        print(f"  {case['label']}")
        print(f"{'─' * 50}")
        session = HCSession(jtbd=case["jtbd"])
        csr = session.scan(case["text"])
        print(f"  CSS:              {csr.css:.3f}  [{csr.gate_status.upper()}]")
        print(f"  Myth Engine:      {csr.myth_engine_score:.3f}")
        print(f"  Pattern Engine:   {csr.pattern_engine_score:.3f}")
        print(f"  Temporal Drift:   {csr.temporal_drift_score:.3f}")
        print(f"  ER / EAS / PEI:   {csr.epistemic_register:.2f} / {csr.evidence_anchoring:.2f} / {csr.pattern_extrapolation:.2f}")
        print(f"  JSD / NCS:        {csr.jtbd_distance:.2f} / {csr.narrative_coherence:.2f}")
        if csr.active_distortions:
            for flag in csr.active_distortions:
                print(f"  ⚠  {flag}")
        if csr.seam_text:
            print(f"  Seam: {csr.seam_text}")
        else:
            print(f"  → {csr.recommended_action}")

    print("\n" + "=" * 60)
    print("Smoke test complete.")
    print("=" * 60)
