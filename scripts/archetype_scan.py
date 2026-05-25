#!/usr/bin/env python3
"""
ARCS Archetype Scan — Resonance Scoring & Force-Directed Graph
Classifies each LinkedIn connection into the 8 ARCS archetypes,
scores resonance against the subject's own stack, and renders
an interactive Plotly HTML visualization.

Subject stack: Builder (primary) → Navigator (secondary) → Chartist (tertiary)
"""

import csv
import json
import os
import math
import collections
import plotly.graph_objects as go
import networkx as nx

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
CSV_PATH    = "/Users/zharris/Downloads/Basic_LinkedInDataExport_05-20-2026.zip/Connections.csv"
OUT_HTML    = os.path.join(os.path.dirname(__file__), "../network_archetype_viz.html")
OUT_JSON    = os.path.join(os.path.dirname(__file__), "../network_archetype.json")
OUT_MD      = os.path.join(os.path.dirname(__file__), "../network_archetype.md")

# Subject archetype stack (weights: primary=1.0, secondary=0.6, tertiary=0.3)
SUBJECT_STACK = [("Builder", 1.0), ("Navigator", 0.6), ("Chartist", 0.3)]

RECENT_YEARS = {2023, 2024, 2025, 2026}

# ─────────────────────────────────────────────────────────────
# ARCHETYPE TAXONOMY
# ─────────────────────────────────────────────────────────────
# Each archetype: (label, hex_color, title_keywords, company_keywords)
ARCHETYPES = [
    {
        "name": "Builder",
        "color": "#00FF9D",   # ARCS green
        "desc": "0→1 operators, founders, CPOs, product builders",
        "title_kw": [
            "founder", "co-founder", "ceo", "cto", "cpo", "chief product",
            "chief executive", "chief technology", "head of product",
            "vp product", "vp engineering", "director of product",
            "director of engineering", "general manager", "gm ",
            "president", "0-to-1", "0 to 1", "startup",
            "entrepreneur", "intrapreneur", "product lead",
            "engineering lead", "tech lead", "principal engineer",
        ],
        "company_kw": [
            "stealth", "co-founder", "seed", "early stage",
        ],
    },
    {
        "name": "Navigator",
        "color": "#4ABDB0",   # ARCS teal
        "desc": "Strategy, Chiefs of Staff, GMs, P&L owners",
        "title_kw": [
            "chief of staff", "strategy", "strategic", "chief strategy",
            "chief operating", "coo", "operations", "chief business",
            "chief revenue", "cro ", "revenue", "growth", "expansion",
            "managing director", "md ", "svp", "evp", "executive vp",
            "head of strategy", "head of growth", "head of operations",
            "business development", "biz dev", "bd ", "partnerships",
            "head of business", "transformation",
        ],
        "company_kw": [],
    },
    {
        "name": "Illuminator",
        "color": "#FFD700",   # ARCS gold
        "desc": "Writers, researchers, educators, thought leaders",
        "title_kw": [
            "writer", "author", "editor", "journalist", "reporter",
            "researcher", "research", "professor", "faculty", "lecturer",
            "educator", "teacher", "academic", "scholar", "fellow",
            "thought leader", "analyst", "columnist", "blogger",
            "content creator", "content strategist", "storyteller",
            "curriculum", "learning",
        ],
        "company_kw": [
            "university", "college", "school", "media", "publishing",
            "press", "journal", "magazine",
        ],
    },
    {
        "name": "Instrumentor",
        "color": "#00F0FF",   # ARCS cyan
        "desc": "Engineers, data scientists, quant analysts",
        "title_kw": [
            "engineer", "developer", "software", "data scientist",
            "data engineer", "machine learning", "ml engineer",
            "ai engineer", "quant", "quantitative", "data analyst",
            "analytics", "infrastructure", "platform engineer",
            "devops", "backend", "frontend", "full stack",
            "site reliability", "sre ", "security engineer",
            "blockchain developer", "smart contract",
        ],
        "company_kw": [],
    },
    {
        "name": "Mediator",
        "color": "#FF9500",   # orange
        "desc": "BD, partnerships, community, connectors",
        "title_kw": [
            "community", "partnerships", "partner", "ecosystem",
            "relations", "relationship", "connector", "network",
            "ambassador", "advocate", "evangelist", "liaison",
            "account manager", "account executive", "client",
            "customer success", "sales", "business development",
        ],
        "company_kw": [],
    },
    {
        "name": "Orienter",
        "color": "#FF4D6D",   # ARCS red/pink
        "desc": "Coaches, advisors, mentors, career pivots",
        "title_kw": [
            "coach", "mentor", "advisor", "adviser", "counselor",
            "therapist", "consultant", "independent consultant",
            "fractional", "interim", "executive coach",
            "life coach", "career coach", "leadership coach",
        ],
        "company_kw": [
            "coaching", "advisory", "advisors",
        ],
    },
    {
        "name": "Chartist",
        "color": "#A855F7",   # purple
        "desc": "Designers, architects, systems thinkers",
        "title_kw": [
            "design", "designer", "architect", "architecture",
            "ux", "ui ", "user experience", "user interface",
            "product design", "visual design", "brand design",
            "creative director", "art director", "creative",
            "systems thinking", "design thinking", "service design",
            "design lead", "design manager", "principal designer",
        ],
        "company_kw": [
            "design", "gensler", "ideo", "frog", "pentagram",
        ],
    },
    {
        "name": "Focused Executor",
        "color": "#64748B",   # slate
        "desc": "Ops, program managers, deep domain specialists",
        "title_kw": [
            "operations", "program manager", "project manager",
            "specialist", "coordinator", "associate", "analyst",
            "administrator", "support", "specialist", "officer",
            "compliance", "legal", "finance", "accounting",
            "hr ", "human resources", "talent", "recruiter",
            "procurement", "supply chain", "logistics",
        ],
        "company_kw": [],
    },
]


# ─────────────────────────────────────────────────────────────
# ARCHETYPE CLASSIFIER
# ─────────────────────────────────────────────────────────────

def classify_archetype(position: str, company: str) -> list[tuple[str, float]]:
    """
    Returns list of (archetype_name, score) sorted descending.
    Scores are weighted keyword hit counts — primary archetype > 0.
    """
    haystack_title   = position.lower()
    haystack_company = company.lower()
    scores = {}
    for arch in ARCHETYPES:
        s = 0.0
        for kw in arch["title_kw"]:
            if kw in haystack_title:
                s += 1.0
        for kw in arch["company_kw"]:
            if kw in haystack_company:
                s += 0.5
        scores[arch["name"]] = s

    ranked = sorted(scores.items(), key=lambda x: -x[1])
    # if no signal at all, fall back to Focused Executor (catch-all)
    if ranked[0][1] == 0:
        ranked = [("Focused Executor", 0.1)] + [r for r in ranked if r[0] != "Focused Executor"]

    return ranked


# ─────────────────────────────────────────────────────────────
# RESONANCE SCORING (NCI — Normalized Coherence Index)
# ─────────────────────────────────────────────────────────────

# Resonance matrix: how much does each archetype resonate with each other
# 1.0 = amplification (same), 0.8 = constructive interference, 0.3 = neutral, 0.1 = dissonant
RESONANCE_MATRIX = {
    #              Builder  Nav   Illum  Instr  Mediat  Orient  Chart   FocEx
    "Builder":     [1.0,   0.85,  0.5,   0.75,  0.7,   0.5,   0.8,   0.4],
    "Navigator":   [0.85,  1.0,   0.6,   0.6,   0.8,   0.65,  0.7,   0.5],
    "Illuminator": [0.5,   0.6,   1.0,   0.5,   0.6,   0.7,   0.65,  0.3],
    "Instrumentor":[0.75,  0.6,   0.5,   1.0,   0.5,   0.3,   0.7,   0.5],
    "Mediator":    [0.7,   0.8,   0.6,   0.5,   1.0,   0.7,   0.55,  0.5],
    "Orienter":    [0.5,   0.65,  0.7,   0.3,   0.7,   1.0,   0.5,   0.4],
    "Chartist":    [0.8,   0.7,   0.65,  0.7,   0.55,  0.5,   1.0,   0.4],
    "Focused Executor": [0.4, 0.5, 0.3,  0.5,   0.5,   0.4,   0.4,   1.0],
}

ARCHETYPE_ORDER = [a["name"] for a in ARCHETYPES]


def resonance_score(contact_ranked: list[tuple[str, float]]) -> float:
    """
    NCI = weighted sum of (contact archetype weight × resonance with subject stack)
    Normalized to [0, 1].
    """
    if not contact_ranked:
        return 0.0

    # normalize contact scores to sum to 1
    total_score = sum(s for _, s in contact_ranked)
    if total_score == 0:
        return 0.0

    nci = 0.0
    for contact_arch, contact_weight in contact_ranked[:3]:
        if contact_arch not in ARCHETYPE_ORDER:
            continue
        contact_idx = ARCHETYPE_ORDER.index(contact_arch)
        # weight the contact contribution by how strong that archetype signal is
        contact_proportion = contact_weight / total_score

        # score against subject stack
        for subject_arch, subject_weight in SUBJECT_STACK:
            if subject_arch not in RESONANCE_MATRIX:
                continue
            row = RESONANCE_MATRIX[subject_arch]
            r = row[contact_idx]
            nci += contact_proportion * subject_weight * r

    # normalize by maximum possible (subject primary + subject secondary + subject tertiary all perfect)
    max_nci = sum(w for _, w in SUBJECT_STACK)
    return min(nci / max_nci, 1.0)


# ─────────────────────────────────────────────────────────────
# PARSE
# ─────────────────────────────────────────────────────────────

def parse_year(s: str):
    for p in s.strip().split():
        if p.isdigit() and len(p) == 4:
            return int(p)
    return None


def load_connections(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        lines = f.readlines()
    start = 0
    for i, line in enumerate(lines):
        if "First Name" in line:
            start = i
            break
    reader = csv.DictReader(lines[start:])
    out = []
    for row in reader:
        first    = (row.get("First Name") or "").strip()
        last     = (row.get("Last Name") or "").strip()
        url      = (row.get("URL") or "").strip()
        company  = (row.get("Company") or "").strip()
        position = (row.get("Position") or "").strip()
        conn_on  = (row.get("Connected On") or "").strip()
        year     = parse_year(conn_on)
        ranked   = classify_archetype(position, company)
        primary  = ranked[0][0]
        nci      = resonance_score(ranked)
        out.append({
            "name":     f"{first} {last}".strip(),
            "url":      url,
            "company":  company,
            "position": position,
            "year":     year,
            "recent":   year in RECENT_YEARS if year else False,
            "primary_archetype": primary,
            "archetype_stack": ranked[:3],
            "nci": round(nci, 4),
        })
    return out


# ─────────────────────────────────────────────────────────────
# AGGREGATE STATS
# ─────────────────────────────────────────────────────────────

def compute_stats(contacts: list[dict]) -> dict:
    by_arch: dict[str, list] = collections.defaultdict(list)
    for c in contacts:
        by_arch[c["primary_archetype"]].append(c)

    stats = {}
    for arch in ARCHETYPE_ORDER:
        members = by_arch.get(arch, [])
        recent  = [m for m in members if m["recent"]]
        top_nci = sorted(members, key=lambda x: -x["nci"])[:20]
        avg_nci = sum(m["nci"] for m in members) / len(members) if members else 0

        stats[arch] = {
            "total":     len(members),
            "recent":    len(recent),
            "avg_nci":   round(avg_nci, 4),
            "top_resonance": [
                {"name": m["name"], "company": m["company"],
                 "position": m["position"], "nci": m["nci"], "year": m["year"]}
                for m in top_nci
            ],
        }
    return stats


# ─────────────────────────────────────────────────────────────
# VISUALIZATION  — two charts:
#   1. Archetype bubble chart (cluster view)
#   2. Force-directed graph of top-400 highest-NCI contacts
# ─────────────────────────────────────────────────────────────

def build_viz(contacts: list[dict], stats: dict) -> go.Figure:
    """
    Returns a single Plotly Figure with two tabs via updatemenus.
    Tab 1: Archetype distribution bubbles
    Tab 2: Force graph of top contacts
    """
    color_map = {a["name"]: a["color"] for a in ARCHETYPES}

    # ── Chart 1: Archetype Bubble Chart ──────────────────────
    arch_names  = []
    arch_totals = []
    arch_recents= []
    arch_nci    = []
    arch_colors = []
    arch_descs  = []
    arch_hover  = []

    for a in ARCHETYPES:
        name = a["name"]
        s    = stats[name]
        arch_names.append(name)
        arch_totals.append(s["total"])
        arch_recents.append(s["recent"])
        arch_nci.append(s["avg_nci"])
        arch_colors.append(color_map[name])
        arch_descs.append(a["desc"])

        top3 = s["top_resonance"][:3]
        top3_str = "<br>".join(
            f"  {t['name']} ({t['company']}) NCI={t['nci']:.2f}" for t in top3
        )
        arch_hover.append(
            f"<b>{name}</b><br>"
            f"Total: {s['total']}<br>"
            f"Recent: {s['recent']}<br>"
            f"Avg NCI: {s['avg_nci']:.3f}<br>"
            f"<br><b>Top resonance:</b><br>{top3_str}"
        )

    # position bubbles in a circle
    n = len(arch_names)
    bubble_x = [math.cos(2 * math.pi * i / n) * 3 for i in range(n)]
    bubble_y = [math.sin(2 * math.pi * i / n) * 3 for i in range(n)]

    bubble_trace = go.Scatter(
        x=bubble_x,
        y=bubble_y,
        mode="markers+text",
        marker=dict(
            size=[math.sqrt(t) * 3.5 for t in arch_totals],
            color=arch_colors,
            opacity=0.85,
            line=dict(color="#1e293b", width=1.5),
        ),
        text=arch_names,
        textposition="middle center",
        textfont=dict(color="#e2e8f0", size=11, family="monospace"),
        hovertext=arch_hover,
        hoverinfo="text",
        customdata=list(zip(arch_totals, arch_recents, arch_nci)),
        name="Archetypes",
        visible=True,
    )

    # add NCI ring indicators (small circles around each bubble, sized by avg NCI)
    nci_trace = go.Scatter(
        x=bubble_x,
        y=bubble_y,
        mode="markers",
        marker=dict(
            size=[math.sqrt(t) * 3.5 + a * 18 for t, a in zip(arch_totals, arch_nci)],
            color=arch_colors,
            opacity=0.12,
            line=dict(color="rgba(0,0,0,0)", width=0),
        ),
        hoverinfo="skip",
        showlegend=False,
        visible=True,
    )

    # ── Chart 2: Force-Directed Graph (top 400 by NCI) ────────
    top_contacts = sorted(
        [c for c in contacts if c["recent"]],
        key=lambda x: -x["nci"]
    )[:200]

    if len(top_contacts) < 50:
        top_contacts = sorted(contacts, key=lambda x: -x["nci"])[:200]

    G = nx.Graph()
    for c in top_contacts:
        G.add_node(c["name"], **c)

    # edges: same company or same primary archetype (within top contacts)
    company_to_nodes: dict[str, list[str]] = collections.defaultdict(list)
    arch_to_nodes: dict[str, list[str]]    = collections.defaultdict(list)
    for c in top_contacts:
        if c["company"]:
            company_to_nodes[c["company"]].append(c["name"])
        arch_to_nodes[c["primary_archetype"]].append(c["name"])

    for nodes in company_to_nodes.values():
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                G.add_edge(nodes[i], nodes[j], weight=2.0)  # same company = strong

    for nodes in arch_to_nodes.values():
        for i in range(min(len(nodes), 8)):
            for j in range(i + 1, min(len(nodes), 8)):
                if not G.has_edge(nodes[i], nodes[j]):
                    G.add_edge(nodes[i], nodes[j], weight=0.5)

    pos = nx.spring_layout(G, seed=42, k=0.8, iterations=50)

    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=0.4, color="#1e293b"),
        hoverinfo="none",
        showlegend=False,
        visible=False,
    )

    node_x, node_y, node_text, node_hover, node_colors, node_sizes = [], [], [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        c = G.nodes[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node[:16] + "…" if len(node) > 16 else node)
        arch = c.get("primary_archetype", "Focused Executor")
        node_colors.append(color_map.get(arch, "#64748B"))
        node_sizes.append(8 + c.get("nci", 0) * 28)
        node_hover.append(
            f"<b>{node}</b><br>"
            f"{c.get('position','')}<br>"
            f"{c.get('company','')}<br>"
            f"Archetype: {arch}<br>"
            f"NCI: {c.get('nci',0):.3f}<br>"
            f"Connected: {c.get('year','')}"
        )

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        marker=dict(
            size=node_sizes,
            color=node_colors,
            opacity=0.9,
            line=dict(color="#0d1117", width=1),
        ),
        text=node_text,
        textposition="top center",
        textfont=dict(color="#94a3b8", size=7, family="monospace"),
        hovertext=node_hover,
        hoverinfo="text",
        showlegend=False,
        visible=False,
    )

    # ── Assemble figure ───────────────────────────────────────
    fig = go.Figure(
        data=[nci_trace, bubble_trace, edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text="ARCS Network Topology — Archetype Resonance Scan",
                font=dict(color="#e2e8f0", size=18, family="monospace"),
                x=0.5,
            ),
            paper_bgcolor="#020408",
            plot_bgcolor="#0d1117",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            font=dict(color="#e2e8f0", family="monospace"),
            margin=dict(l=20, r=20, t=80, b=20),
            height=750,
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    x=0.01, y=1.08,
                    showactive=True,
                    bgcolor="#0d1117",
                    bordercolor="#1e293b",
                    font=dict(color="#e2e8f0", family="monospace", size=12),
                    buttons=[
                        dict(
                            label="Archetype Clusters",
                            method="update",
                            args=[{"visible": [True, True, False, False]}],
                        ),
                        dict(
                            label="Force Graph (Top 200 by NCI)",
                            method="update",
                            args=[{"visible": [False, False, True, True]}],
                        ),
                    ],
                )
            ],
            annotations=[
                dict(
                    x=bx, y=by,
                    text=f"n={t}<br>NCI={n:.2f}",
                    showarrow=False,
                    font=dict(size=8, color="#64748b", family="monospace"),
                    yshift=-int(math.sqrt(t) * 1.8 + 16),
                )
                for bx, by, t, n in zip(bubble_x, bubble_y, arch_totals, arch_nci)
            ],
        )
    )

    return fig


# ─────────────────────────────────────────────────────────────
# MARKDOWN REPORT
# ─────────────────────────────────────────────────────────────

def render_md(contacts: list[dict], stats: dict) -> str:
    lines = []
    lines.append("# ARCS Archetype Resonance Scan")
    lines.append("**Subject stack:** Builder → Navigator → Chartist  |  **Total:** 11,177  |  **Date:** 2026-05-20")
    lines.append("")

    lines.append("## Archetype Distribution")
    lines.append("")
    lines.append("| Archetype | n | Recent | Avg NCI | Triune |")
    lines.append("|-----------|---|--------|---------|--------|")

    total = len(contacts)
    for a in ARCHETYPES:
        s = stats[a["name"]]
        pct = s["total"] / total * 100
        # OM if avg_nci > 0.55, UNDEFINED if > 0.35, NULL otherwise
        triune = "🟢 OM" if s["avg_nci"] > 0.55 else ("🟡 UNDEF" if s["avg_nci"] > 0.35 else "🔴 NULL")
        lines.append(
            f"| {a['name']} | {s['total']} ({pct:.1f}%) | {s['recent']} | {s['avg_nci']:.3f} | {triune} |"
        )

    lines.append("")
    lines.append("## Top Resonance Contacts (NCI ≥ 0.75)")
    lines.append("")
    lines.append("| Name | Company | Position | Archetype | NCI | Year |")
    lines.append("|------|---------|----------|-----------|-----|------|")

    high_nci = sorted([c for c in contacts if c["nci"] >= 0.75], key=lambda x: -x["nci"])[:50]
    for c in high_nci:
        name = f"[{c['name']}]({c['url']})" if c["url"] else c["name"]
        lines.append(
            f"| {name} | {c['company']} | {c['position'][:50]} | "
            f"{c['primary_archetype']} | {c['nci']:.3f} | {c['year']} |"
        )

    lines.append("")
    lines.append("## Top 10 Per Archetype (by NCI)")
    lines.append("")
    for a in ARCHETYPES:
        s = stats[a["name"]]
        lines.append(f"### {a['name']}")
        lines.append(f"*{a['desc']}*  — avg NCI: {s['avg_nci']:.3f}")
        lines.append("")
        for t in s["top_resonance"][:10]:
            lines.append(f"- **{t['name']}** @ {t['company']} — {t['position'][:60]}  (NCI {t['nci']:.3f}, {t['year']})")
        lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print("ARCS Archetype Scan — loading...")
    contacts = load_connections(CSV_PATH)
    print(f"  classified {len(contacts)} contacts")

    print("  computing stats...")
    stats = compute_stats(contacts)

    print("  building visualization...")
    fig = build_viz(contacts, stats)

    out_html = os.path.normpath(OUT_HTML)
    fig.write_html(out_html, include_plotlyjs="cdn", full_html=True)
    print(f"  wrote {out_html}")

    print("  rendering markdown...")
    md = render_md(contacts, stats)
    out_md = os.path.normpath(OUT_MD)
    with open(out_md, "w") as f:
        f.write(md)
    print(f"  wrote {out_md}")

    out_json = os.path.normpath(OUT_JSON)
    with open(out_json, "w") as f:
        json.dump({
            "meta": {"total": len(contacts), "subject_stack": [s[0] for s, _ in zip(SUBJECT_STACK, range(3))]},
            "archetype_stats": stats,
        }, f, indent=2)
    print(f"  wrote {out_json}")

    print("\n── ARCHETYPE DISTRIBUTION ──────────────────────────────")
    for a in ARCHETYPES:
        s = stats[a["name"]]
        bar = "█" * min(s["total"] // 80, 30)
        print(f"  {a['name']:20s} {s['total']:5d}  NCI={s['avg_nci']:.3f}  {bar}")

    print("\n── TOP 20 RESONANCE CONTACTS ───────────────────────────")
    top20 = sorted(contacts, key=lambda x: -x["nci"])[:20]
    for c in top20:
        print(f"  NCI={c['nci']:.3f}  {c['name']:28s} {c['primary_archetype']:18s} @ {c['company'][:30]}")


if __name__ == "__main__":
    main()
