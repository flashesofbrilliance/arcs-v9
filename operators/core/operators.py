from __future__ import annotations

"""
ARCS Operators: Board of Advisors and Systems Logic

Includes:
- Loki (adversarial red-teaming)
- Detective (risk analysis)
- Conductor (sequencing / orchestration)
- init_arcs (10-step reconnaissance with L0 title filter + HCI/PCI scoring)
- crystallize (phase transition requirements)
- chrono_kairos (Temporal Arbitrator for opportune windows)
"""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from loguru import logger

from .governance import decision_receipt


# --------------------------- Board of Advisors ---------------------------- #


@dataclass
class Loki:
    """Adversarial red-teaming advisor.

    Generates threat hypotheses, failure modes, and countermeasures.
    """

    def probe(self, proposal: Mapping[str, object]) -> Dict[str, object]:
        risks: List[str] = []
        countermeasures: List[str] = []

        text = (proposal.get("summary") or "").lower()
        if "schedule" in text:
            risks.append("Schedule slips due to external dependencies")
            countermeasures.append("Add slack buffers and kill-switch criteria")
        if "data" in text or "privacy" in text:
            risks.append("Data leakage or non-compliance")
            countermeasures.append("Apply least-privilege + anonymization + DLP")
        if "ml" in text or "ai" in text:
            risks.append("Model drift + prompt injection vectors")
            countermeasures.append("Guardrails, evals, and red-team prompts")

        receipt = decision_receipt("loki.probe", {"risks": risks, "countermeasures": countermeasures})
        return {"risks": risks, "countermeasures": countermeasures, "receipt": receipt}


@dataclass
class Detective:
    """Risk analyst computing likelihood-impact profiles and risk score."""

    def assess(self, events: Sequence[Mapping[str, float]]) -> Dict[str, object]:
        df = pd.DataFrame(events)
        if df.empty:
            return {"risk_score": 0.0, "detail": [], "receipt": decision_receipt("detective.assess", {"risk_score": 0.0})}
        df = df.fillna(0.0)
        df["score"] = df["likelihood"].clip(0, 1) * df["impact"].clip(0, 1)
        total = float(df["score"].mean())
        detail = df.to_dict(orient="records")
        receipt = decision_receipt("detective.assess", {"risk_score": total, "detail": detail})
        return {"risk_score": total, "detail": detail, "receipt": receipt}


@dataclass
class Conductor:
    """Task sequencing advisor using topological sorting with priority."""

    def sequence(self, tasks: Sequence[Mapping[str, object]]) -> List[str]:
        # tasks: {id, deps: List[str], priority: float}
        graph: Dict[str, List[str]] = {}
        indeg: Dict[str, int] = {}
        priority: Dict[str, float] = {}
        for t in tasks:
            tid = str(t["id"])  # required
            deps = list(t.get("deps", []))
            graph.setdefault(tid, [])
            priority[tid] = float(t.get("priority", 0))
            indeg.setdefault(tid, 0)
            for d in deps:
                graph.setdefault(str(d), [])
                indeg[tid] = indeg.get(tid, 0) + 1
                graph[str(d)].append(tid)

        # Kahn's algorithm with priority (higher first)
        ready = [n for n, deg in indeg.items() if deg == 0]
        ready.sort(key=lambda x: (-priority.get(x, 0), x))
        order: List[str] = []
        while ready:
            node = ready.pop(0)
            order.append(node)
            for nbr in graph.get(node, []):
                indeg[nbr] -= 1
                if indeg[nbr] == 0:
                    ready.append(nbr)
                    ready.sort(key=lambda x: (-priority.get(x, 0), x))

        if len(order) != len(indeg):
            # Cycle detected; fall back to priority-only ordering
            order = sorted(indeg.keys(), key=lambda x: (-priority.get(x, 0), x))

        decision_receipt("conductor.sequence", {"order": order})
        return order


# ------------------------- Systems and Protocols ------------------------- #


L0_TITLE_SYNONYMS: List[str] = [
    # 100+ role/title markers for L0 filtering
    "founder", "co-founder", "ceo", "chief executive officer", "cto", "chief technology officer",
    "cso", "chief science officer", "coo", "cfo", "chief financial officer", "chief product officer",
    "cpo", "head of product", "vp product", "product manager", "senior product manager",
    "director of product", "principal product manager", "product lead", "growth lead",
    "head of growth", "vp growth", "engineering manager", "staff engineer", "principal engineer",
    "distinguished engineer", "software architect", "systems architect", "solutions architect",
    "head of engineering", "vp engineering", "director of engineering", "lead engineer",
    "ml engineer", "machine learning engineer", "ml ops", "mlops", "data scientist",
    "senior data scientist", "head of data", "vp data", "director of data", "analytics lead",
    "research scientist", "applied scientist", "nlp engineer", "ai engineer", "genai engineer",
    "ai product manager", "technical program manager", "tpm", "program manager", "project manager",
    "design lead", "head of design", "vp design", "ux lead", "ux researcher", "design manager",
    "solutions engineer", "sales engineer", "field engineer", "customer engineer", "platform engineer",
    "site reliability engineer", "sre", "devops engineer", "security engineer", "head of security",
    "vp security", "director security", "privacy officer", "dpo", "legal counsel",
    "corporate counsel", "head of legal", "marketing lead", "head of marketing", "vp marketing",
    "growth marketer", "demand gen", "paid media lead", "community lead", "developer advocate",
    "developer relations", "devrel", "solutions architect", "enterprise architect", "it director",
    "cio", "chief information officer", "cio", "principal consultant", "strategy lead",
    "head of strategy", "chief of staff", "bizops", "business operations", "operations lead",
    "gm", "general manager", "regional director", "country manager", "head of partnerships",
    "partnerships manager", "alliances manager", "innovation lead", "r&d lead", "head of ai",
    "vp ai", "director ai", "data platform lead", "analytics engineer", "data engineer",
    "solutions manager", "technical lead", "tech lead", "product marketing manager", "pmm",
]


def init_arcs(
    gmail_threads: Sequence[Mapping[str, str]] | None = None,
    linkedin_profiles: Sequence[Mapping[str, str]] | None = None,
) -> Dict[str, object]:
    """Run v8.1 'Maximum Aperture' reconnaissance.

    Ten-step logic (condensed to essentials for production):
    1) Ingest recent Gmail threads (subject, snippet, sender, date)
    2) Ingest LinkedIn profiles (name, title, company, connection strength)
    3) Normalize + tokenize
    4) L0 title filter (>=100 synonyms) to keep high-signal roles
    5) Entity match across sources (email domain ↔ company, names)
    6) Intent heuristics (verbs: build, buy, hire, partner)
    7) Recency/velocity scoring (temporal decay)
    8) HCI/PCI rubric: Human Collaboration Index, Purchase Conviction Index
    9) Micro-segmentation buckets (buyer, builder, influencer)
    10) Produce prioritized leads + gaps
    """

    gmail = pd.DataFrame(gmail_threads or [])
    li = pd.DataFrame(linkedin_profiles or [])
    gmail = gmail.fillna("")
    li = li.fillna("")

    # 3) normalize
    gmail["sender_domain"] = gmail.get("sender", "").str.split("@").str[-1].str.lower()
    li["title_norm"] = li.get("title", "").str.lower()

    # 4) L0 title filter
    title_set = set(L0_TITLE_SYNONYMS)
    li["l0_keep"] = li["title_norm"].apply(lambda t: any(k in t for k in title_set))
    li_kept = li[li["l0_keep"]]

    # 5) entity match (simple domain/company heuristic)
    li_kept["company_norm"] = li_kept.get("company", "").str.lower().str.replace(" ", "")
    gmail["domain_norm"] = gmail["sender_domain"].str.replace(" ", "")

    # cross join small sets then match
    if not gmail.empty and not li_kept.empty:
        cross = li_kept.assign(key=1).merge(gmail.assign(key=1), on="key").drop(columns=["key"])  # type: ignore[arg-type]
        cross["entity_match"] = cross.apply(
            lambda r: r.get("company_norm", "") in r.get("domain_norm", ""), axis=1
        )
    else:
        cross = pd.DataFrame()

    # 6) intent heuristics
    verbs = {"build", "buy", "hire", "partner", "evaluate", "pilot", "procure"}
    if not cross.empty:
        text = (cross.get("subject", "") + " " + cross.get("snippet", "")).str.lower()
        cross["intent_hits"] = text.apply(lambda s: sum(1 for v in verbs if v in s))

    # 7) recency/velocity (placeholder: if date exists, apply simple decay)
    # For production, integrate actual timestamps. Here we assign uniform recency.
    if not cross.empty:
        cross["recency"] = 1.0

    # 8) HCI/PCI scoring
    def hci(row: Mapping) -> float:
        # Collaboration increases with connection strength and title seniority
        strength = float(row.get("connection_strength", 0) or 0)
        senior = any(k in str(row.get("title_norm", "")) for k in ["head", "vp", "chief", "director", "lead"])
        return min(1.0, 0.5 * strength + (0.3 if senior else 0.0) + 0.2 * float(row.get("intent_hits", 0)))

    def pci(row: Mapping) -> float:
        # Purchase conviction increases with entity match, intent, and recency
        base = 0.4 if bool(row.get("entity_match")) else 0.1
        return min(1.0, base + 0.2 * float(row.get("intent_hits", 0)) + 0.4 * float(row.get("recency", 0)))

    leads = []
    if not cross.empty:
        cross["HCI"] = cross.apply(hci, axis=1)
        cross["PCI"] = cross.apply(pci, axis=1)
        cross["score"] = 0.5 * cross["HCI"] + 0.5 * cross["PCI"]
        leads = (
            cross.sort_values(by=["score"], ascending=False)
            .head(50)
            .to_dict(orient="records")
        )

    # 9) micro-segmentation
    for r in leads:
        if r["PCI"] >= 0.7:
            r["segment"] = "buyer"
        elif r["HCI"] >= 0.7:
            r["segment"] = "builder"
        else:
            r["segment"] = "influencer"

    # 10) gap detection
    gaps = []
    if li_kept.empty:
        gaps.append("No high-signal LI titles found (L0 filter too strict?)")
    if gmail.empty:
        gaps.append("No Gmail threads ingested")

    receipt = decision_receipt("init_arcs.run", {"lead_count": len(leads), "gaps": gaps})
    return {"leads": leads, "gaps": gaps, "receipt": receipt}


def crystallize(requirements: Mapping[str, bool]) -> Dict[str, object]:
    """Evaluate phase transition readiness ('Crystallization').

    Required keys (True/False):
    - validated_molecules
    - feedback_loops
    - temporal_structure
    - commitment_catalyst
    - epistemic_humility
    """

    req_keys = [
        "validated_molecules",
        "feedback_loops",
        "temporal_structure",
        "commitment_catalyst",
        "epistemic_humility",
    ]
    missing = [k for k in req_keys if k not in requirements]
    if missing:
        raise KeyError(f"Missing crystallization keys: {missing}")

    score = sum(1.0 for k in req_keys if bool(requirements[k])) / len(req_keys)
    ready = score >= 0.8  # require at least 4/5 true
    receipt = decision_receipt("crystallize.evaluate", {"score": score, "ready": ready})
    return {"score": score, "ready": ready, "receipt": receipt}


def chrono_kairos(
    scheduled_windows: Sequence[Tuple[int, int]],
    signals: Mapping[str, Sequence[float]],
    threshold: float = 0.7,
) -> Dict[str, object]:
    """Temporal Arbitrator: detect kairos (opportune) windows vs scheduled.

    Parameters
    ----------
    scheduled_windows: Sequence[Tuple[int, int]]
        Planned windows as (start_idx, end_idx) over a shared discrete timeline.
    signals: Mapping[str, Sequence[float]]
        Named signals (e.g., engagement, supply, sentiment). Values in [0, 1].
    threshold: float
        Composite signal threshold to deem a kairos window.

    Returns
    -------
    Dict[str, object]
        {"kairos": List[(start,end)], "composite": np.ndarray, "receipt": ...}
    """

    # Build composite via normalized mean across signals + momentum bonus.
    arrays = [np.asarray(v, dtype=float) for v in signals.values()]
    if not arrays:
        composite = np.zeros(0)
    else:
        length = min(len(a) for a in arrays)
        arrays = [a[:length] for a in arrays]
        stack = np.vstack(arrays)
        base = stack.mean(axis=0)
        # Momentum via first derivative (simple diff)
        momentum = np.concatenate([[0.0], np.diff(base)])
        composite = np.clip(0.8 * base + 0.2 * (momentum - momentum.min()) / (momentum.ptp() or 1.0), 0, 1)

    kairos_windows: List[Tuple[int, int]] = []
    i = 0
    while i < len(composite):
        if composite[i] >= threshold:
            j = i
            while j < len(composite) and composite[j] >= threshold:
                j += 1
            kairos_windows.append((i, j - 1))
            i = j
        else:
            i += 1

    decision_receipt(
        "chrono_kairos.evaluate",
        {"kairos": kairos_windows, "scheduled": list(map(list, scheduled_windows))},
    )
    return {"kairos": kairos_windows, "composite": composite}

