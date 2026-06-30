"""
Seed the ARCS template library with 12 BAR (Belief-Action-Rationale) templates.
One template per cell: stakes ∈ {low, medium, high} × horizon ∈ {today, this-week,
this-quarter, multi-year}.

These are canonical skeletons. Edit the skeleton strings before inserting if any
phrasing feels off — that is the salt-to-taste step. Once inserted, the door closes.

Run after arcs_init_bundles.py:
  python A.R.C.S/arcs_seed_bar.py

Re-running is safe: uses upsert by template_id.
"""

import urllib.request
import json
import sys
from datetime import datetime, timezone

GIGI_BASE = "http://localhost:3142"
CREATED_AT = int(datetime.now(timezone.utc).timestamp() * 1000)

# fmt: off
BAR_TEMPLATES = [
    # ── LOW STAKES ──────────────────────────────────────────────────────────
    {
        "template_id": "BAR_low_today",
        "macro_family": "BAR",
        "stakes": "low",
        "horizon": "today",
        "mode": "decide",
        "skeleton": (
            "Belief: I believe {question} points toward {jtbd}. "
            "The deciding factor today is whether the cost of being wrong is acceptable by end of day. "
            "Action: Choose the path with the lower reversal cost — you can revisit this before the day ends. "
            "Rationale: At low stakes with a same-day horizon, speed of movement beats depth of analysis. "
            "The right answer is the one you can actually execute before tonight."
        ),
        "source": "canonical",
        "version": 1,
        "created_at": CREATED_AT,
    },
    {
        "template_id": "BAR_low_this-week",
        "macro_family": "BAR",
        "stakes": "low",
        "horizon": "this-week",
        "mode": "decide",
        "skeleton": (
            "Belief: Regarding {question} — with {jtbd} as the underlying job — "
            "the stakes are low enough that the cost of a wrong call this week is recoverable. "
            "Action: Make the call now. Assign one check-in point mid-week to scan for drift. "
            "Rationale: Weekly horizon with low stakes rewards decisive motion over deliberation. "
            "A wrong answer corrected by Wednesday is better than the right answer delivered Friday."
        ),
        "source": "canonical",
        "version": 1,
        "created_at": CREATED_AT,
    },
    {
        "template_id": "BAR_low_this-quarter",
        "macro_family": "BAR",
        "stakes": "low",
        "horizon": "this-quarter",
        "mode": "decide",
        "skeleton": (
            "Belief: {question} sits inside the larger frame of {jtbd}. "
            "At low stakes over a quarter, the risk is not making the wrong call — "
            "it is letting a small question occupy disproportionate attention. "
            "Action: Decide once, log the rationale, and set a single quarterly review trigger. "
            "Rationale: Low-stakes quarterly decisions should be batched and minimized. "
            "The real work is elsewhere."
        ),
        "source": "canonical",
        "version": 1,
        "created_at": CREATED_AT,
    },
    {
        "template_id": "BAR_low_multi-year",
        "macro_family": "BAR",
        "stakes": "low",
        "horizon": "multi-year",
        "mode": "decide",
        "skeleton": (
            "Belief: {question} may feel low-stakes, but a multi-year horizon means "
            "even small choices compound. The job-to-be-done — {jtbd} — will look different "
            "in two years than it does today. "
            "Action: Check whether 'low stakes' is accurate over this horizon before deciding. "
            "If still low: decide, document, and schedule a yearly reassessment. "
            "Rationale: Low stakes + long horizon is a common mismatch. "
            "Most 'small' multi-year decisions are actually medium stakes with delayed visibility."
        ),
        "source": "canonical",
        "version": 1,
        "created_at": CREATED_AT,
    },

    # ── MEDIUM STAKES ────────────────────────────────────────────────────────
    {
        "template_id": "BAR_medium_today",
        "macro_family": "BAR",
        "stakes": "medium",
        "horizon": "today",
        "mode": "decide",
        "skeleton": (
            "Belief: {question} — anchored in {jtbd} — is a medium-stakes call "
            "that must land today. The window is closing. "
            "Action: Identify the single piece of information that would most change this call. "
            "If you can get it in under 30 minutes, get it. Otherwise, decide now with what you have. "
            "Rationale: Medium stakes + same-day deadline is the classic paralysis trap. "
            "The cost of delay is now higher than the cost of an imperfect decision. Decide."
        ),
        "source": "canonical",
        "version": 1,
        "created_at": CREATED_AT,
    },
    {
        "template_id": "BAR_medium_this-week",
        "macro_family": "BAR",
        "stakes": "medium",
        "horizon": "this-week",
        "mode": "decide",
        "skeleton": (
            "Belief: {question} is a real decision — not routine noise. "
            "The job it serves ({jtbd}) deserves a structured answer this week. "
            "Action: State the three most likely outcomes. Score each by desirability and reversibility. "
            "Choose the highest-desirability path that is reversible. If none are reversible, "
            "choose the least-bad irreversible option and name the trip-wire that would force a pivot. "
            "Rationale: Medium stakes with a week of runway is enough time to be systematic "
            "without being slow."
        ),
        "source": "canonical",
        "version": 1,
        "created_at": CREATED_AT,
    },
    {
        "template_id": "BAR_medium_this-quarter",
        "macro_family": "BAR",
        "stakes": "medium",
        "horizon": "this-quarter",
        "mode": "decide",
        "skeleton": (
            "Belief: {question} shapes a meaningful part of this quarter. "
            "It is not existential, but it is not trivial — it lands in the zone where "
            "the quality of the decision process matters as much as the outcome. "
            "The underlying job: {jtbd}. "
            "Action: Name the constraints that are actually fixed vs. merely assumed. "
            "For each assumed constraint, test it before locking in. "
            "Rationale: Most medium-stakes quarterly decisions are constrained by assumptions "
            "that could be removed — but only if you look."
        ),
        "source": "canonical",
        "version": 1,
        "created_at": CREATED_AT,
    },
    {
        "template_id": "BAR_medium_multi-year",
        "macro_family": "BAR",
        "stakes": "medium",
        "horizon": "multi-year",
        "mode": "decide",
        "skeleton": (
            "Belief: {question} is medium stakes today but will compound over years. "
            "The job-to-be-done — {jtbd} — will evolve, and this decision seeds that evolution. "
            "Action: Frame the decision as a series of checkpoints, not a single choice. "
            "What must be true at 6 months, 12 months, 24 months for this path to remain correct? "
            "Name those conditions now. Build in one deliberate reassessment per year. "
            "Rationale: Medium stakes + multi-year = the highest-leverage design moment. "
            "The path you choose here is the path you'll optimize within. Choose the wider path."
        ),
        "source": "canonical",
        "version": 1,
        "created_at": CREATED_AT,
    },

    # ── HIGH STAKES ──────────────────────────────────────────────────────────
    {
        "template_id": "BAR_high_today",
        "macro_family": "BAR",
        "stakes": "high",
        "horizon": "today",
        "mode": "decide",
        "skeleton": (
            "Belief: {question} is high-stakes and the clock has run out. "
            "You are deciding now, not because you have enough information, "
            "but because not deciding is also a decision. The job at stake: {jtbd}. "
            "Action: Name the worst-case outcome. Name what you can still do to limit it after the call. "
            "Make the call. Write one sentence explaining why. "
            "Rationale: High stakes + today means the decision is already late. "
            "Every minute of deliberation from here is paid for by execution time. "
            "The clarity you want is not coming. Move."
        ),
        "source": "canonical",
        "version": 1,
        "created_at": CREATED_AT,
    },
    {
        "template_id": "BAR_high_this-week",
        "macro_family": "BAR",
        "stakes": "high",
        "horizon": "this-week",
        "mode": "decide",
        "skeleton": (
            "Belief: {question} carries real weight. The job-to-be-done is {jtbd} — "
            "and a wrong call this week has consequences that extend beyond the week. "
            "Action: Before deciding, pressure-test the framing. Is this actually the decision, "
            "or is it a symptom of a prior un-made decision? "
            "If it is the real decision: identify who else is affected, surface their constraints, "
            "and make the call with full situational awareness by mid-week. "
            "Rationale: High stakes with days of runway is the zone where framing errors are most costly. "
            "The right move is the correctly framed move."
        ),
        "source": "canonical",
        "version": 1,
        "created_at": CREATED_AT,
    },
    {
        "template_id": "BAR_high_this-quarter",
        "macro_family": "BAR",
        "stakes": "high",
        "horizon": "this-quarter",
        "mode": "decide",
        "skeleton": (
            "Belief: {question} is one of the decisions this quarter that will define the quarter. "
            "The underlying job — {jtbd} — deserves your full decision architecture. "
            "Action: Apply BAR in sequence: "
            "(1) Belief — what do you actually believe is true? Not what you hope. "
            "(2) Action — what is the minimum viable move that proves or disproves your belief? "
            "(3) Rationale — what would cause you to reverse? Name it now. "
            "Do not conflate the three. The conflation is where high-stakes decisions fail. "
            "Rationale: Separating belief from action from rationale under pressure is the skill. "
            "The template is the scaffold; the judgment is yours."
        ),
        "source": "canonical",
        "version": 1,
        "created_at": CREATED_AT,
    },
    {
        "template_id": "BAR_high_multi-year",
        "macro_family": "BAR",
        "stakes": "high",
        "horizon": "multi-year",
        "mode": "decide",
        "skeleton": (
            "Belief: {question} is a load-bearing decision. "
            "What you choose here will constrain and enable choices for years. "
            "The job at the root: {jtbd}. "
            "Action: Write the pre-mortem now. Imagine it is two years from now and this decision "
            "has failed. What happened? Work backward to identify the top three failure modes. "
            "For each: is there a structural guard you can build in today? "
            "If yes, build it into the decision. If no, name it as an accepted risk. "
            "Rationale: High stakes + multi-year is the only category where pre-mortem is mandatory, "
            "not optional. You are building load-bearing structure. Inspect the materials now."
        ),
        "source": "canonical",
        "version": 1,
        "created_at": CREATED_AT,
    },
]
# fmt: on


def gigi_post(path: str, body: dict) -> dict:
    url = f"{GIGI_BASE}{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def main():
    try:
        req = urllib.request.Request(f"{GIGI_BASE}/v1/health", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            health = json.loads(resp.read())
        print(f"gigi-stream healthy — {health.get('bundles', 0)} bundles")
    except Exception as e:
        print(f"ERROR: gigi-stream not reachable: {e}")
        sys.exit(1)

    inserted = 0
    for t in BAR_TEMPLATES:
        resp = gigi_post("/v1/bundles/arcs_templates/upsert", {"record": t})
        status = resp.get("status", "error")
        print(f"  {t['template_id']:35s}  {status}")
        if status in ("inserted", "updated"):
            inserted += 1

    print(f"\n{inserted}/{len(BAR_TEMPLATES)} templates seeded.")

    # Verify
    resp = gigi_post(
        "/v1/bundles/arcs_templates/query",
        {"conditions": [{"field": "macro_family", "op": "eq", "value": "BAR"}], "limit": 20},
    )
    count = resp.get("meta", {}).get("count", 0)
    print(f"Query verification: {count} BAR templates in arcs_templates bundle.")


if __name__ == "__main__":
    main()
