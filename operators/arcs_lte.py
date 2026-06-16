"""
arcs_lte.py — ARCS Lossless Translation Engine (LTE)
=====================================================
7-stage pipeline: HC pre-scan → Intake → Altitude Detector →
Lossless Codex → Rhetorical Resonance Engine → Recomp → Transceiver

Spec: ARCS-LTE-SPEC-v1.0 + LTE_Gap_Closure_v1.0
HC integration: arcs_hc.py (fires before Intake; CSS modulates all stages)

Design invariants:
  - Meaning is the carrier wave; expression is the modulation layer
  - IPS ≥ 0.95: no translation drops a semantic invariant
  - CSS < 0.65 gates the pipeline (halt or mandatory seam)
  - Every output carries a visible seam + full TranslationReceipt
"""

from __future__ import annotations

import re
import json
import uuid
import math
import hashlib
from dataclasses import dataclass, field, asdict
from enum import IntEnum
from typing import Optional, Literal
from datetime import datetime, timezone

from arcs_hc import (
    HCSession,
    CognitiveStateRegister,
    CognitiveSafetyScore,
    run_hc_scan,
    CSS_GATE_THRESHOLD,
    CSS_SEAM_WARNING,
    lexical_archetype_scan,
    cold_start_archetype_prior,
)


# ─── Enums & Constants ────────────────────────────────────────────────────────

class AltitudeLevel(IntEnum):
    L0_VISCERAL   = 0   # Short verbs, metaphors, 1 idea — max compression (10:1)
    L1_OPERATIONAL = 1  # Steps, who/what/when, bullets — high compression (7:1)
    L2_TACTICAL   = 2   # Frameworks, tradeoffs, KPIs — medium compression (4:1)
    L3_STRATEGIC  = 3   # Systems, incentives, 2nd-order — low compression (2:1)
    L4_CONCEPTUAL = 4   # Models, principles, optionality — minimal (1.5:1)
    L5_EPISTEMIC  = 5   # Math, meta-frameworks, proofs — expand only


TranslationMode = Literal["inform", "persuade", "brief", "instruct", "receipt"]

# Max compression ratios per altitude delta (invariants must survive regardless)
MAX_COMPRESSION: dict[tuple[int, int], float] = {
    (5, 0): 10.0,   # L5 → L0: strip all frameworks, one verb-noun
    (5, 1): 7.0,
    (5, 2): 4.0,
    (4, 0): 8.0,
    (4, 1): 5.0,
    (3, 0): 6.0,
    (3, 1): 3.0,
    (2, 0): 4.0,
    (1, 0): 2.0,
    (0, 5): 0.125,  # L0 → L5: expansion (8x)
    (0, 4): 0.2,
    (0, 3): 0.33,
    (1, 5): 0.2,
    (2, 5): 0.33,
}

IPS_THRESHOLD    = 0.95   # invariant preservation score minimum
RESONANCE_TARGET = 0.80   # |⟨ψ_msg|ψ_aud⟩|² target
PHASE_DELTA_MAX  = 0.15   # radians — phase misalignment ceiling


# ─── Core Data Models ─────────────────────────────────────────────────────────

@dataclass
class RhetoricalAtom:
    atom_id:    str
    atom_type:  Literal["claim", "evidence", "imperative", "question", "metaphor"]
    text:       str
    weight:     float      # 0.0–1.0
    invariant:  bool       # must survive translation
    droppable:  bool       # can be dropped without changing core meaning


@dataclass
class SemanticSkeleton:
    invariants:      list[str]          # load-bearing claims
    droppable:       list[str]          # stylistic elements
    rhetorical_atoms: list[RhetoricalAtom]
    signal_entropy:  float              # 0.0–1.0 (Shannon entropy proxy)
    raw_altitude_estimate: int = 3


@dataclass
class AltitudeProfile:
    source_altitude:          AltitudeLevel
    altitude_confidence:      float
    abstraction_index:        float    # AI
    density_index:            float    # DI
    urgency_index:            float    # UI
    altitude_delta:           float    # source - target
    translation_direction:    Literal["compress", "expand", "lateral"]
    compression_ratio_required: str   # e.g., "4:1"


@dataclass
class ArchetypeProfile:
    archetype_id:      str
    name:              str
    native_altitude:   int
    value_anchors:     list[str]
    forbidden_vocab:   list[str]
    trust_builders:    list[str]
    kairos_triggers:   list[str]
    energy_signature:  str
    sample_phrases:    list[str]
    belief_states:     list[str]
    amplitudes:        list[float]   # |c_i|^2 = probability weight


@dataclass
class TranslationReceipt:
    receipt_id:                str
    timestamp:                 str
    source_altitude:           int
    target_altitude:           int
    compression_ratio_achieved: str
    ips:                       float
    resonance_amplitude:       float
    phase_delta:               float
    invariants_preserved:      list[str]
    invariants_compressed:     list[str]
    style_dropped:             list[str]
    what_was_compressed:       str
    visible_seam:              str
    confidence_score:          float
    nci_grade:                 int
    sender_css:                Optional[float] = None
    active_distortions:        list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LTERequest:
    raw_signal:     str
    target_altitude: AltitudeLevel
    target_archetype: str              # archetype_id from registry
    mode:           TranslationMode = "inform"
    source_context: Optional[dict]  = None
    jtbd_anchor:    Optional[str]   = None
    hemisphere_scores: Optional[dict] = None   # from HC cold-start


@dataclass
class LTEResponse:
    translated_signal:  str
    source_altitude:    AltitudeLevel
    target_altitude:    AltitudeLevel
    ips:                float
    resonance_amplitude: float
    phase_delta:        float
    receipt:            TranslationReceipt
    gate_status:        str    # "pass" | "warn" | "halt"
    csr:                Optional[CognitiveStateRegister] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        if self.csr:
            d["csr"] = self.csr.to_dict()
        return d


# ─── Lossless Codex ───────────────────────────────────────────────────────────
# The master translation dictionary. Archetype registry + compression rules.

ARCHETYPE_REGISTRY: dict[str, ArchetypeProfile] = {
    "QUANT": ArchetypeProfile(
        archetype_id   = "QUANT",
        name           = "Technical Founder / Analyst",
        native_altitude = 5,
        value_anchors  = ["proof", "ROI", "falsifiability", "baseline", "delta", "statistical significance"],
        forbidden_vocab = ["vibes", "resonance", "feels right", "energy", "authenticity", "narrative"],
        trust_builders  = ["here's the data", "the numbers show", "tested on", "confidence interval", "n="],
        kairos_triggers = ["the model says", "the signal is clear", "p < 0.05"],
        energy_signature = "pulse",
        sample_phrases  = ["what's the effect size?", "can we falsify this?", "show me the baseline"],
        belief_states   = ["evidence over intuition", "models over stories", "measurable over meaningful"],
        amplitudes      = [0.55, 0.30, 0.15],
    ),
    "CONNECTOR": ArchetypeProfile(
        archetype_id   = "CONNECTOR",
        name           = "Rainmaker / Brand Alchemist",
        native_altitude = 2,
        value_anchors  = ["relationship", "trust", "team alignment", "brand", "culture", "vibe"],
        forbidden_vocab = ["statistically", "p-value", "regression", "variance", "null hypothesis"],
        trust_builders  = ["this feels right for the team", "the relationship is strong", "people are aligned"],
        kairos_triggers = ["the moment is right", "the energy in the room", "I'm feeling momentum"],
        energy_signature = "sine",
        sample_phrases  = ["how does this land with people?", "what's the trust level?", "are we aligned?"],
        belief_states   = ["relationships before transactions", "trust is the moat", "culture eats strategy"],
        amplitudes      = [0.45, 0.35, 0.20],
    ),
    "ARCHITECT": ArchetypeProfile(
        archetype_id   = "ARCHITECT",
        name           = "Builder / System Thinker",
        native_altitude = 4,
        value_anchors  = ["system design", "constraints", "moats", "interface contracts", "edge cases"],
        forbidden_vocab = ["vibe check", "gut feel", "seems good", "move fast"],
        trust_builders  = ["here's the system diagram", "the interface is clean", "edge cases are handled"],
        kairos_triggers = ["the architecture is ready", "we've de-risked the critical path"],
        energy_signature = "square",
        sample_phrases  = ["what breaks first?", "where's the bottleneck?", "what's the failure mode?"],
        belief_states   = ["systems over heroics", "constraints clarify", "good interfaces outlast good code"],
        amplitudes      = [0.50, 0.30, 0.20],
    ),
    "INSTITUTIONALIST": ArchetypeProfile(
        archetype_id   = "INSTITUTIONALIST",
        name           = "Strategist / Impact Weaver",
        native_altitude = 3,
        value_anchors  = ["process", "evidence", "alignment", "governance", "stakeholder buy-in"],
        forbidden_vocab = ["disrupt", "move fast", "burn it down", "10x", "moonshot"],
        trust_builders  = ["this is consistent with our process", "stakeholders are aligned", "evidence supports"],
        kairos_triggers = ["the committee meets next week", "the window for alignment is now"],
        energy_signature = "carrier",
        sample_phrases  = ["what's the governance path?", "who are the stakeholders?", "what's the precedent?"],
        belief_states   = ["evolution over revolution", "process as protection", "alignment before action"],
        amplitudes      = [0.40, 0.35, 0.25],
    ),
    "EXECUTOR": ArchetypeProfile(
        archetype_id   = "EXECUTOR",
        name           = "Operator / Manager",
        native_altitude = 1,
        value_anchors  = ["clarity", "owner", "deadline", "deliverable", "unblocked"],
        forbidden_vocab = ["theoretical", "in principle", "philosophically", "it depends", "nuanced"],
        trust_builders  = ["here's the action plan", "owner is assigned", "deadline is set"],
        kairos_triggers = ["the sprint starts Monday", "we're blocked right now"],
        energy_signature = "square",
        sample_phrases  = ["who owns this?", "what's the deadline?", "what's blocking us?"],
        belief_states   = ["done > perfect", "clarity of ownership", "momentum beats optimization"],
        amplitudes      = [0.50, 0.35, 0.15],
    ),
    "PHILOSOPHER": ArchetypeProfile(
        archetype_id   = "PHILOSOPHER",
        name           = "Humanist Founder",
        native_altitude = 3,
        value_anchors  = ["meaning", "identity", "becoming", "purpose", "narrative coherence"],
        forbidden_vocab = ["KPI", "OKR", "throughput", "utilization", "burn rate"],
        trust_builders  = ["this aligns with why we started", "the story holds together", "it's coherent"],
        kairos_triggers = ["this is the moment that defines us", "the inflection point is here"],
        energy_signature = "long_wave",
        sample_phrases  = ["what does this say about who we are?", "is this coherent with our origin?"],
        belief_states   = ["meaning before metrics", "narrative as strategy", "identity is durable"],
        amplitudes      = [0.45, 0.35, 0.20],
    ),
    "CAVEMAN": ArchetypeProfile(
        archetype_id   = "CAVEMAN",
        name           = "Fast Mover / Reactive",
        native_altitude = 0,
        value_anchors  = ["win", "now", "fast", "simple", "clear"],
        forbidden_vocab = ["framework", "strategic", "optimize", "leverage", "stakeholder"],
        trust_builders  = ["one thing", "do this", "it works"],
        kairos_triggers = ["now", "today", "go"],
        energy_signature = "spike",
        sample_phrases  = ["just tell me what to do", "is it good or bad?", "yes or no?"],
        belief_states   = ["action beats analysis", "simple beats complex"],
        amplitudes      = [0.70, 0.30],
    ),
}

def get_archetype(archetype_id: str) -> ArchetypeProfile:
    return ARCHETYPE_REGISTRY.get(archetype_id.upper(), ARCHETYPE_REGISTRY["EXECUTOR"])


# ─── Stage 1: Intake Module (Decomp) ─────────────────────────────────────────

def _estimate_entropy(text: str) -> float:
    """Shannon entropy proxy based on unique token ratio."""
    tokens = text.lower().split()
    if not tokens:
        return 0.0
    unique = len(set(tokens))
    ratio = unique / len(tokens)
    return float(min(1.0, ratio))


def _extract_invariants_stub(raw_signal: str, llm_client=None) -> list[str]:
    """
    G1 stub: extract load-bearing claims from raw signal.
    v1.0: LLM call when client available; sentence-chunking fallback otherwise.
    A claim is invariant if negating it changes the signal's core ask.
    """
    if llm_client is not None:
        try:
            prompt = f"""You are a semantic parsing engine. Extract LOAD-BEARING CLAIMS only.

A load-bearing claim:
1. Cannot be removed without changing what the speaker is fundamentally asking for
2. Could in principle be true or false (falsifiable)
3. Would need to survive word-for-word into any paraphrase

Signal:
<signal>{raw_signal}</signal>

List ONLY load-bearing claims. Maximum 7. Each: one declarative sentence, stripped of emotion.
Do NOT include: tone, examples, analogies, emotional framing, meta-commentary.
Return ONLY a JSON array of strings. No explanation."""
            response = llm_client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            claims = json.loads(text)
            return [c for c in claims if isinstance(c, str)][:7]
        except Exception:
            pass  # fall through to sentence chunking

    # Fallback: sentence chunks as candidate invariants
    sentences = re.split(r'[.!?]+', raw_signal)
    candidates = [s.strip() for s in sentences if len(s.strip()) > 20]
    return candidates[:5]


def run_intake(raw_signal: str, css: float = 1.0, llm_client=None) -> SemanticSkeleton:
    """
    Stage 1: Decompose raw signal into semantic skeleton.
    CSS modulates invariant confidence floor: low CSS flags invariants as conditional.
    """
    invariants = _extract_invariants_stub(raw_signal, llm_client)
    entropy = _estimate_entropy(raw_signal)

    # Everything not in invariants is potentially droppable
    remaining = raw_signal
    for inv in invariants:
        remaining = remaining.replace(inv, "")
    droppable_sentences = [s.strip() for s in re.split(r'[.!?]+', remaining) if len(s.strip()) > 10]

    atoms: list[RhetoricalAtom] = []
    for i, inv in enumerate(invariants):
        atoms.append(RhetoricalAtom(
            atom_id   = f"inv_{i}",
            atom_type = "claim",
            text      = inv,
            weight    = 0.9 if css >= CSS_SEAM_WARNING else 0.7,   # CSS lowers confidence
            invariant = True,
            droppable = False,
        ))
    for i, drop in enumerate(droppable_sentences[:5]):
        atoms.append(RhetoricalAtom(
            atom_id   = f"drop_{i}",
            atom_type = "evidence" if any(w in drop.lower() for w in ["because","data","measured","found"]) else "metaphor",
            text      = drop,
            weight    = 0.3,
            invariant = False,
            droppable = True,
        ))

    return SemanticSkeleton(
        invariants             = invariants,
        droppable              = droppable_sentences[:5],
        rhetorical_atoms       = atoms,
        signal_entropy         = entropy,
        raw_altitude_estimate  = 3,   # will be overwritten by Altitude Detector
    )


# ─── Stage 2: Altitude Detector ───────────────────────────────────────────────

_ABSTRACT_VOCAB = re.compile(
    r"\b(strategy|framework|paradigm|optimize|leverage|architecture|"
    r"ontology|epistem|systemic|emergent|meta|heuristic|inference|"
    r"axiom|coherence|convergence|divergence|derivative|vector|"
    r"orthogonal|canonical|recursive|isomorphic|invariant|modular|"
    r"latent|semantic|synthesis|abstraction|principle|hypothesis)\b",
    re.IGNORECASE,
)

_CONCRETE_VOCAB = re.compile(
    r"\b(do|ship|build|send|call|hire|fire|buy|sell|fix|launch|"
    r"deadline|tomorrow|today|now|step|task|who|what|when|"
    r"meeting|email|budget|cost|number|percent|customer|user)\b",
    re.IGNORECASE,
)

_DENSITY_MARKERS = re.compile(
    r"\b(because|therefore|however|whereas|consequently|furthermore|"
    r"additionally|alternatively|simultaneously|notwithstanding|"
    r"specifically|particularly|arguably|inherently|fundamentally)\b",
    re.IGNORECASE,
)


def _score_abstraction_index(text: str) -> float:
    tokens = max(1, len(text.split()))
    abstract = len(_ABSTRACT_VOCAB.findall(text))
    concrete = len(_CONCRETE_VOCAB.findall(text))
    total = abstract + concrete
    if total == 0:
        return 0.40  # neutral prior
    ratio = abstract / total
    return float(min(1.0, max(0.0, ratio)))


def _score_density_index(text: str) -> float:
    """Concepts per sentence proxy: connective tissue density."""
    tokens = max(1, len(text.split()))
    connectives = len(_DENSITY_MARKERS.findall(text))
    sentences = max(1, len(re.split(r'[.!?]+', text)))
    # Avg concepts per sentence (connective markers signal multi-concept sentences)
    density = (connectives / sentences) / 3.0   # normalize: 3 connectives/sentence = 1.0
    return float(min(1.0, max(0.0, density)))


def _score_urgency_index(text: str) -> float:
    """Reuse HC urgency scoring."""
    from arcs_hc import score_urgency_index
    return score_urgency_index(text)


def run_altitude_detector(
    text: str,
    skeleton: SemanticSkeleton,
    target_altitude: AltitudeLevel,
    csr: Optional[CognitiveStateRegister] = None,
) -> AltitudeProfile:
    """
    Stage 2: Score source signal's cognitive altitude (L0-L5) across 3 axes.
    α=0.45 * AI + β=0.40 * DI + γ=0.15 * UI

    HC modulation: urgency index is dampened if csr.temporal_drift_score is high
    (prevents urgency inflation from a drifting sender inflating altitude estimate).
    """
    ai = _score_abstraction_index(text)
    di = _score_density_index(text)
    ui = _score_urgency_index(text)

    # HC modulation: suppress urgency inflation if sender is temporally drifted
    if csr and csr.temporal_drift_score > 0.60:
        ui = ui * (1.0 - 0.5 * csr.temporal_drift_score)

    raw_score = (0.45 * ai + 0.40 * di + 0.15 * ui) * 5.0
    source_alt = int(round(min(5, max(0, raw_score))))

    delta = source_alt - int(target_altitude)
    if abs(delta) <= 0.5:
        direction = "lateral"
    elif delta > 0:
        direction = "compress"
    else:
        direction = "expand"

    # Compression ratio from table or linear fallback
    ratio_key = (source_alt, int(target_altitude))
    ratio = MAX_COMPRESSION.get(ratio_key, max(1.0, abs(delta) * 1.5))
    if direction == "expand":
        ratio_str = f"1:{int(1/ratio) if ratio < 1 else int(ratio)}"
    elif direction == "compress":
        ratio_str = f"{ratio:.1f}:1"
    else:
        ratio_str = "1:1"

    # Altitude confidence: higher when AI and DI agree
    confidence = 1.0 - abs(ai - di) * 0.5

    skeleton.raw_altitude_estimate = source_alt

    return AltitudeProfile(
        source_altitude           = AltitudeLevel(source_alt),
        altitude_confidence       = round(confidence, 3),
        abstraction_index         = round(ai, 3),
        density_index             = round(di, 3),
        urgency_index             = round(ui, 3),
        altitude_delta            = delta,
        translation_direction     = direction,
        compression_ratio_required = ratio_str,
    )


# ─── Stage 3: Lossless Codex ──────────────────────────────────────────────────

def _wavefunction_resonance(
    message_anchors: list[str],
    archetype: ArchetypeProfile,
) -> tuple[float, float]:
    """
    Simplified resonance score: |⟨ψ_msg|ψ_aud⟩|²
    v1.0: cosine-like overlap of message concepts vs archetype belief states.
    Returns (resonance_score, phase_delta).
    """
    if not message_anchors or not archetype.belief_states:
        return 0.50, 0.30

    msg_text = " ".join(message_anchors).lower()
    belief_text = " ".join(archetype.belief_states + archetype.value_anchors).lower()
    forbidden_text = " ".join(archetype.forbidden_vocab).lower()

    # Count concept overlap
    msg_words = set(re.findall(r"\b[a-z]{3,}\b", msg_text))
    belief_words = set(re.findall(r"\b[a-z]{3,}\b", belief_text))
    forbidden_words = set(re.findall(r"\b[a-z]{3,}\b", forbidden_text))

    overlap = len(msg_words & belief_words)
    friction = len(msg_words & forbidden_words)
    total = len(msg_words) or 1

    raw_resonance = (overlap - friction * 2) / total
    resonance = float(min(1.0, max(0.0, 0.50 + raw_resonance * 2)))

    # Phase delta: how much friction vocabulary creates phase misalignment
    phase_delta = float(min(math.pi, friction / max(1, len(msg_words)) * math.pi))

    return resonance, phase_delta


def run_codex_lookup(
    skeleton: SemanticSkeleton,
    altitude_profile: AltitudeProfile,
    target_archetype: str,
) -> tuple[ArchetypeProfile, float, float]:
    """
    Stage 3: Load archetype + compute resonance baseline.
    Returns (archetype, resonance_score, phase_delta).
    """
    archetype = get_archetype(target_archetype)
    resonance, phase_delta = _wavefunction_resonance(skeleton.invariants, archetype)
    return archetype, resonance, phase_delta


# ─── Stage 4: Rhetorical Resonance Engine (RRE) ───────────────────────────────

def _apply_altitude_shift(
    text: str,
    source_alt: int,
    target_alt: int,
    archetype: ArchetypeProfile,
    llm_client=None,
) -> str:
    """ALTITUDE_SHIFT: rewrite at target L-level vocabulary."""
    if llm_client is not None:
        try:
            alt_map = {
                0: "ground-level: one simple sentence, strong verb, zero jargon",
                1: "operational: steps, who/what/when, bullet-friendly, plain language",
                2: "tactical: frameworks OK, tradeoffs named, KPIs welcome",
                3: "strategic: systems thinking, 2nd-order effects, incentives",
                4: "conceptual: models, principles, optionality framing",
                5: "epistemic: mathematical precision, meta-frameworks, full rigor",
            }
            prompt = f"""Rewrite the following text at altitude level {target_alt} ({alt_map[target_alt]}).
Source altitude: {source_alt} ({alt_map[source_alt]}).
Target audience: {archetype.name}.

Preserve ALL factual claims. Change only vocabulary, density, and framing.
Original:
{text}

Rewrite ONLY. No preamble, no explanation."""
            response = llm_client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()
        except Exception:
            pass

    # Rule-based fallback: replace forbidden vocab with archetype-native terms
    result = text
    for forbidden in archetype.forbidden_vocab:
        # Simple swap: forbidden vocab gets softened/removed
        result = re.sub(rf"\b{re.escape(forbidden)}\b", "", result, flags=re.IGNORECASE)
    return result.strip()


def _apply_value_anchor_inject(text: str, archetype: ArchetypeProfile) -> str:
    """VALUE_ANCHOR_INJECT: front-load trust-building concepts."""
    if not archetype.trust_builders:
        return text
    anchor = archetype.trust_builders[0]
    return f"{anchor}: {text}"


def _apply_forbidden_vocab_strip(text: str, archetype: ArchetypeProfile) -> str:
    """FORBIDDEN_VOCAB_STRIP: remove vocabulary that triggers rejection."""
    result = text
    for vocab in archetype.forbidden_vocab:
        result = re.sub(rf"\b{re.escape(vocab)}\b", "[omitted]", result, flags=re.IGNORECASE)
    result = re.sub(r"\[omitted\](\s*\[omitted\])+", "[omitted]", result)
    return result.strip()


def _apply_kairos_inject(text: str, archetype: ArchetypeProfile, urgency: float) -> str:
    """KAIROS_INJECT: time-stamp signal when urgency is genuine."""
    if urgency < 0.50 or not archetype.kairos_triggers:
        return text
    trigger = archetype.kairos_triggers[0]
    return f"{text}\n\n→ Timing: {trigger}."


def _apply_visceral_translate(text: str, archetype: ArchetypeProfile, llm_client=None) -> str:
    """VISCERAL_TRANSLATE: convert abstract claim to gut-level metaphor (L0-L1 targets)."""
    if llm_client is not None:
        try:
            prompt = f"""Convert this abstract claim into a visceral, gut-level metaphor for someone who thinks in terms of: {', '.join(archetype.value_anchors[:3])}.

One or two sentences max. Use concrete imagery. No jargon.

Claim: {text}

Metaphor only. No explanation."""
            response = llm_client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()
        except Exception:
            pass
    # Fallback: strip all multi-syllable words and keep subject+verb
    words = text.split()
    simple = [w for w in words if len(w) <= 8 or w[0].isupper()][:10]
    return " ".join(simple) + "."


def run_rre(
    skeleton: SemanticSkeleton,
    altitude_profile: AltitudeProfile,
    archetype: ArchetypeProfile,
    mode: TranslationMode,
    csr: Optional[CognitiveStateRegister],
    llm_client=None,
) -> tuple[str, list[str], float]:
    """
    Stage 4: Rhetorical Resonance Engine.
    Returns (transformed_text, ops_applied, resonance_score).

    CSS modulations:
    - Pattern Engine high → suppress BANDWAGON_AMPLIFY
    - Myth Engine high → add 'pattern claim — evidence not verified' seam
    - CSS < WARN → force FORBIDDEN_VOCAB_STRIP regardless of mode
    """
    source_text = " ".join(skeleton.invariants + skeleton.droppable[:2])
    ops_applied: list[str] = []
    result = source_text

    src = int(altitude_profile.source_altitude)
    tgt = int(archetype.native_altitude)

    # Always apply these
    result = _apply_altitude_shift(result, src, tgt, archetype, llm_client)
    ops_applied.append("ALTITUDE_SHIFT")

    result = _apply_forbidden_vocab_strip(result, archetype)
    ops_applied.append("FORBIDDEN_VOCAB_STRIP")

    result = _apply_value_anchor_inject(result, archetype)
    ops_applied.append("VALUE_ANCHOR_INJECT")

    # Conditional ops
    if altitude_profile.urgency_index > 0.50:
        result = _apply_kairos_inject(result, archetype, altitude_profile.urgency_index)
        ops_applied.append("KAIROS_INJECT")

    if tgt <= 1:   # L0 or L1 target: visceral translate
        core = " ".join(skeleton.invariants[:2])
        result = _apply_visceral_translate(core, archetype, llm_client)
        ops_applied.append("VISCERAL_TRANSLATE")

    # CSS gate: suppress social proof if sender is pattern-distorted
    if csr and csr.pattern_engine_score < 0.50 and mode == "persuade":
        result = result + f"\n\n(Adopted by {len(archetype.belief_states) * 100}+ practitioners.)"
        ops_applied.append("BANDWAGON_AMPLIFY")

    resonance, _ = _wavefunction_resonance(skeleton.invariants, archetype)
    return result, ops_applied, resonance


# ─── Stage 5: Recomp Module ───────────────────────────────────────────────────

def _compute_ips(
    original_invariants: list[str],
    translated_text: str,
) -> tuple[float, list[str], list[str]]:
    """
    Invariant Preservation Score: fraction of invariant concepts
    that survive in the translated text.

    v1.0: keyword overlap proxy.
    Future: sentence-transformer cosine similarity per invariant.
    """
    preserved = []
    compressed = []

    for inv in original_invariants:
        # Extract key nouns/verbs from invariant
        inv_words = set(re.findall(r"\b[a-z]{3,}\b", inv.lower()))
        trans_words = set(re.findall(r"\b[a-z]{3,}\b", translated_text.lower()))
        stopwords = {"the","and","for","with","this","that","are","was","have","has"}
        inv_content = inv_words - stopwords
        trans_content = trans_words - stopwords

        if not inv_content:
            preserved.append(inv)
            continue

        overlap = len(inv_content & trans_content) / len(inv_content)
        if overlap >= 0.40:   # at least 40% of key concepts present
            preserved.append(inv)
        else:
            compressed.append(inv)

    ips = len(preserved) / max(1, len(original_invariants))
    return round(ips, 3), preserved, compressed


def _build_seam(
    ips: float,
    resonance: float,
    css: Optional[float],
    what_compressed: str,
    active_distortions: list[str],
) -> str:
    """Build the visible seam string — the Kintsugi mark on the translation."""
    parts = []
    if ips < IPS_THRESHOLD:
        parts.append(f"⚠ Compression note: some nuance was reduced (IPS: {ips:.2f}). {what_compressed}")
    if resonance < RESONANCE_TARGET:
        parts.append(f"Resonance below target ({resonance:.2f}) — may need further tuning.")
    if css is not None and css < CSS_SEAM_WARNING:
        parts.append(f"Sender cognitive confidence: {css:.2f}.")
    for distortion in active_distortions:
        if "MYTH" in distortion:
            parts.append("Pattern claim — check evidence base before transmitting.")
            break
    return " | ".join(parts) if parts else ""


def run_recomp(
    skeleton: SemanticSkeleton,
    altitude_profile: AltitudeProfile,
    archetype: ArchetypeProfile,
    translated_text: str,
    ops_applied: list[str],
    resonance: float,
    phase_delta: float,
    csr: Optional[CognitiveStateRegister],
    target_altitude: AltitudeLevel,
    mode: TranslationMode,
) -> tuple[str, TranslationReceipt]:
    """
    Stage 5: Validate IPS, build receipt, generate seam.
    If IPS < 0.95, append any missing invariants verbatim (recovery pass).
    """
    ips, preserved, compressed_invs = _compute_ips(skeleton.invariants, translated_text)

    # Recovery pass: if IPS too low, inject missing invariants
    if ips < IPS_THRESHOLD and compressed_invs:
        recovery = " | ".join(f"[{inv}]" for inv in compressed_invs)
        translated_text += f"\n\nKey points preserved: {recovery}"
        ips, preserved, compressed_invs = _compute_ips(skeleton.invariants, translated_text)

    src_tokens = max(1, len(" ".join(skeleton.invariants + skeleton.droppable).split()))
    tgt_tokens = max(1, len(translated_text.split()))
    actual_ratio = src_tokens / tgt_tokens
    ratio_str = f"{actual_ratio:.1f}:1" if actual_ratio >= 1 else f"1:{int(1/actual_ratio)}"

    what_compressed = (
        f"Style elements dropped: {', '.join(skeleton.droppable[:2])}."
        if skeleton.droppable else "No content dropped."
    )

    css_val = csr.css if csr else None
    active_dist = csr.active_distortions if csr else []

    seam = _build_seam(ips, resonance, css_val, what_compressed, active_dist)

    confidence = min(1.0, ips * 0.60 + resonance * 0.30 + (css_val or 1.0) * 0.10)
    nci_grade = int(round(confidence * 100))

    receipt = TranslationReceipt(
        receipt_id                 = str(uuid.uuid4()),
        timestamp                  = datetime.now(timezone.utc).isoformat(),
        source_altitude            = int(altitude_profile.source_altitude),
        target_altitude            = int(target_altitude),
        compression_ratio_achieved = ratio_str,
        ips                        = ips,
        resonance_amplitude        = round(resonance, 3),
        phase_delta                = round(phase_delta, 3),
        invariants_preserved       = preserved,
        invariants_compressed      = compressed_invs,
        style_dropped              = skeleton.droppable[:3],
        what_was_compressed        = what_compressed,
        visible_seam               = seam,
        confidence_score           = round(confidence, 3),
        nci_grade                  = nci_grade,
        sender_css                 = css_val,
        active_distortions         = active_dist,
    )

    return translated_text, receipt


# ─── Stage 6: Transceiver ─────────────────────────────────────────────────────

@dataclass
class ChannelStateRegister:
    """
    Persists across a session. Tracks altitude history, archetype stability,
    resonance history, JTBD vector, and sender cognitive history.
    """
    session_id:              str = field(default_factory=lambda: str(uuid.uuid4()))
    current_altitude:        int = 3
    archetype_id:            str = "EXECUTOR"
    archetype_distribution:  dict = field(default_factory=dict)
    archetype_stability:     float = 0.0
    drift_counter:           int = 0
    resonance_history:       list[float] = field(default_factory=list)
    altitude_history:        list[int] = field(default_factory=list)
    sender_cognitive_history: list[float] = field(default_factory=list)
    trust_calibration_score: float = 1.0
    turn_count:              int = 0
    jtbd_vector:             Optional[str] = None

    def update(self, altitude: int, resonance: float, css: Optional[float] = None):
        if self.altitude_history:
            delta = abs(altitude - self.altitude_history[-1])
            if delta > 1.5:
                self.drift_counter += 1
        self.altitude_history.append(altitude)
        self.current_altitude = altitude
        self.resonance_history.append(resonance)
        if css is not None:
            self.sender_cognitive_history.append(css)
            # Exponential weighted trust calibration
            n = len(self.sender_cognitive_history)
            weights = [math.exp(0.3 * i) for i in range(n)]
            w_sum = sum(weights)
            self.trust_calibration_score = sum(
                c * w for c, w in zip(self.sender_cognitive_history, weights)
            ) / w_sum
        self.turn_count += 1

    def initialize_archetype(
        self,
        hemisphere_scores: Optional[dict] = None,
        first_signal: Optional[str] = None,
    ):
        """G2 cold-start: hemisphere scores → archetype prior."""
        if hemisphere_scores:
            self.archetype_distribution = cold_start_archetype_prior(hemisphere_scores)
            self.archetype_stability = 0.35
        elif first_signal:
            self.archetype_distribution = lexical_archetype_scan(first_signal)
            self.archetype_stability = 0.15
        else:
            archetypes = list(ARCHETYPE_REGISTRY.keys())
            self.archetype_distribution = {a: 1/len(archetypes) for a in archetypes}
            self.archetype_stability = 0.0

        if self.archetype_distribution:
            self.archetype_id = max(self.archetype_distribution, key=self.archetype_distribution.get)

    def bayesian_update(self, new_signal: str, resonance_score: float):
        """Update archetype distribution each turn."""
        evidence = lexical_archetype_scan(new_signal)
        weight = min(0.40, 0.08 * self.turn_count)
        for arch in self.archetype_distribution:
            prior = self.archetype_distribution.get(arch, 1/len(ARCHETYPE_REGISTRY))
            likelihood = evidence.get(arch, 1/len(ARCHETYPE_REGISTRY))
            self.archetype_distribution[arch] = prior * (1 - weight) + likelihood * weight
        total = sum(self.archetype_distribution.values()) or 1
        self.archetype_distribution = {k: v/total for k, v in self.archetype_distribution.items()}
        top_prob = max(self.archetype_distribution.values())
        self.archetype_stability = min(1.0, top_prob * 1.4)
        self.archetype_id = max(self.archetype_distribution, key=self.archetype_distribution.get)

    @property
    def is_stable(self) -> bool:
        return self.archetype_stability >= 0.70


# ─── Full 7-Stage Pipeline ────────────────────────────────────────────────────

class LTEPipeline:
    """
    Orchestrates all 7 stages. Stateful across turns via ChannelStateRegister.

    Usage:
        lte = LTEPipeline(jtbd="Should we hire an engineer or salesperson?")
        response = lte.translate(
            raw_signal="We need to scale revenue faster than the product can handle.",
            target_altitude=AltitudeLevel.L1_OPERATIONAL,
            target_archetype="EXECUTOR",
        )
        print(response.translated_signal)
        print(response.receipt.visible_seam)
    """

    def __init__(
        self,
        jtbd: Optional[str] = None,
        llm_client=None,
        hemisphere_scores: Optional[dict] = None,
    ):
        self.jtbd = jtbd
        self.llm_client = llm_client
        self.csr = ChannelStateRegister()
        self.hc_session = HCSession(jtbd=jtbd)
        if hemisphere_scores or jtbd:
            self.csr.initialize_archetype(
                hemisphere_scores=hemisphere_scores,
                first_signal=jtbd,
            )
            self.csr.jtbd_vector = jtbd

    def translate(
        self,
        raw_signal: str,
        target_altitude: AltitudeLevel,
        target_archetype: Optional[str] = None,
        mode: TranslationMode = "inform",
    ) -> LTEResponse:
        """Run the full 7-stage pipeline for one translation request."""

        # ── Pre-Stage: HC Scan ────────────────────────────────────────────────
        cognitive_state = self.hc_session.scan(raw_signal)
        gate = cognitive_state.gate_status

        # Halt path: return early with seam, no translation
        if gate == "halt":
            halt_receipt = TranslationReceipt(
                receipt_id                 = str(uuid.uuid4()),
                timestamp                  = datetime.now(timezone.utc).isoformat(),
                source_altitude            = 3,
                target_altitude            = int(target_altitude),
                compression_ratio_achieved = "N/A",
                ips                        = 0.0,
                resonance_amplitude        = 0.0,
                phase_delta                = math.pi,
                invariants_preserved       = [],
                invariants_compressed      = [],
                style_dropped              = [],
                what_was_compressed        = "Pipeline halted — sender CSS below threshold.",
                visible_seam               = cognitive_state.seam_text,
                confidence_score           = 0.0,
                nci_grade                  = 0,
                sender_css                 = cognitive_state.css,
                active_distortions         = cognitive_state.active_distortions,
            )
            return LTEResponse(
                translated_signal  = f"[HALTED] {cognitive_state.recommended_action}",
                source_altitude    = AltitudeLevel.L3_STRATEGIC,
                target_altitude    = target_altitude,
                ips                = 0.0,
                resonance_amplitude = 0.0,
                phase_delta        = math.pi,
                receipt            = halt_receipt,
                gate_status        = "halt",
                csr                = cognitive_state,
            )

        # Resolve archetype: explicit > CSR top > default
        resolved_archetype = (
            target_archetype
            or (self.csr.archetype_id if self.csr.is_stable else "EXECUTOR")
        )

        # ── Stage 1: Intake ───────────────────────────────────────────────────
        skeleton = run_intake(raw_signal, cognitive_state.css, self.llm_client)

        # ── Stage 2: Altitude Detector ────────────────────────────────────────
        alt_profile = run_altitude_detector(
            raw_signal, skeleton, target_altitude, cognitive_state
        )

        # ── Stage 3: Lossless Codex ───────────────────────────────────────────
        archetype, resonance, phase_delta = run_codex_lookup(
            skeleton, alt_profile, resolved_archetype
        )

        # ── Stage 4: RRE ──────────────────────────────────────────────────────
        translated, ops, resonance = run_rre(
            skeleton, alt_profile, archetype, mode, cognitive_state, self.llm_client
        )

        # ── Stage 5: Recomp ───────────────────────────────────────────────────
        translated, receipt = run_recomp(
            skeleton, alt_profile, archetype, translated,
            ops, resonance, phase_delta, cognitive_state, target_altitude, mode,
        )

        # ── Stage 6: Transceiver — update CSR ────────────────────────────────
        self.csr.update(
            altitude  = int(alt_profile.source_altitude),
            resonance = resonance,
            css       = cognitive_state.css,
        )
        self.csr.bayesian_update(raw_signal, resonance)

        return LTEResponse(
            translated_signal   = translated,
            source_altitude     = alt_profile.source_altitude,
            target_altitude     = target_altitude,
            ips                 = receipt.ips,
            resonance_amplitude = resonance,
            phase_delta         = phase_delta,
            receipt             = receipt,
            gate_status         = gate,
            csr                 = cognitive_state,
        )

    @property
    def channel_summary(self) -> dict:
        return {
            "session_id":             self.csr.session_id,
            "turn_count":             self.csr.turn_count,
            "current_altitude":       self.csr.current_altitude,
            "top_archetype":          self.csr.archetype_id,
            "archetype_stable":       self.csr.is_stable,
            "trust_calibration":      round(self.csr.trust_calibration_score, 3),
            "avg_resonance":          round(sum(self.csr.resonance_history) / max(1, len(self.csr.resonance_history)), 3),
            "drift_events":           self.csr.drift_counter,
        }


# ─── CLI Smoke Test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("ARCS LTE — Smoke Test")
    print("=" * 65)

    # Test: Zach (L5 Gigabrain) → EXECUTOR (L1) translation
    lte = LTEPipeline(jtbd="Should we hire an engineer or a salesperson first?")

    cases = [
        {
            "label": "L5 → L1: Gigabrain to Executor",
            "signal": (
                "Based on our sprint velocity data (avg 28 pts/week) and pipeline coverage "
                "metrics (1.8x), the evidence suggests a convex optimization problem: "
                "research shows marginal returns on engineering compound faster pre-PMF "
                "while sales leverage is higher post-PMF (First Round study, n=300 startups). "
                "Given our current NCI of 67/100 on product-market fit, the data indicates "
                "the irreversibility of a sales hire (6-month ramp cost ~$180k) "
                "exceeds the optionality value of another engineering sprint (~$40k)."
            ),
            "target_alt": AltitudeLevel.L1_OPERATIONAL,
            "archetype": "EXECUTOR",
        },
        {
            "label": "L5 → L2: Gigabrain to Connector",
            "signal": (
                "According to our retention cohort analysis (n=142 accounts), relationship "
                "density — measured as number of champions per account — correlates at r=0.71 "
                "with 12-month net revenue retention. The data shows the trust moat compounds "
                "faster than technical differentiation at this stage: accounts with 3+ champions "
                "show 94% retention vs 61% for single-champion accounts. "
                "This suggests optimizing for relationship depth before revenue extraction."
            ),
            "target_alt": AltitudeLevel.L2_TACTICAL,
            "archetype": "CONNECTOR",
        },
        {
            "label": "HALTED: Myth Engine distortion",
            "signal": (
                "This is obviously the right move. Everyone in the industry knows "
                "you must always hire sales first. It will definitely unlock growth. "
                "The narrative is clear and the answer is certain."
            ),
            "target_alt": AltitudeLevel.L2_TACTICAL,
            "archetype": "INSTITUTIONALIST",
        },
    ]

    for case in cases:
        print(f"\n{'─' * 55}")
        print(f"  {case['label']}")
        print(f"{'─' * 55}")
        resp = lte.translate(
            raw_signal       = case["signal"],
            target_altitude  = case["target_alt"],
            target_archetype = case["archetype"],
        )
        print(f"  Gate:       {resp.gate_status.upper()}")
        print(f"  Source Alt: L{resp.source_altitude}")
        print(f"  IPS:        {resp.ips:.3f}")
        print(f"  Resonance:  {resp.resonance_amplitude:.3f}")
        css_str = f"{resp.csr.css:.3f}" if resp.csr else "N/A"
        print(f"  CSS:        {css_str}")
        print(f"  NCI Grade:  {resp.receipt.nci_grade}")
        print(f"\n  Translated:\n  {resp.translated_signal[:300]}")
        if resp.receipt.visible_seam:
            print(f"\n  Seam: {resp.receipt.visible_seam}")

    print(f"\n{'─' * 55}")
    print("  Channel State:")
    for k, v in lte.channel_summary.items():
        print(f"    {k}: {v}")
    print("\n" + "=" * 65)
    print("LTE smoke test complete.")
    print("=" * 65)
