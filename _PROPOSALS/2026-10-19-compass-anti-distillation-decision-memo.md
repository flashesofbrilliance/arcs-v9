# Decision memo: compass anti-distillation (for Zach to rule)

Status: DECISION NEEDED. Nothing is built until each line below has a ruling.
Date: 2026-10-19. Source audit: `_PROPOSALS/2026-10-15-compass-exposure-audit.md`.
Backlog: `compass-anti-distillation-decisions` (READY P0) unblocks `compass-anti-distillation-build` (HOLDING).
Deadline: GW-002 waiver ends 2026-10-28.

## The situation in three lines

1. `POST /api/compass` is open to anonymous callers and returns the whole model JSON (`...parsed`, route.ts:664), including reasoning fields no anonymous screen shows (court, advisors, geometry, NCI breakdown, lens split, self-grade).
2. The only limit is 10 requests per minute per IP, held in memory per serverless instance (RL-001 interim). Rotating IPs or landing on another instance resets it.
3. The prompt, thresholds and scoring constants do not ship to the browser (audit section 2, verified by build grep).

## The core trade: volume control (GW-002) vs response trimming

| | Volume control (GW-002: Firewall rate rule, per-account cap, spend breaker) | Response trimming (anonymous allowlist plus `_sealed`) |
|---|---|---|
| What it stops | How many samples a distiller can collect, and the bill they run up | How rich each sample is as a training label |
| What it does not stop | A slow, patient distiller under the cap | Distilling the product fields, which must stay (`true_north`, `why`, `tributaries`, `nci_score`) |
| Cost to build | Firewall rule: platform config, no app code, no dependency | Half a day: allowlist, AES-GCM seal, save-route change, bypass for smoke and eval scripts |
| Risk to real users | A real user hitting 60 a day sees a challenge | Save path must decrypt the seal; a bug breaks anonymous save |
| Reversibility | Two-way: edit or delete the rule | Two-way in code; see the one-way note under `_sealed` key |
| Also protects | The Anthropic bill (spend cap), which no trim does | Nothing outside distillation |

Recommendation: do volume control first and now (it is cheap, reversible and also caps spend), then trimming. Trimming without volume control is a speed bump; volume control without trimming still lets each sample carry full reasoning labels. Both are needed, in that order.

## Rulings needed (mark each YES, NO, or an edit)

1. **Firewall numbers (audit 3b.1).** Proposed: `POST /api/compass` at 10 per minute and 60 per day per client IP; challenge, then deny. First step is a read of the current firewall config. Ruling: RULED 2026-10-20 (Zach): measure first. Firewall rule set to LOG ONLY for a week; no 10/min and 60/day numbers are enforced until they come from data. Enforced value will be a stated multiple (default 3x) of the observed peak, with the peak and multiple written into the receipt. Existing in-memory 10/min stays as the only hard gate.
2. **Pull GW-002 forward from 2026-10-28.** Proposed: yes, start this week. Ruling: RULED 2026-10-20 (Zach): YES, start this week (log-only observation counts as the start; the waiver ends 2026-10-28).
3. **Spend breaker (audit 3b.3).** Anthropic key usage limit plus an env flag that switches anonymous callers to a waitlist reply past a daily count. Proposed daily count: ____ (no number in the audit; Zach sets it). Ruling: RULED 2026-10-20 (Zach): measure first. Daily counter added in LOG ONLY mode with no waitlist switch; threshold set later at a stated multiple (default 3x) of the observed peak. Until then the only spend ceiling is the Anthropic key usage limit.
4. **Anonymous allowlist plus `_sealed` (audit 1b).** Proposed: yes. Ruling: RULED 2026-10-20 (Zach): YES. WRITE-LOCK 1 (_sealed key derivation) still has to be declared by Zach before that part ships.
5. **Signed-in response, option A or B.** A (recommended): POST returns only the product fields plus ids; full output read through the owner-gated endpoints the UI already uses. B: keep the full output for owners; a free magic-link account then equals full-schema sampling. Ruling: RULED 2026-10-20 (Zach): A (product fields plus ids; full output through owner-gated endpoints).
6. **Per-account cap for signed-in users (audit 3b.2).** Proposed: 100 per day, counted from existing Receipt rows (no new data category). Ruling: RULED 2026-10-20 (Zach): measure first. Observed maximum is 3 saved receipts per account per day (14 days to 2026-10-20, one account), so no cap is set until there is real signed-in volume. Revisit with data.
7. **Observatory code map public?** Proposed: drop the risk-register rows ("computeYGate unaudited") from the client bundle; keep file sizes. Ruling: RULED 2026-10-20 (Zach): YES, drop the risk-register rows from the client bundle; keep file sizes. (Reversible; keeping the map public is the one-way choice.)
8. **Watermark measurement first (audit 3a).** Read-only aggregate count of active substitution sites over stored receipts, before choosing to build the watermark. Proposed: yes. Ruling: RULED 2026-10-20 (Zach): YES, read-only aggregate count first.
9. **Terms clause and anonymous notice (audit 3d).** Proposed: send the clause to counsel; add a one-line notice under the question box linking /terms. Ruling: RULED 2026-10-20 (Zach): YES, clause to counsel (nothing publishes before review) plus the one-line notice.
10. **App-level hashed-IP counter (audit 3b.4).** Proposed: NO for now; it adds a data category and needs a /privacy line. Revisit only if the Firewall rule proves too weak. Ruling: RULED 2026-10-20 (Zach): NO for now.

## WRITE-LOCK: one-way doors

Most of this is two-way. These items are not, and each needs an explicit write-lock declaration from Zach before its commit:

- **WRITE-LOCK 1: `_sealed` key derivation.** Once anonymous blobs are issued with a key derived from `AUTH_SECRET`, rotating `AUTH_SECRET` invalidates every unsaved blob (up to 7 days of pending saves), and changing the derivation later needs a versioned envelope. Declare: key source, HKDF info string, and a version byte in the blob from day one.
- **WRITE-LOCK 2: terms text.** Published terms bind the record of what visitors were told and when. A later weakening is visible and an earlier absence cannot be backfilled. Counsel review before publish; nothing goes live from this memo.
- **WRITE-LOCK 3: public disclosure.** Anything about the internals that ships public (Observatory map, this memo if ever published) is a permanent disclosure for the patent ledger. Keeping the map public is the one-way choice; removing it is reversible.
- **WRITE-LOCK 4 (conditional): hashed-IP counter.** Only if ruling 10 is YES: adding a stored data category is a privacy-contract change; the /privacy line must ship with it, and removing the category later does not erase what was collected.

Not one-way: the Firewall rule, the response allowlist, option A vs B, per-account caps, the spend breaker. All are config or code that can be reverted in one deploy.

## What happens after the ruling

- Rulings recorded in this file (fill the blanks) and in the backlog row status note.
- ADR number from `python3 scripts/oracle.py next adr` if 4 or 5 is YES.
- `compass-anti-distillation-build` moves from HOLDING to READY with the approved scope only, each control carrying its known-bad and known-good fixture (audit section 4).
