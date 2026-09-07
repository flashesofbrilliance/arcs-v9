#!/usr/bin/env python3
"""gauntlet_cba.py — turn "is this 3M-token gauntlet worth it?" into a number.

Models the cost of the `.claude/workflows/counterpart-gauntlet.js` run and the
per-phase mechanical-vs-judgment split, then projects the token-savings-bank
levers (tier-route, mechanical pre-pass, incremental delta passes).

Stdlib only. Pure arithmetic — no network, no agents. This IS the mechanical
half of ADR-075 (the router): the cost model is deterministic, so it lives in
the shell, not in an LLM. The judgment half — which facets are safe to route
cheaper — is the human decision this script only quantifies.

Pricing cached 2026-06-24 (per claude-api skill). Per-MTok, USD.
Cache read ~0.1x input; cache write ~1.25x input. Parallel fan-out agents each
carry their OWN context, so the 6 facets do NOT share a cache prefix — that is
exactly why the 7x corpus re-read is the waste, and why the fix is architectural
(read the corpus fewer times), not "turn on caching".

Usage:
    python3 scripts/gauntlet_cba.py                 # default 3M-token run
    python3 scripts/gauntlet_cba.py --corpus 400000 # set shared-read size C
    python3 scripts/gauntlet_cba.py --heal-passes 4 # cost over a 4-run heal cycle
"""
import argparse

# --- pricing, per million tokens (in, out) --------------------------------
PRICE = {
    "opus":   (5.0, 25.0),   # claude-opus-5 / claude-opus-4-8
    "sonnet": (2.0, 10.0),   # claude-sonnet-5
    "haiku":  (1.0,  5.0),   # claude-haiku-4-5
}
CACHE_READ_MULT = 0.10       # cached input reads bill at ~10% of input rate

# --- the 6 default facets, tagged by job class ----------------------------
# mechanical  = the defect class is deterministically detectable (grep / diff /
#               set-membership); an LLM here is convenience, not necessity.
# judgment    = reading for meaning/tone; genuinely needs the strong tier.
# mixed       = some of each; keep strong but a pre-pass removes the mechanical part.
FACETS = {
    "builder":      "mixed",      # false precision + claim-vs-data (mech) / mechanism read (judg)
    "practitioner": "judgment",   # "does it respect what they solved" — meaning
    "skeptic":      "mechanical", # oversell, banned lexicon, "words they'd never say" — grep
    "connector":    "judgment",   # "does it feel managed / sized as a lead" — tone
    "situational":  "judgment",   # "does it read their situation right" — deep judgment
    "bitesize":     "mechanical", # density, cross-surface repetition — diff/dedup
}
# tier a facet runs at today vs. what it can SAFELY drop to (correctness first:
# a judgment facet never drops — the honesty gate outranks the budget).
SAFE_TIER = {"mechanical": "sonnet", "mixed": "opus", "judgment": "opus"}


def cost(tier, in_tok, out_tok, cached_in=0):
    pin, pout = PRICE[tier]
    live_in = max(in_tok - cached_in, 0)
    return (live_in * pin + cached_in * pin * CACHE_READ_MULT + out_tok * pout) / 1_000_000


def run_cost(corpus, facet_out, synth_out, facet_tiers):
    """One full gauntlet pass. Every facet reads the whole corpus C once
    (no cross-agent cache). Synth reads C again + all 6 findings."""
    findings_in = 6 * facet_out
    facet_total = sum(cost(facet_tiers[f], corpus, facet_out) for f in FACETS)
    synth_total = cost("opus", corpus + findings_in, synth_out)  # synth is effort:high — always strong
    return facet_total, synth_total


def fmt(x):
    return f"${x:,.2f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=int, default=400_000,
                    help="C = shared read (transcript+comms+surfaces+memory) each agent ingests. "
                         "Default 400k → ~3M-token run.")
    ap.add_argument("--facet-out", type=int, default=8_000, help="findings JSON per facet (output)")
    ap.add_argument("--synth-out", type=int, default=15_000, help="synthesis JSON (output)")
    ap.add_argument("--heal-passes", type=int, default=4,
                    help="how many times the gauntlet is re-run over a heal loop")
    a = ap.parse_args()

    C, FO, SO = a.corpus, a.facet_out, a.synth_out
    total_tokens = 7 * C + 6 * FO + (6 * FO + SO)  # 7 corpus reads + findings in + all outputs
    print(f"\n=== GAUNTLET CBA  (corpus C={C:,}/agent · ~{total_tokens/1e6:.1f}M tokens/run) ===\n")

    # --- baseline: everything on Opus, full re-read every pass ---
    all_opus = {f: "opus" for f in FACETS}
    f0, s0 = run_cost(C, FO, SO, all_opus)
    base = f0 + s0
    print("BASELINE  (all-Opus, full 6-facet corpus re-read):")
    print(f"  phase 1 · 6 facets read corpus x6 : {fmt(f0)}")
    print(f"  phase 2 · synth (reads corpus + 6 findings): {fmt(s0)}")
    print(f"  per run: {fmt(base)}   ·   {a.heal_passes}-pass heal cycle: {fmt(base * a.heal_passes)}\n")

    # --- lever 1: tier-route the mechanical facets to Sonnet ---
    routed = {f: SAFE_TIER[FACETS[f]] for f in FACETS}
    f1, s1 = run_cost(C, FO, SO, routed)
    moved = [f for f in FACETS if routed[f] != "opus"]
    print(f"LEVER 1 · tier-route (Sonnet for: {', '.join(moved)}):")
    print(f"  per run: {fmt(f1 + s1)}   (saves {fmt(base - (f1 + s1))}/run, "
          f"{(base-(f1+s1))/base*100:.0f}%)\n")

    # --- lever 2: mechanical pre-pass (a script) feeds a cached register card ---
    # facets read a distilled register card (~5% of C) instead of the raw corpus,
    # once the pre-pass has extracted it. Correctness goes UP (deterministic
    # defects caught every run); tokens drop because the raw corpus stops being
    # re-ingested 7x. Pre-pass itself is a script = ~$0.
    card = int(C * 0.10)  # register card + changed-surface excerpt
    f2, s2 = run_cost(card, FO, SO, routed)
    print("LEVER 2 · mechanical pre-pass + cached register card (facets read ~10% of C):")
    print(f"  per run: {fmt(f2 + s2)}   (saves {fmt(base - (f2 + s2))}/run vs baseline, "
          f"{(base-(f2+s2))/base*100:.0f}%)")
    print("  + correctness: air-gap leaks / banned lexicon / cross-surface dupes caught")
    print("    deterministically EVERY run, not probabilistically per-agent.\n")

    # --- combined over a heal cycle: pass 1 full, passes 2..N incremental ---
    # pass 1 = lever 1 (full read, tier-routed). passes 2..N = lever 2 (delta:
    # only changed surfaces vs the cached card), and only facets whose class the
    # change touched — model as 3 of 6 facets on the card-sized read.
    pass1 = f1 + s1
    delta_facets = {f: routed[f] for f in list(FACETS)[:3]}  # ~half the facets re-fire
    fd, sd = 0.0, 0.0
    for f in delta_facets:
        fd += cost(delta_facets[f], card, FO)
    sd = cost("opus", card + 3 * FO, SO)
    delta_pass = fd + sd
    cycle = pass1 + delta_pass * (a.heal_passes - 1)
    base_cycle = base * a.heal_passes
    print(f"COMBINED over {a.heal_passes}-pass heal cycle "
          f"(pass 1 full+routed, passes 2-{a.heal_passes} incremental delta):")
    print(f"  pass 1: {fmt(pass1)}   each delta pass: {fmt(delta_pass)}")
    print(f"  cycle total: {fmt(cycle)}   vs baseline cycle {fmt(base_cycle)}   "
          f"→ saves {fmt(base_cycle - cycle)} ({(base_cycle-cycle)/base_cycle*100:.0f}%)\n")

    print("READ THIS: one run is already cheap (~%s). The waste is re-running the" % fmt(base))
    print("full 6-facet corpus re-read on every heal iteration. Correctness never")
    print("drops — judgment facets stay on Opus; the pre-pass ADDS deterministic catches.\n")


if __name__ == "__main__":
    main()
