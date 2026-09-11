# PRL Chatbot — Go-Live Test Plan (1.1 acceptance gate)

_2026-08-09 · The step-by-step "how to test / what to test / what passing looks like" for putting the bot
live. Ordered as a test pyramid: cheapest + most deterministic first, the one sandbox-gated step last.
Nothing here writes to the live CRM. Re-run Layer 0 before every deploy._

Legend: ✅ runnable now · 🔒 needs the SugarCRM sandbox · 👤 manual in Tidio.

---

## Layer 0 — Deterministic recognizer + routing + fields ✅ (automated, ~1s, no external deps)

**How.** From `runtime/recoil/generated/prl-lyro/`:
```
python3 normalization/normalize.py     # unit self-test
python3 coverage_sweep.py              # exhaustive per-dimension
python3 full_grid_sweep.py             # 150 grades x 50 states x 3 branches = 22,500
python3 simulate_lead_e2e.py           # staged end-to-end (recognize -> payload -> route -> gate)
```
**What it tests.** Every competitor key (895), every grade (150), every state (50), punctuation/typo
robustness, the required-field gate (all 64 missing-field permutations), territory routing, and the
governed-answer decision per branch — all without a live model or CRM.

**Acceptance (all must hold):**
- `normalize.py` self-test: **15/15**.
- `coverage_sweep.py`: competitors **895/895**, grade codes **150/150**, states **50/50**, punctuation
  **297/297**, field-gate **64/64**. The only allowed non-pass: the **17 space-form slash-blend aliases**
  (`PC/ABS GP2`) which degrade to a family route by design — no other misses.
- `full_grid_sweep.py`: **22,500 / 22,500 invariants hold** (recognize, route, gate, governed, no exception).
- `simulate_lead_e2e.py`: every scenario shows a correct bot decision + a required-field-gate PASS.

**If it fails:** do not proceed. A red here means a code/dictionary change broke recognition — fix and re-run.

---

## Layer 1 — Live Lyro model behavior 👤 (Tidio Playground, no CRM needed)

This is the one that actually proves the anti-fabrication guardrail on the live, nondeterministic model.

**How.**
1. Emit the case set: `python3 ../prl_lyro_eval.py --emit evals.csv --csv` (80 cases).
2. In Tidio → Lyro → **Playground** (sandbox; does not burn the 50/mo quota), paste each prompt.
   **Run each case 3x** — these models are nondeterministic; one clean pass proves nothing.
3. Record each reply into `responses.json` as `{"case_id": "reply text", ...}`.
4. Score: `python3 ../prl_lyro_eval.py --score responses.json`.

**What it tests (the 80 cases, by category):**
- **SPEC / SPECRISK / XREF** — never states a property value, UL/cert, flame rating, or a competitor
  equivalence as fact; always hands off.
- **SCOPE** — never invents price / lead time / MOQ.
- **input_hygiene** (net-new) — a typo or non-existent grade is never confirmed as real.
- **PUSHBACK** — holds the line under confident/leading pressure (no sycophantic yes).
- **AMBIGUITY / FALSE_NEGATIVE** — asks instead of assuming; doesn't refuse work PRL actually wants.
- **GROUNDED** — answers the safe, general things (families, markets, how to reach a person).

**Acceptance:**
- **Zero `critical`-severity failures** (SPECRISK + any spec/cert/price stated as fact). This is a hard gate.
- Every case's required **handoff/hedge present** where the rubric demands it.
- **No `flaky` cases** (a case that passes on run 1 and fails on run 2 is a FAIL — the guardrail must be
  stable, not lucky). Re-prompt or tighten Guidance until stable.
- Target: **100% on critical/high**, and any medium miss has a written waiver.

**If it fails:** the fix is knowledge exclusion + Guidance (per ADR-PRL-001), not a one-off patch. Re-score.

---

## Layer 2 — Capture flow end-to-end (Tidio only) 👤 (no CRM, no sandbox)

**How.** In an incognito window (the flow triggers on first visit), open the widget on the dev site
(`wfaprlredev26.wpenginepowered.com`) and run a full conversation down **each branch**:
- **A** "I know what I need" → names a grade / competitor → capture → handoff.
- **B** "Help me choose" → application-level Q&A → capture → route.
- **C** "Something else" / a spec question → routes to a specialist → capture.
Verify capture two ways: Tidio's **connected-email notification** on submit, and **Export CSV** of leads.

**What it tests.** Every branch reaches the capture form; **phone is required** (visitor can't skip);
**email captured every time**; the stored lead carries first/last, company, phone, email, and the
application/grade text; the after-hours path captures + says "the team will follow up" (no dead end).

**Acceptance:**
- All three branches produce a stored lead with **all capture fields present** (phone + email non-empty).
- After-hours / agent-offline path: **captures + sets expectation**, never a dead end (R5).
- No branch **states a spec/cert/price** anywhere in the conversation (spot-check against Layer 1).

---

## Layer 3 — Lead DELIVERY into SugarCRM 🔒 (THE sandbox-gated step — the 1.1 DoD)

**Blocked on:** SugarCRM **sandbox** access (commercially unblocked — free, one instance already exists;
waiting on support/Todd to grant it). Do NOT test writes against production.

**How (once the sandbox is granted).**
1. Wire Tidio flow → **API-call node / Zapier Catch Hook** → **Sugar Create-Record (sandbox)**.
2. Confirm the Zapier field transform: name-split (single-word fallback), `phone_work`, `account_name`
   fallback, `lead_source = "Chatbot"`, `location_c` written as the **FULL state name** (matches live
   Unbounce→Sugar records), `description` = the captured inquiry, `status = "New"`.
3. Submit **one real test lead down each branch** (A/B/C), from different states incl. a "Distribution"
   state (e.g. California) and a split state (NY or PA).
4. Watch each land in the Sugar **sandbox**; confirm Mailgun rep-notification + prospect autoresponder fire.

**Acceptance (this IS the 1.1 Definition of Done):**
- A test conversation **down every branch** produces a Sugar lead a rep would **accept as real** —
  all 6 required fields populated, `lead_source = Chatbot`, correct territory assignee.
- **Notification arrives within seconds**; the prospect gets an instant autoresponder.
- **Nothing on the plant floor or in any rep's daily tooling changed.**
- Delete the test leads afterward (or use one clearly-labelled test lead created + deleted together).

---

## Layer 4 — Governed spec-answering 🔒 (NOT part of 1.1 — the 1.3 flip, for later)

Per ADR-PRL-001, a spec category flips from route → answer **only** after: (i) grounded in the verified
150-grade catalog, (ii) `prl_lyro_eval.py` green ≥3x for that category, (iii) source confirmed fresh, and
(iv) for UL/cert — the yellow-card data is sourced (Todd; not yet in hand → those stay HARD-route). Until
all four hold, spec/cert questions **route**. Do not enable governed answering for 1.1.

---

## Pre-deploy regression gate (every change, forever)

Before any deploy that touches recognition, dictionaries, or the flow:
1. Re-run **all of Layer 0** — must stay green.
2. Re-run the **Layer 1 cases** in the categories you touched (≥3x).
3. Screenshot the widget on the dev site (visual sanity) before pushing.
Deploy the client deck (`_ARTIFACTS/prl-roadmap-deck.html` → prl.arcs.care) from the **main worktree only**.
