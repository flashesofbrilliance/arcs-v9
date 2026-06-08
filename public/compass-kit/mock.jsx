// ARCS Compass — mock pipeline. Returns a canned Receipt for any question so the
// kit demos the full flow without a backend. Shape matches arcs-v9 CompassResult.

const SAMPLE = {
  runway: {
    true_north: "Extend runway — the valuation delta at your current growth rate outweighs the optionality cost of six months.",
    why: [
      "At ~12% MoM, six months compounds into a materially higher entry valuation.",
      "Current term sheet prices in execution risk you've already retired.",
      "A bridge note de-risks the wait without resetting the round.",
    ],
    nci_score: 74, coherence_pct: 88, is_satoshi: false,
    door_class: "ONE_WAY", decision_mode: "COURT", y_state: "GREEN",
    render_resolution: "SHARP", nci_delta: 12,
    macro_tags: ["KKL", "BAR"],
    tributaries: [
      { type: "meta", label: "Meta-question", prompt: "What would have to be true for taking the A now to be right regardless of valuation?" },
      { type: "challenge", label: "Challenge", prompt: "If the next two months miss plan, what is your recovery line on the wait?" },
      { type: "adjacent", label: "Adjacent", prompt: "Does a bridge note de-risk the wait without resetting the round terms?" },
    ],
    reasoning: {
      court: [
        { name: "Reversibility", verdict: "TENSION", detail: "A signed A is hard to unwind; the wait is reversible." },
        { name: "Ruin check", verdict: "PASS", detail: "No single failure on the wait path is unrecoverable." },
        { name: "Coherence", verdict: "PASS", detail: "Growth trend and capital need are internally consistent." },
      ],
      court_verdict: "No ruin exposure on the wait. The expensive mistake is locking price too early.",
      fated: {
        facts: "12% MoM, 9 months runway, term sheet at 4× ARR.",
        assumptions: "Growth holds through the wait; market window stays open.",
        tradeoffs: "Higher valuation vs. 6 months of execution + market risk.",
        emotions: "Fear of the window closing is doing more work than the math.",
        direction: "Wait, but instrument the wait with a bridge and a hard re-check date.",
      },
      paths: [
        { id: "a", title: "Take the A now", detail: "Certainty, but prices in retired risk.", tag: "LOCK", status: "viable" },
        { id: "b", title: "Extend 6 months", detail: "Higher entry, bounded downside.", tag: "WAIT", status: "selected" },
        { id: "c", title: "Raise a bridge", detail: "Buys time without resetting terms.", tag: "HEDGE", status: "viable" },
      ],
      advisors: {
        loki_challenge: "You're anchoring on a valuation that assumes growth you haven't banked yet.",
        loki_counter: "The growth is already in the trailing data — this is realized, not projected.",
        bayesian_risk_pct: 31,
        bayesian_rationale: "Base rate of A-round windows closing in 6mo at your stage is moderate, not acute.",
      },
    },
  },
  hire: {
    true_north: "Make the leverage hire now — the cost of the open seat is already higher than the salary you're hesitating over.",
    why: [
      "The bottleneck is your time, and it is the scarcest input in the system.",
      "A strong operator pays for themselves inside two quarters at current margins.",
      "Waiting for the 'perfect' candidate is optimizing the wrong variable.",
    ],
    nci_score: 81, coherence_pct: 91, is_satoshi: true,
    door_class: "REVERSIBLE", decision_mode: "PLAN", y_state: "GREEN",
    render_resolution: "SHARP", nci_delta: null,
    macro_tags: ["ATG"],
    tributaries: [
      { type: "meta", label: "Meta-question", prompt: "What does this hire have to take off your plate to be worth it in 90 days?" },
      { type: "challenge", label: "Challenge", prompt: "If they underperform, how fast and how cleanly can you correct?" },
      { type: "adjacent", label: "Adjacent", prompt: "Is a fractional operator a faster, lower-risk first move?" },
    ],
    reasoning: {
      court: [
        { name: "Reversibility", verdict: "PASS", detail: "A hire is correctable; the open seat compounds." },
        { name: "Coherence", verdict: "PASS", detail: "The need and the budget are aligned." },
      ],
      court_verdict: "Low ruin exposure. The real risk is the status quo, not the hire.",
      fated: {
        facts: "Founder is the bottleneck on 3 of 5 revenue paths.",
        assumptions: "A strong operator exists in your network within 30 days.",
        tradeoffs: "Burn vs. founder leverage and pipeline velocity.",
        emotions: "Hesitation is loss-aversion on cash, not a real constraint.",
        direction: "Hire — but define the 90-day takeover-of-plate explicitly.",
      },
      paths: [
        { id: "a", title: "Hire full-time now", detail: "Maximum leverage, real burn.", tag: "COMMIT", status: "selected" },
        { id: "b", title: "Fractional operator", detail: "Faster, lower risk, less depth.", tag: "HEDGE", status: "viable" },
        { id: "c", title: "Wait one quarter", detail: "Seat stays open, you stay the bottleneck.", tag: "HOLD", status: "blocked" },
      ],
      advisors: {
        loki_challenge: "You can't afford the burn and you're hiring to feel less alone.",
        loki_counter: "The math says the open seat costs more than the salary — this is leverage, not comfort.",
        bayesian_risk_pct: 19,
        bayesian_rationale: "Strong operators in-network at your stage convert well; downside is bounded by reversibility.",
      },
    },
  },
};

function mockCompass(question, { stakes, horizon } = {}) {
  const q = (question || "").toLowerCase();
  const key = /hire|hiring|recruit|team|operator|headcount/.test(q) ? "hire" : "runway";
  const base = JSON.parse(JSON.stringify(SAMPLE[key]));
  base.receipt_id = "rcpt_" + Math.random().toString(36).slice(2, 10);
  base.question = question;
  // High stakes nudges into COURT mode + a touch of weather
  if (stakes === "HIGH" && base.y_state === "GREEN") {
    base.decision_mode = "COURT";
  }
  return base;
}

Object.assign(window, { mockCompass, SAMPLE });
