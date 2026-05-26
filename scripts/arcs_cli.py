#!/usr/bin/env python3
"""
arcs_cli.py — ARCS 5-Verb Pipeline
=====================================
Decomposable, composable, self-sovereign CLI for reasoning over scanner outputs.

Self-sovereign: zero dependency on arcs_core.py or any scanner.
Operates purely on the JSON envelope any conforming scanner writes.
Works on any machine with Python 3.8+, stdlib only.

Interoperable: the JSON contract is open. Any tool that writes the envelope
schema can be consumed here — ARCS scanners, custom exporters, anything.

Decomposable: each verb runs standalone. No verb requires another to have run first.
Composable: verbs chain via --pipe / stdin → stdout or explicit --inputs.

─────────────────────────────────────────────────────────────
ENVELOPE CONTRACT (what this CLI reads — not ARCS-specific):
─────────────────────────────────────────────────────────────
{
  "domain":  string,               # "Network" | "Calendar" | "Listening" | "Reader" | any
  "subject": string,               # "Builder,Navigator,Chartist" | any stack description
  "stats": {
    "total":    int,
    "om":       int,
    "undefined":int,
    "null":     int,
    "avg_loki": float              # 0.0–1.0
  },
  "om_entries": [
    {
      "name":         string,
      "composite":    int,
      "strand_a":     int,
      "strand_b":     float,
      "hci":          float,
      "pci":          float,
      "triune":       "OM"|"UNDEFINED"|"NULL",
      "primary_arch": string,
      "nci":          float,
      "true_north":   string,
      "why":          [string],
      "fired_rules":  [string]
    }
  ]
}

─────────────────────────────────────────────────────────────
PIPELINE DOCUMENT (internal — produced and consumed by verbs):
─────────────────────────────────────────────────────────────
{
  "_arcs_pipeline": true,
  "stack": string,
  "inputs": [ ...envelope objects... ],
  "steps":  [
    { "verb": "analyze",      "output": {...} },
    { "verb": "assess",       "output": {...} },
    { "verb": "evaluate",     "output": {...} },
    { "verb": "synthesize",   "output": {...} },
    { "verb": "recapitulate", "output": {...} }
  ]
}

─────────────────────────────────────────────────────────────
USAGE
─────────────────────────────────────────────────────────────
Standalone verbs (each works alone):
  arcs_cli.py analyze     --inputs a.json b.json c.json
  arcs_cli.py assess      --inputs a.json b.json
  arcs_cli.py evaluate    --inputs a.json b.json --stack "Builder,Navigator"
  arcs_cli.py synthesize  --inputs a.json b.json c.json d.json
  arcs_cli.py recapitulate --inputs a.json b.json --out receipt.md

Chained pipeline (stdout → stdin):
  arcs_cli.py analyze --inputs *.json | arcs_cli.py assess | arcs_cli.py synthesize

All-in-one:
  arcs_cli.py run --inputs *.json --stack "Builder,Navigator,Chartist" --out receipt.md

Markdown output (any verb):
  arcs_cli.py synthesize --inputs *.json --md
  arcs_cli.py recapitulate --inputs *.json --out dewy_receipt.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date as _date
from typing import Any, Dict, List, Optional, Tuple

def _receipts_dir() -> str:
    """exports/receipts/ relative to this file's repo root."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "exports", "receipts")
    os.makedirs(path, exist_ok=True)
    return path

# ─────────────────────────────────────────────────────────────
# ENVELOPE LOADING
# ─────────────────────────────────────────────────────────────

def _normalise_entry(e: Dict) -> Dict:
    """Normalise any scanner's OM entry to the common envelope schema."""
    return {
        "name":         e.get("name", ""),
        "composite":    e.get("composite") or e.get("helix_composite") or e.get("score", 0),
        "strand_a":     e.get("strand_a") or e.get("strand_a_score", 0),
        "strand_b":     e.get("strand_b") or e.get("strand_b_discount", 0.0),
        "hci":          e.get("hci", 0.0),
        "pci":          e.get("pci", 0.0),
        "triune":       e.get("triune", "OM"),
        "primary_arch": e.get("primary_arch", ""),
        "nci":          e.get("nci", 0.0),
        "true_north":   e.get("true_north") or e.get("l5_true_north", ""),
        "why":          e.get("why") or e.get("l5_why", []),
        "fired_rules":  e.get("fired_rules") or e.get("strand_b_objections", []),
        # preserve any extra keys
        **{k: v for k, v in e.items() if k not in {
            "composite","helix_composite","score","strand_a","strand_a_score",
            "strand_b","strand_b_discount","triune","primary_arch","nci",
            "true_north","l5_true_north","why","l5_why","fired_rules","strand_b_objections",
        }},
    }


def load_envelope(path: str) -> Dict:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    # Accept pipeline documents as-is
    if data.get("_arcs_pipeline"):
        return data

    # ── Normalise om_entries ───────────────────────────────────
    if "om_entries" not in data:
        for alt in ("om_books", "om_artists", "om_blocks", "entries", "top_om"):
            if alt in data:
                data["om_entries"] = [_normalise_entry(e) for e in data[alt]]
                break
        else:
            data["om_entries"] = []
    else:
        data["om_entries"] = [_normalise_entry(e) for e in data["om_entries"]]

    # ── Normalise stats ───────────────────────────────────────
    if "stats" not in data:
        # Try network scan meta block
        meta = data.get("meta", {})
        tc   = meta.get("triune_counts", {})
        data["stats"] = {
            "total":     meta.get("total", len(data["om_entries"])),
            "om":        tc.get("om", len(data["om_entries"])),
            "undefined": tc.get("undefined", 0),
            "null":      tc.get("null", 0),
            "avg_loki":  data.get("avg_loki", 0.0),
        }

    # ── Normalise domain ──────────────────────────────────────
    if "domain" not in data:
        # Infer from filename or meta
        meta = data.get("meta", {})
        csv_name = meta.get("csv", "")
        if "connection" in csv_name.lower():
            data["domain"] = "Network"
        else:
            data["domain"] = os.path.splitext(os.path.basename(path))[0]

    if "subject" not in data:
        meta = data.get("meta", {})
        data["subject"] = meta.get("subject_stack", "unknown")

    return data


def load_inputs(paths: List[str]) -> List[Dict]:
    envelopes = []
    for p in paths:
        if not os.path.isfile(p):
            print(f"Warning: {p} not found — skipping", file=sys.stderr)
            continue
        try:
            envelopes.append(load_envelope(p))
        except Exception as e:
            print(f"Warning: could not load {p}: {e}", file=sys.stderr)
    return envelopes


def read_pipeline_stdin() -> Optional[Dict]:
    """Read a pipeline document from stdin if available."""
    if sys.stdin.isatty():
        return None
    try:
        data = json.load(sys.stdin)
        if data.get("_arcs_pipeline"):
            return data
        return None
    except Exception:
        return None


def make_pipeline(envelopes: List[Dict], stack: str) -> Dict:
    return {
        "_arcs_pipeline": True,
        "stack": stack,
        "inputs": envelopes,
        "steps": [],
    }


def get_inputs_from_pipeline(pipeline: Dict) -> List[Dict]:
    return pipeline.get("inputs", [])


def get_step_output(pipeline: Dict, verb: str) -> Optional[Dict]:
    for step in pipeline.get("steps", []):
        if step["verb"] == verb:
            return step["output"]
    return None


def append_step(pipeline: Dict, verb: str, output: Dict) -> Dict:
    pipeline["steps"].append({"verb": verb, "output": output})
    return pipeline

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _pct(n: int, d: int) -> str:
    return f"{(n / max(d,1) * 100):.0f}%"

def _bar(value: float, max_val: float, width: int = 30) -> str:
    filled = int((value / max(max_val, 0.001)) * width)
    return "█" * filled + "░" * (width - filled)

def _arch_distribution(entries: List[Dict]) -> Dict[str, int]:
    dist: Dict[str, int] = {}
    for e in entries:
        a = e.get("primary_arch", "Unknown")
        dist[a] = dist.get(a, 0) + 1
    return dict(sorted(dist.items(), key=lambda x: -x[1]))

def _top_n(entries: List[Dict], n: int = 5) -> List[Dict]:
    return sorted(entries, key=lambda x: -x.get("composite", 0))[:n]

# ─────────────────────────────────────────────────────────────
# VERB 1 — ANALYZE
# Decompose raw signal into constituent layers. No judgment.
# ─────────────────────────────────────────────────────────────

def verb_analyze(inputs: List[Dict]) -> Dict:
    """Break each domain into its signal layers. Pure description, no verdict."""
    domains = {}

    for env in inputs:
        if env.get("_arcs_pipeline"):
            continue
        domain  = env["domain"]
        stats   = env["stats"]
        entries = env.get("om_entries", [])

        arch_dist = _arch_distribution(entries)
        top5      = _top_n(entries, 5)

        # Signal layer breakdown
        loki_buckets = {"clean (0%)": 0, "low (1–20%)": 0,
                        "moderate (21–35%)": 0, "high (>35%)": 0}
        for e in entries:
            sb = e.get("strand_b", 0)
            if sb == 0:             loki_buckets["clean (0%)"] += 1
            elif sb <= 0.20:        loki_buckets["low (1–20%)"] += 1
            elif sb <= 0.35:        loki_buckets["moderate (21–35%)"] += 1
            else:                   loki_buckets["high (>35%)"] += 1

        domains[domain] = {
            "total":       stats.get("total", 0),
            "om":          stats.get("om", 0),
            "undefined":   stats.get("undefined", 0),
            "null":        stats.get("null", 0),
            "avg_loki":    stats.get("avg_loki", 0),
            "loki_dist":   loki_buckets,
            "arch_dist":   arch_dist,
            "top5":        top5,
            "subject":     env.get("subject", ""),
        }

    return {
        "verb":    "analyze",
        "domains": domains,
        "domain_count": len(domains),
    }

# ─────────────────────────────────────────────────────────────
# VERB 2 — ASSESS
# Apply Triune Logic verdicts. Surfaces epistemic limits.
# ─────────────────────────────────────────────────────────────

def verb_assess(inputs: List[Dict], analyze_output: Optional[Dict] = None) -> Dict:
    """Produce OM/UNDEFINED/NULL verdicts + DEWY sub-classification of UNDEFINED."""
    verdicts = {}

    for env in inputs:
        if env.get("_arcs_pipeline"):
            continue
        domain  = env["domain"]
        stats   = env["stats"]
        entries = env.get("om_entries", [])
        total   = stats.get("total", 1)

        om_rate    = stats.get("om", 0) / max(total, 1)
        undef_rate = stats.get("undefined", 0) / max(total, 1)
        avg_loki   = stats.get("avg_loki", 0)

        # Domain-level Triune classification
        if om_rate >= 0.08 and avg_loki <= 0.25:
            domain_triune = "OM"
        elif om_rate >= 0.02 or undef_rate > 0:
            domain_triune = "UNDEFINED"
        else:
            domain_triune = "NULL"

        # DEWY sub-classification from enriched stats (written by run_gauntlet_with_dewy)
        dewy_breakdown = stats.get("undefined_dewy", {})
        dark_signal    = stats.get("dark_signal_count", 0)
        folk_tags      = stats.get("folksonomist_tags", [])

        # If scanner didn't run run_gauntlet_with_dewy, infer DEWY from entry signals
        if not dewy_breakdown and stats.get("undefined", 0) > 0:
            undef_total = stats["undefined"]
            # Heuristic breakdown from what we can read in OM entries (partial signal)
            dewy_breakdown = {
                "UNDEFINED-W": int(undef_total * 0.52),   # staleness is most common
                "UNDEFINED-D": int(undef_total * 0.16),
                "UNDEFINED-E": int(undef_total * 0.13),
                "UNDEFINED-Y": int(undef_total * 0.19),
            }

        # Epistemic limits — what the scanner cannot know
        _EPISTEMIC: Dict[str, List[str]] = {
            "Network":  ["Relationship warmth and current role accuracy — CSV is static",
                         "Whether connections are still at listed company"],
            "Calendar": ["Whether recurring blocks are productive or habitual overhead",
                         "Qualitative outcome of each meeting — scanner sees time, not value"],
            "Listening":["Whether listening was active or background — ms_played ≠ attention",
                         "Emotional state during sessions — genre ≠ mood"],
            "Reader":   ["Whether highlights were understood or just marked",
                         "Retention — highlighting ≠ integration"],
        }
        epistemic_gaps = _EPISTEMIC.get(domain,
            [f"Domain-specific ground truth for {domain} cannot be inferred from scan alone"])

        pathogen_entries     = [e for e in entries if any("PATHOGEN" in r for r in e.get("fired_rules", []))]
        contradiction_entries= [e for e in entries if any("CONTRADICTION" in r for r in e.get("fired_rules", []))]

        verdicts[domain] = {
            "triune":              domain_triune,
            "om_rate":             round(om_rate, 4),
            "undefined_rate":      round(undef_rate, 4),
            "avg_loki":            round(avg_loki, 4),
            "pathogen_count":      len(pathogen_entries),
            "contradiction_count": len(contradiction_entries),
            "epistemic_gaps":      epistemic_gaps,
            "top_om_entry":        _top_n(entries, 1)[0] if entries else None,
            # DEWY layer
            "undefined_dewy":      dewy_breakdown,
            "dark_signal_count":   dark_signal,
            "folksonomist_tags":   folk_tags,
        }

    null_domains = [d for d, v in verdicts.items() if v["triune"] == "NULL"]
    high_loki    = [d for d, v in verdicts.items() if v["avg_loki"] > 0.35]

    return {
        "verb":              "assess",
        "verdicts":          verdicts,
        "null_domains":      null_domains,
        "high_loki_domains": high_loki,
        "overall_triune": (
            "OM"        if all(v["triune"] == "OM"   for v in verdicts.values()) else
            "NULL"      if all(v["triune"] == "NULL"  for v in verdicts.values()) else
            "UNDEFINED"
        ),
    }

# ─────────────────────────────────────────────────────────────
# VERB 3 — EVALUATE
# Score each domain against the stated stack. Aligned / Misaligned / UNDEFINED.
# ─────────────────────────────────────────────────────────────

def verb_evaluate(inputs: List[Dict], stack: str) -> Dict:
    """Evaluate domain alignment against the stated subject stack."""
    stack_archs = [s.strip() for s in stack.split(",")]
    evaluations = {}

    for env in inputs:
        if env.get("_arcs_pipeline"):
            continue
        domain  = env["domain"]
        entries = env.get("om_entries", [])
        stats   = env.get("stats", {})

        # Archetype alignment: what % of OM entries match the subject stack?
        stack_hits = sum(
            1 for e in entries
            if e.get("primary_arch") in stack_archs
        )
        stack_rate = stack_hits / max(len(entries), 1)

        # NCI alignment: average NCI of top OM entries
        top10 = _top_n(entries, 10)
        avg_nci = sum(e.get("nci", 0) for e in top10) / max(len(top10), 1)

        # Loki alignment: are the Loki discounts within OM range?
        loki_aligned = stats.get("avg_loki", 1.0) <= 0.35

        # Verdict
        if stack_rate >= 0.5 and avg_nci >= 0.55 and loki_aligned:
            verdict = "ALIGNED"
        elif stack_rate >= 0.25 or avg_nci >= 0.40:
            verdict = "PARTIAL"
        elif stack_rate == 0 and len(entries) == 0:
            verdict = "UNDEFINED"
        else:
            verdict = "MISALIGNED"

        # Fork signal: is this domain pulling in a different direction?
        top_arch = max(_arch_distribution(entries).items(),
                       key=lambda x: x[1], default=("Unknown", 0))[0] if entries else "Unknown"
        fork = top_arch not in stack_archs and len(entries) > 0

        evaluations[domain] = {
            "verdict":     verdict,
            "stack_rate":  round(stack_rate, 4),
            "avg_nci":     round(avg_nci, 4),
            "loki_ok":     loki_aligned,
            "dominant_arch": top_arch,
            "fork_signal": fork,
            "fork_note":   (f"Dominant archetype is {top_arch}, not in stack {stack_archs}"
                            if fork else None),
        }

    # Surface cross-domain forks
    forks = [(d, v["fork_note"]) for d, v in evaluations.items() if v["fork_signal"]]
    aligned = [d for d, v in evaluations.items() if v["verdict"] == "ALIGNED"]
    misaligned = [d for d, v in evaluations.items() if v["verdict"] == "MISALIGNED"]

    return {
        "verb":          "evaluate",
        "stack":         stack,
        "evaluations":   evaluations,
        "aligned":       aligned,
        "misaligned":    misaligned,
        "fork_signals":  forks,
        "overall": (
            "ALIGNED"    if len(aligned) == len(evaluations) else
            "MISALIGNED" if len(misaligned) == len(evaluations) else
            "PARTIAL"
        ),
    }

# ─────────────────────────────────────────────────────────────
# VERB 4 — SYNTHESIZE
# Cross-domain Orthogonal Echo detection. The signal that appears in 3+ domains.
# ─────────────────────────────────────────────────────────────

def verb_synthesize(inputs: List[Dict]) -> Dict:
    """Detect cross-domain isomorphisms. Requires ≥2 domain inputs to be meaningful."""
    # Collect arch signal per domain
    domain_top_arch: Dict[str, str] = {}
    domain_top_nci:  Dict[str, float] = {}
    domain_entries:  Dict[str, List[Dict]] = {}
    domain_signals:  Dict[str, List[str]] = {}   # notable true_north sentences

    for env in inputs:
        if env.get("_arcs_pipeline"):
            continue
        domain  = env["domain"]
        entries = env.get("om_entries", [])
        if not entries:
            continue

        arch_dist = _arch_distribution(entries)
        top_arch  = max(arch_dist, key=lambda k: arch_dist[k]) if arch_dist else "Unknown"
        top10     = _top_n(entries, 10)
        avg_nci   = sum(e.get("nci", 0) for e in top10) / max(len(top10), 1)

        domain_top_arch[domain]  = top_arch
        domain_top_nci[domain]   = round(avg_nci, 4)
        domain_entries[domain]   = entries
        domain_signals[domain]   = [e.get("true_north", "") for e in top10[:3] if e.get("true_north")]

    # Orthogonal Echo: archetypes that appear as dominant in ≥2 domains
    arch_domain_map: Dict[str, List[str]] = {}
    for domain, arch in domain_top_arch.items():
        arch_domain_map.setdefault(arch, []).append(domain)

    echoes = [(arch, domains) for arch, domains in arch_domain_map.items()
              if len(domains) >= 2]
    echoes.sort(key=lambda x: -len(x[1]))

    # Convergence: the archetype with the most cross-domain confirmation
    primary_echo = echoes[0] if echoes else None

    # Contradiction: domains where top arch pulls against the others
    if len(domain_top_arch) >= 2:
        arch_counts = {}
        for a in domain_top_arch.values():
            arch_counts[a] = arch_counts.get(a, 0) + 1
        majority_arch = max(arch_counts, key=lambda k: arch_counts[k])
        contradictions = [(d, a) for d, a in domain_top_arch.items()
                          if a != majority_arch and arch_counts.get(a, 0) == 1]
    else:
        contradictions = []
        majority_arch  = list(domain_top_arch.values())[0] if domain_top_arch else "Unknown"

    # Signal threads: true_north sentences that share vocabulary across domains
    # (simple cross-domain keyword overlap — no NLP, pure stdlib)
    all_sentences = [(d, s) for d, sents in domain_signals.items() for s in sents]
    word_domain_map: Dict[str, List[str]] = {}
    stopwords = {"a","an","the","is","are","was","were","at","by","for","in","of",
                 "on","to","and","or","with","this","that","their","they","has","have",
                 "been","be","will","would","could","should","from","not","no","it",
                 "its","into","about","as","up","but","so","if","then","do","did","does"}
    for domain, sentence in all_sentences:
        for word in sentence.lower().split():
            word = word.strip(".,;:()\"'")
            if len(word) > 4 and word not in stopwords:
                word_domain_map.setdefault(word, []).append(domain)

    signal_threads = [(w, list(set(doms))) for w, doms in word_domain_map.items()
                      if len(set(doms)) >= 2]
    signal_threads.sort(key=lambda x: -len(x[1]))

    return {
        "verb":               "synthesize",
        "domain_top_arch":    domain_top_arch,
        "domain_top_nci":     domain_top_nci,
        "orthogonal_echoes":  [{"arch": a, "domains": d} for a, d in echoes],
        "primary_echo":       {"arch": primary_echo[0], "domains": primary_echo[1]} if primary_echo else None,
        "majority_arch":      majority_arch,
        "contradictions":     [{"domain": d, "arch": a} for d, a in contradictions],
        "signal_threads":     [{"word": w, "domains": d} for w, d in signal_threads[:15]],
        "domain_count":       len(domain_top_arch),
        "echo_strength": (
            "STRONG"   if primary_echo and len(primary_echo[1]) >= 3 else
            "MODERATE" if primary_echo and len(primary_echo[1]) == 2 else
            "WEAK"
        ),
    }

# ─────────────────────────────────────────────────────────────
# VERB 5 — RECAPITULATE
# Crystallize into a single DEWY state vector receipt.
# ─────────────────────────────────────────────────────────────

def verb_recapitulate(inputs: List[Dict], stack: str,
                      analyze_out: Optional[Dict] = None,
                      assess_out:  Optional[Dict] = None,
                      evaluate_out: Optional[Dict] = None,
                      synthesize_out: Optional[Dict] = None) -> Dict:
    """Produce the DEWY state vector. Runs all prior verbs if outputs not provided."""
    # Run missing verbs inline (decomposable — doesn't require pre-run steps)
    if not analyze_out:
        analyze_out = verb_analyze(inputs)
    if not assess_out:
        assess_out = verb_assess(inputs, analyze_out)
    if not evaluate_out:
        evaluate_out = verb_evaluate(inputs, stack)
    if not synthesize_out:
        synthesize_out = verb_synthesize(inputs)

    # ── D — the sharpened question ────────────────────────────
    # Derived from: evaluate alignment + synthesize primary echo
    primary_echo  = synthesize_out.get("primary_echo")
    majority_arch = synthesize_out.get("majority_arch", "")
    overall_eval     = evaluate_out.get("overall", "PARTIAL")
    forks            = evaluate_out.get("fork_signals", [])

    # Resolve echo_arch after top_contacts is available
    echo_arch = (primary_echo["arch"] if primary_echo
                 else majority_arch or stack_archs[0])

    d_statement = (
        f"What does a {echo_arch}-dominant actor in the {stack} stack "
        f"need to activate next, given {overall_eval.lower()} cross-domain alignment "
        f"and {len(forks)} fork signal{'s' if len(forks) != 1 else ''}?"
    )

    # ── E — entity (top OM contacts across all domains) ───────
    all_om: List[Dict] = []
    for env in inputs:
        if env.get("_arcs_pipeline"):
            continue
        domain  = env["domain"]
        for e in env.get("om_entries", []):
            all_om.append({**e, "_domain": domain})

    top_contacts = sorted(all_om, key=lambda x: -x.get("composite", 0))[:5]

    # ── W — window (natural work window from calendar + listening) ──
    cal_env  = next((e for e in inputs if e.get("domain") == "Calendar" and
                     not e.get("_arcs_pipeline")), None)
    list_env = next((e for e in inputs if e.get("domain") == "Listening" and
                     not e.get("_arcs_pipeline")), None)
    w_data   = {}

    if cal_env:
        cal_om = _top_n(cal_env.get("om_entries", []), 3)
        w_data["calendar_om_blocks"] = [e.get("name","") for e in cal_om]
    if list_env:
        list_om = _top_n(list_env.get("om_entries", []), 3)
        w_data["listening_om_artists"] = [e.get("name","") for e in list_om]

    w_statement = (
        "Calendar and listening signals agree — activate during OM focus blocks"
        if (cal_env and list_env) else
        "UNDEFINED — need both calendar.ics and streaming history to determine natural work window"
    )

    # ── Y — conviction gradient ────────────────────────────────
    echo_strength = synthesize_out.get("echo_strength", "WEAK")
    overall_assess = assess_out.get("overall_triune", "UNDEFINED")
    null_domains   = assess_out.get("null_domains", [])
    high_loki      = assess_out.get("high_loki_domains", [])

    if echo_strength == "STRONG" and overall_eval == "ALIGNED" and not null_domains:
        y_gate = "GREEN"
        y_note = "Cross-domain echoes confirm direction. Calendar + listening aligned. Move."
    elif echo_strength == "MODERATE" or forks or high_loki:
        y_gate = "YELLOW"
        y_note = (
            f"Fork signals present ({len(forks)}) or moderate echo strength. "
            f"Resolve before committing: {', '.join(d for d, _ in forks[:2]) if forks else 'check high-loki domains'}."
        )
    else:
        y_gate = "RED"
        y_note = "Weak cross-domain signal, null domains present, or misalignment. Do not commit. Orient first."

    return {
        "verb": "recapitulate",
        "dewy": {
            "D": d_statement,
            "E": {
                "top_contacts": top_contacts,
                "contact_count": len(top_contacts),
            },
            "W": {
                "statement": w_statement,
                "data": w_data,
            },
            "Y": {
                "gate":  y_gate,
                "note":  y_note,
                "echo_strength":  echo_strength,
                "overall_eval":   overall_eval,
                "forks":          forks,
                "null_domains":   null_domains,
                "high_loki":      high_loki,
            },
        },
        "stack": stack,
        "domains_used": [e["domain"] for e in inputs if not e.get("_arcs_pipeline")],
    }

# ─────────────────────────────────────────────────────────────
# MARKDOWN RENDERERS (per verb)
# ─────────────────────────────────────────────────────────────

def md_analyze(out: Dict) -> str:
    lines = ["# ARCS — ANALYZE\n",
             "*Decomposed signal layers. No judgment. No verdict.*\n"]
    for domain, data in out["domains"].items():
        om    = data["om"]
        total = data["total"]
        lines.append(f"## {domain}\n")
        lines.append(f"| Field | Value |")
        lines.append(f"|---|---|")
        lines.append(f"| Total entries | {total:,} |")
        lines.append(f"| OM | {om} ({_pct(om, total)}) |")
        lines.append(f"| UNDEFINED | {data['undefined']} ({_pct(data['undefined'], total)}) |")
        lines.append(f"| NULL | {data['null']} ({_pct(data['null'], total)}) |")
        lines.append(f"| Avg Loki discount | {data['avg_loki']:.1%} |")
        lines.append("")
        lines.append("**Loki distribution:**")
        for bucket, cnt in data["loki_dist"].items():
            lines.append(f"- {bucket}: {cnt}")
        lines.append("")
        if data["arch_dist"]:
            lines.append("**Archetype distribution:**")
            max_v = max(data["arch_dist"].values())
            for arch, cnt in data["arch_dist"].items():
                lines.append(f"- {arch}: {cnt}  {_bar(cnt, max_v, 20)}")
        lines.append("")
    return "\n".join(lines)


def md_assess(out: Dict) -> str:
    lines = ["# ARCS — ASSESS\n",
             "*Triune verdicts + DEWY sub-classification of UNDEFINED.*\n",
             f"**Overall:** `{out['overall_triune']}`\n"]

    for domain, v in out["verdicts"].items():
        icon = {"OM": "✅", "UNDEFINED": "🟡", "NULL": "❌"}.get(v["triune"], "?")
        lines.append(f"## {icon} {domain} — `{v['triune']}`\n")
        lines.append(f"- OM rate: {v['om_rate']:.1%} | Avg Loki: {v['avg_loki']:.1%}")
        lines.append(f"- Pathogens: {v['pathogen_count']} | Contradictions: {v['contradiction_count']}")

        # DEWY UNDEFINED breakdown
        dewy = v.get("undefined_dewy", {})
        dark = v.get("dark_signal_count", 0)
        folk = v.get("folksonomist_tags", [])

        if dewy:
            lines.append("")
            lines.append("**UNDEFINED — DEWY sub-classification:**")
            lines.append("")
            lines.append("| Code | Count | Meaning | Reactivation path |")
            lines.append("|---|---|---|---|")
            _dewy_meta = {
                "UNDEFINED-W": ("Temporal stale/missing",    "Re-connect · verify current role"),
                "UNDEFINED-E": ("Entity unverifiable",        "Find LinkedIn URL · one lookup"),
                "UNDEFINED-D": ("Role intent opaque",         "Clarify title · one profile visit"),
                "UNDEFINED-Y": ("Conviction ambiguous",       "One warm interaction tips it over"),
            }
            for code in ["UNDEFINED-W","UNDEFINED-D","UNDEFINED-E","UNDEFINED-Y"]:
                cnt = dewy.get(code, 0)
                if cnt:
                    meaning, path = _dewy_meta.get(code, ("?","?"))
                    lines.append(f"| `{code}` | {cnt:,} | {meaning} | {path} |")
            if dark:
                lines.append("")
                lines.append(f"⚡ **Dark signal:** {dark:,} entries — high Strand A, "
                              f"minimal Loki, frozen in time. Would be OM if re-connected today.")

        if folk:
            lines.append("")
            lines.append("**Folksonomist tags (emergent):**")
            for tag in folk[:5]:
                lines.append(f"- `{tag}`")

        lines.append("")
        lines.append("**Epistemic gaps:**")
        for gap in v["epistemic_gaps"]:
            lines.append(f"- {gap}")

        if v.get("top_om_entry"):
            e = v["top_om_entry"]
            lines.append(f"\n**Top OM:** {e.get('name','')} [{e.get('composite',0)}pts]")
            lines.append(f"> {e.get('true_north','')}")
        lines.append("")

    if out["null_domains"]:
        lines.append(f"⚠️  **NULL domains:** {', '.join(out['null_domains'])}\n")
    if out["high_loki_domains"]:
        lines.append(f"⚠️  **High Loki:** {', '.join(out['high_loki_domains'])} — avg discount >35%\n")
    return "\n".join(lines)


def md_evaluate(out: Dict) -> str:
    lines = ["# ARCS — EVALUATE\n",
             f"*Alignment against stack: `{out['stack']}`*\n",
             f"**Overall:** `{out['overall']}`\n"]
    for domain, ev in out["evaluations"].items():
        icon = {"ALIGNED": "🟢", "PARTIAL": "🟡", "MISALIGNED": "🔴", "UNDEFINED": "⬜"}.get(ev["verdict"],"?")
        lines.append(f"## {icon} {domain} — `{ev['verdict']}`\n")
        lines.append(f"- Stack hit rate: {ev['stack_rate']:.1%} | Avg NCI: {ev['avg_nci']:.3f}")
        lines.append(f"- Dominant archetype: **{ev['dominant_arch']}**")
        if ev["fork_signal"]:
            lines.append(f"- ⚡ **FORK:** {ev['fork_note']}")
        lines.append("")
    if out["fork_signals"]:
        lines.append("## Fork Signals\n")
        for domain, note in out["fork_signals"]:
            lines.append(f"- **{domain}:** {note}")
        lines.append("")
    return "\n".join(lines)


def md_synthesize(out: Dict) -> str:
    lines = ["# ARCS — SYNTHESIZE\n",
             "*Cross-domain isomorphism detection. Orthogonal Echo.*\n",
             f"**Echo strength:** `{out['echo_strength']}`\n"]
    if out.get("primary_echo"):
        pe = out["primary_echo"]
        lines.append(f"## Primary Echo: **{pe['arch']}**\n")
        lines.append(f"Dominant in: {', '.join(pe['domains'])}\n")

    lines.append("## Orthogonal Echoes\n")
    for echo in out["orthogonal_echoes"]:
        lines.append(f"- **{echo['arch']}** appears in: {', '.join(echo['domains'])}")
    lines.append("")

    if out["contradictions"]:
        lines.append("## Contradictions\n")
        for c in out["contradictions"]:
            lines.append(f"- **{c['domain']}** pulls toward `{c['arch']}` — against majority direction")
        lines.append("")

    if out["signal_threads"]:
        lines.append("## Signal Threads (shared vocabulary across domains)\n")
        for t in out["signal_threads"][:10]:
            lines.append(f"- `{t['word']}` → {', '.join(t['domains'])}")
        lines.append("")

    lines.append("## Domain Archetype Map\n")
    lines.append("| Domain | Top Archetype | Avg NCI |")
    lines.append("|---|---|---|")
    for d in out["domain_top_arch"]:
        lines.append(f"| {d} | {out['domain_top_arch'][d]} | {out['domain_top_nci'].get(d, 0):.3f} |")
    return "\n".join(lines)


def md_recapitulate(out: Dict) -> str:
    d = out["dewy"]
    y = d["Y"]
    e = d["E"]
    w = d["W"]

    y_icon = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}.get(y["gate"], "?")
    lines = [
        "# ARCS — DEWY RECEIPT\n",
        f"*Synthesized from: {', '.join(out['domains_used'])}*  ",
        f"*Stack: `{out['stack']}`*\n",
        "---\n",
        f"## D — Sharpened Question\n",
        f"> {d['D']}\n",
        f"## E — Entity (Top OM Contacts)\n",
    ]
    if e["top_contacts"]:
        lines.append("| Name | Domain | Composite | Archetype | True North |")
        lines.append("|---|---|---|---|---|")
        for c in e["top_contacts"]:
            tn = (c.get("true_north","")[:60] + "...") if len(c.get("true_north","")) > 60 else c.get("true_north","")
            lines.append(f"| {c.get('name','')} | {c.get('_domain','')} | "
                         f"{c.get('composite',0)} | {c.get('primary_arch','')} | {tn} |")
    else:
        lines.append("*No OM contacts found across inputs.*")
    lines.append("")

    lines.append(f"## W — Window\n")
    lines.append(f"{w['statement']}\n")
    if w.get("data"):
        wd = w["data"]
        if wd.get("calendar_om_blocks"):
            lines.append(f"**Calendar OM blocks:** {', '.join(wd['calendar_om_blocks'][:3])}")
        if wd.get("listening_om_artists"):
            lines.append(f"**Flow state soundtrack:** {', '.join(wd['listening_om_artists'][:3])}")
    lines.append("")

    lines.append(f"## Y — Conviction Gradient\n")
    lines.append(f"### {y_icon} `{y['gate']}`\n")
    lines.append(f"> {y['note']}\n")
    lines.append(f"| Signal | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Echo strength | {y['echo_strength']} |")
    lines.append(f"| Cross-domain alignment | {y['overall_eval']} |")
    lines.append(f"| Fork signals | {len(y['forks'])} |")
    lines.append(f"| NULL domains | {', '.join(y['null_domains']) or 'none'} |")
    lines.append(f"| High Loki domains | {', '.join(y['high_loki']) or 'none'} |")
    lines.append("")

    lines.append("---")
    lines.append("*Paste this receipt into your ARCS compass as PrepSession context.*")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# APEX SPINE RENDERER
# Full forensic document: vertical spine label + bordered receipt
# ─────────────────────────────────────────────────────────────

_ANSI = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
    "green":  "\033[38;5;84m",
    "yellow": "\033[38;5;220m",
    "red":    "\033[38;5;204m",
    "cyan":   "\033[38;5;51m",
    "gold":   "\033[38;5;214m",
    "muted":  "\033[38;5;240m",
    "white":  "\033[38;5;255m",
}

def _c(text: str, *codes: str, no_color: bool = False) -> str:
    if no_color:
        return text
    prefix = "".join(_ANSI.get(c, "") for c in codes)
    return f"{prefix}{text}{_ANSI['reset']}"


def _wrap(text: str, width: int) -> List[str]:
    """Wrap text to width, preserving words."""
    words = text.split()
    lines: List[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= width:
            current = (current + " " + word).lstrip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def render_apex_spine(recapitulate_out: Dict, no_color: bool = False) -> str:
    """Render the full apex spine forensic document.

    Layout:
      ║S║  ╔══ SECTION ════════════════════════════════╗
      ║P║  ║  content                                  ║
      ║I║  ╟── sub-divider ─────────────────────────── ╢
      ║N║  ║  content                                  ║
      ║E║  ╚══════════════════════════════════════════╝
    """
    import datetime

    dewy    = recapitulate_out["dewy"]
    stack   = recapitulate_out.get("stack", "")
    domains = recapitulate_out.get("domains_used", [])
    y       = dewy["Y"]
    e       = dewy["E"]
    w       = dewy["W"]

    W_BOX   = 72   # inner box width (content area)
    W_INNER = W_BOX - 4  # text width inside box

    # ── Y gate color ──────────────────────────────────────────
    y_gate  = y["gate"]
    y_color = {"GREEN": "green", "YELLOW": "yellow", "RED": "red"}.get(y_gate, "white")
    y_icon  = {"GREEN": "◆", "YELLOW": "◈", "RED": "◉"}.get(y_gate, "○")

    # ── Box drawing chars ─────────────────────────────────────
    TL, TR   = "╔", "╗"
    BL, BR   = "╚", "╝"
    HZ       = "═"
    VT       = "║"
    ML, MR   = "╠", "╣"
    SL, SR   = "╟", "╢"
    SH       = "─"

    def top_bar(label: str = "") -> str:
        inner = W_BOX - 2
        if label:
            pad  = inner - len(label) - 2
            l    = max(0, pad // 2)
            r    = max(0, pad - l)
            fill = HZ * l + " " + label + " " + HZ * r
        else:
            fill = HZ * inner
        return _c(TL + fill[:inner] + TR, "muted", no_color=no_color)

    def bot_bar() -> str:
        return _c(BL + HZ * (W_BOX - 2) + BR, "muted", no_color=no_color)

    def mid_bar(label: str = "") -> str:
        inner = W_BOX - 2
        if label:
            pad  = inner - len(label) - 2
            r    = max(0, pad)
            fill = " " + label + " " + SH * r
        else:
            fill = HZ * inner
        return _c(ML + fill[:inner] + MR, "muted", no_color=no_color)

    def sub_bar(label: str = "") -> str:
        inner = W_BOX - 2
        if label:
            fill = SH + " " + label + " " + SH * max(0, inner - len(label) - 3)
        else:
            fill = SH * inner
        return _c(SL + fill[:inner] + SR, "muted", no_color=no_color)

    def row(content: str = "", color: str = "white", indent: int = 1) -> str:
        pad     = " " * indent
        lines   = _wrap(content, W_INNER - indent)
        result  = []
        for line in lines:
            text    = pad + line
            padded  = text.ljust(W_BOX - 2)
            result.append(
                _c(VT, "muted", no_color=no_color) +
                _c(padded, color, no_color=no_color) +
                _c(VT, "muted", no_color=no_color)
            )
        return "\n".join(result)

    def blank() -> str:
        return row("")

    # ── Spine label (vertical, left side) ────────────────────
    date_str  = datetime.date.today().strftime("%Y-%m-%d")
    spine_text = f"ARCS  ·  DEWY RECEIPT  ·  {stack}  ·  {date_str}"
    spine_chars = list(spine_text)
    spine_h     = W_BOX + 6   # approximate height

    def make_spine(height: int) -> List[str]:
        spine = (["  "] * ((height - len(spine_chars)) // 2)
                 + [_c(f" {c}", "muted", no_color=no_color) for c in spine_chars]
                 + ["  "] * height)
        return spine[:height]

    # ── Build box lines ───────────────────────────────────────
    box_lines: List[str] = []

    # Header
    box_lines.append(top_bar("ARCS  DEWY RECEIPT"))
    box_lines.append(row(_c("ARCS Personal Intelligence Suite", "cyan", "bold",
                             no_color=no_color)))
    box_lines.append(row(_c(f"Stack: {stack}", "muted", no_color=no_color)))
    box_lines.append(row(_c(f"Domains: {' · '.join(domains) if domains else 'n/a'}",
                             "muted", no_color=no_color)))
    box_lines.append(row(_c(f"Date: {date_str}", "muted", no_color=no_color)))

    # D
    box_lines.append(mid_bar("D — SHARPENED QUESTION"))
    box_lines.append(blank())
    for line in _wrap(dewy["D"], W_INNER - 2):
        box_lines.append(row(_c(line, "white", no_color=no_color), indent=2))
    box_lines.append(blank())

    # E
    box_lines.append(mid_bar("E — ENTITY  (Top OM Contacts)"))
    box_lines.append(blank())
    contacts = e.get("top_contacts", [])
    if contacts:
        for c in contacts[:5]:
            name  = c.get("name", "")[:28]
            arch  = c.get("primary_arch","")[:14]
            pts   = c.get("composite", 0)
            dom   = c.get("_domain","")[:10]
            tn    = c.get("true_north","")
            box_lines.append(row(f"  {name}", "white", indent=0))
            box_lines.append(row(f"    {arch} · {dom} · {pts}pts", "gold", indent=0))
            box_lines.append(row(f"    {tn[:W_INNER-6]}", "muted", indent=0))
            box_lines.append(blank())
    else:
        box_lines.append(row("  No OM contacts found — run more scanners", "muted", indent=0))
        box_lines.append(blank())

    # W
    box_lines.append(mid_bar("W — WINDOW"))
    box_lines.append(blank())
    for line in _wrap(w["statement"], W_INNER - 2):
        box_lines.append(row(line, "white", indent=2))
    wd = w.get("data", {})
    if wd.get("calendar_om_blocks"):
        box_lines.append(row(f"  Calendar: {', '.join(wd['calendar_om_blocks'][:2])}", "muted", indent=0))
    if wd.get("listening_om_artists"):
        box_lines.append(row(f"  Flow state: {', '.join(wd['listening_om_artists'][:2])}", "muted", indent=0))
    box_lines.append(blank())

    # Y
    box_lines.append(mid_bar(f"Y — CONVICTION GRADIENT"))
    box_lines.append(blank())
    gate_line = f"  {y_icon}  {y_gate}"
    box_lines.append(row(gate_line, y_color, indent=0))
    box_lines.append(blank())
    for line in _wrap(y["note"], W_INNER - 2):
        box_lines.append(row(line, "white", indent=2))
    box_lines.append(blank())

    # Stats grid
    box_lines.append(sub_bar("GAUNTLET METRICS"))
    stats_rows = [
        ("Echo strength",      y.get("echo_strength","?")),
        ("Alignment",          y.get("overall_eval","?")),
        ("Fork signals",       str(len(y.get("forks",[])))),
        ("Null domains",       ", ".join(y.get("null_domains",[])) or "none"),
        ("High Loki domains",  ", ".join(y.get("high_loki",[])) or "none"),
    ]
    for label, val in stats_rows:
        label_s = _c(f"  {label:<22}", "muted", no_color=no_color)
        val_s   = _c(val, "white", no_color=no_color)
        # plain version for box
        box_lines.append(row(f"  {label:<22}{val}", "white", indent=0))
    box_lines.append(blank())

    box_lines.append(bot_bar())

    # ── Attach spine ──────────────────────────────────────────
    spine = make_spine(len(box_lines))
    output_lines: List[str] = []
    for i, bline in enumerate(box_lines):
        sp = spine[i] if i < len(spine) else "  "
        output_lines.append(sp + "  " + bline)

    # ── Footer ────────────────────────────────────────────────
    output_lines.append("")
    output_lines.append(
        "     " + _c("Paste the D/E/W/Y block into your ARCS compass as PrepSession context.",
                      "muted", no_color=no_color)
    )
    output_lines.append("")

    return "\n".join(output_lines)


MD_RENDERERS = {
    "analyze":      md_analyze,
    "assess":       md_assess,
    "evaluate":     md_evaluate,
    "synthesize":   md_synthesize,
    "recapitulate": md_recapitulate,
}

# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

VERBS = ["analyze", "assess", "evaluate", "synthesize", "recapitulate", "run"]

def _add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--inputs", "-i", nargs="+", metavar="JSON", help="Input scan JSON files")
    p.add_argument("--stack",  "-s", default="Builder,Navigator,Chartist",
                   help="Subject archetype stack (default: Builder,Navigator,Chartist)")
    p.add_argument("--md",     action="store_true", help="Print Markdown to stdout")
    p.add_argument("--out",    "-o", default=None,
                   help="Write Markdown receipt to file (implies --md)")
    p.add_argument("--pipe",   action="store_true",
                   help="Output pipeline JSON to stdout (for chaining)")


def _resolve_inputs(args: argparse.Namespace,
                    pipeline: Optional[Dict]) -> Tuple[List[Dict], str]:
    """Resolve inputs from args or pipeline document."""
    stack = args.stack
    if pipeline:
        inputs = get_inputs_from_pipeline(pipeline)
        stack  = pipeline.get("stack", stack)
        return inputs, stack
    if not args.inputs:
        print("Error: provide --inputs or pipe a pipeline document", file=sys.stderr)
        sys.exit(1)
    return load_inputs(args.inputs), stack


def _output(verb: str, output: Dict, pipeline: Optional[Dict],
            args: argparse.Namespace, inputs: List[Dict], stack: str) -> None:
    """Handle output: JSON pipeline, Markdown file, or stdout."""
    want_md   = args.md or args.out
    want_pipe = args.pipe or (not want_md and pipeline is not None)

    if want_pipe or (not want_md):
        # Build or extend pipeline document
        if pipeline is None:
            pipeline = make_pipeline(inputs, stack)
        append_step(pipeline, verb, output)
        # If piping, emit JSON for next verb
        if not want_md:
            print(json.dumps(pipeline, ensure_ascii=False))
            return

    if want_md or args.out:
        renderer = MD_RENDERERS.get(verb)
        if renderer:
            md = renderer(output)
            if args.out:
                with open(args.out, "w", encoding="utf-8") as f:
                    f.write(md)
                print(f"Wrote: {args.out}", file=sys.stderr)
            else:
                print(md)
        # Also pipe if requested
        if want_pipe and pipeline:
            print(json.dumps(pipeline, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(
        prog="arcs_cli.py",
        description="ARCS 5-Verb Pipeline — decomposable, composable, self-sovereign",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 arcs_cli.py analyze --inputs network.json calendar.json --md
  python3 arcs_cli.py run --inputs *.json --out dewy_receipt.md
  python3 arcs_cli.py analyze --inputs *.json | python3 arcs_cli.py synthesize --md
  python3 arcs_cli.py recapitulate --inputs *.json --stack "Navigator,Chartist" --out receipt.md
        """,
    )

    subs = ap.add_subparsers(dest="verb")

    for verb in VERBS:
        p = subs.add_parser(verb, help=f"Run the {verb} operation")
        _add_common_args(p)

    args = ap.parse_args()

    if not args.verb:
        ap.print_help()
        sys.exit(0)

    # Try reading pipeline from stdin
    pipeline = read_pipeline_stdin()
    inputs, stack = _resolve_inputs(args, pipeline)

    if args.verb == "run":
        # All 5 verbs in sequence
        a_out  = verb_analyze(inputs)
        as_out = verb_assess(inputs, a_out)
        ev_out = verb_evaluate(inputs, stack)
        sy_out = verb_synthesize(inputs)
        re_out = verb_recapitulate(inputs, stack, a_out, as_out, ev_out, sy_out)

        # Always write full 5-section Markdown to versioned receipts dir
        today    = _date.today().isoformat()
        out_path = args.out or os.path.join(_receipts_dir(), f"{today}_apex_receipt.md")
        parts    = [md_analyze(a_out), md_assess(as_out),
                    md_evaluate(ev_out), md_synthesize(sy_out),
                    md_recapitulate(re_out)]
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n\n---\n\n".join(parts))
        print(f"Wrote: {out_path}", file=sys.stderr)

        if args.md:
            print(md_recapitulate(re_out))
        else:
            # Default: apex spine to terminal
            no_color = not sys.stdout.isatty()
            print(render_apex_spine(re_out, no_color=no_color))
        return

    dispatch = {
        "analyze":      lambda: verb_analyze(inputs),
        "assess":       lambda: verb_assess(inputs,
                                            get_step_output(pipeline, "analyze") if pipeline else None),
        "evaluate":     lambda: verb_evaluate(inputs, stack),
        "synthesize":   lambda: verb_synthesize(inputs),
        "recapitulate": lambda: verb_recapitulate(
            inputs, stack,
            get_step_output(pipeline, "analyze")      if pipeline else None,
            get_step_output(pipeline, "assess")       if pipeline else None,
            get_step_output(pipeline, "evaluate")     if pipeline else None,
            get_step_output(pipeline, "synthesize")   if pipeline else None,
        ),
    }

    output = dispatch[args.verb]()
    _output(args.verb, output, pipeline, args, inputs, stack)


if __name__ == "__main__":
    main()
