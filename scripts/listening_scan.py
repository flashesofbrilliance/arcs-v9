#!/usr/bin/env python3
"""
listening_scan.py — ARCS Listening Gauntlet
============================================
Run the full ARCS Double Helix + Triune Logic on a Spotify streaming history export.

Your listening data knows when you're in flow state. This script surfaces:
  - OM listening windows (write-lock focus schedule)
  - Chronotype signal: when your creative energy peaks
  - OM artists / albums: what you actually listen to with intent vs background noise
  - Emotional terrain map: energy arc across the week

Data source:
  Spotify → Profile icon → Account → Privacy settings → Download your data
  Select: "Extended streaming history" (takes up to 30 days) or "Account data" (immediate)
  File: StreamingHistory_music_0.json (or multiple numbered files)

Usage:
  python3 listening_scan.py StreamingHistory_music_0.json
  python3 listening_scan.py StreamingHistory_music_0.json --subject "Builder,Navigator"
  python3 listening_scan.py StreamingHistory_music_0.json --out ./my_report

Output: {basename}_arcs_scan.md + {basename}_arcs_scan.json

Requirements: Python 3.8+, no external packages.
"""

import argparse
import json
import os
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
    versioned_out_dir,
    RECENT, ACTIVE, NOW,
)

# ─────────────────────────────────────────────────────────────
# LISTENING-DOMAIN CONFIG
# ─────────────────────────────────────────────────────────────

def _listening_strand_a(entry, config) -> tuple:
    """Strand A for listening domain.
    Score is based on engagement depth (hours listened, track diversity, intent signals)
    rather than professional archetype keywords.
    """
    score = 0
    signals = []
    hrs   = entry.extra.get("hrs_total", 0)
    plays = entry.extra.get("track_count", 0)
    skip  = entry.extra.get("skip_rate", 1.0)
    year  = entry.year or 2020

    # Engagement depth (hours → up to 80pts)
    if hrs >= 10:
        pts = 80; signals.append(f"Deep listen {hrs:.1f}h → +80")
    elif hrs >= 3:
        pts = int(hrs / 10 * 80); signals.append(f"Active listen {hrs:.1f}h → +{pts}")
    elif hrs >= 0.5:
        pts = int(hrs / 10 * 80); signals.append(f"Casual listen {hrs:.1f}h → +{pts}")
    else:
        pts = 0
    score += pts

    # Low skip rate = intentional listening (up to +40)
    intent_pts = int((1.0 - skip) * 40)
    score += intent_pts
    signals.append(f"Intent rate {1-skip:.0%} → +{intent_pts}")

    # Track diversity (>3 distinct tracks = not single-track loop) +15
    if plays >= 3:
        score += 15; signals.append(f"Diversity {plays} tracks → +15")

    # Tier-1 / canonical-signal artist +30
    name_lo = entry.name.lower()
    if any(t in name_lo for t in config.tier1_contexts):
        score += 30; signals.append(f"Canonical signal artist → +30")

    # Recency
    rec = 30 if year >= 2023 else 18 if year >= 2020 else 5
    score += rec; signals.append(f"Recency {year} → +{rec}")

    return score, signals


LISTENING_DOMAIN_CONFIG = DomainConfig(
    domain_name="Listening",
    strand_a_fn=_listening_strand_a,
    tier1_contexts={
        # Artists with elevated cultural signal (expands with domain resonance)
        "radiohead","nine inch nails","boards of canada","aphex twin","burial",
        "jon hopkins","four tet","max richter","brian eno","nils frahm",
        "kendrick lamar","frank ocean","tyler the creator","kanye west",
        "beethoven","bach","debussy","satie","arvo pärt","philip glass",
    },
    strand_b_rules=[
        LokiRule(
            name="skip_rate",
            discount=0.15,
            condition_fn=lambda e: e.extra.get("ms_played", 30001) < 30000,
            explanation="Track played <30s — skip signal, not intentional listening",
        ),
        LokiRule(
            name="shuffle_noise",
            discount=0.10,
            condition_fn=lambda e: e.extra.get("shuffle", False) is True
                                   and e.extra.get("ms_played", 0) < 60000,
            explanation="Short play in shuffle mode — low intent, high noise",
        ),
        LokiRule(
            name="ambient_loop",
            discount=0.05,
            condition_fn=lambda e: (e.extra.get("repeat_in_session", 0) > 5
                                    and e.extra.get("ms_played", 0) < 120000),
            explanation="Track repeated many times but short plays — background loop, not deep listening",
        ),
    ],
    receipt_labels={
        "top_om_section": "Flow State Windows — OM Listening Sessions",
        "cluster_section": "Archetype / Genre Topology",
        "strat_section":   "Temporal Stratigraphy (Year-by-Year)",
    },
)

# ─────────────────────────────────────────────────────────────
# GENRE / ENERGY CLASSIFICATION
# ─────────────────────────────────────────────────────────────

# Maps to ARCS archetypes for resonance scoring
LISTENING_GENRES = [
    ("Focus / Instrumental",  ["instrumental","ambient","classical","piano","orchestra",
                                "electronic","techno","minimal","drone","soundtrack",
                                "lo-fi","lofi","study"]),
    ("Builder Energy",        ["hip hop","rap","trap","drill","punk","metal","rock",
                                "hard","aggressive","gym","workout","run"]),
    ("Navigator / Jazz",      ["jazz","blues","soul","funk","r&b","rnb","bossa nova",
                                "swing","improvisation"]),
    ("Creative / Indie",      ["indie","alternative","folk","singer-songwriter","acoustic",
                                "bedroom pop","art rock","experimental","noise"]),
    ("Illuminator / World",   ["world","afrobeats","reggae","latin","samba","cumbia",
                                "bossa","flamenco","global"]),
    ("Social / Pop",          ["pop","dance","edm","house","disco","party",
                                "top 40","charts","mainstream"]),
]

def classify_genre(artist: str, track: str) -> str:
    h = (artist + " " + track).lower()
    for label, kws in LISTENING_GENRES:
        if any(k in h for k in kws):
            return label
    return "Unclassified"

# Map genre → archetype for NCI scoring
GENRE_TO_ARCHETYPE: Dict[str, str] = {
    "Focus / Instrumental":  "Chartist",
    "Builder Energy":        "Builder",
    "Navigator / Jazz":      "Navigator",
    "Creative / Indie":      "Illuminator",
    "Illuminator / World":   "Illuminator",
    "Social / Pop":          "Mediator",
    "Unclassified":          "Focused Executor",
}

# ─────────────────────────────────────────────────────────────
# LOAD SPOTIFY JSON
# ─────────────────────────────────────────────────────────────

def load_spotify(path: str) -> List[Dict]:
    """Load Spotify StreamingHistory_music_*.json — handles both old and new formats."""
    with open(path, encoding="utf-8-sig") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print(f"Warning: unexpected format in {path}", file=sys.stderr)
        return []

    parsed = []
    for item in data:
        # New extended format
        ts_raw     = item.get("ts") or item.get("endTime") or ""
        ms_played  = item.get("ms_played") or item.get("msPlayed") or 0
        artist     = item.get("master_metadata_album_artist_name") or item.get("artistName") or ""
        track      = item.get("master_metadata_track_name") or item.get("trackName") or ""
        album      = item.get("master_metadata_album_album_name") or ""
        shuffle    = item.get("shuffle", False)
        reason_end = item.get("reason_end", "")

        if not track and not artist:
            continue

        year = None
        hour = None
        month = None
        if ts_raw:
            try:
                from datetime import datetime
                # New format: "2024-01-15T09:12:34"
                # Old format: "2024-01-15 09:12"
                for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                    try:
                        dt = datetime.strptime(ts_raw[:len(fmt)+2].strip(), fmt)
                        year  = dt.year
                        hour  = dt.hour
                        month = dt.month
                        break
                    except ValueError:
                        continue
                else:
                    year = parse_year(ts_raw)
            except Exception:
                year = parse_year(ts_raw)

        parsed.append({
            "artist":     artist,
            "track":      track,
            "album":      album,
            "ms_played":  int(ms_played),
            "year":       year,
            "hour":       hour,
            "month":      month,
            "shuffle":    shuffle,
            "reason_end": reason_end,
        })

    return parsed

# ─────────────────────────────────────────────────────────────
# BUILD SESSION AGGREGATES (artist-level)
# ─────────────────────────────────────────────────────────────

def aggregate_artist_sessions(tracks: List[Dict]) -> List[Dict]:
    """Aggregate tracks into per-artist listening sessions."""
    artists: Dict[str, Dict] = {}

    for t in tracks:
        art = t["artist"]
        if not art:
            continue
        if art not in artists:
            artists[art] = {
                "artist":    art,
                "ms_total":  0,
                "plays":     0,
                "skips":     0,
                "years":     set(),
                "hours":     [],
                "tracks":    set(),
                "shuffles":  0,
                "min_year":  9999,
            }
        a = artists[art]
        a["ms_total"]  += t["ms_played"]
        a["plays"]     += 1
        if t["ms_played"] < 30000:
            a["skips"] += 1
        if t["year"]:
            a["years"].add(t["year"])
            a["min_year"] = min(a["min_year"], t["year"])
        if t["hour"] is not None:
            a["hours"].append(t["hour"])
        if t["track"]:
            a["tracks"].add(t["track"])
        if t.get("shuffle"):
            a["shuffles"] += 1

    result = []
    for art, d in artists.items():
        plays       = d["plays"]
        skip_rate   = d["skips"] / max(plays, 1)
        shuffle_pct = d["shuffles"] / max(plays, 1)
        hrs_total   = d["ms_total"] / 3_600_000
        avg_hour    = sum(d["hours"]) / len(d["hours"]) if d["hours"] else 12
        most_recent = max(d["years"]) if d["years"] else None
        result.append({
            "artist":      art,
            "ms_total":    d["ms_total"],
            "plays":       plays,
            "skip_rate":   round(skip_rate, 3),
            "shuffle_pct": round(shuffle_pct, 3),
            "hrs_total":   round(hrs_total, 2),
            "track_count": len(d["tracks"]),
            "year":        most_recent,
            "min_year":    d["min_year"] if d["min_year"] < 9999 else None,
            "avg_hour":    round(avg_hour, 1),
        })

    result.sort(key=lambda x: -x["ms_total"])
    return result

# ─────────────────────────────────────────────────────────────
# MAP ARTIST SESSIONS → GAUNTLET ENTRIES
# ─────────────────────────────────────────────────────────────

def artists_to_entries(artists: List[Dict]) -> Tuple[List[GauntletEntry], Dict[str, int]]:
    genre_registry: Dict[str, int] = {}
    entries: List[GauntletEntry] = []

    for a in artists:
        artist  = a["artist"]
        genre   = classify_genre(artist, "")
        arch    = GENRE_TO_ARCHETYPE.get(genre, "Focused Executor")
        genre_registry[genre] = genre_registry.get(genre, 0) + 1

        # Position: "Genre: ArtistName" → archetype keyword matches work
        position = f"{arch}: {artist}"
        company  = genre

        # Completeness
        completeness = sum([
            bool(artist),
            bool(a["year"]),
            a["plays"] > 5,
            a["track_count"] > 2,
        ]) / 4.0

        entries.append(GauntletEntry(
            name=artist,
            position=position,
            company=company,
            year=a["year"],
            extra={
                "ms_total":          a["ms_total"],
                "plays":             a["plays"],
                "ms_played":         int(a["ms_total"] / max(a["plays"], 1)),  # avg per play
                "skip_rate":         a["skip_rate"],
                "hrs_total":         a["hrs_total"],
                "track_count":       a["track_count"],
                "shuffle":           a["shuffle_pct"] > 0.7,
                "avg_hour":          a["avg_hour"],
                "genre":             genre,
                "data_completeness": completeness,
                "repeat_in_session": a["plays"] if a["track_count"] == 1 else 0,
            },
        ))

    return entries, genre_registry

# ─────────────────────────────────────────────────────────────
# LISTENING-SPECIFIC RECEIPT SECTIONS
# ─────────────────────────────────────────────────────────────

def render_listening_sections(results: List[GauntletResult],
                               raw_tracks: List[Dict]) -> str:
    lines = []

    # Chronotype signal — hour-of-day listening intensity
    hour_ms: Dict[int, float] = {}
    for t in raw_tracks:
        if t["hour"] is not None and t["ms_played"] > 30000:
            hour_ms[t["hour"]] = hour_ms.get(t["hour"], 0) + t["ms_played"]

    if hour_ms:
        lines.append("## Chronotype Signal — When You Actually Listen\n")
        lines.append("Hours ranked by total intentional listening time (>30s plays only).\n")
        peak_hour = max(hour_ms, key=lambda h: hour_ms[h])
        peak_hrs  = ["late night (0–5)", "early morning (5–8)", "morning (8–11)",
                     "midday (11–14)", "afternoon (14–17)", "evening (17–20)",
                     "night (20–23)"]
        bucket = min(peak_hour // 4, 6)
        lines.append(f"**Peak listening window:** `{peak_hour:02d}:00` — {peak_hrs[bucket]}")
        lines.append("")
        for h in sorted(hour_ms, key=lambda x: -hour_ms[x])[:12]:
            bar = "█" * min(int(hour_ms[h] / 600_000), 40)
            hrs = hour_ms[h] / 3_600_000
            lines.append(f"- `{h:02d}:00` {hrs:5.1f}h  {bar}")
        lines.append("")

    # Day-of-week pattern
    from datetime import datetime as _dt
    dow_ms: Dict[int, float] = {}
    for t in raw_tracks:
        if t.get("year") and t.get("month") and t.get("hour") is not None and t["ms_played"] > 30000:
            try:
                d = _dt(t["year"], t["month"], 1)
                dow = d.weekday()
                dow_ms[dow] = dow_ms.get(dow, 0) + t["ms_played"]
            except Exception:
                pass
    if dow_ms:
        days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        lines.append("## Weekly Energy Terrain\n")
        for d in range(7):
            hrs = dow_ms.get(d, 0) / 3_600_000
            bar = "█" * min(int(hrs * 2), 40)
            lines.append(f"- **{days[d]}** {hrs:5.1f}h  {bar}")
        lines.append("")

    # OM artists summary
    om_artists = [r for r in results if r.triune == "OM"]
    if om_artists:
        lines.append("## OM Artists — Intent Listening Roster\n")
        lines.append("These artists cleared the full gauntlet: high engagement, low skip rate, "
                     "multi-track diversity, temporal depth.\n")
        lines.append("| Artist | Hours | Tracks | Archetype | NCI |")
        lines.append("|---|---|---|---|---|")
        for r in om_artists[:20]:
            hrs      = r.entry.extra.get("hrs_total", 0)
            tracks   = r.entry.extra.get("track_count", 0)
            lines.append(f"| {r.entry.name} | {hrs:.1f}h | {tracks} | {r.primary_arch} | {r.nci:.3f} |")
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
    ap = argparse.ArgumentParser(description="ARCS Listening Gauntlet — Spotify forensic receipt")
    ap.add_argument("json_file", help="Path to StreamingHistory_music_*.json")
    ap.add_argument("--subject", default="Builder,Navigator,Chartist",
                    help="Your archetype stack (default: Builder,Navigator,Chartist)")
    ap.add_argument("--top",  type=int, default=20, help="Top N OM entries (default: 20)")
    ap.add_argument("--out",  default=None, help="Output directory (default: same as input)")
    args = ap.parse_args()

    if not os.path.isfile(args.json_file):
        print(f"Error: file not found: {args.json_file}", file=sys.stderr)
        sys.exit(1)

    config = LISTENING_DOMAIN_CONFIG
    config.subject_weights = parse_subject_weights(args.subject)

    out_dir  = args.out or versioned_out_dir("listening")
    os.makedirs(out_dir, exist_ok=True)
    basename = os.path.splitext(os.path.basename(args.json_file))[0]

    print(f"\nARCS Listening Scan — Gauntlet + Double Helix")
    print(f"  JSON:   {args.json_file}")
    print(f"  Stack:  {args.subject}")
    print(f"  Output: {out_dir}\n")

    print("  Loading streaming history ...", end=" ")
    raw_tracks = load_spotify(args.json_file)
    print(f"{len(raw_tracks)} track plays loaded")

    print("  Aggregating artist sessions ...", end=" ")
    artists  = aggregate_artist_sessions(raw_tracks)
    print(f"{len(artists)} artists")

    entries, genre_registry = artists_to_entries(artists)

    print("  Running gauntlet ...")
    results, _undef_receipts, _folk_tags, stats = run_gauntlet_with_dewy(entries, config, genre_registry, top_n=args.top)
    print(f"  Triune: OM={stats['om']} | UNDEFINED={stats['undefined']} | NULL={stats['null']}")
    print()

    # Render
    md   = render_receipt(results, config, stats, top_n=args.top)
    md  += "\n" + render_listening_sections(results, raw_tracks)

    md_path   = os.path.join(out_dir, f"{basename}_arcs_scan.md")
    json_path = os.path.join(out_dir, f"{basename}_arcs_scan.json")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    json_out = {
        "domain":  "Listening",
        "subject": args.subject,
        "stats":   stats,
        "om_entries": [
            {
                "name":         r.entry.name,
                "genre":        r.entry.extra.get("genre",""),
                "composite":    r.composite,
                "strand_a":     r.strand_a,
                "strand_b":     r.strand_b,
                "hci":          r.hci,
                "pci":          r.pci,
                "triune":       r.triune,
                "primary_arch": r.primary_arch,
                "nci":          r.nci,
                "hrs_total":    r.entry.extra.get("hrs_total",0),
                "track_count":  r.entry.extra.get("track_count",0),
                "true_north":   r.l5_true_north,
                "why":          r.l5_why,
                "fired_rules":  r.fired_rules,
            }
            for r in results if r.triune == "OM"
        ],
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_out, f, indent=2)

    print(f"  Wrote: {md_path}")
    print(f"  Wrote: {json_path}")

    print(f"\n── TOP {min(10, stats['om'])} OM ARTISTS ─────────────────────────────────\n")
    om = [r for r in results if r.triune == "OM"]
    for i, r in enumerate(om[:10], 1):
        hrs = r.entry.extra.get("hrs_total", 0)
        print(f"  {i:2d}. [{r.composite}pts Loki:{int(r.strand_b*100)}%] "
              f"{r.entry.name[:35]:<35} {hrs:5.1f}h  {r.entry.extra.get('genre','')}")


if __name__ == "__main__":
    main()
