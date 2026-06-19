from __future__ import annotations

"""
Governance: Bar Raiser Quality Gate and Decision Receipts

Provides a weighted scoring gate enforcing S-Tier at >= 0.90 composite and
immutable decision receipts using Loguru with SHA-256 hashes.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import Dict, Mapping, Tuple

from loguru import logger


# Configure logger for production-friendly, structured receipts
logger.remove()
logger.add(
    sink=lambda m: print(m, end=""),
    format="{time:YYYY-MM-DDTHH:mm:ss.SSS} | {level} | {message}",
    level="INFO",
    enqueue=True,
)


def decision_receipt(action: str, payload: Mapping) -> Dict[str, str]:
    """Emit an immutable receipt for a governance event.

    Parameters
    ----------
    action: str
        The action or decision name.
    payload: Mapping
        JSON-serializable content of the decision.

    Returns
    -------
    Dict[str, str]
        A dict with action, sha256, and canonical JSON string.
    """
    canonical = json.dumps({"action": action, "payload": payload}, sort_keys=True)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    logger.info(f"receipt action={action} sha256={digest}")
    return {"action": action, "sha256": digest, "canonical": canonical}


@dataclass(frozen=True)
class Weights:
    rigor: float = 0.25
    completeness: float = 0.25
    testability: float = 0.20
    clarity: float = 0.20
    novelty: float = 0.10

    def normalize(self) -> "Weights":
        total = self.rigor + self.completeness + self.testability + self.clarity + self.novelty
        if abs(total - 1.0) < 1e-9:
            return self
        return Weights(
            rigor=self.rigor / total,
            completeness=self.completeness / total,
            testability=self.testability / total,
            clarity=self.clarity / total,
            novelty=self.novelty / total,
        )


class BarRaiser:
    """Weighted quality gate with tiering.

    Scores are expected in [0, 1]. S-Tier requires composite >= 0.90.
    """

    def __init__(self, weights: Weights | None = None, s_threshold: float = 0.90):
        self.weights = (weights or Weights()).normalize()
        self.s_threshold = s_threshold

    def evaluate(self, scores: Mapping[str, float]) -> Tuple[float, str, bool]:
        """Evaluate a candidate against the gate.

        Parameters
        ----------
        scores: Mapping[str, float]
            Keys: rigor, completeness, testability, clarity, novelty.

        Returns
        -------
        Tuple[float, str, bool]
            composite, tier, passed (True if S-tier or higher)
        """
        r = float(scores.get("rigor", 0))
        c = float(scores.get("completeness", 0))
        t = float(scores.get("testability", 0))
        cl = float(scores.get("clarity", 0))
        n = float(scores.get("novelty", 0))

        comp = (
            r * self.weights.rigor
            + c * self.weights.completeness
            + t * self.weights.testability
            + cl * self.weights.clarity
            + n * self.weights.novelty
        )

        tier = (
            "S" if comp >= self.s_threshold
            else "A" if comp >= 0.80
            else "B" if comp >= 0.70
            else "C" if comp >= 0.60
            else "D"
        )

        decision_receipt("bar_raiser.evaluate", {"scores": dict(scores), "composite": comp, "tier": tier})
        return comp, tier, comp >= self.s_threshold

