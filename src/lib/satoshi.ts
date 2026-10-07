// Satoshi flag: the server-side bar for `is_satoshi`, and the one prompt line that
// tells the model the same rule. Prompt and gate share these constants so they
// cannot drift apart (tests/unit/satoshi.test.ts pins the agreement).
//
// JTBD: keep `is_satoshi` meaning "rare, category-defining move" (Receipt.isSatoshi
//   in prisma/schema.prisma, the gold "Peak" gauge in InstrumentCluster) so the
//   badge stays worth something. Measured 2026-10-06 in prod, aggregates only:
//   34 of 267 receipts flagged (12.7%). 33 of the 34 were PLAN mode on the fast
//   model at MEDIUM stakes through a TWO_WAY door, median nci 78. The model read
//   "high nci" as "satoshi": 26 of 63 receipts scoring 70-79 and 6 of 6 scoring
//   90+ carried the flag. COURT mode on the deep model flagged 1 of 96.
// TOOL-FIT: a pure server gate over a prompt-only rewording. The fast model
//   already had a "rare" rule and ignored it on 1 in 5 PLAN runs; a prompt line
//   cannot be unit-tested and drifts with every model swap in claude-models.ts.
//   This gate is deterministic, runs on both write paths (compass and the
//   client-attested EPHEMERAL_SAVE), and the prompt line below is built from
//   the same constants, so the model is told the rule it is held to.
// EX-ANTE: predict the gate holds the prod rate under 1 in 50. Replaying the bar
//   over the 267 rows keeps 1 of the 34 flags (0.4%) and caps the eligible
//   population (HIGH stakes and nci >= 70) at 8 of 267 (3.0%). Scored ex-post
//   by re-running the same aggregates after 50 new receipts.
//
// The bar: the model must claim it, stakes must be HIGH, and nci_score must be at
// least SATOSHI_MIN_NCI. HIGH stakes is the route's own trigger for COURT mode and
// a ONE_WAY door (selectMode / doorClass in compass/route.ts); a category-defining
// move at LOW or MEDIUM stakes is a contradiction. 70 is the STEEP manifold
// curvature threshold in ygate.ts. The gate only ever clears the flag. It never
// promotes one the model did not claim, and historical rows are not rewritten.
//
// Canon note, not resolved here: operators/arcs_rom.py SATOSHI_CRITERIA defines a
// satoshi as the smallest buildable coherence unit (nci >= 50, irreversibility
// <= 0.5, on purpose, axioms checked), under which most PASS receipts qualify.
// The compass field, the schema comment and the gauge all mean the rare move.
// Same word, two definitions; this file enforces the compass meaning only.

export const SATOSHI_MIN_NCI = 70
export const SATOSHI_STAKES = "HIGH"
export const SATOSHI_BASE_RATE = "fewer than 1 in 50"

// Interpolated into the compass SYSTEM prompt as one RULES line.
export const SATOSHI_RULE =
  `is_satoshi: true only for a rare, category-defining move: expect ${SATOSHI_BASE_RATE} decisions. ` +
  `It requires STAKES ${SATOSHI_STAKES} and nci_score of at least ${SATOSHI_MIN_NCI}, and even then default to false. ` +
  `A high nci_score on its own is never a reason.`

export interface SatoshiInput {
  claimed: unknown  // the model's (or a client's) is_satoshi: untrusted
  nciScore: unknown // nci_score as parsed: untrusted
  stakes: unknown   // the stakes string the route actually used for mode and door
}

// True only when the claim is a literal boolean true AND the bar is met. A string
// "true", a lowercase "high", or a non-numeric score all clear the flag.
export function satoshiGate({ claimed, nciScore, stakes }: SatoshiInput): boolean {
  if (claimed !== true) return false
  if (stakes !== SATOSHI_STAKES) return false
  return typeof nciScore === "number" && Number.isFinite(nciScore) && nciScore >= SATOSHI_MIN_NCI
}
