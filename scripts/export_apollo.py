#!/usr/bin/env python3
"""
ARCS → Apollo.io Enrichment Export
Generates a CSV of the top N contacts by NCI score,
formatted for Apollo.io People CSV Import.

Apollo import format:
  First Name, Last Name, Title, Company, LinkedIn URL
  (Apollo will enrich: email, Twitter/X, company funding, headcount, etc.)

Usage:
  python3 export_apollo.py           # top 500 by NCI
  python3 export_apollo.py 1000      # top 1000
  python3 export_apollo.py 500 recent   # top 500 among recent connections only
"""

import csv
import sys
import os

CSV_PATH = "/Users/zharris/Downloads/Basic_LinkedInDataExport_05-20-2026.zip/Connections.csv"
OUT_DIR  = os.path.join(os.path.dirname(__file__), "../exports")

RECENT_YEARS = {2023, 2024, 2025, 2026}

# ── inline archetype classifier (mirrors archetype_scan.py) ──

ARCHETYPES = [
    ("Builder", [
        "founder","co-founder","ceo","cto","cpo","chief product","chief executive",
        "chief technology","head of product","vp product","vp engineering",
        "director of product","director of engineering","general manager","gm ",
        "president","0-to-1","startup","entrepreneur","product lead","tech lead",
        "principal engineer",
    ], []),
    ("Navigator", [
        "chief of staff","strategy","strategic","chief operating","coo",
        "chief revenue","cro ","revenue","growth","managing director","svp","evp",
        "head of strategy","head of growth","head of operations","business development",
        "biz dev","bd ","partnerships","transformation",
    ], []),
    ("Illuminator", [
        "writer","author","editor","journalist","researcher","professor","faculty",
        "educator","teacher","academic","thought leader","analyst","content creator",
        "content strategist","storyteller",
    ], ["university","college","media","publishing"]),
    ("Instrumentor", [
        "engineer","developer","software","data scientist","data engineer",
        "machine learning","ml engineer","ai engineer","quant","infrastructure",
        "devops","backend","frontend","full stack","site reliability","sre ",
        "blockchain developer","smart contract",
    ], []),
    ("Mediator", [
        "community","partnerships","partner","ecosystem","relations",
        "connector","ambassador","advocate","evangelist","account manager",
        "account executive","customer success","sales",
    ], []),
    ("Orienter", [
        "coach","mentor","advisor","adviser","consultant","fractional","interim",
        "executive coach","life coach","career coach","leadership coach",
    ], ["coaching","advisory"]),
    ("Chartist", [
        "design","designer","architect","ux","ui ","user experience","user interface",
        "product design","visual design","brand design","creative director",
        "art director","creative","design lead","design manager",
    ], ["design","gensler","ideo"]),
    ("Focused Executor", [
        "operations","program manager","project manager","specialist","coordinator",
        "associate","analyst","administrator","compliance","legal","accounting",
        "hr ","human resources","talent","recruiter","supply chain",
    ], []),
]

SUBJECT_STACK = [("Builder", 1.0), ("Navigator", 0.6), ("Chartist", 0.3)]

RESONANCE_MATRIX = {
    "Builder":          [1.0, 0.85, 0.5, 0.75, 0.7,  0.5,  0.8,  0.4],
    "Navigator":        [0.85,1.0, 0.6, 0.6,  0.8,  0.65, 0.7,  0.5],
    "Illuminator":      [0.5, 0.6, 1.0, 0.5,  0.6,  0.7,  0.65, 0.3],
    "Instrumentor":     [0.75,0.6, 0.5, 1.0,  0.5,  0.3,  0.7,  0.5],
    "Mediator":         [0.7, 0.8, 0.6, 0.5,  1.0,  0.7,  0.55, 0.5],
    "Orienter":         [0.5, 0.65,0.7, 0.3,  0.7,  1.0,  0.5,  0.4],
    "Chartist":         [0.8, 0.7, 0.65,0.7,  0.55, 0.5,  1.0,  0.4],
    "Focused Executor": [0.4, 0.5, 0.3, 0.5,  0.5,  0.4,  0.4,  1.0],
}
ARCH_ORDER = [a[0] for a in ARCHETYPES]


def classify(position: str, company: str) -> list:
    h_t = position.lower()
    h_c = company.lower()
    scores = {}
    for name, title_kw, co_kw in ARCHETYPES:
        s = sum(1.0 for kw in title_kw if kw in h_t)
        s += sum(0.5 for kw in co_kw if kw in h_c)
        scores[name] = s
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    if ranked[0][1] == 0:
        ranked = [("Focused Executor", 0.1)] + [r for r in ranked if r[0] != "Focused Executor"]
    return ranked


def nci(ranked: list, year, position: str, company: str) -> float:
    """
    Composite NCI = base_resonance (60%) + recency (20%) + seniority (20%)
    This prevents ceiling collapse where all CEOs score identically.
    """
    total = sum(s for _, s in ranked)
    if not total:
        return 0.0

    # base resonance [0,1]
    base = 0.0
    for arch, w in ranked[:3]:
        if arch not in ARCH_ORDER:
            continue
        idx = ARCH_ORDER.index(arch)
        prop = w / total
        for subj_arch, subj_w in SUBJECT_STACK:
            base += prop * subj_w * RESONANCE_MATRIX[subj_arch][idx]
    base = min(base / sum(w for _, w in SUBJECT_STACK), 1.0)

    # recency score [0,1]
    if year is None:
        recency = 0.3
    elif year >= 2025:
        recency = 1.0
    elif year >= 2023:
        recency = 0.85
    elif year >= 2021:
        recency = 0.65
    elif year >= 2018:
        recency = 0.45
    elif year >= 2015:
        recency = 0.3
    else:
        recency = 0.15

    # seniority score [0,1] — depth of title keyword signal
    pos = position.lower()
    co  = company.lower()
    C_SUITE    = ["ceo","cto","cpo","coo","cmo","cfo","chief ","president","founder","co-founder"]
    VP_DIR     = ["vp ","svp","evp","vice president","director","managing director","md ","general manager","gm ","head of","principal"]
    MID        = ["lead","manager","senior","sr ","staff","partner"]

    if any(k in pos for k in C_SUITE):
        seniority = 1.0
    elif any(k in pos for k in VP_DIR):
        seniority = 0.75
    elif any(k in pos for k in MID):
        seniority = 0.5
    else:
        seniority = 0.25

    # notable company bonus [0, 0.1]
    NOTABLE = [
        "google","apple","amazon","meta","microsoft","openai","anthropic",
        "stripe","coinbase","grayscale","a16z","sequoia","y combinator",
        "andreessen","softbank","blackrock","goldman","morgan stanley",
    ]
    company_bonus = 0.1 if any(n in co for n in NOTABLE) else 0.0

    composite = (base * 0.60) + (recency * 0.20) + (seniority * 0.20) + company_bonus
    return round(min(composite, 1.0), 4)


def parse_year(s):
    for p in s.strip().split():
        if p.isdigit() and len(p) == 4:
            return int(p)
    return None


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        lines = f.readlines()
    start = next(i for i, l in enumerate(lines) if "First Name" in l)
    out = []
    for row in csv.DictReader(lines[start:]):
        first    = (row.get("First Name") or "").strip()
        last     = (row.get("Last Name") or "").strip()
        company  = (row.get("Company") or "").strip()
        position = (row.get("Position") or "").strip()
        url      = (row.get("URL") or "").strip()
        year     = parse_year(row.get("Connected On") or "")
        ranked   = classify(position, company)
        out.append({
            "first": first, "last": last,
            "company": company, "position": position,
            "url": url, "year": year,
            "recent": year in RECENT_YEARS if year else False,
            "primary_arch": ranked[0][0],
            "nci": nci(ranked, year, position, company),
        })
    return out


def main():
    top_n    = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    mode     = sys.argv[2] if len(sys.argv) > 2 else "all"

    print(f"Loading connections...")
    contacts = load(CSV_PATH)

    if mode == "recent":
        pool = [c for c in contacts if c["recent"]]
        label = "recent"
    else:
        pool = contacts
        label = "all"

    # Stratified sampling: take top N/8 per archetype so the export is
    # diverse across archetypes rather than 100% Builder ceiling-collapse.
    per_arch = max(1, top_n // len(ARCHETYPES))
    top = []
    for arch_name, _, _ in ARCHETYPES:
        bucket = sorted(
            [c for c in pool if c["primary_arch"] == arch_name],
            key=lambda x: -x["nci"]
        )[:per_arch]
        top.extend(bucket)
    # fill remainder with globally highest NCI not already included
    included = {(c["first"], c["last"], c["company"]) for c in top}
    remainder = sorted(
        [c for c in pool if (c["first"], c["last"], c["company"]) not in included],
        key=lambda x: -x["nci"]
    )
    top.extend(remainder[:max(0, top_n - len(top))])
    top = top[:top_n]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"apollo_top{top_n}_{label}.csv")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Apollo expected headers for people import
        writer.writerow([
            "First Name", "Last Name", "Title", "Company",
            "LinkedIn URL", "ARCS Archetype", "ARCS NCI", "Connected Year"
        ])
        for c in top:
            writer.writerow([
                c["first"], c["last"], c["position"], c["company"],
                c["url"], c["primary_arch"], c["nci"], c["year"] or ""
            ])

    print(f"  Exported {len(top)} contacts → {out_path}")
    print()

    # Summary breakdown
    from collections import Counter
    arch_counts = Counter(c["primary_arch"] for c in top)
    nci_buckets = {"≥0.9": 0, "0.8–0.9": 0, "0.7–0.8": 0, "<0.7": 0}
    for c in top:
        n = c["nci"]
        if n >= 0.9:   nci_buckets["≥0.9"] += 1
        elif n >= 0.8: nci_buckets["0.8–0.9"] += 1
        elif n >= 0.7: nci_buckets["0.7–0.8"] += 1
        else:          nci_buckets["<0.7"] += 1

    print("NCI distribution in export:")
    for bucket, count in nci_buckets.items():
        print(f"  {bucket}: {count}")
    print()
    print("Archetype breakdown:")
    for arch, count in arch_counts.most_common():
        print(f"  {arch:20s} {count}")
    print()
    print("Apollo import steps:")
    print("  1. app.apollo.io → Lists → Import People from CSV")
    print("  2. Map: First Name, Last Name, Title, Company, LinkedIn URL")
    print("  3. Skip ARCS Archetype / NCI / Connected Year (custom fields)")
    print("  4. Enable 'Enrich new records' → gets email, Twitter, company data")
    print(f"  5. Free tier = 50 enrichments/export. Paid = full {len(top)}.")
    print()
    print(f"File: {out_path}")


if __name__ == "__main__":
    main()
