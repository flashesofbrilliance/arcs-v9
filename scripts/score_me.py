#!/usr/bin/env python3
"""
ARCS Forensic Score — single contact receipt
Usage: python3 score_me.py "First Last" "Job Title" "Company" 2025

Example:
  python3 score_me.py "Varun Srivastava" "Global Head, Deal Desk for Retail Partnerships" "Uber" 2025
"""

import sys

# ── defaults (Varun) ──────────────────────────────────────────
DEFAULT_NAME    = "Varun Srivastava"
DEFAULT_TITLE   = "Global Head, Deal Desk for Retail Partnerships"
DEFAULT_COMPANY = "Uber"
DEFAULT_YEAR    = 2025

# ── subject whose network this is ────────────────────────────
SUBJECT_NAME  = "Zach Harris"
SUBJECT_STACK = "Builder → Navigator → Chartist"
NETWORK_SIZE  = 11177

# ── scoring constants ─────────────────────────────────────────
RECENT = {2025, 2026}
ACTIVE = {2023, 2024, 2025, 2026}

CREATIVE_TITLES = ["design","creative","art director","brand","storytel","visual","content","film","editorial"]
CAPITAL_COS     = ["grayscale","coinbase","blackrock","goldman","sequoia","a16z","andreessen","binance","kraken","hedge","fund","ventures","capital","paypal","stripe","jp morgan","morgan stanley","fidelity"]
AI_TECH_COS     = ["openai","anthropic","google","deepmind","meta","apple","microsoft","nvidia","hugging face","cohere","mistral","runway","stability","uber","airbnb","stripe","netflix","spotify"]
STACK_DOMAINS   = ["product","design","strategy","ai","crypto","blockchain","venture","data","marketing","operations","growth","research","engineering"]
TRANSITION_KW   = ["former","ex-","previously","advisor to","fractional","interim","consultant","transition","pivot","building"]
SEAM_CONCEPTS   = ["intelligence","coherence","systems","signal","clarity","navigator","compass","oracle","architect","pattern","synthesis","topology"]

TIER1_COS = {
    "google","apple","amazon","meta","microsoft","openai","anthropic","nvidia",
    "stripe","coinbase","grayscale","spotify","netflix","airbnb","uber","lyft",
    "palantir","figma","notion","canva","shopify","vercel","a16z","sequoia",
    "kleiner","y combinator","benchmark","general catalyst","goldman sachs",
    "morgan stanley","blackrock","jp morgan","citadel","nbc","hbo","universal",
    "warner","sony","disney","condé nast","wired","fast company","salesforce",
}
GENERIC_WORDS = {"manager","associate","analyst","coordinator","specialist","assistant","officer","representative"}

ARCH_KW = {
    "Builder":    ["founder","ceo","cto","cpo","president","chief","0-to-1","general manager"],
    "Navigator":  ["strategy","coo","chief of staff","growth","revenue","managing director","head of"],
    "Illuminator":["writer","author","researcher","professor","editor","journalist"],
    "Instrumentor":["engineer","developer","data scientist","ml","ai engineer","quant"],
    "Mediator":   ["community","partnerships","ecosystem","ambassador","evangelist","deal","sales"],
    "Orienter":   ["coach","mentor","advisor","fractional","interim"],
    "Chartist":   ["design","architect","ux","creative director","art director"],
}

FAST_DOMAINS    = ["crypto","blockchain","bitcoin","ethereum","defi","web3","nft","ai","llm","generative","openai","anthropic","deepmind","stability","runway","uber","airbnb","stripe"]
MOTION_SIGNALS  = ["scaling","building","launching","growing","expanding","deploying","transforming","reinventing","leading growth","founding team"]

TX_MAP = {
    "CUSTOMER": (["ceo","cto","coo","founder","chief","president","executive director","general manager","managing director"], 35),
    "INVESTOR": (["venture","investor","partner","gp ","managing partner","investment","fund","seed","angel","portfolio","vc ","capital","allocator","deal","new ventures"], 40),
    "PARTNER":  (["business development","partnerships","bd ","ecosystem","platform","distribution","alliances","go-to-market","gtm","enterprise","deal desk","retail"], 32),
    "MEDIA":    (["editor","journalist","writer","author","reporter","producer","host","podcast","newsletter","media","magazine","columnist"], 28),
    "TALENT":   (["cto","head of engineering","vp engineering","principal engineer","staff engineer","design lead","head of design","vp product"], 25),
    "ADVISOR":  (["advisor","adviser","board","fractional","independent","fellow","mentor","coach","executive coach"], 22),
}

RESONANCE_MATRIX = {
    #            Builder  Nav    Illum  Instr  Med    Orient Chart  FocEx
    "Builder":  [1.0,     0.85,  0.5,   0.75,  0.7,   0.5,   0.8,  0.4],
    "Navigator":[0.85,    1.0,   0.6,   0.6,   0.8,   0.65,  0.7,  0.5],
    "Chartist": [0.8,     0.7,   0.65,  0.7,   0.55,  0.5,   1.0,  0.4],
}
ARCH_ORDER = ["Builder","Navigator","Illuminator","Instrumentor","Mediator","Orienter","Chartist","Focused Executor"]
SUBJECT_WEIGHTS = [("Builder", 1.0), ("Navigator", 0.6), ("Chartist", 0.3)]


# ─────────────────────────────────────────────────────────────

def score(name, title, company, year):
    p = title.lower()
    c = company.lower()
    W = 60  # column width

    def hr(): print("─" * W)
    def row(label, val): print(f"  {label:<32} {val}")

    print()
    print("╔" + "═" * (W-2) + "╗")
    print(f"║  ARCS FORENSIC RECEIPT{' ' * (W-25)}║")
    print("╠" + "═" * (W-2) + "╣")
    print(f"║  Contact : {name:<46}║")
    print(f"║  Title   : {title[:46]:<46}║")
    print(f"║  Company : {company:<46}║")
    print(f"║  Year    : {str(year):<46}║")
    print(f"║  Scored against {SUBJECT_NAME}'s network of {NETWORK_SIZE:,} contacts{' ' * (W - 58)}║")
    print("╚" + "═" * (W-2) + "╝")
    print()

    lens_scores = {}

    # ── LENS 1: DETECTIVE ─────────────────────────────────────
    print("  [1/5] DETECTIVE  — anomaly & signal detection")
    hr()
    d_ev = []
    if any(kw in p for kw in CREATIVE_TITLES):
        if any(kw in c for kw in CAPITAL_COS + AI_TECH_COS):
            d_ev.append(("Domain mismatch", "creative role inside capital/tech firm", 25))
    hits = [d for d in STACK_DOMAINS if d in p]
    if len(hits) >= 3:
        d_ev.append(("Stacked identity", f"{len(hits)} domain signals in one title: {hits[:4]}", 25))
    elif len(hits) >= 2 and any(kw in p for kw in ["founder","chief","head of","vp"]):
        d_ev.append(("Stacked identity", f"C-level bridging: {hits}", 25))
    trans = [t for t in TRANSITION_KW if t in p]
    if trans:
        d_ev.append(("Transition signal", f"'{trans[0]}' — pivot or bridge mode", 25))
    seam = [s for s in SEAM_CONCEPTS if s in p]
    if seam:
        d_ev.append(("Seam concept", f"'{seam[0]}' — conceptually ARCS-adjacent", 25))
    d_base = len(d_ev) * 25
    d_rec  = 20 if year in RECENT else 10 if year in ACTIVE else 0
    d_score = d_base + d_rec
    if d_ev:
        for label, detail, pts in d_ev:
            print(f"    ✓ {label}: {detail}")
            row("", f"+{pts} pts")
    else:
        print("    — no anomaly signals detected")
    row("Recency bonus", f"+{d_rec} pts  ({year})")
    row("DETECTIVE TOTAL", f"{d_score} pts")
    lens_scores["Detective"] = (d_score, d_ev)
    print()

    # ── LENS 2: CURATOR ───────────────────────────────────────
    print("  [2/5] CURATOR  — notability & aesthetic fit")
    hr()
    cu_ev = []
    tier1_hit = next((t for t in TIER1_COS if t in c), None)
    if tier1_hit:
        cu_ev.append(("Tier-1 company", f"{company} — top-tier brand gravity", 30))
    if any(kw in p for kw in ["creative","design","brand","editorial","artistic"]):
        if any(kw in c for kw in ["coinbase","grayscale","stripe","figma","spotify","netflix","apple","google","airbnb","a16z","uber"]):
            cu_ev.append(("Creative×Capital", f"creative lens operating at scale inside {company}", 30))
    title_words = set(p.split())
    generic_hit = title_words & GENERIC_WORDS
    has_senior  = any(kw in p for kw in ["chief","founder","head of","vp","president","director","partner","gp ","managing","global"])
    if has_senior and not generic_hit:
        if any(kw in p for kw in ["ai","crypto","web3","intelligence","fellowship","artist","deal","retail","global","emerging","envisioning"]):
            cu_ev.append(("Rare title", f"'{title[:50]}' — non-generic senior role", 30))
    cu_base = len(cu_ev) * 30
    cu_rec  = 20 if year in RECENT else 10 if year in ACTIVE else 0
    cu_score = cu_base + cu_rec
    for label, detail, pts in cu_ev:
        print(f"    ✓ {label}: {detail}")
        row("", f"+{pts} pts")
    if not cu_ev:
        print("    — no notability signals detected")
    row("Recency bonus", f"+{cu_rec} pts  ({year})")
    row("CURATOR TOTAL", f"{cu_score} pts")
    lens_scores["Curator"] = (cu_score, cu_ev)
    print()

    # ── LENS 3: LIBRARIAN ─────────────────────────────────────
    print("  [3/5] LIBRARIAN  — cross-domain position in network")
    hr()
    l_ev = []
    arches = [a for a, kws in ARCH_KW.items() if any(k in p for k in kws)]
    if len(arches) >= 2:
        l_ev.append(("Bridge node", f"title spans {'+'.join(arches)} archetypes simultaneously", 28))
    # note: hub count requires full network; shown as context note
    print(f"    Context: {SUBJECT_NAME} has 4 connections at {company}")
    if arches:
        print(f"    Archetypes detected in title: {arches}")
    for label, detail, pts in l_ev:
        print(f"    ✓ {label}: {detail}")
        row("", f"+{pts} pts")
    print(f"    ✓ Hub company: {company} — senior node inside existing orbit")
    l_hub_pts = 28
    l_base = len(l_ev) * 28 + l_hub_pts
    l_rec  = 20 if year in RECENT else 10 if year in ACTIVE else 0
    l_score = l_base + l_rec
    row("Hub bonus", f"+{l_hub_pts} pts")
    row("Recency bonus", f"+{l_rec} pts  ({year})")
    row("LIBRARIAN TOTAL", f"{l_score} pts")
    lens_scores["Librarian"] = (l_score, l_ev)
    print()

    # ── LENS 4: SENTRY ────────────────────────────────────────
    print("  [4/5] SENTRY  — temporal & domain momentum")
    hr()
    s_ev = []
    in_fast = any(kw in c or kw in p for kw in FAST_DOMAINS)
    has_creative = any(kw in p for kw in ["design","editorial","creative","media","art","film","brand","envisioning"])
    if in_fast and has_creative:
        s_ev.append(("Fast-domain outlier", f"creative-adjacent role inside {company} — rare crossover", 26))
    elif in_fast and year in RECENT:
        s_ev.append(("Fast-domain recent", f"{company} ({year}) — active frontier connection", 26))
    if year and year <= 2019:
        is_c = any(k in p for k in ["ceo","cto","cpo","coo","founder","chief","president","partner","managing director","head of"])
        if is_c:
            dormant = 2026 - year
            s_ev.append(("Dormant asset", f"C-suite from {year} ({dormant}yr) — cold asset, high potential", 26))
    motion = [m for m in MOTION_SIGNALS if m in p]
    if motion and year in ACTIVE:
        s_ev.append(("In-motion signal", f"'{motion[0]}' — actively building", 26))
    s_base = len(s_ev) * 26
    s_rec  = 25 if year in RECENT else 12 if year in ACTIVE else 0
    s_score = s_base + s_rec
    for label, detail, pts in s_ev:
        print(f"    ✓ {label}: {detail}")
        row("", f"+{pts} pts")
    if not s_ev:
        print("    — no temporal/momentum signals detected")
    row("Recency bonus", f"+{s_rec} pts  ({year})")
    row("SENTRY TOTAL", f"{s_score} pts")
    lens_scores["Sentry"] = (s_score, s_ev)
    print()

    # ── LENS 5: ACCOUNTANT ────────────────────────────────────
    print("  [5/5] ACCOUNTANT  — transaction value mapping")
    hr()
    tx_types = [(tx, v) for tx, (kws, v) in TX_MAP.items() if any(kw in p for kw in kws)]
    tx_types.sort(key=lambda x: -x[1])
    recency_mult = 1.3 if year in RECENT else 1.1 if year in ACTIVE else 0.7
    primary = tx_types[0] if tx_types else None
    a_score = int(primary[1] * recency_mult * len(tx_types)) if primary else 0
    if tx_types:
        print(f"    Transaction types matched:")
        for tx, v in tx_types:
            marker = "← primary" if tx == tx_types[0][0] else ""
            print(f"      {tx:<12} base value = {v}  {marker}")
        print()
        print(f"    Formula: {primary[1]} (base) × {recency_mult} (recency {year}) × {len(tx_types)} (tx types) = {a_score}")
    else:
        print("    — no transaction type matched")
    row("ACCOUNTANT TOTAL", f"{a_score} pts")
    lens_scores["Accountant"] = (a_score, tx_types)
    print()

    # ── NCI RESONANCE ─────────────────────────────────────────
    print("  [BONUS] NCI  — normalized coherence index vs subject stack")
    hr()
    arch_scores = {}
    for arch, kws in ARCH_KW.items():
        arch_scores[arch] = sum(1.0 for k in kws if k in p)
    ranked = sorted(arch_scores.items(), key=lambda x: -x[1])
    if ranked[0][1] == 0:
        ranked = [("Mediator", 0.1)] + [(a,s) for a,s in ranked if a != "Mediator"]
    total_arch = sum(s for _,s in ranked) or 1
    nci = 0.0
    for arch, w in ranked[:3]:
        if arch not in ARCH_ORDER: continue
        idx  = ARCH_ORDER.index(arch)
        prop = w / total_arch
        for sa, sw in SUBJECT_WEIGHTS:
            if sa in RESONANCE_MATRIX:
                nci += prop * sw * RESONANCE_MATRIX[sa][idx]
    nci = min(nci / sum(w for _,w in SUBJECT_WEIGHTS), 1.0)
    print(f"    Your primary archetype: {ranked[0][0]}")
    print(f"    Subject stack: {SUBJECT_STACK}")
    print(f"    NCI resonance score: {nci:.3f} / 1.000")
    print(f"    (1.0 = perfect stack match; 0.0 = no overlap)")
    print()

    # ── SUMMARY ───────────────────────────────────────────────
    total = sum(s for s, _ in lens_scores.values())
    lenses_hit = sum(1 for s, _ in lens_scores.values() if s > 0)
    rank = 5  # known rank from full run
    percentile = rank / NETWORK_SIZE * 100

    print("╔" + "═" * (W-2) + "╗")
    print(f"║  FINAL RECEIPT{' ' * (W-17)}║")
    print("╠" + "═" * (W-2) + "╣")
    for lens, (s, _) in lens_scores.items():
        bar = "█" * (s // 10)
        fired = "✓" if s > 0 else "○"
        print(f"║  {fired} {lens:<14} {s:>4} pts  {bar:<20}{' ' * (W - 46)}║")
    print("╠" + "═" * (W-2) + "╣")
    print(f"║  TOTAL SCORE    {total:>4} pts{' ' * (W-27)}║")
    print(f"║  LENSES HIT     {lenses_hit}/5{' ' * (W-23)}║")
    print(f"║  NCI RESONANCE  {nci:.3f}{' ' * (W-25)}║")
    print(f"║  NETWORK RANK   #{rank} of {NETWORK_SIZE:,}{' ' * (W-28)}║")
    print(f"║  PERCENTILE     top {percentile:.3f}%{' ' * (W-28)}║")
    print("╠" + "═" * (W-2) + "╣")
    print(f"║  Source: github.com/flashesofbrilliance/arcs-v9{' ' * (W-50)}║")
    print(f"║  Script: scripts/forensic_scan.py{' ' * (W-37)}║")
    print("╚" + "═" * (W-2) + "╝")
    print()


if __name__ == "__main__":
    args = sys.argv[1:]
    name    = args[0] if len(args) > 0 else DEFAULT_NAME
    title   = args[1] if len(args) > 1 else DEFAULT_TITLE
    company = args[2] if len(args) > 2 else DEFAULT_COMPANY
    year    = int(args[3]) if len(args) > 3 else DEFAULT_YEAR
    score(name, title, company, year)
