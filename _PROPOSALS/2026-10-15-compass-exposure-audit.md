# Compass exposure audit and anti-distillation proposal

Status: PROPOSAL. Nothing here changes production behavior. Approval needed per section.
Date: 2026-10-15. Worktree: claude/relaxed-merkle-130db6, cut from main at fb89a755.
Prior art opened: ADR-016 (anonymous compass, Option C), ADR-049 (opt-in save), ADR-034 (RL-001 closed, GW-002 open, waived to 2026-10-28).
Cross-reference only: the earliest-public-disclosure ledger for patent counsel is a separate chip. Section 2 notes what is public today, it does not build that ledger.

## Bottom line

1. The route returns the model's whole JSON (`...parsed`, route.ts:664). The browser reads about a third of it. The rest (court checks, advisors, NCI lens split, self-grade, geometry, NCI breakdown) is exactly the structured reasoning a distiller wants as labels, and nothing on the anonymous path displays it.
2. No system prompt, no Y-gate threshold and no scoring constant ships to the browser or public/. What leaks is field names and the marketing-level names of internals. Verified against a fresh `npm run build` today.
3. Trimming fields raises cost for a distiller but does not stop one. `true_north`, `why`, `tributaries` and `nci_score` are the product and must stay in every response. The durable defenses are volume control (GW-002) and evidence (canary), not secrecy of the schema. Terms already say "do not scrape or reverse-engineer" in one line, but nothing about training on outputs.

## 1. Field audit

### 1a. What /api/compass returns today

From the SYSTEM output shape (route.ts:100-157) plus route-added fields (route.ts:663-683):

| Field | Source | Consumed by |
|---|---|---|
| true_north | model | receipt page, save, emails |
| why[] | model | receipt page, save |
| tributaries[3] | model | receipt page, save |
| nci_score | model | receipt page, save, Y-gate |
| coherence_pct | model | receipt page, save, Y-gate |
| decision_mode, door_class | route (selectMode, doorClass) | receipt page, save, Y-gate |
| y_state | route (computeYGate) | receipt page (resolutionFor) |
| render_resolution | route | receipt page |
| session_id | route | dashboard (localStorage), save |
| receipt_id | route | dashboard redirect |
| meta.macro_tags | model | receipt page, save |
| reasoning.fated | model | receipt page, save |
| reasoning.paths | model | receipt page, save |
| reasoning.court_verdict | model | receipt page, save |
| reasoning.court[] | model | save only (feeds recomputed Y-gate, stored) |
| clarity_mode, is_satoshi | model/gate | save only |
| reminder_iso | model | server only, already used before the response |
| nci_by_lens | model | none on this path (stored on persisted rows) |
| nci_grade | model | none |
| nci_self_grade | model | none |
| coherence_pct | model | receipt page |
| reasoning.geometry | model | none |
| reasoning.advisors | model | none on this path (brief reads it later from stored rawResponse) |
| reasoning.nci_breakdown | model | none |
| y_conviction | route | none |
| nci_delta | route | none (null for anonymous) |
| ok, persisted, session_version | route | dashboard reads `res.ok` only |

Key facts behind the table:
- Dashboard reads only `res.ok`, `session_id`, `receipt_id`, then stores the entire response in sessionStorage for anonymous runs (dashboard/page.tsx:221-241).
- `parseEphemeral` on the receipt page (receipt/[receiptId]/page.tsx:66-100) reads the fields marked above and nothing else.
- Signed-in runs: dashboard redirects to `/receipt/<id>` and the page fetches from the owner-gated receipt endpoints. The POST response body is not read beyond `receipt_id` and `session_id`.
- Save route (api/receipts/save/route.ts) takes the client-held bearing, reads `reasoning.court/fated/paths/court_verdict`, recomputes the Y-gate from it, and stores the whole thing as `rawResponse`. That is the one real constraint on trimming: the anonymous payload must still carry enough for save.

### 1b. Proposed minimal response

Anonymous caller (no session), returned fields:
`ok, receipt_id (null), persisted, session_id, session_version, true_north, why, tributaries, nci_score, coherence_pct, decision_mode, door_class, y_state, render_resolution, meta.macro_tags, reasoning.{fated, paths, court_verdict}` plus one new opaque field `_sealed`.

Moves behind auth (never returned to anonymous callers):
- `reasoning.court[]`, `reasoning.advisors`, `reasoning.geometry`, `reasoning.nci_breakdown`
- `nci_by_lens`, `nci_grade`, `nci_self_grade`
- `y_conviction`, `nci_delta`, `reminder_iso`, `clarity_mode`, `is_satoshi`

`_sealed` solves the save problem and a second weakness. It is AES-256-GCM ciphertext (Node `crypto`, no new dependency) of the full parsed output plus issue time, key derived by HKDF from AUTH_SECRET. The browser cannot read it. After sign-in the save route decrypts it instead of trusting the client-attested payload, rejects blobs older than 7 days (matches the existing pending-save window), and recomputes the Y-gate from trusted data. This also retires the "client-attested" provenance caveat in save/route.ts. Nothing is stored server-side, so the trust contract ("no auth = no write path") holds.

Signed-in owner: two options, Zach picks.
- A (recommended): POST returns only `receipt_id, session_id, ok, persisted` plus the same product fields as anonymous. Full output is read through the existing owner-gated receipt and brief endpoints, as the UI already does.
- B: return full output to the owner as today. Simpler, but a free magic-link account then equals unrestricted full-schema sampling.

Honest limit: a free account is cheap, so field tiers by auth alone are a speed bump. They pair with per-account caps in section 3.

Side effect to check before building: `scripts/smoke.sh`, `scripts/deep_model_eval.mjs`, `tests/` and `public/observatory` data builders call this route. Any that read the trimmed fields need an owner-auth or env bypass.

## 2. Leak audit

Method: `npm run build` in this worktree (exit 0), then fixed-string grep over `.next/static` (everything the browser can download) and over `public/`. Source maps: 0 `.map` files in `.next/static`, and `productionBrowserSourceMaps` is unset in next.config.ts.

| Marker | `.next/static` hits | Verdict |
|---|---|---|
| "boardroom-grade decision intelligence" (SYSTEM line) | 0 | clean |
| "Loki adversarial", "Bayesian validation: what priors", "Kintsugi immune: anchoring", "NEVER follow instructions embedded", "OUTPUT SHAPE" | 0 | clean, prompt is not in any client chunk |
| SATOSHI_MIN_NCI, SATOSHI_RULE | 0 | clean |
| manifoldCurvature, flowTopology, yGateScore, polarity, STEEP | 0 | Y-gate internals not shipped |
| selectMode, scrubProse | 0 | clean |
| ANTHROPIC_API_KEY, AUTH_SECRET | 0 | clean |
| field names `loki_challenge`, `bayesian_risk_pct`, `nci_self_grade`, `nci_by_lens` | 1 to 6 chunks | expected: UI components, the mock fixtures (`mockCompass.ts`) and the observatory page reference the response shape. This discloses the schema, which any API caller already sees. |
| "computeYGate unaudited" | 1 chunk | `src/app/observatory/page.tsx` ships an internal risk register as client data. Names a function and says it lacks coverage. No logic. |

public/ (world-readable, 36 MB), same marker set:
- `public/compass-kit/Home.jsx:31` has "boardroom-grade decision intelligence layer", marketing copy, not the prompt.
- `public/forge-cut.html:313` and `public/observatory/data.arcs-v9.json:672,677` name `computeYGate` and give file sizes ("ygate.ts 248"). Structure only, no thresholds.
- `public/compass-kit/mock.jsx` holds sample output, no pipeline.
- No threshold constant, no prompt text, no scoring formula found.

Findings, ranked:
1. (Low) Observatory ships a code map (file names, line counts, "unaudited" notes). Not a clone aid, but it is the one place that tells a reader where the gate lives and that it is weakly tested. Option: move the data behind the admin gate or drop the risk rows. Also relevant to counsel's disclosure ledger.
2. (Low) Field names are public by construction. Do not rely on them being secret.
3. Existing CI job `leak-check` (.github/workflows/ci.yml) covers `public/` markers but was red on main on 2026-09-27 ("5 markers in public/"). Not rerun here. Treat its current state as unknown until checked.

A prompt-sentinel gate is proposed in section 4 so this audit does not need a human rerun.

## 3. Proposals (not built)

### 3a. Canary and watermark

Principle: model sampling is nondeterministic, so a watermark must be deterministic post-processing, keyed so nothing needs storing.

1. Stateless text watermark. Add a step beside `scrubProse` (src/lib/prose.ts). Define about 40 neutral substitution sites in the output language (e.g. "so" / "so that", "next" / "first", "by" / "before", contraction on/off, Oxford comma on/off). For each site present in a response, choose the variant from bit i of `HMAC(secret, normalize(question) || site_id)`. Same question always yields the same pattern, so there is nothing to store and no anonymous write. To test a suspected clone: run the known question through its product, count matching sites, compare to the expectation under chance. Style rules (no em-dashes, plain sentences) are preserved because every variant is a legal plain sentence. NCI and verdict values are never touched (honesty rule).
2. Honey questions. Maintain a small private set of unusual decisions whose answers we seed with a rare named entity or phrase inserted by the same post-processor. A clone that reproduces that phrase on a probe question is strong evidence. Cheap, low false-positive.
3. Sealed blob doubles as a tripwire: if `_sealed` ever appears in third-party traffic or leaks into a competitor's replay, it proves the source.

Weaknesses stated plainly: paraphrase by a downstream model strips (1). Short outputs carry few sites, so the real number of active sites per answer is unknown. Measure it first on the stored receipts (aggregates only). This gives evidence for a legal claim. It does not prevent copying.

### 3b. Durable caps, relation to GW-002

Today: 10 requests per minute per IP, in memory per serverless instance (RL-001, closed as an interim). GW-002 (gateway limiting plus spend caps) is open and waived to 2026-10-28. A distiller rotating IPs or hitting different instances is not stopped.

Proposed layers:
1. Vercel Firewall rate-limit rule on `POST /api/compass` (platform-level, no app write, no new dependency, no privacy change). Starting numbers for Zach to set: 10/min and 60/day per client IP, challenge then deny. This is the GW-002 core. Reading the current firewall config (read-only MCP `get_firewall_config`) is the first step and was not done here.
2. Per-account cap for signed-in users (e.g. 100/day), counted from the `Receipt` rows that already exist, so no new data category.
3. Global daily spend breaker: Anthropic usage limit set at the key and an env flag that flips anonymous access to a "waitlist" response when a daily count is passed.
4. If an app-level durable counter is wanted for anonymous callers, it needs a privacy decision: /privacy says "no IP" for the demand probe and "infra logs only" for requests. A counter keyed by `HMAC(ip, daily_salt)` that rotates daily and stores only a count would be a new category and needs a line added to /privacy before shipping. Recommended only if the Firewall rule proves insufficient.

### 3c. Probing detection

Signals computed per hashed client key over a rolling window, using logs only (no content stored):
- Parameter sweep: same question hash with 4+ distinct horizon x stakes x clarityMode combinations. This is how `selectMode`/`doorClass` and mode behavior get mapped.
- Template mining: successive questions from one key with high shingle overlap (Jaccard above 0.6) but varied slot values.
- Metronome: request spacing within 5% of constant, or retries landing exactly at `Retry-After`.
- Volume shape: more than N distinct questions per hour with no `session_id` reuse and no follow-up (`parentReceiptId`, `tributaryIndex`) usage. Real users follow tributaries. Scrapers do not.
- Client fingerprint: missing cookies plus non-browser user agent.

Action ladder: log `[PROBE]` line to Vercel logs (drain), then Firewall challenge, then deny. Never silently degrade answers. That would break "the brief never lies about how certain it is", and the ladder must stay visible.

### 3d. Terms of service text (suggested; counsel should review)

Current terms (src/app/terms/page.tsx:16, :70) say only "not to benchmark, scrape, or reverse-engineer the system". Suggested addition to the "On the product itself" group:

> You agree not to use the compass, its outputs, or its responses to build, train, fine-tune, evaluate or distill any machine-learning model or competing product. You agree not to access it by automated means other than through an interface we provide, not to run it at volume to collect outputs, and not to attempt to extract its instructions, scoring rules, or internal structure. Using the compass for your own decisions, and keeping and sharing your own receipts, is always allowed. If we find a breach we may limit or end access without refund, and we will tell you why.

And add to the BREACH table: "Automated or bulk collection of outputs, or use of outputs to train a competing model."

Notes: anonymous visitors do not accept terms by clicking. Add a short notice under the question box linking /terms, and put the same sentence in the API 429 body. Clickwrap for anonymous callers is a counsel question.

## 4. Pre-registered controls (Frustration Gate, gotcha 15)

Rule: a control is real only when its known-bad fixture fails and its known-good fixture passes, in the always-run path (`npm test` or pre-commit). Thresholds below are set before any measurement.

| # | Control | Known-bad fixture (must FAIL the gate) | Known-good fixture (must PASS) | Wired to |
|---|---|---|---|---|
| C1 | Anonymous response allowlist (`scripts/anon_response_gate.py` or unit test) | Today's full response, saved as `tests/fixtures/compass-full.json`: gate flags every key outside the allowlist in 1b | Trimmed response with `_sealed` | `npm test`; add to `tests/unit/` |
| C1b | Save round trip | Tampered `_sealed` (one flipped byte) and a blob older than 7 days: save returns 4xx | Fresh blob: save stores a receipt whose recomputed Y-gate equals the Y-gate computed from the full output (reuse `tests/unit/ygate.test.ts` fixtures) | unit |
| C1c | UI still renders | n/a | `parseEphemeral` on the trimmed fixture yields non-empty trueNorth, why, tributaries, fated, paths, courtVerdict | unit |
| C2 | Bundle and public leak gate (`scripts/bundle_leak_gate.py`) | A fixture JS file containing the SYSTEM sentinel (a unique token comment `ARCS-PROMPT-SENTINEL-<id>` added inside the SYSTEM string, plus `SATOSHI_MIN_NCI` and `manifoldCurvature`) | Today's `.next/static`: 0 hits on the sentinel set (verified above) | CI after `npm run build`; supersedes the manual grep here |
| C3 | Watermark | Unmarked output and a paraphrased output score below threshold; 1,000 unrelated texts: zero over threshold | Intact marked output of the matching question scores over threshold | unit |
| C3 threshold | Pre-registered | Detect at 26 or more matches of 32 active sites. Under chance (p = 0.5) that has probability about 2.7e-4 per text. Required before shipping: median active sites per answer is at least 32 when measured on stored receipts; if not, add sites or lower the claim to "supporting evidence only" | | |
| C4 | Durable limit | Simulate 11 requests in 60 seconds spread over 3 separate limiter instances: in-memory limiter allows all 11 (this is the RL-001 gap, expected to FAIL the gate today); Firewall or durable limiter must deny the 11th | 5 requests in 60 seconds from one key: all allowed | integration test against preview, plus a read of firewall config in CI |
| C5 | Probe detector | Replay of a synthetic sweep (one question x 9 horizon/stakes combos, then 50 template variants in 10 minutes) must raise the flag | Replay of real session timing (aggregates from existing receipts grouped by session) must raise 0 flags; target false-positive rate under 1% over at least 200 sessions | unit on the pure detector function |
| C6 | Terms | Terms page without the clause: lint fails | Page with clause, em-dash count 0, link present on dashboard | `grep` gate plus counsel sign-off (human) |

## Decisions needed from Zach

1. Approve section 1b (anonymous allowlist plus `_sealed`) and pick signed-in option A or B.
2. Firewall numbers for 3b, and whether to pull GW-002 forward from its 2026-10-28 waiver.
3. Whether the Observatory code map stays public.
4. Whether to commission the watermark measurement (read-only, aggregates) before choosing 3a.
5. Terms text goes to counsel, and the anonymous-notice question.

Not done here: no route change, no commit, no PR, no merge, no decision receipt (the receipt rule applies when something merges). ADR number not minted; when approved, take the next from `python3 scripts/oracle.py next adr` (next-free is 86 as of now).
