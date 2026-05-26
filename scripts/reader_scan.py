#!/usr/bin/env python3
"""
reader_scan.py — ARCS Reader Gauntlet
======================================
Run the full ARCS Double Helix + Triune Logic on your Kindle My Clippings.txt.

Your highlights are your intellectual DNA. This script surfaces:
  - OM books (high-density diverse highlighting = genuine deep reading)
  - Intellectual topology: top concept clusters you return to
  - Cross-domain isomorphisms: the same idea in wildly different books (Orthogonal Echo)
  - Reading arc: how your concept landscape has evolved year-by-year

Data source:
  Connect Kindle via USB → open Kindle drive in Finder/Explorer
  Copy: /documents/My Clippings.txt

Usage:
  python3 reader_scan.py "My Clippings.txt"
  python3 reader_scan.py "My Clippings.txt" --subject "Builder,Chartist,Illuminator"
  python3 reader_scan.py "My Clippings.txt" --out ./my_report

Output: {basename}_arcs_scan.md + {basename}_arcs_scan.json

Note on zero-deps design choice:
  The 12-domain concept taxonomy is a hardcoded keyword dict — not NLP.
  This is intentional: a curated taxonomy is inspectable, auditable, and
  more ARCS-aligned than a black-box model. The taxonomy IS the intellectual fingerprint.

Requirements: Python 3.8+, no external packages.
"""

import argparse
import json
import os
import re
import sys
import collections
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_here = Path(__file__).resolve().parent
if str(_here) not in sys.path:
    sys.path.insert(0, str(_here))

from arcs_core import (
    DomainConfig, GauntletEntry, GauntletResult, LokiRule,
    run_gauntlet_with_dewy, render_receipt, parse_year,
    RECENT, ACTIVE, NOW,
)

# ─────────────────────────────────────────────────────────────
# READER-DOMAIN CONFIG
# ─────────────────────────────────────────────────────────────

READER_DOMAIN_CONFIG = DomainConfig(
    domain_name="Reader",
    tier1_contexts={
        # Canonical works in high-signal intellectual domains
        "thinking fast and slow","antifragile","the hard thing about hard things",
        "zero to one","poor charlie's almanack","the innovator's dilemma",
        "gödel escher bach","the structure of scientific revolutions",
        "influence","the power broker","working","the remains of the day",
        "on writing","blood meridian","infinite jest","the master and margarette",
    },
    strand_b_rules=[
        LokiRule(
            name="proximity_cluster",
            discount=0.12,
            condition_fn=lambda e: e.extra.get("proximity_cluster", False),
            explanation="3+ highlights within 10 Kindle location units — scanning behavior, not deep reading",
        ),
        LokiRule(
            name="short_highlight",
            discount=0.08,
            condition_fn=lambda e: e.extra.get("word_count", 20) < 10,
            explanation="Highlight <10 words — likely a phrase capture, insufficient for concept signal",
        ),
        LokiRule(
            name="single_book_dominance",
            discount=0.10,
            condition_fn=lambda e: e.extra.get("book_share", 0) > 0.60,
            explanation=">60% of all highlights from one book — concentration bias may inflate NCI",
        ),
    ],
    receipt_labels={
        "top_om_section": "OM Books — Genuine Deep Reading",
        "cluster_section": "Intellectual Topology (Concept Clusters)",
        "strat_section":   "Reading Arc (Year-by-Year)",
    },
)

# ─────────────────────────────────────────────────────────────
# 12-DOMAIN CONCEPT TAXONOMY
# (hardcoded keyword dict — inspectable, curated, ARCS-aligned)
# This IS the intellectual fingerprint. P8 repair.
# ─────────────────────────────────────────────────────────────

CONCEPT_TAXONOMY = [
    ("Systems",        ["system","feedback","loop","emergent","complexity","network","structure",
                         "model","second-order","dynamic","equilibrium","tipping point",
                         "nonlinear","adaptive","self-organizing"]),
    ("Capital",        ["capital","investment","return","value","risk","portfolio","asset",
                         "equity","leverage","compounding","liquidity","market","arbitrage",
                         "incentive","principal","agent","cost","price","profit","margin"]),
    ("Human Behavior", ["human","behavior","behaviour","psychology","cognitive","bias",
                         "decision","emotion","habit","motivation","identity","belief",
                         "perception","social","irrational","heuristic","judgment"]),
    ("Technology",     ["technology","software","algorithm","code","data","digital",
                         "machine","artificial","compute","platform","network effect",
                         "scalable","automation","tool","infrastructure","protocol"]),
    ("Craft",          ["craft","practice","skill","mastery","deliberate","process","work",
                         "discipline","iteration","feedback","learn","improve","expert",
                         "flow","attention","effort","quality","make","build","create"]),
    ("Leadership",     ["leadership","team","trust","culture","mission","vision","strategy",
                         "execute","hire","fire","decision","accountability","clarity",
                         "founder","ceo","manage","power","organization","influence"]),
    ("Philosophy",     ["meaning","truth","knowledge","consciousness","existence","ethical",
                         "moral","virtue","justice","freedom","beauty","language","logic",
                         "metaphor","narrative","ontology","epistemology","reason"]),
    ("Science",        ["science","experiment","hypothesis","evidence","data","theory",
                         "discovery","research","biology","physics","chemistry","evolution",
                         "brain","neuroscience","measurement","empirical","cause","effect"]),
    ("Narrative",      ["story","character","plot","tension","voice","scene","dialogue",
                         "author","reader","point of view","theme","metaphor","arc",
                         "beginning","ending","conflict","resolution","novel","fiction"]),
    ("Design",         ["design","form","function","aesthetic","user","interface","experience",
                         "prototype","iteration","constraint","elegance","visual","space",
                         "material","pattern","simplicity","purpose","beauty","architecture"]),
    ("Spirituality",   ["spirit","soul","presence","mindfulness","meditation","consciousness",
                         "transcendence","divine","sacred","ritual","surrender","awareness",
                         "ego","stillness","breath","acceptance","compassion","love","being"]),
    ("Economics",      ["economic","market","supply","demand","inflation","growth","gdp",
                         "trade","monetary","fiscal","policy","inequality","labor","wage",
                         "employment","production","consumption","wealth","distribution"]),
]

def classify_concept(highlight_text: str) -> Optional[str]:
    h = highlight_text.lower()
    scores: Dict[str, int] = {}
    for label, kws in CONCEPT_TAXONOMY:
        count = sum(1 for k in kws if k in h)
        if count:
            scores[label] = count
    if not scores:
        return None
    return max(scores, key=lambda k: scores[k])

# ─────────────────────────────────────────────────────────────
# PARSE MY CLIPPINGS.TXT
# ─────────────────────────────────────────────────────────────

CLIPPING_SEP = "=========="

def parse_clippings(path: str) -> List[Dict]:
    """Parse Kindle My Clippings.txt → list of highlight dicts."""
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        content = f.read()

    sections = content.split(CLIPPING_SEP)
    highlights = []

    for section in sections:
        lines = [l.strip() for l in section.strip().splitlines() if l.strip()]
        if len(lines) < 3:
            continue

        # Line 0: "Book Title (Author Name)"
        title_line = lines[0]
        author_match = re.search(r'\(([^)]+)\)\s*$', title_line)
        author = author_match.group(1) if author_match else ""
        title  = title_line[:title_line.rfind("(")-1].strip() if author_match else title_line

        # Line 1: "- Your Highlight on page X | Location Y-Z | Added on..."
        meta_line = lines[1]

        # Extract location
        loc_match = re.search(r'Location\s+(\d+)', meta_line, re.IGNORECASE)
        location  = int(loc_match.group(1)) if loc_match else 0

        # Extract year
        date_match = re.search(r'\b(20\d\d)\b', meta_line)
        year       = int(date_match.group(1)) if date_match else None

        # Is it a highlight (not a note)?
        if "highlight" not in meta_line.lower():
            continue

        # Line 2+: highlight text
        text = " ".join(lines[2:]).strip()
        if not text or text == "You have reached the clipping limit for this item.":
            continue

        word_count = len(text.split())
        highlights.append({
            "title":      title.strip(),
            "author":     author.strip(),
            "location":   location,
            "year":       year,
            "text":       text,
            "word_count": word_count,
        })

    return highlights

# ─────────────────────────────────────────────────────────────
# AGGREGATE BY BOOK
# ─────────────────────────────────────────────────────────────

def aggregate_books(highlights: List[Dict]) -> Tuple[List[Dict], Dict[str, int]]:
    """Aggregate highlights per book → book-level sessions."""
    books: Dict[str, Dict] = {}
    total = len(highlights)

    for h in highlights:
        t = h["title"]
        if t not in books:
            books[t] = {
                "title":        t,
                "author":       h["author"],
                "highlights":   [],
                "locations":    [],
                "years":        set(),
                "concepts":     collections.Counter(),
            }
        b = books[t]
        b["highlights"].append(h)
        b["locations"].append(h["location"])
        if h["year"]:
            b["years"].add(h["year"])
        concept = classify_concept(h["text"])
        if concept:
            b["concepts"][concept] += 1

    # Post-process
    result = []
    for title, b in books.items():
        hl    = b["highlights"]
        n     = len(hl)
        locs  = sorted(b["locations"])
        years = sorted(b["years"])

        # Proximity cluster detection: any 3+ highlights within 10 location units
        proximity_cluster = False
        for i in range(len(locs) - 2):
            if locs[i + 2] - locs[i] <= 10:
                proximity_cluster = True
                break

        # Location spread (high spread = reading the whole book)
        loc_range   = (max(locs) - min(locs)) if len(locs) >= 2 else 0
        loc_density = n / max(loc_range / 100, 1)  # highlights per 100 location units

        # Concept diversity
        top_concept = b["concepts"].most_common(1)[0][0] if b["concepts"] else None
        concept_div = len(b["concepts"])  # number of distinct concept domains

        book_share  = n / max(total, 1)
        avg_wc      = sum(h["word_count"] for h in hl) / max(n, 1)
        most_recent = max(years) if years else None

        completeness = sum([
            bool(b["author"]),
            bool(years),
            n > 3,
            concept_div > 1,
        ]) / 4.0

        result.append({
            "title":             title,
            "author":            b["author"],
            "highlight_count":   n,
            "year":              most_recent,
            "years":             years,
            "loc_range":         loc_range,
            "loc_density":       round(loc_density, 3),
            "proximity_cluster": proximity_cluster,
            "top_concept":       top_concept,
            "concept_diversity": concept_div,
            "concepts":          dict(b["concepts"].most_common()),
            "book_share":        round(book_share, 4),
            "avg_word_count":    round(avg_wc, 1),
            "data_completeness": completeness,
        })

    result.sort(key=lambda x: -x["highlight_count"])
    concept_registry = collections.Counter()
    for b in result:
        for c, cnt in b["concepts"].items():
            concept_registry[c] += cnt

    return result, dict(concept_registry)

# ─────────────────────────────────────────────────────────────
# MAP BOOKS → GAUNTLET ENTRIES
# ─────────────────────────────────────────────────────────────

def books_to_entries(books: List[Dict]) -> Tuple[List[GauntletEntry], Dict[str, int]]:
    concept_registry: Dict[str, int] = {}
    entries: List[GauntletEntry] = []

    for b in books:
        title   = b["title"]
        concept = b["top_concept"] or "Focused Executor"

        # Map concept domain → archetype for NCI
        CONCEPT_TO_ARCH = {
            "Systems":        "Chartist",
            "Capital":        "Navigator",
            "Human Behavior": "Mediator",
            "Technology":     "Instrumentor",
            "Craft":          "Builder",
            "Leadership":     "Builder",
            "Philosophy":     "Illuminator",
            "Science":        "Instrumentor",
            "Narrative":      "Illuminator",
            "Design":         "Chartist",
            "Spirituality":   "Orienter",
            "Economics":      "Navigator",
        }
        arch     = CONCEPT_TO_ARCH.get(concept, "Focused Executor")
        position = f"{arch}: {title}"
        company  = b["author"] or concept

        concept_registry[concept] = concept_registry.get(concept, 0) + b["highlight_count"]

        entries.append(GauntletEntry(
            name=title[:80],
            position=position,
            company=company,
            year=b["year"],
            extra={
                "highlight_count":   b["highlight_count"],
                "concept_diversity": b["concept_diversity"],
                "top_concept":       concept,
                "loc_range":         b["loc_range"],
                "proximity_cluster": b["proximity_cluster"],
                "book_share":        b["book_share"],
                "avg_word_count":    b["avg_word_count"],
                "data_completeness": b["data_completeness"],
                "word_count":        int(b["avg_word_count"]),
                "concepts":          b["concepts"],
            },
        ))

    return entries, concept_registry

# ─────────────────────────────────────────────────────────────
# READER-SPECIFIC RECEIPT SECTIONS
# ─────────────────────────────────────────────────────────────

def find_orthogonal_echoes(books: List[Dict]) -> List[Tuple[str, List[str]]]:
    """Detect the same concept appearing in wildly different domains (Orthogonal Echo)."""
    # A concept is 'echoing' if it appears in books from ≥3 different top-concept domains
    concept_books: Dict[str, List[str]] = {}
    for b in books:
        for concept, cnt in b["concepts"].items():
            if cnt >= 2:  # at least 2 highlights on this concept in this book
                concept_books.setdefault(concept, []).append(b["title"][:40])

    echoes = [(c, titles) for c, titles in concept_books.items() if len(titles) >= 3]
    echoes.sort(key=lambda x: -len(x[1]))
    return echoes


def render_reader_sections(results: List[GauntletResult],
                            books: List[Dict],
                            highlights: List[Dict],
                            concept_registry: Dict[str, int]) -> str:
    lines = []

    # Intellectual topology
    lines.append("## Intellectual Topology — Your Concept Landscape\n")
    lines.append("Ranked by total highlight density across all books.\n")
    lines.append("| Concept Domain | Highlights | % of total |")
    lines.append("|---|---|---|")
    total_h = sum(concept_registry.values())
    for concept, cnt in sorted(concept_registry.items(), key=lambda x: -x[1])[:12]:
        pct = (cnt / max(total_h, 1)) * 100
        lines.append(f"| **{concept}** | {cnt} | {pct:.1f}% |")
    lines.append("")

    # Orthogonal Echo Detector
    echoes = find_orthogonal_echoes(books)
    if echoes:
        lines.append("## Orthogonal Echo Detector\n")
        lines.append("The same concept appearing across wildly different books — "
                     "this is cross-domain isomorphism. These are your deepest intellectual threads.\n")
        for concept, book_titles in echoes[:8]:
            lines.append(f"### {concept}")
            for t in book_titles[:6]:
                lines.append(f"  - *{t}*")
            lines.append("")

    # Reading arc — concept evolution year-by-year
    year_concepts: Dict[int, collections.Counter] = {}
    for h in highlights:
        if h["year"]:
            concept = classify_concept(h["text"])
            if concept:
                year_concepts.setdefault(h["year"], collections.Counter())[concept] += 1

    if len(year_concepts) >= 2:
        lines.append("## Reading Arc — Concept Evolution\n")
        lines.append("How your intellectual landscape has shifted year-by-year.\n")
        for yr in sorted(year_concepts):
            top = year_concepts[yr].most_common(3)
            top_str = ", ".join(f"{c} ({n})" for c, n in top)
            lines.append(f"- **{yr}**: {top_str}")
        lines.append("")

    # OM books table
    om_books = [r for r in results if r.triune == "OM"]
    if om_books:
        lines.append("## OM Books — Deep Reading Verified\n")
        lines.append("| Book | Highlights | Concepts | Loc Range | NCI |")
        lines.append("|---|---|---|---|---|")
        for r in om_books[:20]:
            n    = r.entry.extra.get("highlight_count", 0)
            div  = r.entry.extra.get("concept_diversity", 0)
            rng  = r.entry.extra.get("loc_range", 0)
            lines.append(f"| {r.entry.name[:40]} | {n} | {div} domains | {rng} | {r.nci:.3f} |")
        lines.append("")

    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────
# CLI ENTRY POINT
# ─────────────────────────────────────────────────────────────

def parse_subject_weights(s: str) -> List[Tuple[str, float]]:
    parts   = [p.strip() for p in s.split(",")]
    weights = [1.0, 0.6, 0.3, 0.2, 0.15, 0.1, 0.1, 0.1]
    return [(p, weights[i] if i < len(weights) else 0.1) for i, p in enumerate(parts)]


def main():
    ap = argparse.ArgumentParser(description="ARCS Reader Gauntlet — Kindle forensic receipt")
    ap.add_argument("clippings", help="Path to Kindle 'My Clippings.txt'")
    ap.add_argument("--subject", default="Builder,Chartist,Illuminator",
                    help="Your archetype stack (default: Builder,Chartist,Illuminator)")
    ap.add_argument("--top",  type=int, default=20, help="Top N OM books (default: 20)")
    ap.add_argument("--out",  default=None, help="Output directory (default: same as input)")
    args = ap.parse_args()

    if not os.path.isfile(args.clippings):
        print(f"Error: file not found: {args.clippings}", file=sys.stderr)
        sys.exit(1)

    config = READER_DOMAIN_CONFIG
    config.subject_weights = parse_subject_weights(args.subject)

    out_dir  = args.out or os.path.dirname(os.path.abspath(args.clippings))
    os.makedirs(out_dir, exist_ok=True)
    basename = os.path.splitext(os.path.basename(args.clippings))[0]

    print(f"\nARCS Reader Scan — Gauntlet + Double Helix")
    print(f"  Clippings: {args.clippings}")
    print(f"  Stack:     {args.subject}")
    print(f"  Output:    {out_dir}\n")

    print("  Parsing clippings ...", end=" ")
    highlights = parse_clippings(args.clippings)
    print(f"{len(highlights)} highlights loaded")

    print("  Aggregating books ...", end=" ")
    books, concept_registry = aggregate_books(highlights)
    print(f"{len(books)} books")

    entries, _ = books_to_entries(books)

    print("  Running gauntlet ...")
    results, _undef_receipts, _folk_tags, stats = run_gauntlet_with_dewy(entries, config, concept_registry, top_n=args.top)
    print(f"  Triune: OM={stats['om']} | UNDEFINED={stats['undefined']} | NULL={stats['null']}")
    print()

    md   = render_receipt(results, config, stats, top_n=args.top)
    md  += "\n" + render_reader_sections(results, books, highlights, concept_registry)

    md_path   = os.path.join(out_dir, f"{basename}_arcs_scan.md")
    json_path = os.path.join(out_dir, f"{basename}_arcs_scan.json")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    json_out = {
        "domain":  "Reader",
        "subject": args.subject,
        "stats":   stats,
        "concept_topology": concept_registry,
        "om_books": [
            {
                "title":          r.entry.name,
                "author":         r.entry.company,
                "composite":      r.composite,
                "triune":         r.triune,
                "primary_arch":   r.primary_arch,
                "nci":            r.nci,
                "top_concept":    r.entry.extra.get("top_concept",""),
                "concept_diversity": r.entry.extra.get("concept_diversity", 0),
                "highlight_count": r.entry.extra.get("highlight_count", 0),
                "true_north":     r.l5_true_north,
                "why":            r.l5_why,
                "fired_rules":    r.fired_rules,
            }
            for r in results if r.triune == "OM"
        ],
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_out, f, indent=2)

    print(f"  Wrote: {md_path}")
    print(f"  Wrote: {json_path}")

    print(f"\n── TOP {min(10, stats['om'])} OM BOOKS ───────────────────────────────────\n")
    om = [r for r in results if r.triune == "OM"]
    for i, r in enumerate(om[:10], 1):
        n = r.entry.extra.get("highlight_count", 0)
        print(f"  {i:2d}. [{r.composite}pts] {r.entry.name[:45]:<45}  "
              f"{n} highlights  {r.entry.extra.get('top_concept','')}")


if __name__ == "__main__":
    main()
