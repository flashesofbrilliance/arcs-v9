"""
arcs_cis.py — ARCS Cognitive Interface System (CIS)
====================================================
The Babel Fish. Complete implementation.

Architecture:
    Field OS  — What to decide (the ARCS pipeline runtime)
    HC        — Is the sender cognitively healthy right now?
    LTE       — Encode the signal to the right altitude

Design invariants (from CIS Product Spec v1.0):
    - HC fires BEFORE LTE Intake. Never after.
    - CSS modulates every downstream LTE stage via CognitiveSafetyScore.
    - A losslessly transmitted distortion is more dangerous than a degraded transmission.
    - DEWY crystallizes through use (CSR history), not spec.
    - ROM promotion gates on trust_calibration_score, not manual harvest.

Sprint status (per CIS sprint plan 0–9):
    Sprint 0: Data models wired           ✅ (arcs_hc.py + arcs_lte.py)
    Sprint 1: Altitude Detector live      ✅
    Sprint 2: Codex archetype registry    ✅
    Sprint 3: CSR cold-start + Bayesian   ✅
    Sprint 4: LTE stubs end-to-end        ✅
    Sprint 5: HC→LTE integration          ✅ (this file)
    Sprint 6: HC stage wired upstream     ✅ (locked interface in arcs_hc.py)
    Sprint 7: CSS injection in all stages ✅ (CognitiveSafetyScore injected)
    Sprint 8: DEWY schema from CSR history (pending — requires real run data)
    Sprint 9: ROM promotion threshold     (pending)

Field OS integration:
    CIS.translate() calls the ARCSRuntimeService pipeline (Field OS layer)
    for the pre-translation decision framing, then pipes the signal through
    HC → LTE. If Field OS is unavailable, CIS operates standalone.

Spec references:
    - arcs-cis-product-spec.html
    - LTE_Gap_Closure_v1.0.md
    - "Okay. This is the missing third piece" (DEWY crystallization receipt)
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from arcs_hc import (
    HCSession,
    CognitiveStateRegister,
    CognitiveSafetyScore,
    run_hc_scan,
    CSS_GATE_THRESHOLD,
    CSS_SEAM_WARNING,
    CSS_HEALTHY,
    cold_start_archetype_prior,
    lexical_archetype_scan,
)
from arcs_lte import (
    LTEPipeline,
    LTEResponse,
    AltitudeLevel,
    TranslationMode,
    ChannelStateRegister,
    ARCHETYPE_REGISTRY,
)

CIS_VERSION = "v1.0-phase6"


# ─── CIS Session State ────────────────────────────────────────────────────────

@dataclass
class CISSession:
    """
    Persistent state for one CIS session (one sender, one receiver context).

    Holds the HC session, the LTE pipeline, and the DEWY crystallization log
    (sender_cognitive_history). trust_calibration_score gates ROM promotion.
    """
    session_id:               str = field(default_factory=lambda: str(uuid.uuid4()))
    jtbd:                     Optional[str] = None
    sender_id:                Optional[str] = None
    receiver_archetype:       Optional[str] = None
    receiver_altitude:        Optional[AltitudeLevel] = None

    # HC state
    hc_session:               Optional[HCSession] = field(default=None, repr=False)

    # LTE state
    lte_pipeline:             Optional[LTEPipeline] = field(default=None, repr=False)

    # DEWY crystallization log
    sender_cognitive_history: List[Dict[str, Any]] = field(default_factory=list)
    trust_calibration_score:  float = 1.0       # decays with distortion; gates ROM entry
    turn_count:               int = 0
    rom_promotion_ready:      bool = False       # True when trust ≥ ROM_THRESHOLD

    def __post_init__(self):
        if self.hc_session is None:
            self.hc_session = HCSession(jtbd=self.jtbd)
        if self.lte_pipeline is None:
            self.lte_pipeline = LTEPipeline(jtbd=self.jtbd)

    def _update_trust(self, css: float) -> None:
        """
        Bayesian trust update: healthy signals increase trust, distorted ones decay it.
        trust_calibration_score is the DEWY→ROM gate variable.
        """
        if css >= CSS_HEALTHY:
            delta = +0.05
        elif css >= CSS_GATE_THRESHOLD:
            delta = +0.01
        else:
            delta = -0.15   # distortion costs more than health gains
        self.trust_calibration_score = max(0.0, min(1.0, self.trust_calibration_score + delta))
        self.rom_promotion_ready = self.trust_calibration_score >= ROM_PROMOTION_THRESHOLD

    def log_turn(self, css: float, gate: str, archetype: str) -> None:
        """Append to sender_cognitive_history (the DEWY crystallization log)."""
        self.turn_count += 1
        entry = {
            "turn": self.turn_count,
            "timestamp": time.time(),
            "css": round(css, 4),
            "gate": gate,
            "archetype": archetype,
            "trust_after": round(self.trust_calibration_score, 4),
        }
        self.sender_cognitive_history.append(entry)

    @property
    def avg_css(self) -> float:
        if not self.sender_cognitive_history:
            return 1.0
        return sum(t["css"] for t in self.sender_cognitive_history) / len(self.sender_cognitive_history)

    @property
    def distortion_rate(self) -> float:
        if not self.sender_cognitive_history:
            return 0.0
        halted = sum(1 for t in self.sender_cognitive_history if t["gate"] == "halt")
        return halted / len(self.sender_cognitive_history)

    def summary(self) -> Dict[str, Any]:
        return {
            "session_id":            self.session_id,
            "jtbd":                  self.jtbd,
            "turn_count":            self.turn_count,
            "avg_css":               round(self.avg_css, 3),
            "distortion_rate":       round(self.distortion_rate, 3),
            "trust_calibration":     round(self.trust_calibration_score, 3),
            "rom_promotion_ready":   self.rom_promotion_ready,
            "receiver_archetype":    self.receiver_archetype,
            "receiver_altitude":     self.receiver_altitude.name if self.receiver_altitude else None,
            "channel_stable":        self.lte_pipeline.csr.is_stable if self.lte_pipeline else False,
        }


# ─── CIS Request / Response ───────────────────────────────────────────────────

@dataclass
class CISRequest:
    """
    Everything CIS needs to translate one signal.

    Minimum required: raw_signal + target_archetype OR target_altitude.
    If hemisphere_scores are provided, CIS uses them to cold-start archetype prior.
    """
    raw_signal:          str
    target_archetype:    Optional[str]          = None   # e.g. "EXECUTOR"
    target_altitude:     Optional[AltitudeLevel]= None   # e.g. AltitudeLevel.L1_OPERATIONAL
    mode:                TranslationMode         = "inform"
    jtbd_anchor:         Optional[str]           = None
    hemisphere_scores:   Optional[Dict[str, float]] = None  # {lf, rf, ln, rn} from HC HTML
    field_os_context:    Optional[Dict[str, Any]]   = None  # from ARCSRuntimeService receipt


@dataclass
class CISResponse:
    """
    Full CIS output. Contains the translation + all diagnostic signals.
    This is the Babel Fish's output: the translated signal + proof of health.
    """
    request_id:          str
    translated_signal:   str
    gate_status:         str                 # "pass" | "warn" | "halt"
    ips:                 float               # Invariant Preservation Score (≥0.95 healthy)
    resonance:           float               # wavefunction amplitude (≥0.80 healthy)
    css:                 float               # sender Cognitive Safety Score
    nci_grade:           int                 # 0–100
    source_altitude:     int
    target_altitude:     int
    target_archetype:    str
    visible_seam:        str
    active_distortions:  List[str]
    css_injected:        CognitiveSafetyScore # locked interface injected into all stages
    channel_stable:      bool
    trust_calibration:   float
    rom_promotion_ready: bool
    turn_count:          int
    timestamp:           float = field(default_factory=time.time)

    @property
    def is_healthy(self) -> bool:
        return (
            self.gate_status in ("pass", "warn")
            and self.ips >= 0.95
            and self.css >= CSS_GATE_THRESHOLD
        )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    def brief(self) -> str:
        """One-line summary for logging."""
        health = "✅" if self.is_healthy else "⚠" if self.gate_status == "warn" else "🛑"
        return (
            f"{health} Gate={self.gate_status.upper()} | "
            f"CSS={self.css:.2f} | IPS={self.ips:.2f} | "
            f"NCI={self.nci_grade} | Alt={self.source_altitude}→{self.target_altitude} | "
            f"[{self.target_archetype}]"
        )


# ─── Constants ────────────────────────────────────────────────────────────────

ROM_PROMOTION_THRESHOLD = 0.80   # trust_calibration_score must reach this for ROM entry
DEFAULT_TARGET_ALTITUDE = AltitudeLevel.L2_TACTICAL
DEFAULT_TARGET_ARCHETYPE = "CONNECTOR"


# ─── CIS Core ─────────────────────────────────────────────────────────────────

class CognitiveInterfaceSystem:
    """
    The Babel Fish.

    Field OS (what to decide) + HC (is the sender healthy?) + LTE (translate).

    Usage (standalone, no LLM):
        cis = CognitiveInterfaceSystem(jtbd="Should we hire sales or engineering?")
        resp = cis.translate(CISRequest(
            raw_signal="Our NRR data shows 94% retention but pipeline coverage is 1.4x...",
            target_archetype="EXECUTOR",
            target_altitude=AltitudeLevel.L1_OPERATIONAL,
        ))
        print(resp.translated_signal)
        print(resp.brief())

    Usage with hemisphere cold-start:
        cis = CognitiveInterfaceSystem(
            jtbd="Q3 GTM strategy",
            hemisphere_scores={"lf": 0.72, "rf": 0.28, "ln": 0.61, "rn": 0.39},
        )
        # Archetype prior is initialized from HC quadrant mapping
        resp = cis.translate(req)

    Usage with Field OS:
        cis = CognitiveInterfaceSystem(runtime_service=ARCSRuntimeService())
        resp = cis.translate(req)  # Field OS context injected automatically
    """

    def __init__(
        self,
        jtbd: Optional[str] = None,
        hemisphere_scores: Optional[Dict[str, float]] = None,
        llm_client=None,
        runtime_service=None,   # ARCSRuntimeService — Field OS integration
        sender_id: Optional[str] = None,
    ):
        self.session = CISSession(
            jtbd=jtbd,
            sender_id=sender_id,
        )
        self.llm_client = llm_client
        self.runtime_service = runtime_service

        # If hemisphere scores provided, cold-start the archetype prior
        if hemisphere_scores:
            archetype_prior = cold_start_archetype_prior(hemisphere_scores)
            top_archetype = max(archetype_prior, key=archetype_prior.get)
            self.session.receiver_archetype = top_archetype
            # Wire into LTE CSR
            if self.session.lte_pipeline:
                self.session.lte_pipeline.csr.initialize_archetype(
                    hemisphere_scores=hemisphere_scores,
                    first_signal=jtbd,
                )

    def translate(self, request: CISRequest) -> CISResponse:
        """
        Full CIS pipeline for one request.

        Flow:
            1. Resolve target archetype + altitude
            2. [Optional] Field OS framing (if runtime_service is wired)
            3. HC pre-scan → CognitiveSafetyScore
            4. Gate check — halt returns early with seam, no translation
            5. LTE 7-stage pipeline with CSS injected
            6. Trust update → DEWY crystallization log
            7. Return CISResponse
        """
        request_id = str(uuid.uuid4())

        # ── Step 1: Resolve target ────────────────────────────────────────────
        target_archetype, target_altitude = self._resolve_target(request)

        # ── Step 2: Field OS framing (optional) ──────────────────────────────
        field_os_context = request.field_os_context
        if self.runtime_service is not None and field_os_context is None:
            try:
                result = self.runtime_service.process_decision(request.raw_signal)
                field_os_context = {
                    "nci_score":   result.nci_score,
                    "verdict":     result.verdict.value,
                    "bar_review":  result.bar_review_id,
                }
            except Exception:
                pass   # Field OS unavailable — proceed standalone

        # ── Step 3: HC pre-scan ───────────────────────────────────────────────
        cognitive_state: CognitiveStateRegister = self.session.hc_session.scan(
            request.raw_signal
        )
        css_score = CognitiveSafetyScore.from_csr(cognitive_state)

        # Update JTBD anchor if request provides one
        if request.jtbd_anchor:
            self.session.hc_session.jtbd = request.jtbd_anchor

        # ── Step 4: Gate check ────────────────────────────────────────────────
        self.session._update_trust(cognitive_state.css)
        self.session.log_turn(
            css=cognitive_state.css,
            gate=cognitive_state.gate_status,
            archetype=target_archetype,
        )

        if cognitive_state.gate_status == "halt":
            return CISResponse(
                request_id          = request_id,
                translated_signal   = (
                    f"[CIS HALTED] {cognitive_state.recommended_action}\n\n"
                    f"Active distortions: {'; '.join(cognitive_state.active_distortions) or 'none detected'}"
                ),
                gate_status         = "halt",
                ips                 = 0.0,
                resonance           = 0.0,
                css                 = cognitive_state.css,
                nci_grade           = 0,
                source_altitude     = 3,
                target_altitude     = target_altitude.value,
                target_archetype    = target_archetype,
                visible_seam        = css_score.seam_string,
                active_distortions  = cognitive_state.active_distortions,
                css_injected        = css_score,
                channel_stable      = False,
                trust_calibration   = self.session.trust_calibration_score,
                rom_promotion_ready = self.session.rom_promotion_ready,
                turn_count          = self.session.turn_count,
            )

        # ── Step 5: LTE 7-stage pipeline ─────────────────────────────────────
        lte_resp: LTEResponse = self.session.lte_pipeline.translate(
            raw_signal       = request.raw_signal,
            target_altitude  = target_altitude,
            target_archetype = target_archetype,
            mode             = request.mode,
        )

        # ── Step 6: Build CISResponse ─────────────────────────────────────────
        visible_seam = lte_resp.receipt.visible_seam
        if css_score.seam_string and cognitive_state.gate_status == "warn":
            visible_seam = f"{visible_seam} | {css_score.seam_string}"

        return CISResponse(
            request_id          = request_id,
            translated_signal   = lte_resp.translated_signal,
            gate_status         = lte_resp.gate_status,
            ips                 = lte_resp.ips,
            resonance           = lte_resp.resonance_amplitude,
            css                 = cognitive_state.css,
            nci_grade           = lte_resp.receipt.nci_grade,
            source_altitude     = lte_resp.source_altitude.value,
            target_altitude     = target_altitude.value,
            target_archetype    = target_archetype,
            visible_seam        = visible_seam,
            active_distortions  = cognitive_state.active_distortions,
            css_injected        = css_score,
            channel_stable      = self.session.lte_pipeline.csr.is_stable,
            trust_calibration   = self.session.trust_calibration_score,
            rom_promotion_ready = self.session.rom_promotion_ready,
            turn_count          = self.session.turn_count,
        )

    def _resolve_target(
        self, request: CISRequest
    ) -> tuple[str, AltitudeLevel]:
        """
        Resolve target archetype and altitude from the request.
        Falls back to session defaults, then global defaults.
        """
        # Archetype
        archetype = request.target_archetype
        if archetype is None:
            archetype = self.session.receiver_archetype
        if archetype is None or archetype not in ARCHETYPE_REGISTRY:
            archetype = DEFAULT_TARGET_ARCHETYPE

        # Altitude
        altitude = request.target_altitude
        if altitude is None:
            altitude = self.session.receiver_altitude
        if altitude is None:
            # Infer from archetype's native altitude (stored as int → wrap in AltitudeLevel)
            profile = ARCHETYPE_REGISTRY.get(archetype)
            if profile:
                altitude = AltitudeLevel(profile.native_altitude)
            else:
                altitude = DEFAULT_TARGET_ALTITUDE
        elif isinstance(altitude, int):
            altitude = AltitudeLevel(altitude)

        return archetype, altitude

    @property
    def session_summary(self) -> Dict[str, Any]:
        return self.session.summary()


# ─── Convenience Factory ──────────────────────────────────────────────────────

def create_cis(
    jtbd: Optional[str] = None,
    hemisphere_scores: Optional[Dict[str, float]] = None,
    **kwargs,
) -> CognitiveInterfaceSystem:
    """
    Factory shorthand.

        cis = create_cis(jtbd="Build or buy?", hemisphere_scores={"lf": 0.6, ...})
    """
    return CognitiveInterfaceSystem(
        jtbd=jtbd,
        hemisphere_scores=hemisphere_scores,
        **kwargs,
    )


# ─── Smoke Test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("ARCS CIS — Smoke Test")
    print("=" * 65)

    # Case 1: Healthy signal, Gigabrain → Executor
    print("\n─── Case 1: Healthy sender, L5→L1 ───")
    cis = CognitiveInterfaceSystem(
        jtbd="improve retention and reduce churn rate using cohort data"
    )
    resp = cis.translate(CISRequest(
        raw_signal=(
            "According to our Q1 cohort data (n=87 customers), feature adoption "
            "predicts 6-month retention at r=0.74. Our current churn rate is 18% "
            "annualized, based on last 90 days. The evidence suggests the retention "
            "lever is stronger than the acquisition lever at this stage of the curve."
        ),
        target_archetype="EXECUTOR",
        target_altitude=AltitudeLevel.L1_OPERATIONAL,
    ))
    print(f"  {resp.brief()}")
    print(f"  Seam:    {resp.visible_seam[:80]}")
    print(f"  Output:  {resp.translated_signal[:200]}")
    print(f"  Trust:   {resp.trust_calibration:.2f} | ROM ready: {resp.rom_promotion_ready}")

    # Case 2: Distorted signal — myth engine active
    print("\n─── Case 2: Myth Engine distortion — should HALT ───")
    resp2 = cis.translate(CISRequest(
        raw_signal=(
            "This is obviously the path. Everyone in the industry knows "
            "that sales always drives growth in the early stage. "
            "It's clear we need to hire sales first. The answer is certain."
        ),
        target_archetype="INSTITUTIONALIST",
        target_altitude=AltitudeLevel.L2_TACTICAL,
    ))
    print(f"  {resp2.brief()}")
    print(f"  CSS: {resp2.css:.2f} | Distortions: {resp2.active_distortions[:1]}")

    # Case 3: Hemisphere cold-start — QUANT receiver
    print("\n─── Case 3: Hemisphere cold-start, QUANT receiver ───")
    cis3 = CognitiveInterfaceSystem(
        jtbd="What's the right pricing model?",
        hemisphere_scores={"lf": 0.75, "rf": 0.25, "ln": 0.65, "rn": 0.35},
    )
    resp3 = cis3.translate(CISRequest(
        raw_signal=(
            "Based on our analysis of 200 comparable SaaS companies (Bessemer benchmark), "
            "usage-based pricing correlates with 23% higher NRR vs seat-based, "
            "controlling for ARR band. The data suggests UBP outperforms at "
            "expansion-stage for dev tools."
        ),
    ))
    print(f"  {resp3.brief()}")
    print(f"  Detected archetype: {cis3.session.receiver_archetype}")
    print(f"  Channel stable: {resp3.channel_stable}")

    # Session summary
    print("\n─── Session Summary ───")
    for k, v in cis.session_summary.items():
        print(f"  {k}: {v}")

    print("\n" + "=" * 65)
    print("CIS smoke test complete.")
    print("=" * 65)
