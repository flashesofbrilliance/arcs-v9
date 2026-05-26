#!/usr/bin/env python3
"""
ARCS Network Scan — Full Portable Edition
==========================================
Runs the complete ARCS gauntlet on any LinkedIn Connections.csv export.

Pipeline:
  L0  Activation filter       — minimum threshold gate (≥40/60)
  L1  Loki adversarial        — steel-man objection per high-signal contact
  L2  Bayesian validation     — HCI/PCI scoring, UNDEFINED labelling
  L3  Kintsugi pathogen scan  — sycophancy detection, halo effect flags
  L4  NCI meta-review         — self-grade, antithesis, "What I Don't Know"
  L5  Atomic Intel delivery   — True North + ≤3 why bullets

Double Helix Protocol:
  Strand A (forward)  — topology + archetype + 5-lens forensic scoring
  Strand B (reverse)  — Loki discount + pathogen penalties
  Helix composite     = A × (1 - B_discount_rate)
  OM requires BOTH strands to clear threshold. UNDEFINED = insufficient data.
  NULL = failed validation or NEVER rule triggered.

Triune Logic (v8.5 Diamond):
  OM        Validated, n≥5, confidence ≥80%, methodology documented
  UNDEFINED Insufficient data — labelled explicitly, never treated as OM
  NULL      Failed validation or NEVER rule triggered

Usage:
  python3 network_scan_full.py Connections.csv
  python3 network_scan_full.py Connections.csv --subject "Builder,Navigator,Chartist"
  python3 network_scan_full.py Connections.csv --top 30 --out ./my_report

Requirements: Python 3.8+, no external packages.
"""

import csv
import json
import math
import os
import re
import sys
import collections
import argparse
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────

RECENT  = {2024, 2025, 2026}
ACTIVE  = {2022, 2023, 2024, 2025, 2026}
NOW     = 2026

L0_THRESHOLD       = 40      # minimum raw signal to enter pipeline
OM_COMPOSITE_MIN   = 160     # helix composite score to reach OM
OM_LOKI_MAX        = 0.35    # max Loki discount rate for OM status
UNDEF_COMPOSITE_MIN = 80     # minimum composite for UNDEFINED (vs NULL)

# ─────────────────────────────────────────────────────────────
# INDUSTRY TAXONOMY
# ─────────────────────────────────────────────────────────────

INDUSTRY_TAXONOMY = [
    ("Crypto / Web3 / Blockchain", [
        "crypto","blockchain","bitcoin","ethereum","defi","web3","nft","grayscale",
        "coinbase","binance","kraken","ledger","bitgo","chainalysis","alchemy",
        "polygon","solana","avalanche","pyusd","digital asset","virtual currency",
        "token","dao","decentralized","galaxis","opensea","animoca","yuga",
    ]),
    ("Venture / PE / Investment", [
        "venture","venture capital","vc ","private equity","pe ","seed","angel investor",
        "general partner","limited partner","fund","andreessen","sequoia","a16z",
        "kleiner","benchmark","accel","softbank","tiger global","blackrock",
        "investment firm","asset management","allocator",
    ]),
    ("Fintech / Payments", [
        "fintech","payments","paypal","stripe","square","affirm","klarna","robinhood",
        "plaid","marqeta","chime","brex","insurtech","wealthtech","nerdwallet",
    ]),
    ("Traditional Finance / Banking", [
        "goldman sachs","morgan stanley","jp morgan","jpmorgan","bank of america",
        "citigroup","citi","wells fargo","barclays","deutsche bank","ubs",
        "blackstone","carlyle","hedge fund","derivatives","investment bank",
    ]),
    ("Real Estate", [
        "real estate","corcoran","elliman","douglas elliman","compass","sotheby",
        "coldwell","redfin","zillow","related","cushman","cbre","jll","colliers",
        "broker","realtor","property","residential","commercial real","reit","proptech",
    ]),
    ("Big Tech (FAANG+)", [
        "google","apple","amazon","meta","microsoft","netflix","alphabet","waymo",
        "deepmind","openai","anthropic","salesforce","oracle","ibm","intel",
        "nvidia","amd","qualcomm","broadcom","cisco","vmware","servicenow",
        "workday","splunk","palo alto",
    ]),
    ("AI / ML / Data", [
        "artificial intelligence","machine learning","deep learning","natural language",
        "computer vision","data science","llm","generative ai","ai startup",
        "hugging face","mistral","cohere","stability","midjourney","runway",
        "scale ai","databricks","snowflake",
    ]),
    ("SaaS / Enterprise Software", [
        "saas","enterprise software","hubspot","zendesk","twilio","figma",
        "notion","airtable","atlassian","jira","zoom","docusign","dropbox","intercom",
    ]),
    ("Startup / Stealth", [
        "stealth","stealth startup","stealth ai","co-founder","cofounder",
        "founder & ceo","founding team",
    ]),
    ("Design / Architecture / Creative", [
        "design","gensler","skidmore","aecom","hok","kpf","interior design",
        "industrial design","graphic design","ux design","product design",
        "creative director","art director","brand design","architecture",
    ]),
    ("Media / Entertainment / Publishing", [
        "media","entertainment","film","television","streaming","music","spotify",
        "universal music","sony music","warner","publishing","journalism","news",
        "magazine","editorial","podcast","content","production company","studio",
    ]),
    ("Healthcare / Wellness / Biotech", [
        "health","healthcare","wellness","medical","biotech","pharma","clinical",
        "hospital","therapy","mental health","digital health","medtech","lifesciences",
    ]),
    ("Consulting / Advisory", [
        "mckinsey","bain","bcg","boston consulting","deloitte","accenture",
        "pwc","kpmg","ey ","ernst & young","consulting","advisory","strategy consulting",
    ]),
    ("Government / Policy / Non-profit", [
        "government","policy","federal","department of","nonprofit","non-profit",
        "ngo","un ","united nations","world bank","foundation","philanthropy",
    ]),
    ("Education / Academia", [
        "university","college","school of","professor","faculty","researcher",
        "phd","postdoc","academic","education","edtech",
    ]),
    ("Self-employed / Freelance", [
        "self-employed","self employed","freelance","independent","fractional",
    ]),
]

# ─────────────────────────────────────────────────────────────
# ARCHETYPE TAXONOMY
# ─────────────────────────────────────────────────────────────

ARCHETYPES = [
    ("Builder",    "#00FF9D", "0→1 operators, founders, CPOs, product builders",
     ["founder","co-founder","ceo","cto","cpo","chief product","chief executive",
      "chief technology","head of product","vp product","vp engineering",
      "director of product","general manager","president","startup","entrepreneur",
      "product lead","tech lead","principal engineer"], []),
    ("Navigator",  "#4ABDB0", "Strategy, Chiefs of Staff, GMs, P&L owners",
     ["chief of staff","strategy","strategic","chief operating","coo",
      "chief revenue","cro ","revenue","growth","managing director","svp","evp",
      "head of strategy","head of growth","head of operations","business development",
      "biz dev","bd ","partnerships","transformation"], []),
    ("Illuminator","#FFD700", "Writers, researchers, educators, thought leaders",
     ["writer","author","editor","journalist","researcher","professor","faculty",
      "educator","teacher","academic","thought leader","content creator",
      "content strategist","storyteller","analyst"], ["university","college","media","publishing"]),
    ("Instrumentor","#00F0FF","Engineers, data scientists, quant analysts",
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
      "executive coach","life coach","career coach","leadership coach"], ["coaching","advisory"]),
    ("Chartist",   "#A855F7", "Designers, architects, systems thinkers",
     ["design","designer","architect","ux","ui ","user experience","user interface",
      "product design","visual design","brand design","creative director",
      "art director","creative","systems thinking","design lead"], ["design","gensler","ideo"]),
    ("Focused Executor","#64748B","Ops, program managers, deep domain specialists",
     ["operations","program manager","project manager","specialist","coordinator",
      "associate","analyst","administrator","compliance","legal","accounting",
      "hr ","human resources","talent","recruiter","supply chain"], []),
]
ARCH_ORDER = [a[0] for a in ARCHETYPES]

RESONANCE_MATRIX = {
    "Builder":          [1.0, 0.85, 0.5, 0.75, 0.7,  0.5,  0.8,  0.4],
    "Navigator":        [0.85,1.0,  0.6, 0.6,  0.8,  0.65, 0.7,  0.5],
    "Illuminator":      [0.5, 0.6,  1.0, 0.5,  0.6,  0.7,  0.65, 0.3],
    "Instrumentor":     [0.75,0.6,  0.5, 1.0,  0.5,  0.3,  0.7,  0.5],
    "Mediator":         [0.7, 0.8,  0.6, 0.5,  1.0,  0.7,  0.55, 0.5],
    "Orienter":         [0.5, 0.65, 0.7, 0.3,  0.7,  1.0,  0.5,  0.4],
    "Chartist":         [0.8, 0.7,  0.65,0.7,  0.55, 0.5,  1.0,  0.4],
    "Focused Executor": [0.4, 0.5,  0.3, 0.5,  0.5,  0.4,  0.4,  1.0],
}

TX_MAP = {
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

TIER1_COS = {
    "google","apple","amazon","meta","microsoft","openai","anthropic","nvidia","stripe",
    "coinbase","grayscale","spotify","netflix","airbnb","uber","lyft","palantir",
    "figma","notion","shopify","vercel","a16z","sequoia","kleiner","y combinator",
    "benchmark","general catalyst","goldman sachs","morgan stanley","blackrock",
    "jp morgan","citadel","nbc","hbo","universal","warner","sony","disney",
    "wired","fast company","salesforce","fidelity","circle",
}

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def parse_year(s):
    for p in (s or "").strip().split():
        if p.isdigit() and len(p) == 4:
            return int(p)
    return None

def load_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        lines = f.readlines()
    start = next((i for i, l in enumerate(lines) if "First Name" in l), 0)
    out = []
    for row in csv.DictReader(lines[start:]):
        first   = (row.get("First Name") or "").strip()
        last    = (row.get("Last Name") or "").strip()
        company = (row.get("Company") or "").strip()
        pos     = (row.get("Position") or "").strip()
        url     = (row.get("URL") or "").strip()
        year    = parse_year(row.get("Connected On") or "")
        if not first and not last:
            continue
        out.append({"name": f"{first} {last}".strip(), "first": first, "last": last,
                    "company": company, "pos": pos, "url": url, "year": year})
    return out

def classify_industry(company, pos):
    h = (company + " " + pos).lower()
    for label, kws in INDUSTRY_TAXONOMY:
        if any(kw in h for kw in kws):
            return label
    return "Other / Unclassified"

def classify_archetype(pos, company):
    h_t, h_c = pos.lower(), company.lower()
    scores = {}
    for name, _, _, title_kw, co_kw in ARCHETYPES:
        s = sum(1.0 for k in title_kw if k in h_t) + sum(0.5 for k in co_kw if k in h_c)
        scores[name] = s
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    if ranked[0][1] == 0:
        ranked = [("Focused Executor", 0.1)] + [r for r in ranked if r[0] != "Focused Executor"]
    return ranked

def compute_nci(ranked, subject_weights):
    total = sum(s for _, s in ranked)
    if not total:
        return 0.0
    nci = 0.0
    for arch, w in ranked[:3]:
        if arch not in ARCH_ORDER:
            continue
        idx = ARCH_ORDER.index(arch)
        prop = w / total
        for sa, sw in subject_weights:
            if sa in RESONANCE_MATRIX:
                nci += prop * sw * RESONANCE_MATRIX[sa][idx]
    return min(nci / max(sum(w for _, w in subject_weights), 0.001), 1.0)

# ─────────────────────────────────────────────────────────────
# STRAND A — FORWARD SCORING (topology + archetype + forensic)
# ─────────────────────────────────────────────────────────────

def strand_a_score(c, company_registry, subject_weights):
    pos, co = c["pos"].lower(), c["company"].lower()
    year = c["year"]
    signals = []
    score = 0

    # ── Archetype resonance ───────────────────────────────────
    ranked = classify_archetype(c["pos"], c["company"])
    nci = compute_nci(ranked, subject_weights)
    arch_score = int(nci * 80)
    score += arch_score
    signals.append(f"NCI {nci:.3f} ({ranked[0][0]}) → +{arch_score}")

    # ── Recency ───────────────────────────────────────────────
    rec = 30 if year in RECENT else 18 if year in ACTIVE else 5
    score += rec
    signals.append(f"Recency {year} → +{rec}")

    # ── Tier-1 company ────────────────────────────────────────
    tier1 = next((t for t in TIER1_COS if t in co), None)
    if tier1:
        score += 30
        signals.append(f"Tier-1: {c['company']} → +30")

    # ── Seniority ─────────────────────────────────────────────
    C_SUITE = ["ceo","cto","cpo","coo","cmo","cfo","chief ","founder","co-founder",
               "president","managing partner","general partner"]
    VP_DIR  = ["vp ","svp","evp","vice president","director","managing director",
               "md ","general manager","head of","principal","partner"]
    if any(k in pos for k in C_SUITE):
        score += 25; signals.append("C-suite → +25")
    elif any(k in pos for k in VP_DIR):
        score += 15; signals.append("VP/Director → +15")

    # ── TX value ──────────────────────────────────────────────
    tx_hits = [(tx, v) for tx, (kws, v) in TX_MAP.items() if any(k in pos for k in kws)]
    tx_hits.sort(key=lambda x: -x[1])
    if tx_hits:
        tx_score = int(tx_hits[0][1] * (1.2 if year in RECENT else 1.0) * len(tx_hits))
        score += tx_score
        signals.append(f"TX:{tx_hits[0][0]}×{len(tx_hits)} → +{tx_score}")

    # ── Cross-domain bridge ───────────────────────────────────
    arches_in_title = [a for a, _, _, kws, _ in ARCHETYPES if any(k in pos for k in kws)]
    if len(arches_in_title) >= 2:
        score += 20
        signals.append(f"Bridge {'+'.join(arches_in_title[:3])} → +20")

    # ── Hub company ───────────────────────────────────────────
    co_count = company_registry.get(c["company"], 0)
    if co_count >= 3 and any(k in pos for k in ["founder","ceo","director","vp","head of","partner"]):
        score += 18
        signals.append(f"Hub ({co_count} connections @ {c['company']}) → +18")

    # ── Long-arc root node ────────────────────────────────────
    if year and year <= 2013:
        score += 15
        signals.append(f"Root node ({year}) → +15")

    c["strand_a_score"] = score
    c["strand_a_signals"] = signals
    c["archetype_ranked"] = ranked
    c["nci"] = round(nci, 4)
    c["primary_arch"] = ranked[0][0]
    return score

# ─────────────────────────────────────────────────────────────
# STRAND B — REVERSE / LOKI ADVERSARIAL (L1 + L3)
# Returns a discount rate [0.0 – 1.0] and a list of objections
# ─────────────────────────────────────────────────────────────

HALO_TITLE_KW   = ["manager","associate","analyst","coordinator","specialist",
                   "assistant","representative","officer","support"]
STALE_THRESHOLD = 5    # years since connection = stale signal
INFLATION_KW    = ["global","chief","head","vp","director","senior","lead",
                   "principal","executive","president"]

def strand_b_loki(c, company_registry):
    pos, co = c["pos"].lower(), c["company"].lower()
    year = c["year"]
    objections = []
    discount_total = 0.0

    # L1a: HALO EFFECT — big brand but generic title
    tier1_hit = any(t in co for t in TIER1_COS)
    generic_title = any(k in pos for k in HALO_TITLE_KW)
    if tier1_hit and generic_title:
        objections.append("HALO: Tier-1 company with generic/mid-level title — score may be inflated by brand prestige, not role")
        discount_total += 0.25

    # L1b: STALE — high score but old connection with no recent signal
    if year and (NOW - year) >= STALE_THRESHOLD:
        age = NOW - year
        stale_discount = min(0.05 * (age - STALE_THRESHOLD + 1), 0.30)
        objections.append(f"STALE: connected {year} ({age}yr ago) — relationship may be cold; no recency signal")
        discount_total += stale_discount

    # L1c: TITLE INFLATION — 3+ seniority keywords in one title
    inflation_hits = [k for k in INFLATION_KW if k in pos]
    if len(inflation_hits) >= 3:
        objections.append(f"INFLATION: {len(inflation_hits)} seniority signals in one title ({inflation_hits[:3]}) — possible title padding")
        discount_total += 0.15

    # L1d: SELF-EMPLOYED NOISE — senior title but self-employed
    if any(k in co for k in ["self-employed","self employed","freelance","independent"]):
        if any(k in pos for k in ["chief","ceo","president","founder","head of"]):
            objections.append("NOISE: C-suite title but self-employed — could indicate gap, pivot, or solo operation with limited leverage")
            discount_total += 0.10

    # L1e: UNKNOWN COMPANY — strong title signals but unrecognised company
    co_words = len(co.split())
    is_unknown = not tier1_hit and company_registry.get(c["company"], 0) <= 1
    high_title = any(k in pos for k in ["chief","founder","ceo","president","global head"])
    if high_title and is_unknown and not any(k in co for k in ["stealth","startup"]):
        objections.append("UNKNOWN CO: strong title at unrecognised company — validate company size/stage before activating")
        discount_total += 0.10

    # L3: KINTSUGI PATHOGEN SCAN — sycophancy detection
    # Flag: if ALL positive signals come from brand prestige alone
    if tier1_hit and not any(k in pos for k in
        ["founder","chief","ceo","cto","vp","director","head of","partner","gp","president"]):
        objections.append("PATHOGEN: BRAND SYCOPHANCY — all positive signals trace to company name alone; role contributes nothing")
        discount_total += 0.30

    # L3b: CONTRADICTION — title claims leadership but TX map finds nothing
    tx_hits = [tx for tx, (kws, _) in TX_MAP.items() if any(k in pos for k in kws)]
    if not tx_hits and any(k in pos for k in ["chief","ceo","president","founder"]):
        objections.append("CONTRADICTION: C-suite title with no transaction-type mapping — title may be honorific or solo operation")
        discount_total += 0.10

    discount_rate = min(discount_total, 0.75)  # cap at 75% — never fully nullify
    c["strand_b_discount"] = round(discount_rate, 3)
    c["strand_b_objections"] = objections
    return discount_rate, objections

# ─────────────────────────────────────────────────────────────
# L2 — BAYESIAN VALIDATION (HCI / PCI / UNDEFINED labelling)
# ─────────────────────────────────────────────────────────────

def l2_bayesian(c, helix_composite):
    hci_factors = []
    pci_factors = []
    undefined_flags = []

    # HCI (Human Coherence Index) — is the profile internally consistent?
    pos, co = c["pos"].lower(), c["company"].lower()
    if c["year"] and c["company"]:
        hci_factors.append(("has year + company", 0.2))
    if len(c["pos"]) > 10:
        hci_factors.append(("non-trivial title", 0.2))
    if c["url"]:
        hci_factors.append(("LinkedIn URL present", 0.2))
    if c["nci"] > 0.5:
        hci_factors.append(("NCI > 0.5", 0.2))
    if c["strand_b_discount"] < 0.2:
        hci_factors.append(("low Loki discount", 0.2))
    hci = round(sum(w for _, w in hci_factors), 2)

    # PCI (Predictive Confidence Index) — how confident are we in the score?
    if helix_composite >= OM_COMPOSITE_MIN:
        pci_factors.append(("composite ≥ OM threshold", 0.3))
    if c["strand_b_discount"] <= OM_LOKI_MAX:
        pci_factors.append(("Loki discount ≤ 35%", 0.3))
    if c["year"] in RECENT:
        pci_factors.append(("recent connection", 0.2))
    if len(c["strand_b_objections"]) == 0:
        pci_factors.append(("zero Loki objections", 0.2))
    pci = round(sum(w for _, w in pci_factors), 2)

    # UNDEFINED flags — things we can't know from CSV data alone
    if not c.get("url"):
        undefined_flags.append("No LinkedIn URL — cannot verify profile")
    if not c["year"]:
        undefined_flags.append("No connection date — temporal layer UNDEFINED")
    if c["nci"] < 0.4:
        undefined_flags.append(f"NCI {c['nci']:.3f} < 0.4 — archetype resonance UNDEFINED")
    if c["company"] in {"", "Unknown", "N/A"}:
        undefined_flags.append("No company data — industry layer UNDEFINED")

    c["hci"] = hci
    c["pci"] = pci
    c["undefined_flags"] = undefined_flags
    return hci, pci, undefined_flags

# ─────────────────────────────────────────────────────────────
# L0 — ACTIVATION FILTER
# ─────────────────────────────────────────────────────────────

def l0_activation(strand_a):
    """Returns (passes: bool, gate_score: int)"""
    return strand_a >= L0_THRESHOLD, strand_a

# ─────────────────────────────────────────────────────────────
# DOUBLE HELIX — COMPOSITE
# ─────────────────────────────────────────────────────────────

def helix_composite(strand_a, strand_b_discount):
    return round(strand_a * (1.0 - strand_b_discount))

# ─────────────────────────────────────────────────────────────
# TRIUNE CLASSIFICATION
# ─────────────────────────────────────────────────────────────

def triune(helix, loki_discount, hci, pci, undefined_flags):
    if helix >= OM_COMPOSITE_MIN and loki_discount <= OM_LOKI_MAX and hci >= 0.6 and pci >= 0.6:
        return "OM"
    if helix >= UNDEF_COMPOSITE_MIN or undefined_flags:
        return "UNDEFINED"
    return "NULL"

# ─────────────────────────────────────────────────────────────
# L4 — NCI META-REVIEW (antithesis + self-grade + What I Don't Know)
# ─────────────────────────────────────────────────────────────

def l4_meta_review(c, helix, status):
    antithesis = []
    what_i_dont_know = []

    if status == "OM":
        antithesis.append(f"This contact scored OM — but the scan only sees title/company/year. Actual relationship warmth, current role accuracy, and receptivity are all UNDEFINED.")
    if c["strand_b_discount"] > 0.0:
        antithesis.append(f"Loki discount {c['strand_b_discount']:.0%}: {c['strand_b_objections'][0] if c['strand_b_objections'] else 'minor signal noise'}")
    if c["year"] and (NOW - c["year"]) > 3:
        what_i_dont_know.append(f"Whether this person is still at {c['company']} — connected {c['year']}, {NOW - c['year']}yr ago")
    if not c["url"]:
        what_i_dont_know.append("Cannot cross-reference LinkedIn profile — URL missing")
    what_i_dont_know.append("Mutual connection depth, relationship history, and current priorities")

    self_grade = "HIGH" if helix >= OM_COMPOSITE_MIN and len(antithesis) <= 1 else \
                 "MEDIUM" if helix >= UNDEF_COMPOSITE_MIN else "LOW"

    c["l4_antithesis"] = antithesis
    c["l4_what_i_dont_know"] = what_i_dont_know
    c["l4_self_grade"] = self_grade
    return antithesis, what_i_dont_know, self_grade

# ─────────────────────────────────────────────────────────────
# L5 — ATOMIC INTEL (True North + ≤3 why bullets)
# ─────────────────────────────────────────────────────────────

def l5_atomic_intel(c, subject_stack_str):
    pos, co = c["pos"], c["company"]
    arch = c["primary_arch"]
    helix = c["helix_composite"]
    tx_hits = [(tx, v) for tx, (kws, v) in TX_MAP.items()
               if any(k in pos.lower() for k in kws)]
    tx_hits.sort(key=lambda x: -x[1])

    # True North: single sentence about the relationship value
    if tx_hits:
        primary_tx = tx_hits[0][0]
        tx_map_text = {
            "INVESTOR": "a capital or deal-structure relationship",
            "PARTNER":  "a distribution or co-build relationship",
            "CUSTOMER": "a direct product or service relationship",
            "MEDIA":    "an amplification or publishing relationship",
            "TALENT":   "a team or capability relationship",
            "ADVISOR":  "a guidance or board relationship",
        }
        true_north = f"{c['name']} represents {tx_map_text.get(primary_tx, 'a high-signal relationship')} — {arch} archetype at {co}."
    else:
        true_north = f"{c['name']} is a {arch} at {co} with strong resonance to the {subject_stack_str} stack."

    # ≤3 why bullets
    why = []
    if c["strand_a_signals"]:
        why.append(c["strand_a_signals"][0].split("→")[0].strip())
    if tx_hits and len(tx_hits) >= 2:
        why.append(f"Multi-mode: {' + '.join(t for t, _ in tx_hits[:2])} — leverageable in {len(tx_hits)} transaction types")
    if c["strand_b_objections"]:
        why.append(f"Loki flag: {c['strand_b_objections'][0][:80]}")
    elif c["year"] in RECENT:
        why.append(f"Recent connection ({c['year']}) — activation window is open now")
    why = why[:3]

    c["l5_true_north"] = true_north
    c["l5_why"] = why
    return true_north, why

# ─────────────────────────────────────────────────────────────
# TOPOLOGY CLUSTERS
# ─────────────────────────────────────────────────────────────

def build_clusters(contacts):
    by_industry = collections.defaultdict(list)
    for c in contacts:
        by_industry[c["industry"]].append(c)
    clusters = {}
    for label, members in by_industry.items():
        recent  = [m for m in members if m.get("year") in RECENT]
        companies = set(m["company"] for m in members if m["company"])
        n = len(members)
        r = len(recent)
        # Triune for cluster — OM requires n≥5, r≥2, documented pattern
        if n >= 5 and r >= 2:
            cl_triune = "OM"
        elif n >= 3:
            cl_triune = "UNDEFINED"
        else:
            cl_triune = "NULL"
        co_counts = collections.Counter(m["company"] for m in members if m["company"])
        clusters[label] = {
            "total": n, "recent": r,
            "unique_companies": len(companies),
            "top_companies": [c for c, _ in co_counts.most_common(5)],
            "triune": cl_triune,
            "avg_helix": round(sum(m.get("helix_composite",0) for m in members) / n, 1) if n else 0,
        }
    return dict(sorted(clusters.items(), key=lambda x: -x[1]["total"]))

# ─────────────────────────────────────────────────────────────
# TEMPORAL STRATIGRAPHY
# ─────────────────────────────────────────────────────────────

def stratigraphy(contacts):
    by_year = collections.Counter(c["year"] for c in contacts if c["year"])
    return dict(sorted(by_year.items()))

# ─────────────────────────────────────────────────────────────
# FULL PIPELINE
# ─────────────────────────────────────────────────────────────

def run_pipeline(contacts, subject_weights, subject_stack_str):
    total = len(contacts)
    print(f"  {total} contacts loaded")

    # Enrich industry + company registry
    for c in contacts:
        c["industry"] = classify_industry(c["company"], c["pos"])
    company_registry = collections.Counter(c["company"] for c in contacts if c["company"])

    print("  L0  activation filter...")
    passed, killed = [], []
    for c in contacts:
        ranked = classify_archetype(c["pos"], c["company"])
        c["archetype_ranked"] = ranked
        c["primary_arch"]     = ranked[0][0]
        c["nci"]              = round(compute_nci(ranked, subject_weights), 4)
        a_score = strand_a_score(c, company_registry, subject_weights)
        passes, _ = l0_activation(a_score)
        if passes:
            passed.append(c)
        else:
            c["triune"] = "NULL"
            c["helix_composite"] = 0
            killed.append(c)
    print(f"       passed: {len(passed)} | killed: {len(killed)}")

    print("  L1  Loki adversarial (Strand B)...")
    for c in passed:
        strand_b_loki(c, company_registry)

    print("  L2  Bayesian validation (HCI/PCI)...")
    for c in passed:
        h = helix_composite(c["strand_a_score"], c["strand_b_discount"])
        c["helix_composite"] = h
        hci, pci, undef = l2_bayesian(c, h)

    print("  L3  Kintsugi pathogen scan (embedded in Strand B)...")
    pathogen_count = sum(1 for c in passed if any("PATHOGEN" in o for o in c.get("strand_b_objections",[])))
    print(f"       pathogens detected: {pathogen_count}")

    print("  L4  NCI meta-review + Triune classification...")
    for c in passed:
        h = c["helix_composite"]
        status = triune(h, c["strand_b_discount"], c["hci"], c["pci"], c["undefined_flags"])
        c["triune"] = status
        l4_meta_review(c, h, status)

    # kill contacts also need helix_composite for consistency
    for c in killed:
        c.update({"strand_a_score":0,"strand_a_signals":[],"strand_b_discount":0,
                  "strand_b_objections":[],"hci":0,"pci":0,"undefined_flags":[],
                  "l4_antithesis":[],"l4_what_i_dont_know":[],"l4_self_grade":"LOW",
                  "l5_true_north":"","l5_why":[]})

    print("  L5  Atomic intel delivery...")
    om_contacts = [c for c in passed if c["triune"] == "OM"]
    for c in om_contacts:
        l5_atomic_intel(c, subject_stack_str)
    for c in passed:
        if c["triune"] != "OM":
            c["l5_true_north"] = ""
            c["l5_why"] = []

    all_contacts = passed + killed
    om_n    = sum(1 for c in all_contacts if c["triune"] == "OM")
    undef_n = sum(1 for c in all_contacts if c["triune"] == "UNDEFINED")
    null_n  = sum(1 for c in all_contacts if c["triune"] == "NULL")
    print(f"  Triune: OM={om_n} | UNDEFINED={undef_n} | NULL={null_n}")

    clusters  = build_clusters(all_contacts)
    strat     = stratigraphy(all_contacts)
    top_om    = sorted(om_contacts, key=lambda x: -x["helix_composite"])

    return all_contacts, clusters, strat, top_om, {"om": om_n, "undefined": undef_n, "null": null_n}

# ─────────────────────────────────────────────────────────────
# RENDER
# ─────────────────────────────────────────────────────────────

def render_md(contacts, clusters, strat, top_om, counts,
              subject_stack_str, csv_path, top_n):

    scan_date = datetime.now().strftime("%Y-%m-%d")
    total = len(contacts)
    lines = []

    # Header
    lines += [
        "# ARCS Full Network Scan",
        f"**Subject stack:** {subject_stack_str}  |  "
        f"**Contacts:** {total:,}  |  **Date:** {scan_date}",
        f"**Source:** `{os.path.basename(csv_path)}`",
        "",
        "---",
        "",
        "## Gauntlet Summary",
        "",
        "| Gate | Result |",
        "|------|--------|",
        f"| L0 Activation | {counts['om'] + counts['undefined']} passed / {counts['null']} killed |",
        f"| L1 Loki objections | {sum(len(c.get('strand_b_objections',[])) for c in contacts)} total across all contacts |",
        f"| L3 Pathogens detected | {sum(1 for c in contacts if any('PATHOGEN' in o for o in c.get('strand_b_objections',[])))} brand-sycophancy flags |",
        f"| Triune OM | {counts['om']} contacts ({counts['om']/total*100:.1f}%) |",
        f"| Triune UNDEFINED | {counts['undefined']} contacts ({counts['undefined']/total*100:.1f}%) |",
        f"| Triune NULL | {counts['null']} contacts ({counts['null']/total*100:.1f}%) |",
        "",
        "---",
        "",
    ]

    # L5 Top contacts
    lines += [
        f"## L5 Atomic Intel — Top {min(top_n, len(top_om))} OM Contacts",
        "*Sorted by Double Helix composite score. Every contact here survived both Strand A (forward) and Strand B (Loki adversarial).*",
        "",
    ]
    for i, c in enumerate(top_om[:top_n], 1):
        name_str = f"[{c['name']}]({c['url']})" if c["url"] else c["name"]
        lines += [
            f"### {i}. {c['name']}",
            f"**{c['pos']}** @ {c['company']}  |  "
            f"Archetype: {c['primary_arch']}  |  "
            f"NCI: {c['nci']:.3f}  |  "
            f"Helix: {c['helix_composite']}  |  "
            f"Loki discount: {c['strand_b_discount']:.0%}  |  "
            f"Connected: {c['year']}",
            "",
        ]
        if c.get("l5_true_north"):
            lines.append(f"**True North:** {c['l5_true_north']}")
            lines.append("")
        if c.get("l5_why"):
            for w in c["l5_why"]:
                lines.append(f"- {w}")
            lines.append("")
        if c.get("strand_b_objections"):
            lines.append(f"*Loki: {c['strand_b_objections'][0]}*")
            lines.append("")
        if c.get("l4_what_i_dont_know"):
            lines.append(f"*Unknown: {c['l4_what_i_dont_know'][0]}*")
            lines.append("")

    lines += ["---", ""]

    # Topology clusters
    lines += [
        "## Topology — Industry Clusters (Triune Logic)",
        "",
        "| Cluster | n | Recent | Avg Helix | Triune |",
        "|---------|---|--------|-----------|--------|",
    ]
    for label, d in sorted(clusters.items(), key=lambda x: -x[1]["total"]):
        badge = {"OM": "🟢 OM", "UNDEFINED": "🟡 UNDEFINED", "NULL": "🔴 NULL"}[d["triune"]]
        lines.append(
            f"| {label} | {d['total']} | {d['recent']} | {d['avg_helix']} | {badge} |"
        )
    lines += ["", "---", ""]

    # Temporal stratigraphy
    lines += ["## Temporal Stratigraphy", "", "| Year | n | Wave |", "|------|---|------|"]
    for yr, n in sorted(strat.items()):
        bar = "█" * min(n // max(1, max(strat.values()) // 30), 30)
        lines.append(f"| {yr} | {n} | {bar} |")
    lines += ["", "---", ""]

    # Archetype distribution
    arch_counts = collections.Counter(c["primary_arch"] for c in contacts)
    arch_nci    = collections.defaultdict(list)
    for c in contacts:
        arch_nci[c["primary_arch"]].append(c["nci"])
    lines += [
        "## Archetype Distribution",
        "",
        "| Archetype | n | % | Avg NCI | OM count |",
        "|-----------|---|---|---------|----------|",
    ]
    for arch in ARCH_ORDER:
        n = arch_counts.get(arch, 0)
        avg_nci = round(sum(arch_nci[arch]) / len(arch_nci[arch]), 3) if arch_nci[arch] else 0
        om_n = sum(1 for c in contacts if c["primary_arch"] == arch and c["triune"] == "OM")
        lines.append(f"| {arch} | {n} | {n/total*100:.1f}% | {avg_nci} | {om_n} |")
    lines += ["", "---", ""]

    # UNDEFINED zone warnings
    undef_contacts = [c for c in contacts if c["triune"] == "UNDEFINED" and c.get("undefined_flags")]
    if undef_contacts:
        lines += [
            "## UNDEFINED Zone — Insufficient Data Flags",
            "*These contacts have signal but missing data prevents OM classification. Do not treat as OM.*",
            "",
        ]
        for c in sorted(undef_contacts, key=lambda x: -x.get("helix_composite", 0))[:20]:
            flags = " | ".join(c["undefined_flags"][:2])
            lines.append(f"- **{c['name']}** ({c['pos']} @ {c['company']}, {c['year']}) → {flags}")
        lines += ["", "---", ""]

    lines += [
        "## Methodology",
        "",
        "This scan applies the ARCS L0–L5 pipeline to a LinkedIn connections export.",
        "",
        "**Double Helix Protocol:**",
        "- Strand A (forward): archetype NCI resonance + recency + seniority + TX value + network position",
        "- Strand B (reverse): Loki adversarial objections (halo effect, staleness, title inflation, sycophancy)",
        "- Helix composite = Strand A × (1 − Strand B discount rate)",
        "- OM requires: composite ≥ 160, Loki discount ≤ 35%, HCI ≥ 0.6, PCI ≥ 0.6",
        "",
        "**Triune Logic (v8.5 Diamond):**",
        "- OM: validated, composite threshold met, methodology documented",
        "- UNDEFINED: insufficient data — labelled explicitly, never treated as OM",
        "- NULL: failed L0 activation or Loki killed the signal",
        "",
        f"Full source: https://github.com/flashesofbrilliance/arcs-v9/blob/main/scripts/network_scan_full.py",
    ]

    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

ARCHETYPE_NAMES = [a[0] for a in ARCHETYPES]

def parse_subject_stack(stack_str):
    parts = [s.strip() for s in re.split(r"[,→>]", stack_str)]
    weights = [1.0, 0.6, 0.3]
    result = []
    for i, part in enumerate(parts[:3]):
        # fuzzy match
        match = next((a for a in ARCHETYPE_NAMES if a.lower().startswith(part.lower()[:5])), None)
        if match:
            result.append((match, weights[i]))
    if not result:
        result = [("Builder", 1.0), ("Navigator", 0.6), ("Chartist", 0.3)]
    return result

def main():
    parser = argparse.ArgumentParser(
        description="ARCS Full Network Scan — runs the complete L0–L5 gauntlet on your LinkedIn export",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 network_scan_full.py Connections.csv
  python3 network_scan_full.py Connections.csv --subject "Builder,Navigator,Chartist"
  python3 network_scan_full.py Connections.csv --top 50 --out ./my_scan
  python3 network_scan_full.py Connections.csv --subject "Mediator,Navigator,Illuminator"

Archetype options (pick 1–3, in order of dominance):
  Builder · Navigator · Illuminator · Instrumentor · Mediator · Orienter · Chartist · Focused Executor
        """
    )
    parser.add_argument("csv", help="Path to LinkedIn Connections.csv")
    parser.add_argument("--subject", default="Builder,Navigator,Chartist",
                        help='Your archetype stack, e.g. "Builder,Navigator,Chartist" (default)')
    parser.add_argument("--top", type=int, default=30,
                        help="How many top OM contacts to show in the report (default: 30)")
    parser.add_argument("--out", default=None,
                        help="Output directory (default: next to CSV file)")
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"Error: file not found: {args.csv}")
        sys.exit(1)

    subject_weights  = parse_subject_stack(args.subject)
    subject_stack_str = " → ".join(a for a, _ in subject_weights)

    if args.out:
        out_dir = args.out
    else:
        today   = datetime.today().strftime("%Y-%m-%d")
        _root   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out_dir = os.path.join(_root, "exports", "network", today)
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(args.csv))[0]
    out_md   = os.path.join(out_dir, f"{base}_arcs_scan.md")
    out_json = os.path.join(out_dir, f"{base}_arcs_scan.json")

    print(f"\nARCS Network Scan — Full Gauntlet + Double Helix")
    print(f"  CSV:    {args.csv}")
    print(f"  Stack:  {subject_stack_str}")
    print(f"  Output: {out_dir}")
    print()

    contacts = load_csv(args.csv)
    all_contacts, clusters, strat, top_om, counts = run_pipeline(
        contacts, subject_weights, subject_stack_str
    )

    md = render_md(all_contacts, clusters, strat, top_om, counts,
                   subject_stack_str, args.csv, args.top)
    with open(out_md, "w") as f:
        f.write(md)

    json_out = {
        "meta": {
            "scan_date": datetime.now().strftime("%Y-%m-%d"),
            "csv": os.path.basename(args.csv),
            "total": len(all_contacts),
            "subject_stack": subject_stack_str,
            "triune_counts": counts,
        },
        "top_om": [
            {k: v for k, v in c.items()
             if k in ["name","pos","company","url","year","primary_arch","nci",
                      "helix_composite","strand_b_discount","triune",
                      "l5_true_north","l5_why","strand_b_objections",
                      "undefined_flags","l4_self_grade"]}
            for c in top_om[:args.top]
        ],
        "clusters": clusters,
        "stratigraphy": strat,
    }
    with open(out_json, "w") as f:
        json.dump(json_out, f, indent=2)

    print(f"\n  Wrote: {out_md}")
    print(f"  Wrote: {out_json}")
    print(f"\n── TOP 20 OM CONTACTS (Double Helix) ───────────────────────\n")
    for i, c in enumerate(top_om[:20], 1):
        disc = f"Loki:{c['strand_b_discount']:.0%}"
        print(f"  {i:2d}. [{c['helix_composite']:3d}pts {disc}] {c['name'][:28]:28s} "
              f"{c['primary_arch'][:12]:12s} @ {c['company'][:28]}")
        if c.get("l5_true_north"):
            print(f"      → {c['l5_true_north'][:85]}")
    print()

if __name__ == "__main__":
    main()
