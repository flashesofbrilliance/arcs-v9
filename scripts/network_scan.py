#!/usr/bin/env python3
"""
ARCS Network Topology Scan — Deep Write Lock Analysis
Applies Triune Logic (OM/UNDEFINED/NULL) to professional social graph.

Input:  LinkedIn Connections.csv export
Output: network_scan.json + network_scan.md
"""

import csv
import json
import re
import os
import sys
import collections
from datetime import datetime
import anthropic

# ─────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────
CSV_PATH  = "/Users/zharris/Downloads/Basic_LinkedInDataExport_05-20-2026.zip/Connections.csv"
OUT_JSON  = os.path.join(os.path.dirname(__file__), "../network_scan.json")
OUT_MD    = os.path.join(os.path.dirname(__file__), "../network_scan.md")

# ─────────────────────────────────────────────────────────────
# INDUSTRY TAXONOMY  (order matters — first match wins)
# ─────────────────────────────────────────────────────────────
TAXONOMY = [
    ("Crypto / Web3 / Blockchain", [
        "crypto", "blockchain", "bitcoin", "ethereum", "defi", "nft", "web3",
        "grayscale", "coinbase", "binance", "kraken", "ledger", "bitgo",
        "chainalysis", "alchemy", "polygon", "solana", "avalanche", "pyusd",
        "digital asset", "virtual currency", "token", "dao", "decentralized",
        "galaxis", "opensea", "animoca", "yuga",
    ]),
    ("Venture / Private Equity / Investment", [
        "venture", "venture capital", "vc ", "private equity", "pe ", "seed",
        "angel investor", "general partner", "limited partner", "fund",
        "andreessen", "sequoia", "a16z", "kleiner", "benchmark", "accel",
        "softbank", "tiger global", "blackrock", "vanguard", "capital group",
        "investment firm", "asset management",
    ]),
    ("Fintech / Payments / Insurtech", [
        "fintech", "payments", "paypal", "stripe", "square", "affirm", "klarna",
        "robinhood", "plaid", "marqeta", "chime", "brex", "checkout.com",
        "insurtech", "lemonade", "wealthtech", "nerdwallet", "betterment",
        "wealth management",
    ]),
    ("Traditional Finance / Banking", [
        "goldman sachs", "morgan stanley", "jp morgan", "jpmorgan",
        "bank of america", "citigroup", "citi", "wells fargo", "barclays",
        "deutsche bank", "ubs", "credit suisse", "blackstone", "carlyle",
        "hedge fund", "derivatives", "fixed income", "equities",
        "investment bank", "financial services",
    ]),
    ("Real Estate", [
        "real estate", "corcoran", "elliman", "douglas elliman", "compass",
        "sotheby", "coldwell", "century 21", "redfin", "zillow", "related",
        "cushman", "cbre", "jll", "colliers", "broker", "realtor",
        "property", "residential", "commercial real", "reit", "proptech",
    ]),
    ("Big Tech (FAANG+)", [
        "google", "apple", "amazon", "meta", "microsoft", "netflix",
        "alphabet", "waymo", "deepmind", "openai", "anthropic",
        "salesforce", "oracle", "ibm", "intel", "nvidia", "amd",
        "qualcomm", "broadcom", "cisco", "vmware", "servicenow",
        "workday", "splunk", "palo alto networks",
    ]),
    ("AI / ML / Data", [
        "artificial intelligence", "machine learning", "deep learning",
        "natural language", "computer vision", "data science", "llm",
        "generative ai", "ai startup", "ml platform", "ai research",
        "hugging face", "mistral", "cohere", "stability", "midjourney",
        "runway", "scale ai", "weights & biases", "databricks", "snowflake",
    ]),
    ("SaaS / Enterprise Software", [
        "saas", "enterprise software", "b2b", "platform",
        "hubspot", "zendesk", "twilio", "sendgrid", "segment", "amplitude",
        "figma", "notion", "airtable", "atlassian", "jira", "slack",
        "zoom", "docusign", "dropbox", "box ", "intercom",
    ]),
    ("Startup / Stealth", [
        "stealth", "stealth startup", "stealth ai", "co-founder",
        "cofounder", "founder & ceo", "founding team",
    ]),
    ("Design / Architecture / Creative", [
        "design", "gensler", "skidmore", "aecom", "hok", "kpf",
        "interior design", "industrial design", "graphic design",
        "ux design", "product design", "creative director",
        "art director", "brand design", "architecture", "architectural",
    ]),
    ("Media / Entertainment / Publishing", [
        "media", "entertainment", "film", "television", "streaming",
        "music", "spotify", "universal music", "sony music", "warner",
        "publishing", "journalism", "news", "magazine", "editorial",
        "podcast", "content", "production company", "studio",
    ]),
    ("Healthcare / Wellness / Biotech", [
        "health", "healthcare", "wellness", "medical", "biotech", "pharma",
        "pharmaceutical", "clinical", "hospital", "patient", "therapy",
        "mental health", "digital health", "medtech", "lifesciences",
    ]),
    ("Consulting / Advisory / Professional Services", [
        "mckinsey", "bain", "bcg", "boston consulting", "deloitte",
        "accenture", "pwc", "kpmg", "ey ", "ernst & young",
        "consulting", "advisory", "strategy consulting", "management consulting",
    ]),
    ("Government / Policy / Non-profit", [
        "government", "policy", "federal", "state dept", "department of",
        "nonprofit", "non-profit", "ngo", "un ", "united nations",
        "world bank", "imf ", "foundation", "philanthropy",
    ]),
    ("Education / Academia", [
        "university", "college", "school of", "professor", "faculty",
        "research fellow", "phd", "postdoc", "academic", "education",
        "edtech", "coursera", "udemy", "khan academy",
    ]),
    ("Self-employed / Freelance", [
        "self-employed", "self employed", "freelance", "independent",
        "consultant", "fractional",
    ]),
]

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

SENIOR_KEYWORDS = [
    "chief", "ceo", "cto", "coo", "cfo", "cpo", "cmo", "founder",
    "president", "partner", "managing director", "md ", "svp", "evp",
    "vp ", "vice president", "general manager", "director",
    "principal", "head of", "global",
]


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def classify_industry(company: str, position: str) -> str:
    haystack = (company + " " + position).lower()
    for label, keywords in TAXONOMY:
        for kw in keywords:
            if kw in haystack:
                return label
    return "Other / Unclassified"


def parse_year(connected_on: str):
    if not connected_on:
        return None
    parts = connected_on.strip().split()
    for p in parts:
        if p.isdigit() and len(p) == 4:
            return int(p)
    return None


def is_senior(position: str) -> bool:
    pos = position.lower()
    return any(kw in pos for kw in SENIOR_KEYWORDS)


def triune_status(n: int, recent_n: int, unique_companies: int) -> str:
    """OM if n≥5 and recent activity. NULL if <3. UNDEFINED otherwise."""
    if n < 3:
        return "NULL"
    if n >= 5 and recent_n >= 2:
        return "OM"
    if n >= 5:
        return "UNDEFINED"
    return "UNDEFINED"


# ─────────────────────────────────────────────────────────────
# PARSE
# ─────────────────────────────────────────────────────────────

def load_connections(path: str) -> list[dict]:
    connections = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        # skip the LinkedIn notes header lines before the real header
        lines = f.readlines()

    # find the real header row (contains "First Name")
    start = 0
    for i, line in enumerate(lines):
        if "First Name" in line:
            start = i
            break

    reader = csv.DictReader(lines[start:])
    for row in reader:
        first    = (row.get("First Name") or "").strip()
        last     = (row.get("Last Name") or "").strip()
        url      = (row.get("URL") or "").strip()
        company  = (row.get("Company") or "").strip()
        position = (row.get("Position") or "").strip()
        conn_on  = (row.get("Connected On") or "").strip()
        year     = parse_year(conn_on)
        industry = classify_industry(company, position)
        senior   = is_senior(position)

        connections.append({
            "name": f"{first} {last}".strip(),
            "url": url,
            "company": company,
            "position": position,
            "connected_year": year,
            "industry": industry,
            "senior": senior,
        })
    return connections


# ─────────────────────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────────────────────

RECENT_YEARS = {2023, 2024, 2025, 2026}

def analyze_clusters(connections: list[dict]) -> dict:
    by_industry: dict[str, list[dict]] = collections.defaultdict(list)
    for c in connections:
        by_industry[c["industry"]].append(c)

    clusters = {}
    for label, members in by_industry.items():
        recent = [m for m in members if m["connected_year"] in RECENT_YEARS]
        senior_members = [m for m in members if m["senior"]]
        companies = set(m["company"] for m in members if m["company"])
        status = triune_status(len(members), len(recent), len(companies))

        # top companies in cluster
        co_counts = collections.Counter(m["company"] for m in members if m["company"])
        top_cos = [c for c, _ in co_counts.most_common(5)]

        # write-lock nodes: senior + in recent + OM cluster
        write_lock_nodes = [
            m for m in members
            if m["senior"] and m["connected_year"] in RECENT_YEARS
        ][:10]  # cap for readability

        clusters[label] = {
            "total": len(members),
            "recent": len(recent),
            "senior_count": len(senior_members),
            "unique_companies": len(companies),
            "top_companies": top_cos,
            "triune": status,
            "write_lock_nodes": write_lock_nodes,
        }

    return dict(sorted(clusters.items(), key=lambda x: -x[1]["total"]))


def temporal_stratigraphy(connections: list[dict]) -> dict:
    by_year: dict[int, int] = collections.Counter()
    for c in connections:
        if c["connected_year"]:
            by_year[c["connected_year"]] += 1
    return dict(sorted(by_year.items()))


def cross_domain_isomorphisms(clusters: dict) -> list[str]:
    """
    Surface structural similarities across clusters —
    clusters with similar size/recency profiles that suggest
    kinematic overlap (Orthogonal Echo Detector).
    """
    iso = []

    # Find clusters that co-peak in the same temporal window
    # (simplified: flag OM clusters that both have heavy 2013-2015 wave)
    om_clusters = [k for k, v in clusters.items() if v["triune"] == "OM"]
    if len(om_clusters) >= 3:
        iso.append(
            f"Multi-domain OM convergence: {', '.join(om_clusters[:3])} all reach "
            f"write-lock independently — suggests these aren't separate orbits but a "
            f"shared professional substrate."
        )

    # Real estate + finance cluster proximity
    re = clusters.get("Real Estate", {})
    fi = clusters.get("Traditional Finance / Banking", {})
    cr = clusters.get("Crypto / Web3 / Blockchain", {})
    if re.get("total", 0) > 20 and (fi.get("total", 0) > 10 or cr.get("total", 0) > 20):
        iso.append(
            "Real Estate × Finance/Crypto kinematic overlap: high density in both "
            "suggests an asset-class lens that bridges physical and digital value stores. "
            "ARCS signal: your network treats capital as a substrate, not an industry."
        )

    # Self-employed density
    se = clusters.get("Self-employed / Freelance", {})
    if se.get("total", 0) > 80:
        iso.append(
            f"Freelance/independent density ({se['total']}) well above baseline: "
            "your network skews toward operators and principal agents, not org-embedded employees. "
            "ARCS signal: autonomy as a shared value, not just a career mode."
        )

    return iso


# ─────────────────────────────────────────────────────────────
# CLAUDE L5 SYNTHESIS
# ─────────────────────────────────────────────────────────────

def l5_synthesis(clusters: dict, stratigraphy: dict, isos: list[str], total: int) -> str:
    client = anthropic.Anthropic()

    om_clusters = {k: v for k, v in clusters.items() if v["triune"] == "OM"}
    undef_clusters = {k: v for k, v in clusters.items() if v["triune"] == "UNDEFINED"}
    null_clusters = {k: v for k, v in clusters.items() if v["triune"] == "NULL"}

    cluster_summary = "\n".join(
        f"- {k}: n={v['total']}, recent={v['recent']}, senior={v['senior_count']}, "
        f"top_cos={v['top_companies'][:3]}, status={v['triune']}"
        for k, v in sorted(clusters.items(), key=lambda x: -x[1]["total"])[:20]
    )

    strat_str = ", ".join(f"{yr}: {n}" for yr, n in sorted(stratigraphy.items()))
    iso_str = "\n".join(f"- {i}" for i in isos) if isos else "- None detected"

    prompt = f"""You are ARCS v9 running an L5 atomic intel synthesis pass on a professional social network topology scan.

CONTEXT:
- Total connections: {total}
- Scan date: 2026-05-20
- Triune status counts: OM={len(om_clusters)}, UNDEFINED={len(undef_clusters)}, NULL={len(null_clusters)}
- Connection history: {strat_str}

TOP CLUSTERS (sorted by size):
{cluster_summary}

ORTHOGONAL ECHO ISOMORPHISMS:
{iso_str}

OM-STATUS CLUSTERS (write-lock confirmed):
{json.dumps({k: {"total": v["total"], "recent": v["recent"], "top_cos": v["top_companies"]} for k, v in om_clusters.items()}, indent=2)}

TASK:
Apply ARCS L5 Atomic Intel delivery. The subject is NOT a single decision — it is a 20-year professional network as a coherence object.

Produce EXACTLY this structure (use the exact headers):

## True North
[One sentence. What does this network fundamentally reveal about who this person is and where they have irreducible leverage?]

## Why
1. [First structural reason — grounded in the cluster data]
2. [Second structural reason — temporal pattern or cross-domain isomorphism]
3. [Third structural reason — contrast between OM and UNDEFINED zones]

## Write-Lock Signal
[What is the single highest-confidence claim this network makes about this person's professional identity? State it as a falsifiable prediction.]

## UNDEFINED Zone Warning
[What does this network conspicuously NOT contain that should be there? What's the gap that would change the True North if filled?]

## Kairos Window
[Given the temporal stratigraphy (connection waves), what is the current activation window? Is the network growing, consolidating, or in drift?]

Rules:
- No flattery. No hedging. No "may" or "might."
- Write-lock = OM status only. Don't promote UNDEFINED to OM.
- Be specific about cluster names and numbers. Vague analysis is NULL output.
- NOTOMATION: this scan scaffolds the person's cognition, it does not tell them what to do.
- Max 400 words total across all sections."""

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


# ─────────────────────────────────────────────────────────────
# RENDER MARKDOWN
# ─────────────────────────────────────────────────────────────

def render_markdown(
    total: int,
    clusters: dict,
    stratigraphy: dict,
    isos: list[str],
    l5: str,
) -> str:
    lines = []
    lines.append("# ARCS Network Topology Scan")
    lines.append(f"**Date:** 2026-05-20  **Total connections:** {total}  **Scan type:** Deep Write Lock")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(l5)
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Triune Classification — All Clusters")
    lines.append("")
    lines.append("| Cluster | n | Recent | Senior | Status |")
    lines.append("|---------|---|--------|--------|--------|")
    for label, data in sorted(clusters.items(), key=lambda x: -x[1]["total"]):
        status_badge = {"OM": "🟢 OM", "UNDEFINED": "🟡 UNDEFINED", "NULL": "🔴 NULL"}[data["triune"]]
        lines.append(
            f"| {label} | {data['total']} | {data['recent']} | "
            f"{data['senior_count']} | {status_badge} |"
        )
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Temporal Stratigraphy — Connection Waves")
    lines.append("")
    lines.append("| Year | Connections |")
    lines.append("|------|-------------|")
    for yr, n in sorted(stratigraphy.items()):
        bar = "█" * min(n // 40, 30)
        lines.append(f"| {yr} | {n:5d}  {bar} |")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Orthogonal Echo — Cross-Domain Isomorphisms")
    lines.append("")
    if isos:
        for iso in isos:
            lines.append(f"- {iso}")
    else:
        lines.append("- No cross-domain kinematic overlaps detected above threshold.")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Write-Lock Nodes — Highest-Signal Contacts")
    lines.append("*(Senior title + recent connection + OM cluster)*")
    lines.append("")
    om_clusters = {k: v for k, v in clusters.items() if v["triune"] == "OM"}
    node_count = 0
    for cluster_label, data in om_clusters.items():
        nodes = data.get("write_lock_nodes", [])
        if not nodes:
            continue
        lines.append(f"### {cluster_label}")
        for node in nodes[:5]:
            profile = f"[{node['name']}]({node['url']})" if node["url"] else node["name"]
            lines.append(f"- {profile} — {node['position']} @ {node['company']} ({node['connected_year']})")
            node_count += 1
        lines.append("")

    if node_count == 0:
        lines.append("*No write-lock nodes surfaced — no senior + recent + OM cluster intersections found.*")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Raw Cluster Detail (JSON embedded)")
    lines.append("")
    lines.append("```json")
    # strip write_lock_nodes from the compact embed to keep it readable
    compact = {
        k: {kk: vv for kk, vv in v.items() if kk != "write_lock_nodes"}
        for k, v in clusters.items()
    }
    lines.append(json.dumps(compact, indent=2))
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print("ARCS Network Topology Scan — loading connections...")
    connections = load_connections(CSV_PATH)
    print(f"  loaded {len(connections)} connections")

    print("  clustering by industry...")
    clusters = analyze_clusters(connections)

    print("  building temporal stratigraphy...")
    stratigraphy = temporal_stratigraphy(connections)

    print("  running orthogonal echo detector...")
    isos = cross_domain_isomorphisms(clusters)

    print("  skipping L5 synthesis (no API key) — will embed placeholder...")
    l5 = "[[L5 SYNTHESIS — see session output]]"

    print("  rendering output...")
    md = render_markdown(len(connections), clusters, stratigraphy, isos, l5)

    # strip write_lock_nodes URLs for JSON (privacy — keep names only)
    json_safe_clusters = {}
    for label, data in clusters.items():
        d = dict(data)
        d["write_lock_nodes"] = [
            {"name": n["name"], "company": n["company"],
             "position": n["position"], "year": n["connected_year"]}
            for n in d.get("write_lock_nodes", [])
        ]
        json_safe_clusters[label] = d

    output = {
        "meta": {
            "scan_date": "2026-05-20",
            "total_connections": len(connections),
            "scan_type": "deep_write_lock",
        },
        "l5_synthesis": l5,
        "clusters": json_safe_clusters,
        "stratigraphy": stratigraphy,
        "isomorphisms": isos,
    }

    out_json = os.path.normpath(OUT_JSON)
    out_md   = os.path.normpath(OUT_MD)

    with open(out_json, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  wrote {out_json}")

    with open(out_md, "w") as f:
        f.write(md)
    print(f"  wrote {out_md}")

    print("\n── ARCS L5 SYNTHESIS ──────────────────────────────────\n")
    print(l5)
    print("\n───────────────────────────────────────────────────────\n")
    print(f"Scan complete. Clusters: {len(clusters)}")
    om = sum(1 for v in clusters.values() if v["triune"] == "OM")
    un = sum(1 for v in clusters.values() if v["triune"] == "UNDEFINED")
    nl = sum(1 for v in clusters.values() if v["triune"] == "NULL")
    print(f"  OM={om}  UNDEFINED={un}  NULL={nl}")


if __name__ == "__main__":
    main()
