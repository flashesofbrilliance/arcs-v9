#!/usr/bin/env python3
"""
ARCS v9 Deep Forensic Scan
Five detection lenses applied to the full 11,177-contact network.

DETECTIVE  — finds anomalies: title/company mismatch, stacked identity, transition signals
CURATOR    — selects on notability + aesthetic fit + creative-capital alignment
LIBRARIAN  — indexes cross-domain bridge nodes, multi-cluster connectors
SENTRY     — flags temporal gates, dormant high-value, fast-moving domain outliers
ACCOUNTANT — maps value transactions: customer / investor / partner / media / talent / advisor

Final verdict = contacts surfacing in 3+ lenses. These are the write-lock activations.
"""

import csv, json, re, os, collections, math
from datetime import datetime

CSV_PATH = "/Users/zharris/Downloads/Basic_LinkedInDataExport_05-20-2026.zip/Connections.csv"
OUT_DIR  = os.path.join(os.path.dirname(__file__), "../exports")
OUT_MD   = os.path.join(os.path.dirname(__file__), "../forensic_scan.md")
OUT_JSON = os.path.join(os.path.dirname(__file__), "../forensic_scan.json")

RECENT = {2025, 2026}
ACTIVE = {2023, 2024, 2025, 2026}

# ─────────────────────────────────────────────────────────────
# DATA LOAD
# ─────────────────────────────────────────────────────────────

def parse_year(s):
    for p in (s or "").strip().split():
        if p.isdigit() and len(p) == 4:
            return int(p)
    return None

def load(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        lines = f.readlines()
    start = next(i for i, l in enumerate(lines) if "First Name" in l)
    out = []
    for row in csv.DictReader(lines[start:]):
        first   = (row.get("First Name") or "").strip()
        last    = (row.get("Last Name") or "").strip()
        company = (row.get("Company") or "").strip()
        pos     = (row.get("Position") or "").strip()
        url     = (row.get("URL") or "").strip()
        year    = parse_year(row.get("Connected On") or "")
        out.append({
            "name":    f"{first} {last}".strip(),
            "first":   first, "last": last,
            "company": company, "pos": pos,
            "url":     url, "year": year,
            "slug":    f"{first}|{last}|{company}",
        })
    return out

# ─────────────────────────────────────────────────────────────
# LENS 1: DETECTIVE
# Looks for:
#   A. Domain mismatch: creative/design title at finance/crypto company
#   B. Stacked identity: title contains 3+ domain keywords
#   C. Transition signals: "former", "ex-", "advisor to", pivot language
#   D. Seam people: title references ARCS-adjacent concepts (intelligence, systems, coherence)
# ─────────────────────────────────────────────────────────────

CREATIVE_TITLES  = ["design","creative","art director","brand","storytel","visual","content","film","editorial"]
CAPITAL_COS      = ["grayscale","coinbase","blackrock","goldman","sequoia","a16z","andreessen",
                    "binance","kraken","paradigm","multicoin","pantera","hedge","fund","ventures",
                    "capital","paypal","stripe","jp morgan","morgan stanley","fidelity"]
AI_TECH_COS      = ["openai","anthropic","google","deepmind","meta","apple","microsoft",
                    "nvidia","hugging face","cohere","mistral","runway","stability"]
STACK_DOMAINS    = ["product","design","strategy","ai","crypto","blockchain","venture",
                    "data","marketing","operations","growth","research","engineering"]
TRANSITION_WORDS = ["former","ex-","previously","advisor to","fractional","interim",
                    "consultant","exploring","transition","pivot","building"]
SEAM_CONCEPTS    = ["intelligence","coherence","systems","signal","clarity","navigator",
                    "compass","oracle","architect of","pattern","synthesis","topology"]

def score_detective(c):
    pos = c["pos"].lower()
    co  = c["company"].lower()
    evidence = []

    # A. domain mismatch: creative title at capital/tech company
    if any(kw in pos for kw in CREATIVE_TITLES):
        if any(kw in co for kw in CAPITAL_COS + AI_TECH_COS):
            evidence.append(f"MISMATCH: creative title @ capital/tech firm ({c['company']})")

    # B. stacked identity (3+ distinct domain signals in one title)
    hits = [d for d in STACK_DOMAINS if d in pos]
    if len(hits) >= 3:
        evidence.append(f"STACKED: {len(hits)} domain signals in title → {hits[:4]}")
    elif len(hits) >= 2 and any(kw in pos for kw in ["founder","chief","head of","vp"]):
        evidence.append(f"STACKED: C-level with {hits} span")

    # C. transition signals
    trans = [t for t in TRANSITION_WORDS if t in pos.lower() or t in c["name"].lower()]
    if trans:
        evidence.append(f"TRANSITION: {trans[0]} signal — pivot or bridge person")

    # D. seam concepts
    seam = [s for s in SEAM_CONCEPTS if s in pos.lower()]
    if seam:
        evidence.append(f"SEAM: '{seam[0]}' in title — conceptually adjacent to ARCS")

    score = len(evidence) * 25 + (20 if c["year"] in RECENT else 10 if c["year"] in ACTIVE else 0)
    return score, evidence

# ─────────────────────────────────────────────────────────────
# LENS 2: CURATOR
# Selects on:
#   A. Notable company prestige (top-tier brand recognition)
#   B. Creative-capital alignment (design/media/creative AT scale)
#   C. Title rarity — unusual, non-generic, memorable role
# ─────────────────────────────────────────────────────────────

TIER1_COS = {
    "google","apple","amazon","meta","microsoft","openai","anthropic","nvidia",
    "stripe","coinbase","grayscale","spotify","netflix","airbnb","uber","lyft",
    "palantir","figma","notion","canva","shopify","vercel","linear",
    "a16z","sequoia","kleiner","y combinator","benchmark","general catalyst",
    "goldman sachs","morgan stanley","blackrock","jp morgan","citadel",
    "nbc","hbo","universal","warner","sony","disney","condé nast","vogue",
    "time","the atlantic","new york times","wired","fast company",
}

GENERIC_WORDS = {"manager","associate","analyst","coordinator","specialist",
                 "assistant","officer","representative","consultant","advisor"}

def score_curator(c):
    pos = c["pos"].lower()
    co  = c["company"].lower()
    evidence = []

    # A. tier-1 company
    co_words = set(re.sub(r"[^a-z0-9 ]", "", co).split())
    tier1_hit = next((t for t in TIER1_COS if t in co), None)
    if tier1_hit:
        evidence.append(f"TIER1: {c['company']}")

    # B. creative-capital alignment: design/media/creative at notable scale
    if any(kw in pos for kw in ["creative","design","brand","editorial","artistic"]):
        if any(kw in co for kw in ["coinbase","grayscale","stripe","figma","spotify","netflix",
                                    "apple","google","airbnb","a16z"]):
            evidence.append(f"CREATIVE×CAPITAL: {c['pos']} @ {c['company']}")

    # C. title rarity: role that is non-generic and senior
    title_words = set(pos.split())
    generic_hit = title_words & GENERIC_WORDS
    has_senior  = any(kw in pos for kw in ["chief","founder","head of","vp","president","director","partner","gp ","managing"])
    if has_senior and not generic_hit:
        # extra credit for unusual combos
        if any(kw in pos for kw in ["ai","crypto","web3","intelligence","fellowship","artist"]):
            evidence.append(f"RARE TITLE: '{c['pos'][:60]}' — unusual senior role")

    score = len(evidence) * 30 + (20 if c["year"] in RECENT else 10 if c["year"] in ACTIVE else 0)
    return score, evidence

# ─────────────────────────────────────────────────────────────
# LENS 3: LIBRARIAN
# Cross-references:
#   A. Multi-cluster people: title spans 2+ archetype domains
#   B. Hubs: same company appears 3+ times — flag the most senior
#   C. Long-arc connections: connected early (pre-2014) AND still notable
# ─────────────────────────────────────────────────────────────

ARCH_KW = {
    "Builder":   ["founder","ceo","cto","cpo","president","chief","0-to-1"],
    "Navigator": ["strategy","coo","chief of staff","growth","revenue","managing director"],
    "Illuminator":["writer","author","researcher","professor","editor","journalist"],
    "Instrumentor":["engineer","developer","data scientist","ml","ai engineer","quant"],
    "Mediator":  ["community","partnerships","ecosystem","ambassador","evangelist"],
    "Orienter":  ["coach","mentor","advisor","fractional","interim"],
    "Chartist":  ["design","architect","ux","creative director","art director"],
}

def title_archetypes(pos):
    p = pos.lower()
    return [a for a, kws in ARCH_KW.items() if any(k in p for k in kws)]

def score_librarian(c, company_registry):
    pos = c["pos"].lower()
    evidence = []

    # A. multi-cluster: title spans 2+ archetypes
    arches = title_archetypes(c["pos"])
    if len(arches) >= 2:
        evidence.append(f"BRIDGE: {'+'.join(arches)} — cross-cluster node")

    # B. hub company: senior person at a company with 3+ of your connections
    co_count = company_registry.get(c["company"], 0)
    if co_count >= 3:
        is_senior = any(k in pos for k in ["founder","ceo","cto","cpo","president","chief","vp","director","partner","head of"])
        if is_senior:
            evidence.append(f"HUB: {c['company']} has {co_count} connections — you're inside this orbit")

    # C. long-arc: early connection who is still notable
    if c["year"] and c["year"] <= 2013:
        is_notable = (title_archetypes(c["pos"]) or
                      any(k in c["pos"].lower() for k in ["founder","ceo","chief","director","vp","head of"]))
        if is_notable:
            evidence.append(f"LONG-ARC: connected {c['year']} — this is a root node")

    score = len(evidence) * 28 + (20 if c["year"] in RECENT else 10 if c["year"] in ACTIVE else 0)
    return score, evidence

# ─────────────────────────────────────────────────────────────
# LENS 4: SENTRY
# Watches for:
#   A. Fast-domain outliers: non-crypto/AI person who is at crypto/AI company
#   B. Dormant high-value: C-suite connected pre-2020, never activated
#   C. Recent solo signals: connected 2025-2026, no cluster peers (rare archetype)
#   D. Company-in-motion signals: title suggests company is in transition/growth
# ─────────────────────────────────────────────────────────────

FAST_DOMAINS = ["crypto","blockchain","bitcoin","ethereum","defi","web3","nft","ai","llm",
                "generative","openai","anthropic","deepmind","stability","runway"]

MOTION_SIGNALS = ["scaling","building","launching","growing","expanding","deploying",
                  "transforming","reinventing","leading growth","early","founding team"]

def score_sentry(c, arch_year_registry):
    pos = c["pos"].lower()
    co  = c["company"].lower()
    evidence = []

    # A. fast-domain outlier: unexpected title in hot domain
    in_fast = any(kw in co or kw in pos for kw in FAST_DOMAINS)
    has_creative_title = any(kw in pos for kw in ["design","editorial","creative","media","art","film","brand"])
    if in_fast and has_creative_title:
        evidence.append(f"FAST-DOMAIN OUTLIER: creative lens in {c['company']} — rare crossover")
    elif in_fast and c["year"] in RECENT:
        evidence.append(f"FAST-DOMAIN RECENT: {c['company']} connected {c['year']}")

    # B. dormant high-value: C-suite from before 2020
    if c["year"] and c["year"] <= 2019:
        is_c_suite = any(k in pos for k in ["ceo","cto","cpo","coo","founder","chief","president","partner","managing director"])
        if is_c_suite:
            dormant_years = 2026 - c["year"]
            evidence.append(f"DORMANT: C-suite connected {c['year']} ({dormant_years}yr ago) — cold asset worth warming")

    # C. motion signals in title
    motion = [m for m in MOTION_SIGNALS if m in pos]
    if motion and c["year"] in ACTIVE:
        evidence.append(f"IN-MOTION: '{motion[0]}' in title — active builder")

    score = len(evidence) * 26 + (25 if c["year"] in RECENT else 12 if c["year"] in ACTIVE else 0)
    return score, evidence

# ─────────────────────────────────────────────────────────────
# LENS 5: ACCOUNTANT
# Maps each contact to a transaction type and values the ledger:
#   CUSTOMER    — could use ARCS; decision-maker under pressure
#   INVESTOR    — could fund ARCS or adjacent work
#   PARTNER     — could distribute, integrate, or co-build
#   MEDIA       — could cover, amplify, or publish
#   TALENT      — could join or advise
#   ADVISOR     — could provide domain-specific guidance
# ─────────────────────────────────────────────────────────────

TX_MAP = {
    "CUSTOMER":  (["ceo","cto","coo","founder","chief","president","decision","executive director",
                   "general manager","managing director"], 35),
    "INVESTOR":  (["venture","investor","partner","gp ","managing partner","investment","fund","seed",
                   "angel","portfolio","vc ","capital","allocator"], 40),
    "PARTNER":   (["business development","partnerships","bd ","ecosystem","platform","distribution",
                   "alliances","go-to-market","gtm","enterprise"], 32),
    "MEDIA":     (["editor","journalist","writer","author","reporter","producer","host","podcast",
                   "newsletter","media","magazine","columnist","correspondent"], 28),
    "TALENT":    (["cto","head of engineering","vp engineering","principal engineer","staff engineer",
                   "design lead","head of design","vp product"], 25),
    "ADVISOR":   (["advisor","adviser","board","fractional","independent","emeritus","fellow",
                   "mentor","coach","executive coach"], 22),
}

def score_accountant(c):
    pos = c["pos"].lower()
    evidence = []
    tx_types = []

    for tx, (keywords, base_value) in TX_MAP.items():
        if any(kw in pos for kw in keywords):
            tx_types.append((tx, base_value))

    if not tx_types:
        return 0, []

    # value the highest-value tx type
    tx_types.sort(key=lambda x: -x[1])
    primary_tx = tx_types[0]
    evidence.append(f"TX:{primary_tx[0]} (value={primary_tx[1]}) — {c['pos'][:50]}")

    # bonus: multiple tx types = multi-use contact
    if len(tx_types) >= 2:
        evidence.append(f"MULTI-TX: also {tx_types[1][0]} — leverageable in 2 modes")

    # recency multiplier
    recency_mult = 1.3 if c["year"] in RECENT else 1.1 if c["year"] in ACTIVE else 0.7

    score = int(primary_tx[1] * recency_mult * len(tx_types))
    return score, evidence

# ─────────────────────────────────────────────────────────────
# SYNTHESIS
# ─────────────────────────────────────────────────────────────

def run_all_lenses(contacts):
    # build company registry for librarian
    company_registry = collections.Counter(c["company"] for c in contacts if c["company"])
    # build arch×year registry for sentry
    arch_year_registry = collections.defaultdict(set)

    results = []
    for c in contacts:
        d_score, d_ev = score_detective(c)
        cu_score, cu_ev = score_curator(c)
        l_score, l_ev = score_librarian(c, company_registry)
        s_score, s_ev = score_sentry(c, arch_year_registry)
        a_score, a_ev = score_accountant(c)

        lenses_hit = sum(1 for sc in [d_score, cu_score, l_score, s_score, a_score] if sc > 0)
        total = d_score + cu_score + l_score + s_score + a_score

        results.append({
            **c,
            "lenses_hit": lenses_hit,
            "total_score": total,
            "detective":   {"score": d_score,  "evidence": d_ev},
            "curator":     {"score": cu_score, "evidence": cu_ev},
            "librarian":   {"score": l_score,  "evidence": l_ev},
            "sentry":      {"score": s_score,  "evidence": s_ev},
            "accountant":  {"score": a_score,  "evidence": a_ev},
        })

    return sorted(results, key=lambda x: (-x["lenses_hit"], -x["total_score"]))


def top_per_lens(results, n=15):
    return {
        "detective":  sorted(results, key=lambda x: -x["detective"]["score"])[:n],
        "curator":    sorted(results, key=lambda x: -x["curator"]["score"])[:n],
        "librarian":  sorted(results, key=lambda x: -x["librarian"]["score"])[:n],
        "sentry":     sorted(results, key=lambda x: -x["sentry"]["score"])[:n],
        "accountant": sorted(results, key=lambda x: -x["accountant"]["score"])[:n],
    }


# ─────────────────────────────────────────────────────────────
# RENDER
# ─────────────────────────────────────────────────────────────

LENS_META = {
    "detective":  ("🔍 Detective",  "Anomalies, mismatches, stacked identities, seam concepts"),
    "curator":    ("🎨 Curator",    "Notability, creative-capital alignment, title rarity"),
    "librarian":  ("📚 Librarian",  "Cross-domain bridges, hub companies, long-arc root nodes"),
    "sentry":     ("🛡 Sentry",     "Fast-domain outliers, dormant high-value, in-motion builders"),
    "accountant": ("💰 Accountant", "Transaction type: Customer / Investor / Partner / Media / Talent"),
}

def render_md(results, by_lens):
    lines = []
    lines.append("# ARCS v9 Deep Forensic Scan")
    lines.append("**Mode:** Detective × Curator × Librarian × Sentry × Accountant")
    lines.append(f"**Corpus:** 11,177 contacts  |  **Date:** 2026-05-25")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Final Verdict — contacts hitting 3+ lenses
    verdict = [r for r in results if r["lenses_hit"] >= 3]
    lines.append(f"## Final Verdict — {len(verdict)} contacts surfaced in 3+ lenses")
    lines.append("*These are the write-lock activations. Each one is independently flagged by multiple detection modes.*")
    lines.append("")
    lines.append("| # | Name | Company | Title | Lenses | Score | Why |")
    lines.append("|---|------|---------|-------|--------|-------|-----|")

    for i, r in enumerate(verdict[:30], 1):
        lens_icons = ""
        if r["detective"]["score"] > 0:   lens_icons += "🔍"
        if r["curator"]["score"] > 0:     lens_icons += "🎨"
        if r["librarian"]["score"] > 0:   lens_icons += "📚"
        if r["sentry"]["score"] > 0:      lens_icons += "🛡"
        if r["accountant"]["score"] > 0:  lens_icons += "💰"

        all_ev = (r["detective"]["evidence"] + r["curator"]["evidence"] +
                  r["librarian"]["evidence"] + r["sentry"]["evidence"] +
                  r["accountant"]["evidence"])
        top_ev = all_ev[0][:70] if all_ev else ""

        name_link = f"[{r['name']}]({r['url']})" if r["url"] else r["name"]
        lines.append(
            f"| {i} | {name_link} | {r['company'][:30]} | {r['pos'][:45]} | "
            f"{lens_icons} | {r['total_score']} | {top_ev} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")

    # Per-lens breakdowns
    for lens_key, (lens_label, lens_desc) in LENS_META.items():
        top = by_lens[lens_key]
        lines.append(f"## {lens_label}")
        lines.append(f"*{lens_desc}*")
        lines.append("")
        lines.append("| Name | Company | Title | Year | Score | Evidence |")
        lines.append("|------|---------|-------|------|-------|----------|")
        for r in top:
            ev = r[lens_key]["evidence"]
            ev_str = ev[0][:70] if ev else "—"
            name_link = f"[{r['name']}]({r['url']})" if r["url"] else r["name"]
            lines.append(
                f"| {name_link} | {r['company'][:28]} | {r['pos'][:40]} | "
                f"{r['year']} | {r[lens_key]['score']} | {ev_str} |"
            )
        lines.append("")
        lines.append("---")
        lines.append("")

    # Outreach priority breakdown by transaction type
    lines.append("## Accountant Ledger — Transaction Type Breakdown")
    lines.append("")
    tx_buckets = collections.defaultdict(list)
    for r in results:
        for ev in r["accountant"]["evidence"]:
            for tx in ["CUSTOMER","INVESTOR","PARTNER","MEDIA","TALENT","ADVISOR"]:
                if f"TX:{tx}" in ev:
                    tx_buckets[tx].append(r)
    for tx, members in sorted(tx_buckets.items(), key=lambda x: -len(x[1])):
        top5 = sorted(members, key=lambda x: -x["accountant"]["score"])[:5]
        lines.append(f"### {tx} ({len(members)} contacts)")
        for r in top5:
            name_link = f"[{r['name']}]({r['url']})" if r["url"] else r["name"]
            lines.append(f"- {name_link} — {r['pos'][:55]} @ {r['company']} ({r['year']})")
        lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print("ARCS v9 Forensic Scan — loading contacts...")
    contacts = load(CSV_PATH)
    print(f"  {len(contacts)} contacts loaded")

    print("  running 5 detection lenses...")
    results = run_all_lenses(contacts)
    by_lens = top_per_lens(results, n=15)

    verdict = [r for r in results if r["lenses_hit"] >= 3]
    print(f"  write-lock activations (3+ lenses): {len(verdict)}")

    lens_counts = collections.Counter(r["lenses_hit"] for r in results)
    for k in sorted(lens_counts.keys(), reverse=True):
        print(f"    {k} lenses: {lens_counts[k]} contacts")

    print("  rendering markdown...")
    md = render_md(results, by_lens)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_MD, "w") as f:
        f.write(md)
    print(f"  wrote {OUT_MD}")

    # JSON export — verdict contacts only (clean, no internal evidence verbosity limit)
    json_out = []
    for r in verdict[:50]:
        json_out.append({
            "name": r["name"], "company": r["company"],
            "position": r["pos"], "url": r["url"], "year": r["year"],
            "lenses_hit": r["lenses_hit"], "total_score": r["total_score"],
            "evidence": {
                k: r[k]["evidence"] for k in ["detective","curator","librarian","sentry","accountant"]
                if r[k]["evidence"]
            }
        })
    with open(OUT_JSON, "w") as f:
        json.dump(json_out, f, indent=2)
    print(f"  wrote {OUT_JSON}")

    print("\n── FINAL VERDICT (top 30, sorted by lens coverage) ──────────\n")
    for i, r in enumerate(verdict[:30], 1):
        icons = ""
        if r["detective"]["score"]>0:  icons += "🔍"
        if r["curator"]["score"]>0:    icons += "🎨"
        if r["librarian"]["score"]>0:  icons += "📚"
        if r["sentry"]["score"]>0:     icons += "🛡"
        if r["accountant"]["score"]>0: icons += "💰"
        print(f"  {i:2d}. {icons} [{r['lenses_hit']} lenses | {r['total_score']:3d}pts] "
              f"{r['name'][:28]:28s} — {r['pos'][:45]}")
        all_ev = (r["detective"]["evidence"] + r["curator"]["evidence"] +
                  r["librarian"]["evidence"] + r["sentry"]["evidence"] +
                  r["accountant"]["evidence"])
        for ev in all_ev[:2]:
            print(f"       → {ev[:80]}")
    print()


if __name__ == "__main__":
    main()
