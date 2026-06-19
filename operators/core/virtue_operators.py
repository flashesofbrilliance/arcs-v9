from __future__ import annotations

"""
Greek/Stoic Virtue Operators for ARCS orchestration

Composes virtue atoms with existing advisors/operators:
- MetisRedTeamOperator: Metis + Detective (+ optional Loki mode)
- ParrhesiaAuditorOperator: Parrhesia + Auditor + Librarian (+ Immune)
- KairosMatchmakerOperator: KairosAlignment + Chrono-Kairos orchestration
- AtaraxiaGuardianOperator: Ataraxia + Wise Elder (Bar Raiser) gate

All outputs include immutable receipts compatible with ARCS governance.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional

from loguru import logger

from .governance import BarRaiser, Weights, decision_receipt
from .virtue_atoms import AtaraxiaAtom, KairosAlignmentAtom, MetisAtom, ParrhesiaAtom


# Minimal protocol-like callables for external systems, kept optional.
AuditorGapFn = Callable[[Mapping], float]  # returns gap score 0..1
LibrarianTransparencyFn = Callable[[Mapping], float]  # transparency 0..1
ImmunePathogenFn = Callable[[Mapping], float]  # pathogen risk 0..1
DetectiveFindModesFn = Callable[[Mapping, Mapping], int]  # number of modes


@dataclass
class MetisRedTeamOperator:
    metis: MetisAtom
    detective_find_failure_modes: DetectiveFindModesFn
    loki_mode: bool = False

    def evaluate(self, candidate: Mapping, role: Mapping, org: Mapping) -> Dict[str, Any]:
        ms = self.metis.score(candidate, role, org)
        modes = int(self.detective_find_failure_modes(role, org))
        mischief = 1.15 if self.loki_mode else 1.0
        red_team_value = float(ms["score"]) * modes * mischief
        r = decision_receipt("op.metis_red_team", {"metis": ms["score"], "modes": modes, "loki": self.loki_mode, "value": red_team_value})
        return {"metis": ms, "failure_modes": modes, "red_team_value": red_team_value, "receipt": r}


@dataclass
class ParrhesiaAuditorOperator:
    parrhesia: ParrhesiaAtom
    auditor_gap: AuditorGapFn
    librarian_transparency: LibrarianTransparencyFn
    immune_pathogen: Optional[ImmunePathogenFn] = None

    def evaluate(self, candidate: Mapping, role: Mapping, org: Mapping) -> Dict[str, Any]:
        ps = self.parrhesia.score(candidate, role, org)
        gaps = float(self.auditor_gap(org))
        transparency = float(self.librarian_transparency(org))
        pathogen = float(self.immune_pathogen(org)) if self.immune_pathogen else 0.0
        risk_of_silencing = max(0.0, gaps + pathogen - transparency) * (1.0 - float(ps["score"]))
        r = decision_receipt("op.parrhesia_audit", {
            "parrhesia": ps["score"], "gaps": gaps, "transparency": transparency,
            "pathogen": pathogen, "risk_of_silencing": risk_of_silencing,
        })
        return {
            "parrhesia": ps, "audit_gaps": gaps, "transparency": transparency,
            "pathogen": pathogen, "risk_of_silencing": risk_of_silencing, "receipt": r,
        }


@dataclass
class KairosMatchmakerOperator:
    kairos: KairosAlignmentAtom

    def evaluate(self, candidate: Mapping, role: Mapping, org: Mapping) -> Dict[str, Any]:
        ks = self.kairos.score(candidate, role, org)
        # Threshold for triggering a move can be tuned; default 0.65
        match_ready = float(ks["score"]) >= 0.65
        r = decision_receipt("op.kairos_match", {"kairos": ks["score"], "match_ready": match_ready})
        return {"kairos": ks, "match_ready": match_ready, "receipt": r}


@dataclass
class AtaraxiaGuardianOperator:
    ataraxia: AtaraxiaAtom
    elder: BarRaiser
    min_ataraxia: float = 0.6

    def evaluate(self, candidate: Mapping, role: Mapping, org: Mapping, base_scores: Mapping[str, float]) -> Dict[str, Any]:
        as_ = self.ataraxia.score(candidate, role, org)
        # Enforce minimum Ataraxia; if low, veto regardless of base composite.
        veto = float(as_["score"]) < self.min_ataraxia
        composite, tier, passed = self.elder.evaluate(base_scores)
        gate_passed = (not veto) and passed
        r = decision_receipt("op.ataraxia_guard", {
            "ataraxia": as_["score"], "min": self.min_ataraxia, "veto": veto,
            "bar_composite": composite, "bar_tier": tier, "gate_passed": gate_passed,
        })
        return {
            "ataraxia": as_, "veto": veto, "bar_raiser": {"composite": composite, "tier": tier, "passed": passed},
            "gate_passed": gate_passed, "receipt": r,
        }

