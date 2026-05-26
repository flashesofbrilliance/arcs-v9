#!/usr/bin/env python3
"""
calendar_scan.py — ARCS Calendar Gauntlet
==========================================
Run the full ARCS Double Helix + Triune Logic on a .ics calendar export.

Your calendar is a crime scene. This script surfaces:
  - OM calendar blocks (write-lock focus time + high-value external meetings)
  - Deep work % vs meeting debt ratio
  - Fork points: weeks where meeting density spiked
  - Q-by-Q temporal stratigraphy (are you gaining or losing clarity?)

Data source:
  Google Calendar:  calendar.google.com → Settings → Export
  Apple Calendar:   File → Export → Export...

Usage:
  python3 calendar_scan.py calendar.ics
  python3 calendar_scan.py calendar.ics --subject "Builder,Navigator" --top 20
  python3 calendar_scan.py calendar.ics --out ./my_report

Output: {basename}_arcs_scan.md + {basename}_arcs_scan.json

Requirements: Python 3.8+, no external packages.
"""

import argparse
import collections
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ── Import shared kernel ──────────────────────────────────────
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
# CALENDAR-DOMAIN CONFIG
# ─────────────────────────────────────────────────────────────

def _calendar_strand_a(entry, config) -> tuple:
    """Strand A for calendar domain.

    Scores on intent + external signal rather than professional archetype keywords.
    Works for person-to-person Gmail calendars as well as institutional organizers.
    """
    score   = 0
    signals = []
    summary = entry.position.lower()   # event title
    org     = entry.company.lower()    # organizer domain
    year    = entry.year or 2024
    dur     = entry.extra.get("duration_min", 60)
    recur   = entry.extra.get("recurrence_count", 0)

    # ── Intent classification (up to 80pts) ──────────────────
    FOCUS_KW    = ["deep work","focus","writing","thinking","blocked","no meetings",
                   "strategy","planning","research","build","create","architect","draft",
                   "book reading","meditation","yoga","journal","reading","exercise",
                   "morning routine","evening routine","workout","run","walk","swim"]
    EXTERNAL_KW = ["investor","board","client","customer","partner","demo","pitch",
                   "interview","advisory","keynote","conference","summit","panel",
                   "workshop","offsite","intro","introduction","call with","meet with",
                   "catch-up","catch up","coffee with","lunch with"]
    BUILDER_KW  = ["arcs","product","launch","roadmap","spec","prototype","mvp",
                   "fundraise","deck","investor deck","website","branding","woof",
                   "wormhole","fractional","ita ","venture","startup",
                   # 4HWW / Atomic Habits / flow architecture vocabulary
                   "deep work","mit ","most important","big 3","power hour",
                   "maker time","maker block","maker day","manager day",
                   "theme day","themed","batch","batching","gsd","get shit done",
                   "flow","flow state","no meeting","protected","anchor",
                   "habit","routine block","weekly review","monthly review",
                   "quarterly review","annual review","shutdown","shutdown ritual"]

    is_focus    = any(k in summary for k in FOCUS_KW)
    is_external = any(k in summary for k in EXTERNAL_KW)
    is_builder  = any(k in summary for k in BUILDER_KW)

    if is_focus:
        pts = 80; signals.append(f"Focus block → +80")
    elif is_external and is_builder:
        pts = 80; signals.append(f"External Builder meeting → +80")
    elif is_external:
        pts = 65; signals.append(f"External meeting → +65")
    elif is_builder:
        pts = 55; signals.append(f"Builder work block → +55")
    else:
        pts = 20; signals.append(f"Unclassified event → +20")
    score += pts

    # ── External organizer domain (non-gmail = institutional signal) (+30) ──
    personal_domains = {"gmail.com","googlemail.com","icloud.com","yahoo.com",
                        "hotmail.com","outlook.com","me.com","mac.com",""}
    is_external_org = org not in personal_domains and org != ""
    if is_external_org:
        score += 30; signals.append(f"External organizer {org} → +30")

    # ── Tier-1 org in organizer domain (+30) ──
    if any(t in org for t in config.tier1_contexts):
        score += 30; signals.append(f"Tier-1 org → +30")

    # ── Recurrence = relationship depth (+15) ──
    if 2 <= recur <= 8:
        score += 15; signals.append(f"Recurring relationship ({recur}×) → +15")

    # ── Duration signal — substantive blocks (+15) ──
    if dur >= 60:
        score += 15; signals.append(f"Substantive block {dur}min → +15")

    # ── Recency ──
    rec = 30 if year >= 2025 else 18 if year >= 2023 else 5
    score += rec; signals.append(f"Recency {year} → +{rec}")

    return score, signals


CALENDAR_DOMAIN_CONFIG = DomainConfig(
    domain_name="Calendar",
    strand_a_fn=_calendar_strand_a,
    om_composite_min=130,   # personal/self-employed calendar — 130 is OM, not 160
    tier1_contexts={
        "external partner", "board", "investor", "customer", "client",
        "advisory", "advisor", "keynote", "panel", "conference", "summit",
        "venture", "vc", "founder", "ceo", "executive",
    },
    strand_b_rules=[
        LokiRule(
            name="recurrence_debt",
            discount=0.15,
            condition_fn=lambda e: e.extra.get("recurrence_count", 0) > 8,
            explanation="Same event recurring >8× per quarter — likely recurring overhead, not high-signal time",
        ),
        LokiRule(
            name="back_to_back",
            discount=0.10,
            condition_fn=lambda e: (e.extra.get("same_day_count", 0) >= 3
                                    and e.extra.get("duration_min", 60) < 30),
            explanation="3+ short events same day — context-switch cost; only penalises short blocks",
        ),
        LokiRule(
            name="short_recurring",
            discount=0.10,
            condition_fn=lambda e: (e.extra.get("duration_min", 60) < 15
                                     and e.extra.get("recurrence_count", 0) > 4),
            explanation="Short (<15min) recurring event — likely a status ping, not a meaningful block",
        ),
        LokiRule(
            name="no_summary",
            discount=0.08,
            condition_fn=lambda e: not e.position or e.position.strip().lower() in
                {"busy","block","hold","tentative",""},
            explanation="No meaningful event title — opaque block, cannot classify intent",
        ),
    ],
    receipt_labels={
        "top_om_section": "Top OM Calendar Blocks",
        "cluster_section": "Meeting Topology",
        "strat_section":   "Temporal Stratigraphy (Q-by-Q)",
    },
)

# ─────────────────────────────────────────────────────────────
# EVENT CLASSIFICATION (domain-specific → maps to archetypes)
# ─────────────────────────────────────────────────────────────

MEETING_TYPES = [
    ("Focus Block",     ["deep work","focus","writing","thinking","blocked","no meetings",
                         "strategy","planning","review","prep","research"]),
    ("1:1",             ["1:1","1-1","one on one","one-on-one","sync with","check-in with",
                         "checkin with","coffee with","lunch with","meet with"]),
    ("External",        ["call with","meeting with","investor","board","client","customer",
                         "partner","demo","pitch","interview","advisory","keynote","conference",
                         "summit","panel","workshop","offsite"]),
    ("Team Sync",       ["team","standup","stand-up","all hands","all-hands","retrospective",
                         "sprint","scrum","weekly","monthly","quarterly"]),
    ("Admin / Personal",["doctor","dentist","personal","family","travel","flight","appointment",
                         "haircut","gym","workout","dinner","lunch"]),
]

def classify_event_type(summary: str) -> str:
    h = summary.lower()
    for label, kws in MEETING_TYPES:
        if any(k in h for k in kws):
            return label
    return "Unclassified"

# ─────────────────────────────────────────────────────────────
# .ICS PARSER (stdlib only — scoped to what ARCS needs)
#
# Fields extracted: SUMMARY, ORGANIZER, DTSTART, DTEND/DURATION, RRULE
# VTIMEZONE, VALARM, ATTENDEES intentionally ignored in v1
# ─────────────────────────────────────────────────────────────

def _unfold(text: str) -> str:
    """Unfold .ics line continuations (RFC 5545 §3.1)."""
    return re.sub(r"\r?\n[ \t]", "", text)

def _parse_dt(val: str) -> Optional[datetime]:
    """Parse DTSTART/DTEND value (date or datetime, local or UTC)."""
    val = val.split(";")[-1]  # strip VALUE=DATE or TZID= prefix if present
    val = val.replace("Z", "").strip()
    for fmt in ("%Y%m%dT%H%M%S", "%Y%m%d"):
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            pass
    return None

def _parse_duration(val: str) -> int:
    """Parse DURATION:PT1H30M → minutes."""
    minutes = 0
    for days in re.findall(r"(\d+)D", val):
        minutes += int(days) * 1440
    for hours in re.findall(r"(\d+)H", val):
        minutes += int(hours) * 60
    for mins in re.findall(r"(\d+)M", val):
        minutes += int(mins)
    return minutes or 60  # default 60 if unparseable

def parse_ics(path: str) -> List[Dict]:
    """Parse .ics file → list of event dicts."""
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        raw = f.read()

    text    = _unfold(raw)
    events  = []
    current: Optional[Dict] = None

    for line in text.splitlines():
        line = line.strip()

        if line == "BEGIN:VEVENT":
            current = {}
            continue
        if line == "END:VEVENT":
            if current is not None:
                events.append(current)
            current = None
            continue
        if current is None:
            continue

        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.split(";")[0].upper()  # strip params

        if key == "SUMMARY":
            current["summary"] = val.strip()
        elif key in ("DTSTART", "DTSTART;VALUE=DATE"):
            current["dtstart_raw"] = val.strip()
            dt = _parse_dt(val.strip())
            if dt:
                current["year"]  = dt.year
                current["month"] = dt.month
                current["hour"]  = dt.hour
        elif key in ("DTEND", "DTEND;VALUE=DATE"):
            current["dtend_raw"] = val.strip()
            dt_end = _parse_dt(val.strip())
            if dt_end and "year" in current:
                dt_start = _parse_dt(current.get("dtstart_raw", ""))
                if dt_start:
                    diff = (dt_end - dt_start).total_seconds() / 60
                    current["duration_min"] = max(int(diff), 0)
        elif key == "DURATION":
            current["duration_min"] = _parse_duration(val)
        elif key == "RRULE":
            # Heuristic: count approximate annual occurrences
            freq = re.search(r"FREQ=(\w+)", val)
            freq_val = (freq.group(1) if freq else "").upper()
            freq_count = {"DAILY": 260, "WEEKLY": 52, "BIWEEKLY": 26,
                          "MONTHLY": 12, "YEARLY": 1}.get(freq_val, 4)
            current["recurrence_count"] = current.get("recurrence_count", 0) + freq_count
        elif key == "ORGANIZER":
            # Extract display name or email
            name_match = re.search(r'CN=([^:;]+)', line, re.IGNORECASE)
            current["organizer"] = name_match.group(1).strip() if name_match else val.strip()

    return events

# ─────────────────────────────────────────────────────────────
# BUILD COMPANY REGISTRY (event type → event count for hub bonus)
# ─────────────────────────────────────────────────────────────

def build_event_registry(events: List[Dict]) -> Dict[str, int]:
    reg: Dict[str, int] = {}
    for e in events:
        org = e.get("organizer") or e.get("summary", "")[:40]
        reg[org] = reg.get(org, 0) + 1
    return reg

# ─────────────────────────────────────────────────────────────
# MAP EVENTS → GAUNTLET ENTRIES
# ─────────────────────────────────────────────────────────────

def events_to_entries(events: List[Dict]) -> Tuple[List[GauntletEntry], Dict[str, int]]:
    """Convert .ics events to GauntletEntry objects + event registry."""
    # Count events per day to detect back-to-back density
    day_counts: Dict[str, int] = {}
    for ev in events:
        if ev.get("year") and ev.get("month"):
            key = f"{ev['year']}-{ev['month']:02d}"
            day_counts[key] = day_counts.get(key, 0) + 1

    entries: List[GauntletEntry] = []
    event_type_registry: Dict[str, int] = {}

    for ev in events:
        summary  = ev.get("summary") or "Untitled"
        org      = ev.get("organizer") or "Unknown"
        year     = ev.get("year")
        dur      = ev.get("duration_min", 60)
        recur    = ev.get("recurrence_count", 0)
        ev_type  = classify_event_type(summary)
        event_type_registry[ev_type] = event_type_registry.get(ev_type, 0) + 1

        # Count same-day events as proxy for back-to-back density
        month_key     = f"{year}-{ev.get('month', 1):02d}" if year else ""
        same_day_approx = max(0, day_counts.get(month_key, 0) // 22 - 1)  # rough daily avg

        # data_completeness for HCI
        completeness = sum([
            bool(summary and len(summary) > 5),
            bool(org and org != "Unknown"),
            bool(year),
            bool(dur and dur > 0),
        ]) / 4.0

        entries.append(GauntletEntry(
            name=summary[:60],
            position=f"{ev_type}: {summary}"[:120],
            company=org[:60],
            year=year,
            extra={
                "duration_min":       dur,
                "recurrence_count":   recur,
                "same_day_count":     same_day_approx,
                "event_type":         ev_type,
                "data_completeness":  completeness,
                "hour":               ev.get("hour"),
                "month":              ev.get("month"),
            },
        ))

    # Use event_type as company_registry proxy for hub detection
    return entries, event_type_registry

# ─────────────────────────────────────────────────────────────
# CALENDAR-SPECIFIC RECEIPT SECTIONS
# ─────────────────────────────────────────────────────────────

def render_calendar_sections(results: List[GauntletResult],
                              entries: List[GauntletEntry]) -> str:
    """Extra sections specific to calendar domain."""
    lines = []

    # Deep Work % Arc
    lines.append("## Deep Work % Arc\n")
    focus_count  = sum(1 for r in results if "focus block" in r.entry.position.lower()
                       or "focus" in r.entry.extra.get("event_type", "").lower())
    total_passed = len(results)
    deep_pct     = (focus_count / max(total_passed, 1)) * 100
    meeting_debt = 100 - deep_pct
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Total events (L0 passed) | {total_passed} |")
    lines.append(f"| Focus / deep work blocks | {focus_count} ({deep_pct:.0f}%) |")
    lines.append(f"| Meeting + admin overhead | {total_passed - focus_count} ({meeting_debt:.0f}%) |")
    lines.append("")

    # Fork Points — months with highest event density
    month_counts: Dict[str, int] = {}
    for r in results:
        if r.entry.year and r.entry.extra.get("month"):
            key = f"{r.entry.year}-{r.entry.extra['month']:02d}"
            month_counts[key] = month_counts.get(key, 0) + 1

    if month_counts:
        avg = sum(month_counts.values()) / len(month_counts)
        fork_months = [(k, v) for k, v in month_counts.items() if v > avg * 1.5]
        fork_months.sort(key=lambda x: -x[1])
        if fork_months:
            lines.append("## Fork Points (High-Density Months)\n")
            lines.append("Months where meeting load spiked >50% above your average.")
            lines.append("These are FORK events — commitments that reshaped your terrain.\n")
            for month, cnt in fork_months[:8]:
                bar = "█" * min(cnt // 3, 30)
                lines.append(f"- **{month}**: {cnt} events  {bar}")
            lines.append("")

    # Hour-of-day distribution (when do meetings happen?)
    hour_counts: Dict[int, int] = {}
    for r in results:
        h = r.entry.extra.get("hour")
        if h is not None:
            hour_counts[h] = hour_counts.get(h, 0) + 1
    if hour_counts:
        lines.append("## Meeting Time Distribution\n")
        for h in sorted(hour_counts):
            bar = "█" * min(hour_counts[h] // 2, 30)
            label = f"{h:02d}:00"
            lines.append(f"- `{label}` {hour_counts[h]:3d}  {bar}")
        lines.append("")

    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────
# CLI ENTRY POINT
# ─────────────────────────────────────────────────────────────

def parse_subject_weights(subject_str: str) -> List[Tuple[str, float]]:
    parts    = [p.strip() for p in subject_str.split(",")]
    weights  = [1.0, 0.6, 0.3, 0.2, 0.15, 0.1, 0.1, 0.1]
    return [(p, weights[i] if i < len(weights) else 0.1) for i, p in enumerate(parts)]


def main():
    ap = argparse.ArgumentParser(description="ARCS Calendar Gauntlet — .ics forensic receipt")
    ap.add_argument("ics", help="Path to .ics calendar export file")
    ap.add_argument("--subject", default="Builder,Navigator,Chartist",
                    help="Your archetype stack, comma-separated (default: Builder,Navigator,Chartist)")
    ap.add_argument("--top",  type=int, default=20, help="Top N OM entries to show (default: 20)")
    ap.add_argument("--out",  default=None, help="Output directory (default: same as input)")
    args = ap.parse_args()

    if not os.path.isfile(args.ics):
        print(f"Error: file not found: {args.ics}", file=sys.stderr)
        sys.exit(1)

    # Config
    config = CALENDAR_DOMAIN_CONFIG
    config.subject_weights = parse_subject_weights(args.subject)

    out_dir  = args.out or versioned_out_dir("calendar")
    os.makedirs(out_dir, exist_ok=True)
    basename = os.path.splitext(os.path.basename(args.ics))[0]

    print(f"\nARCS Calendar Scan — Gauntlet + Double Helix")
    print(f"  ICS:    {args.ics}")
    print(f"  Stack:  {args.subject}")
    print(f"  Output: {out_dir}\n")

    # Parse
    print("  Parsing .ics ...", end=" ")
    events = parse_ics(args.ics)
    print(f"{len(events)} events loaded")

    # Map to entries
    entries, event_registry = events_to_entries(events)

    # Run gauntlet
    print("  Running gauntlet ...")
    results, _undef_receipts, _folk_tags, stats = run_gauntlet_with_dewy(entries, config, event_registry, top_n=args.top)

    om_count = stats["om"]
    print(f"  Triune: OM={om_count} | UNDEFINED={stats['undefined']} | NULL={stats['null']}")
    print(f"  Pathogens detected: {stats['pathogens']}")
    print()

    # Build report
    md   = render_receipt(results, config, stats, top_n=args.top)
    md  += "\n" + render_calendar_sections(results, entries)

    # Write outputs
    md_path   = os.path.join(out_dir, f"{basename}_arcs_scan.md")
    json_path = os.path.join(out_dir, f"{basename}_arcs_scan.json")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    json_out = {
        "domain":  "Calendar",
        "subject": args.subject,
        "stats":   stats,
        "om_entries": [
            {
                "name":         r.entry.name,
                "position":     r.entry.position,
                "company":      r.entry.company,
                "year":         r.entry.year,
                "composite":    r.composite,
                "strand_a":     r.strand_a,
                "strand_b":     r.strand_b,
                "hci":          r.hci,
                "pci":          r.pci,
                "triune":       r.triune,
                "primary_arch": r.primary_arch,
                "nci":          r.nci,
                "true_north":   r.l5_true_north,
                "why":          r.l5_why,
                "fired_rules":  r.fired_rules,
                "event_type":   r.entry.extra.get("event_type",""),
                "duration_min": r.entry.extra.get("duration_min", 0),
            }
            for r in results if r.triune == "OM"
        ],
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_out, f, indent=2)

    print(f"  Wrote: {md_path}")
    print(f"  Wrote: {json_path}")

    # Print top 10 to terminal
    print(f"\n── TOP {min(10, om_count)} OM CALENDAR BLOCKS ──────────────────────────\n")
    om_results = [r for r in results if r.triune == "OM"]
    for i, r in enumerate(om_results[:10], 1):
        loki_pct = int(r.strand_b * 100)
        print(f"  {i:2d}. [{r.composite}pts Loki:{loki_pct}%] {r.entry.name[:45]:<45} "
              f"({r.entry.extra.get('event_type','?')})")
        print(f"      → {r.l5_true_north[:90]}")


if __name__ == "__main__":
    main()
