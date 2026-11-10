#!/usr/bin/env python3
"""
lenses.py - run the repo's real SAGE -> LAB -> BAR -> COURT code on the Gravity Call/Put.

The operators need inputs the claim does not carry (a numeric time series, axiom marks,
somatic scores, HCI, irreversibility). Every such input below is JUDGMENT and is varied so the
report can say which verdicts depend on the choice. NGI writes go to the scratchpad, not ~/.arcs.
Usage: python3 lenses.py <repo-root>
"""
import io, json, os, sys, contextlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ["ARCS_NGI_PATH"] = str(HERE / "ngi_scratch.jsonl")
sys.path.insert(0, str(Path(sys.argv[1]) / "operators"))

from arcs_primitives import CoherenceSignal, FATEDReasoning, AxiomCheck, SomaticReading  # noqa: E402
from arcs_operators_sage import SAGEOperator  # noqa: E402
from arcs_operators_lab import LABOperator, LokiChallenge  # noqa: E402
from arcs_operators_bar import BAROperator  # noqa: E402
from arcs_constitutional_court import ConstitutionalCourt  # noqa: E402

mc = json.loads((HERE / "mc_results.json").read_text())
fw = mc["forward_P_event"]

FATED = FATEDReasoning(
    facts="x402 >165M agent tx by Apr 2026, ~half tests (rzlt.io); Allium strict filter ~$1.6M/mo real agent volume (nevermined.ai); "
          "median L2 fee 20c Feb 2024 -> 0.06c Apr 2026 (growthepie); OCC stablecoin rule effective 2027-01-18 (occ.gov); "
          "market-structure cloture failed 49-50 on 2026-09-15 (American Banker); Worldpay: agent liability unsettled.",
    assumptions="A card network or issuer will name an intent record as the dispute basis; 'requires' and 'intent record' are undefined; "
                "'or issuer' counts any issuer; ARCS's human-decision receipt is close to what a network would require.",
    tradeoffs="Entering small before the rule vs waiting for the rule; a public probability is cheap to post and cheap to lose.",
    emotions="Candidate page for a role: incentive to show a sharp, contrarian call; ARCS would sell the remedy.",
    direction="Post the call with a pre-registered resolution rule and resolver; post the outcome on 2027-06-30.",
)
SOMATIC = SomaticReading(0.5, 0.5, 0.5, 0.5, 0.5, 0.5)  # not measured: Zach's, unknowable here (judgment neutral)

SIGNALS = {  # judgment: monthly 'rule readiness' index, Nov 2025 -> Nov 2026; no sourced series exists at this grain
    "rising": [0.10, 0.12, 0.13, 0.15, 0.18, 0.20, 0.22, 0.25, 0.27, 0.29, 0.30, 0.32, 0.33],
    "flat_noisy": [0.20, 0.26, 0.18, 0.24, 0.21, 0.27, 0.19, 0.25, 0.22, 0.20, 0.26, 0.21, 0.23],
}
AXIOMS = {  # judgment
    "as_posted": AxiomCheck("TENSION", "YES", "YES", "TENSION"),  # clarity: 1/3 has no stated basis; kairos: date chosen, window not argued
    "pre_registered": AxiomCheck("YES", "YES", "YES", "TENSION"),
}
IRREV = {"public_call": 0.2, "build_commit": 0.75}  # judgment: posting a number vs committing weeks of build to the rule

LOKI = LokiChallenge(  # the substantive challenge, written from the MC, not auto-generated
    challenge_statement=("The resolution rule is not registered. Under the same priors P is about "
                         f"{fw['network_only']['p50']:.2f} (network rule only), {fw['as_written']['p50']:.2f} (as written), "
                         f"{fw['loose']['p50']:.2f} (existing agent programs count). The reading moves P more than any driver."),
    failure_modes=["'or issuer' lets any one issuer resolve it YES", "'intent record' undefined: AP2 Intent Mandate may already count",
                   "announce vs effective date not stated", "the resolver is the author, who sells the remedy"],
    hidden_assumptions=["networks move on a dispute rule within 7.6 months", "ARCS's human receipt is near a network-grade signed mandate"],
    worst_case_scenario="Author grades his own call under a reading chosen after the fact; the public ledger loses its value as proof.",
    loki_confidence=0.70, can_be_dismissed=True,
    dismissal_argument="Answerable: pre-register reading, sources and resolver before posting.",
)


def run(sig_name, ax_name, irr_name, custom_loki):
    sig = CoherenceSignal(signal=SIGNALS[sig_name], domain="decision", label=f"gravity-call/{sig_name}")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        s = SAGEOperator().run(sig, FATED, AXIOMS[ax_name], SOMATIC, hci_score=70.0, phase_id="gravity",
                               next_action="pre-register resolution", irreversibility=IRREV[irr_name])
        lab = LABOperator().run(s, "gravity", loki_challenge=LOKI if custom_loki else None)
        bar = BAROperator().run(s, lab, "gravity")
        court = ConstitutionalCourt().adjudicate(s, lab, bar, "gravity")  # docstring: harmless off RUIN_RISK
    return {"signal": sig_name, "axioms": ax_name, "irreversibility": irr_name, "loki": "custom" if custom_loki else "auto",
            "sage_nci": s.nci_score, "sage_class": s.signal_classification, "pci": round(s.pci_score, 1),
            "lab_threat": lab.loki.threat_score(), "lab_posterior": lab.bayesian.posterior_confidence,
            "lab_rec": lab.lab_recommendation, "lab_threat_level": lab.lab_threat_level,
            "bar_verdict": bar.bar_verdict, "bar_floor_nci": bar.baseline.floor_nci, "bar_asym": bar.asymmetry.asymmetry_ratio,
            "bar_kelly": bar.asymmetry.kelly_fraction, "bar_ruin": bar.ruin.ruin_detected,
            "court_verdict": court.verdict, "court_weight": court.evidence_weight,
            "court_tests": {t.test_name: t.passes for t in court.tests},
            "court_conditions": [c.condition_id for c in court.conditions]}


rows = [run(sg, ax, ir, cl) for sg in SIGNALS for ax in AXIOMS for ir in IRREV for cl in (True, False)]
out = {"note": "Real repo operators (SAGE/LAB/BAR/COURT). Inputs are judgment; see lenses.py.", "runs": rows}
(HERE / "lens_results.json").write_text(json.dumps(out, indent=1))
for r in rows:
    print({k: r[k] for k in ("signal", "axioms", "irreversibility", "loki", "sage_nci", "sage_class", "lab_threat", "lab_posterior",
                             "lab_rec", "bar_verdict", "bar_asym", "bar_kelly", "bar_ruin", "court_verdict", "court_weight", "court_tests")})
