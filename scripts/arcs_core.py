#!/usr/bin/env python3
"""
arcs_core.py — ARCS Personal Data Science Kernel (Pass 1 MVP)
==============================================================
Shared gauntlet engine for all domain scanners.

Architecture: DomainConfig pattern (P5 repair)
  Each adapter injects its own constants via DomainConfig.
  The kernel computes; adapters define domain meaning.

Golden Inchworm — Pass 1 contains only what calendar_scan.py needs.
Extended in Pass 2 (listening_scan.py) and Pass 3 (reader_scan.py).

Double Helix Protocol:
  composite = Strand_A × (1 − Strand_B_discount)

Triune Logic:
  OM        composite ≥ 160, loki ≤ 0.35, HCI ≥ 0.6, PCI ≥ 0.6
  UNDEFINED insufficient data — never treated as OM
  NULL      failed validation

Requirements: Python 3.8+, stdlib only.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────
# THRESHOLDS (constitutional — do not adjust per domain)
# ─────────────────────────────────────────────────────────────

OM_COMPOSITE_MIN    = 160
OM_LOKI_MAX         = 0.35
UNDEF_COMPOSITE_MIN = 80
L0_THRESHOLD        = 40
NOW                 = 2026
RECENT              = {2024, 2025, 2026}
ACTIVE              = {2022, 2023, 2024, 2025, 2026}

# ─────────────────────────────────────────────────────────────
# ARCHETYPE TAXONOMY (cross-domain — shared by all scanners)
# ─────────────────────────────────────────────────────────────

ARCHETYPES: List[Tuple[str, str, str, List[str], List[str]]] = [
    ("Builder",    "#00FF9D", "0→1 operators, founders, product builders",
     ["founder","co-founder","ceo","cto","cpo","chief product","chief executive",
      "chief technology","head of product","vp product","vp engineering",
      "director of product","general manager","president","startup","entrepreneur",
      "product lead","tech lead","principal engineer"], []),
    ("Navigator",  "#4ABDB0", "Strategy, chiefs of staff, GMs, P&L owners",
     ["chief of staff","strategy","strategic","chief operating","coo","chief revenue",
      "cro ","revenue","growth","managing director","svp","evp","head of strategy",
      "head of growth","head of operations","business development","biz dev","bd ",
      "partnerships","transformation"], []),
    ("Illuminator","#FFD700", "Writers, researchers, educators, thought leaders",
     ["writer","author","editor","journalist","researcher","professor","faculty",
      "educator","teacher","academic","thought leader","content creator",
      "content strategist","storyteller","analyst"],
     ["university","college","media","publishing"]),
    ("Instrumentor","#00F0FF","Engineers, data scientists, quantitative analysts",
     ["engineer","developer","software","data scientist","data engineer",
      "machine learning","ml engineer","ai engineer","quant","infrastructure",
      "devops","backend","frontend","full stack","site reliability","sre ",
      "blockchain developer","smart contract"], []),
    ("Mediator",   "#FF9500", "BD, partnerships, community, connectors",
     ["community","partnerships","partner","ecosystem","relations","connector",
      "ambassador","advocate","evangelist","liaison","account manager",
      "account executive","customer success","sales"], []),
    ("Orienter",   "#FF4D6D", "Coaches, advisors, mentors, career pivots",
     ["coach","mentor","advisor","adviser","counselor","fractional","interim",
      "executive coach","life coach","career coach","leadership coach"],
     ["coaching","advisory"]),
    ("Chartist",   "#A855F7", "Designers, architects, systems thinkers",
     ["design","designer","architect","ux","ui ","user experience","user interface",
      "product design","visual design","brand design","creative director",
      "art director","creative","systems thinking","design lead"],
     ["design","gensler","ideo"]),
    ("Focused Executor","#64748B","Ops, program managers, deep domain specialists",
     ["operations","program manager","project manager","specialist","coordinator",
      "associate","analyst","administrator","compliance","legal","accounting",
      "hr ","human resources","talent","recruiter","supply chain"], []),
]

ARCH_ORDER = [a[0] for a in ARCHETYPES]

RESONANCE_MATRIX: Dict[str, List[float]] = {
    "Builder":          [1.0, 0.85, 0.5,  0.75, 0.7,  0.5,  0.8,  0.4],
    "Navigator":        [0.85,1.0,  0.6,  0.6,  0.8,  0.65, 0.7,  0.5],
    "Illuminator":      [0.5, 0.6,  1.0,  0.5,  0.6,  0.7,  0.65, 0.3],
    "Instrumentor":     [0.75,0.6,  0.5,  1.0,  0.5,  0.3,  0.7,  0.5],
    "Mediator":         [0.7, 0.8,  0.6,  0.5,  1.0,  0.7,  0.55, 0.5],
    "Orienter":         [0.5, 0.65, 0.7,  0.3,  0.7,  1.0,  0.5,  0.4],
    "Chartist":         [0.8, 0.7,  0.65, 0.7,  0.55, 0.5,  1.0,  0.4],
    "Focused Executor": [0.4, 0.5,  0.3,  0.5,  0.5,  0.4,  0.4,  1.0],
}

TX_MAP: Dict[str, Tuple[List[str], int]] = {
    "CUSTOMER": (["ceo","cto","coo","founder","chief","president","executive director",
                  "general manager","managing director"], 35),
    "INVESTOR": (["venture","investor","partner","gp ","managing partner","investment",
                  "fund","seed","angel","portfolio","vc ","capital","allocator",
                  "new ventures","deal"], 40),
    "PARTNER":  (["business development","partnerships","bd ","ecosystem","platform",
                  "distribution","alliances","go-to-market","gtm","enterprise",
                  "deal desk","retail partnerships"], 32),
    "MEDIA":    (["editor","journalist","writer","author","reporter","producer","host",
                  "podcast","newsletter","media","magazine","columnist"], 28),
    "TALENT":   (["cto","head of engineering","vp engineering","principal engineer",
                  "staff engineer","design lead","head of design","vp product"], 25),
    "ADVISOR":  (["advisor","adviser","board","fractional","fellow","mentor",
                  "executive coach"], 22),
}

TIER1_COS_DEFAULT = {
    "google","apple","amazon","meta","microsoft","openai","anthropic","nvidia","stripe",
    "coinbase","spotify","netflix","airbnb","uber","lyft","palantir","figma","notion",
    "shopify","vercel","a16z","sequoia","kleiner","y combinator","benchmark",
    "general catalyst","goldman sachs","morgan stanley","blackrock","jp morgan",
    "citadel","nbc","hbo","universal","warner","sony","disney","wired","fast company",
    "salesforce","fidelity","circle","grayscale",
}

# ─────────────────────────────────────────────────────────────
# DOMAIN CONFIG — P5 repair: adapters inject domain constants
# ─────────────────────────────────────────────────────────────

@dataclass
class LokiRule:
    """A single Strand B adversarial discount rule.

    condition_fn receives a GauntletEntry and returns True if the rule fires.
    discount is added to the total Loki rate when the rule fires (capped at 0.75).
    """
    name:         str
    discount:     float
    condition_fn: Callable[["GauntletEntry"], bool]
    explanation:  str = ""


@dataclass
class DomainConfig:
    """Domain-specific constants injected by each adapter.

    tier1_contexts: set of strings considered high-prestige in this domain
                    (e.g. "external partner" for calendar, Tier-1 companies for LinkedIn)
    subject_weights: list of (archetype_name, weight) tuples — the subject's stack
    strand_b_rules:  list of LokiRule applied after built-in Loki audit
    receipt_labels:  override default section headers in the Markdown receipt
    """
    domain_name:     str
    tier1_contexts:  set                                     = field(default_factory=set)
    subject_weights: List[Tuple[str, float]]                 = field(default_factory=lambda: [
        ("Builder", 1.0), ("Navigator", 0.6), ("Chartist", 0.3)
    ])
    strand_b_rules:  List[LokiRule]                          = field(default_factory=list)
    receipt_labels:  Dict[str, str]                          = field(default_factory=dict)

    def label(self, key: str, default: str) -> str:
        return self.receipt_labels.get(key, default)


# ─────────────────────────────────────────────────────────────
# UNIVERSAL ENTRY — the dict every adapter maps to
# ─────────────────────────────────────────────────────────────

@dataclass
class GauntletEntry:
    """Universal domain-agnostic contact dict.

    All adapters map their domain objects to this schema before
    passing to the gauntlet engine.

    extra: arbitrary domain-specific fields (e.g. duration_min, ms_played,
           recurrence_count) used by LokiRule condition_fns.
    """
    name:    str
    position: str        # title / role / event name / track name
    company:  str        # org / artist / book title / meeting organizer
    year:     Optional[int]
    extra:    Dict[str, Any] = field(default_factory=dict)


@dataclass
class GauntletResult:
    """Full forensic receipt for one entry."""
    entry:        GauntletEntry
    strand_a:     int
    strand_b:     float
    composite:    int
    hci:          float
    pci:          float
    triune:       str          # OM / UNDEFINED / NULL
    l5_true_north: str
    l5_why:       List[str]
    fired_rules:  List[str]    # names of Loki rules that fired (audit chain)
    primary_arch: str
    nci:          float
    arch_ranked:  List[Tuple[str, float]]

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def parse_year(s: str) -> Optional[int]:
    for p in (s or "").strip().split():
        if p.isdigit() and len(p) == 4:
            return int(p)
    return None

# ─────────────────────────────────────────────────────────────
# ARCHETYPE SCORING (domain-agnostic)
# ─────────────────────────────────────────────────────────────

def classify_archetype(position: str, company: str) -> List[Tuple[str, float]]:
    h_t, h_c = position.lower(), company.lower()
    scores: Dict[str, float] = {}
    for name, _, _, title_kw, co_kw in ARCHETYPES:
        s = sum(1.0 for k in title_kw if k in h_t) + sum(0.5 for k in co_kw if k in h_c)
        scores[name] = s
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    if ranked[0][1] == 0:
        ranked = [("Focused Executor", 0.1)] + [r for r in ranked if r[0] != "Focused Executor"]
    return ranked


def compute_nci(ranked: List[Tuple[str, float]],
                subject_weights: List[Tuple[str, float]]) -> float:
    total = sum(s for _, s in ranked)
    if not total:
        return 0.0
    nci = 0.0
    for arch, w in ranked[:3]:
        if arch not in ARCH_ORDER:
            continue
        idx  = ARCH_ORDER.index(arch)
        prop = w / total
        for sa, sw in subject_weights:
            if sa in RESONANCE_MATRIX:
                nci += prop * sw * RESONANCE_MATRIX[sa][idx]
    return min(nci / max(sum(w for _, w in subject_weights), 0.001), 1.0)

# ─────────────────────────────────────────────────────────────
# STRAND A — FORWARD SCORING
# ─────────────────────────────────────────────────────────────

_C_SUITE = {"ceo","cto","cpo","coo","cmo","cfo"}
_C_SUITE_KW = ["chief ","founder","co-founder","president","managing partner","general partner"]
_VP_DIR_KW  = ["vp ","svp","evp","vice president","director","managing director",
               "md ","general manager","head of","principal","partner"]

def strand_a_score(entry: GauntletEntry,
                   config: DomainConfig,
                   company_registry: Optional[Dict[str, int]] = None) -> Tuple[int, List[str]]:
    """Compute Strand A forward score.

    Returns (score, signals_list).
    company_registry maps company → connection count (optional; used for hub bonus).
    """
    pos  = entry.position.lower()
    co   = entry.company.lower()
    year = entry.year
    company_registry = company_registry or {}
    score   = 0
    signals = []

    # Archetype resonance (NCI)
    ranked    = classify_archetype(entry.position, entry.company)
    nci       = compute_nci(ranked, config.subject_weights)
    arch_pts  = int(nci * 80)
    score    += arch_pts
    signals.append(f"NCI {nci:.3f} ({ranked[0][0]}) → +{arch_pts}")

    # Recency
    rec = 30 if year in RECENT else 18 if year in ACTIVE else 5
    score   += rec
    signals.append(f"Recency {year} → +{rec}")

    # Tier-1 / high-prestige context
    is_tier1 = any(t in co for t in TIER1_COS_DEFAULT) or \
               any(t in co for t in config.tier1_contexts)
    if is_tier1:
        score += 30
        signals.append(f"Tier-1 context: {entry.company} → +30")

    # Seniority
    if any(k in pos for k in _C_SUITE_KW) or any(k in pos for k in _C_SUITE):
        score += 25; signals.append("C-suite → +25")
    elif any(k in pos for k in _VP_DIR_KW):
        score += 15; signals.append("VP/Director → +15")

    # TX value
    tx_hits = [(tx, v) for tx, (kws, v) in TX_MAP.items() if any(k in pos for k in kws)]
    tx_hits.sort(key=lambda x: -x[1])
    if tx_hits:
        tx_pts = int(tx_hits[0][1] * (1.2 if year in RECENT else 1.0) * len(tx_hits))
        score += tx_pts
        signals.append(f"TX:{tx_hits[0][0]}×{len(tx_hits)} → +{tx_pts}")

    # Cross-domain bridge
    bridges = [a for a, _, _, kws, _ in ARCHETYPES if any(k in pos for k in kws)]
    if len(bridges) >= 2:
        score += 20
        signals.append(f"Bridge {'+'.join(bridges[:3])} → +20")

    # Hub company
    co_count = company_registry.get(entry.company, 0)
    if co_count >= 3 and any(k in pos for k in ["founder","ceo","director","vp","head of","partner"]):
        score += 18
        signals.append(f"Hub ({co_count} connections @ {entry.company}) → +18")

    # Long-arc root
    if year and year <= 2013:
        score += 15
        signals.append(f"Root node ({year}) → +15")

    return score, signals

# ─────────────────────────────────────────────────────────────
# STRAND B — REVERSE / LOKI ADVERSARIAL
# ─────────────────────────────────────────────────────────────

_HALO_TITLE_KW = ["manager","associate","analyst","coordinator","specialist",
                  "assistant","representative","officer","support"]
_INFLATION_KW  = ["global","chief","head","vp","director","senior","lead",
                  "principal","executive","president"]
_STALE_THRESHOLD = 5

def strand_b_loki(entry: GauntletEntry,
                  config: DomainConfig,
                  company_registry: Optional[Dict[str, int]] = None) -> Tuple[float, List[str]]:
    """Compute Strand B Loki adversarial discount.

    Returns (discount_rate [0.0–0.75], fired_rule_names).
    Runs built-in rules first, then any domain-specific LokiRules in config.
    """
    pos   = entry.position.lower()
    co    = entry.company.lower()
    year  = entry.year
    company_registry = company_registry or {}
    fired:    List[str]  = []
    discount: float      = 0.0

    tier1_hit = (any(t in co for t in TIER1_COS_DEFAULT) or
                 any(t in co for t in config.tier1_contexts))

    # Built-in: HALO EFFECT
    if tier1_hit and any(k in pos for k in _HALO_TITLE_KW):
        fired.append("HALO: Tier-1 brand with generic title — brand inflation likely")
        discount += 0.25

    # Built-in: STALENESS
    if year and (NOW - year) >= _STALE_THRESHOLD:
        age = NOW - year
        stale = min(0.05 * (age - _STALE_THRESHOLD + 1), 0.30)
        fired.append(f"STALE: {age}yr old signal — relationship may be cold")
        discount += stale

    # Built-in: TITLE INFLATION
    inf_hits = [k for k in _INFLATION_KW if k in pos]
    if len(inf_hits) >= 3:
        fired.append(f"INFLATION: {len(inf_hits)} seniority signals in one title")
        discount += 0.15

    # Built-in: SELF-EMPLOYED NOISE
    if any(k in co for k in ["self-employed","self employed","freelance","independent"]):
        if any(k in pos for k in ["chief","ceo","president","founder","head of"]):
            fired.append("NOISE: C-suite title at self-employed entity")
            discount += 0.10

    # Built-in: UNKNOWN COMPANY
    is_unknown = not tier1_hit and company_registry.get(entry.company, 0) <= 1
    if any(k in pos for k in ["chief","founder","ceo","president","global head"]) and \
       is_unknown and not any(k in co for k in ["stealth","startup"]):
        fired.append("UNKNOWN CO: strong title at unrecognised company")
        discount += 0.10

    # Built-in: BRAND SYCOPHANCY (Kintsugi pathogen)
    senior_title = any(k in pos for k in
        ["founder","chief","ceo","cto","vp","director","head of","partner","gp","president"])
    if tier1_hit and not senior_title:
        fired.append("PATHOGEN: BRAND SYCOPHANCY — all signal from company name, role contributes nothing")
        discount += 0.30

    # Built-in: CONTRADICTION
    tx_hits = [tx for tx, (kws, _) in TX_MAP.items() if any(k in pos for k in kws)]
    if not tx_hits and any(k in pos for k in ["chief","ceo","president","founder"]):
        fired.append("CONTRADICTION: C-suite title with no TX mapping")
        discount += 0.10

    # Domain-specific LokiRules (injected by adapter via DomainConfig)
    for rule in config.strand_b_rules:
        try:
            if rule.condition_fn(entry):
                label = rule.explanation or rule.name
                fired.append(f"{rule.name.upper()}: {label}")
                discount += rule.discount
        except Exception:
            pass

    return min(discount, 0.75), fired

# ─────────────────────────────────────────────────────────────
# L2 — BAYESIAN VALIDATION (HCI / PCI)
# ─────────────────────────────────────────────────────────────

def l2_bayesian(entry: GauntletEntry,
                nci: float,
                strand_b: float,
                composite: int,
                fired_rules: List[str]) -> Tuple[float, float]:
    """Returns (HCI, PCI) each in [0.0, 1.0]."""
    hci = 0.0
    if entry.year and entry.company:         hci += 0.2
    if len(entry.position) > 10:             hci += 0.2
    if nci > 0.5:                            hci += 0.2
    if strand_b < 0.2:                       hci += 0.2
    # extra: domain completeness (adapter populates entry.extra["data_completeness"])
    if entry.extra.get("data_completeness", 0) > 0.5: hci += 0.2
    hci = round(min(hci, 1.0), 2)

    pci = 0.0
    if composite >= OM_COMPOSITE_MIN:        pci += 0.3
    if strand_b <= OM_LOKI_MAX:             pci += 0.3
    if entry.year in RECENT:                 pci += 0.2
    if len(fired_rules) == 0:               pci += 0.2
    pci = round(min(pci, 1.0), 2)

    return hci, pci

# ─────────────────────────────────────────────────────────────
# TRIUNE CLASSIFICATION
# ─────────────────────────────────────────────────────────────

def triune_classify(composite: int, loki: float, hci: float, pci: float) -> str:
    if composite >= OM_COMPOSITE_MIN and loki <= OM_LOKI_MAX and hci >= 0.6 and pci >= 0.6:
        return "OM"
    if composite >= UNDEF_COMPOSITE_MIN:
        return "UNDEFINED"
    return "NULL"

# ─────────────────────────────────────────────────────────────
# L5 — ATOMIC INTEL
# ─────────────────────────────────────────────────────────────

def l5_atomic_intel(entry: GauntletEntry,
                    arch: str,
                    signals: List[str],
                    fired_rules: List[str]) -> Tuple[str, List[str]]:
    pos = entry.position
    co  = entry.company
    tx_hits = [(tx, v) for tx, (kws, v) in TX_MAP.items()
               if any(k in pos.lower() for k in kws)]
    tx_hits.sort(key=lambda x: -x[1])

    TX_TEXT = {
        "INVESTOR": "a capital or deal-structure relationship",
        "PARTNER":  "a distribution or co-build relationship",
        "CUSTOMER": "a direct product or service relationship",
        "MEDIA":    "an amplification or publishing relationship",
        "TALENT":   "a team or capability relationship",
        "ADVISOR":  "a guidance or board relationship",
    }
    if tx_hits:
        true_north = (f"{entry.name} represents "
                      f"{TX_TEXT.get(tx_hits[0][0], 'a high-signal relationship')} — "
                      f"{arch} archetype at {co}.")
    else:
        true_north = f"{entry.name} is a {arch} at {co} with strong resonance to the subject stack."

    why = []
    if signals:
        why.append(signals[0])
    if fired_rules:
        why.append(f"Loki audit: {fired_rules[0]}")
    else:
        why.append("No Loki objections — clean signal")
    if entry.year:
        why.append(f"Connected / recorded {entry.year}")

    return true_north, why[:3]

# ─────────────────────────────────────────────────────────────
# FULL GAUNTLET PIPELINE
# ─────────────────────────────────────────────────────────────

def run_gauntlet(entries: List[GauntletEntry],
                 config: DomainConfig,
                 company_registry: Optional[Dict[str, int]] = None,
                 top_n: int = 20) -> Tuple[List[GauntletResult], Dict]:
    """Run the full L0–L5 gauntlet on a list of GauntletEntry objects.

    Returns (results_sorted_by_composite, stats_dict).
    results contains ALL entries that passed L0; sorted descending by composite.
    """
    company_registry = company_registry or {}
    results: List[GauntletResult] = []
    stats = {"total": len(entries), "l0_passed": 0, "l0_killed": 0,
             "om": 0, "undefined": 0, "null": 0,
             "pathogens": 0, "avg_loki": 0.0}

    all_loki: List[float] = []

    for entry in entries:
        # Strand A
        sa, signals = strand_a_score(entry, config, company_registry)

        # L0 gate
        if sa < L0_THRESHOLD:
            stats["l0_killed"] += 1
            continue
        stats["l0_passed"] += 1

        # Strand B
        sb, fired = strand_b_loki(entry, config, company_registry)
        all_loki.append(sb)
        if "PATHOGEN" in " ".join(fired):
            stats["pathogens"] += 1

        # Composite
        composite = round(sa * (1.0 - sb))

        # L2 Bayesian
        ranked = classify_archetype(entry.position, entry.company)
        nci    = compute_nci(ranked, config.subject_weights)
        hci, pci = l2_bayesian(entry, nci, sb, composite, fired)

        # Triune
        status = triune_classify(composite, sb, hci, pci)
        stats[status.lower()] += 1

        # L5 (OM only — saves compute for large datasets)
        arch = ranked[0][0]
        if status == "OM":
            true_north, why = l5_atomic_intel(entry, arch, signals, fired)
        else:
            true_north = f"{entry.name} — {arch} @ {entry.company}"
            why = signals[:1] if signals else []

        results.append(GauntletResult(
            entry=entry, strand_a=sa, strand_b=sb, composite=composite,
            hci=hci, pci=pci, triune=status,
            l5_true_north=true_north, l5_why=why,
            fired_rules=fired, primary_arch=arch, nci=round(nci, 4),
            arch_ranked=ranked,
        ))

    results.sort(key=lambda r: -r.composite)
    stats["avg_loki"] = round(sum(all_loki) / max(len(all_loki), 1), 3)
    return results, stats

# ─────────────────────────────────────────────────────────────
# RENDER — MARKDOWN RECEIPT
# ─────────────────────────────────────────────────────────────

def render_receipt(results: List[GauntletResult],
                   config: DomainConfig,
                   stats: Dict,
                   top_n: int = 20) -> str:
    """Render a Markdown receipt from gauntlet results."""
    om_results = [r for r in results if r.triune == "OM"]
    lines = []

    lines.append(f"# ARCS {config.domain_name} Scan — Gauntlet Receipt\n")

    # Gauntlet summary
    lines.append("## Gauntlet Summary\n")
    lines.append(f"| Field | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Total entries | {stats['total']} |")
    lines.append(f"| L0 passed | {stats['l0_passed']} |")
    lines.append(f"| L0 killed | {stats['l0_killed']} |")
    lines.append(f"| OM | {stats['om']} |")
    lines.append(f"| UNDEFINED | {stats['undefined']} |")
    lines.append(f"| NULL | {stats['null']} |")
    lines.append(f"| Pathogens detected | {stats['pathogens']} |")
    lines.append(f"| Avg Loki discount | {stats['avg_loki']:.1%} |")
    lines.append("")

    # Top OM entries
    top_label = config.label("top_om_section", "Top OM Entries")
    lines.append(f"## {top_label}\n")
    for i, r in enumerate(om_results[:top_n], 1):
        loki_pct = int(r.strand_b * 100)
        lines.append(f"### {i}. {r.entry.name} [{r.composite}pts | Loki:{loki_pct}%]")
        lines.append(f"**{r.primary_arch}** @ {r.entry.company} | {r.entry.year or 'n/a'}")
        lines.append(f"> {r.l5_true_north}")
        if r.l5_why:
            lines.append("**Why:**")
            for w in r.l5_why:
                lines.append(f"- {w}")
        if r.fired_rules:
            lines.append(f"*Loki audit: {r.fired_rules[0]}*")
        lines.append("")

    # Cluster topology (by archetype)
    cluster_label = config.label("cluster_section", "Archetype / Context Topology")
    lines.append(f"## {cluster_label}\n")
    arch_counts: Dict[str, int] = {}
    for r in results:
        arch_counts[r.primary_arch] = arch_counts.get(r.primary_arch, 0) + 1
    for arch, cnt in sorted(arch_counts.items(), key=lambda x: -x[1]):
        bar = "█" * min(cnt // 5, 40)
        lines.append(f"- **{arch}**: {cnt:,}  {bar}")
    lines.append("")

    # Temporal stratigraphy
    strat_label = config.label("strat_section", "Temporal Stratigraphy")
    lines.append(f"## {strat_label}\n")
    year_counts: Dict[int, int] = {}
    for r in results:
        if r.entry.year:
            year_counts[r.entry.year] = year_counts.get(r.entry.year, 0) + 1
    for yr in sorted(year_counts):
        bar = "█" * min(year_counts[yr] // 3, 50)
        lines.append(f"- **{yr}**: {year_counts[yr]:,}  {bar}")
    lines.append("")

    # UNDEFINED warnings
    undef_results = [r for r in results if r.triune == "UNDEFINED"]
    if undef_results:
        lines.append("## UNDEFINED Zone Warnings\n")
        lines.append("The following entries had insufficient data for OM classification.")
        lines.append("Never treat UNDEFINED as OM — re-evaluate when more data is available.\n")
        for r in undef_results[:10]:
            lines.append(f"- **{r.entry.name}** @ {r.entry.company} "
                         f"(composite={r.composite}, Loki={r.strand_b:.0%})")
        lines.append("")

    # Methodology
    lines.append("## Methodology\n")
    lines.append("**Double Helix Protocol:**")
    lines.append("```")
    lines.append("composite = Strand_A × (1 − Strand_B_discount)")
    lines.append("OM requires: composite ≥ 160, Loki ≤ 35%, HCI ≥ 0.6, PCI ≥ 0.6")
    lines.append("```")
    lines.append("")
    lines.append("**Triune Logic:** OM (validated) / UNDEFINED (insufficient data) / NULL (failed)")
    lines.append("")
    lines.append(f"**Domain:** {config.domain_name}")
    if config.strand_b_rules:
        lines.append("**Domain-specific Loki rules:**")
        for rule in config.strand_b_rules:
            lines.append(f"- `{rule.name}` discount={rule.discount:.0%}: {rule.explanation or rule.name}")

    return "\n".join(lines)
