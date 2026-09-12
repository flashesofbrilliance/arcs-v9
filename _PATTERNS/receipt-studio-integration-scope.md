# Receipt Studio integration — scope (Robin tenant + reuse)

_2026-08-07. The interactive, API-backed receipt-close, generalized from the Louisville Receipt Studio
to the counterpart forge family. Blueprint sec 7 ("Interactive receipt builder, per-tenant") + D6
("data-driven render + JSON export now; stateful RLS air-gapped tenant deferred to engagement-live")._

## Where this sits
Today the receipt-close is a **static, hand/SSOT-authored** surface: `forge_counterpart.py --surface
receipt` renders `public/<name>-receipt.html` from `runtime/recoil/generated/<name>-receipt.json`. It is
a *rendered card* of a bet that was already scored offline. The Studio adds the **live loop**: file a bet
interactively, seal it, and later close/score it against reality, as portable JSON, per counterpart.

## What already exists (do not rebuild)
- **API:** `src/app/api/louisville/receipts/route.ts` — tenant-scoped seal + read. `POST` validates and
  seals a bet (`bet / assumptions / falsifier / killScale / atRisk / scoreBackDate / parentId / payload`),
  server-sets `tenant/brand/userId`, caps body/rows, best-effort IP throttle. `GET ?sessionId=` reads
  session-scoped with an explicit `PUBLIC_SELECT` (never the raw row).
- **Model:** `SessionReceipt` (Prisma) — tenant + brand + sessionId scoped, lineage via `parentId`
  (no cross-session grafts), `status`, `sealedAt`, `payload` JSON.
- **Anon flow:** `sessionId` from client localStorage (the ADR-016 claim pattern). Anonymous-safe.
- **Static forge side:** `scripts/gen_receipt_close.py` (scaffold a receipt SSOT from a recoil) +
  `forge_counterpart.py` receipt renderer + `scripts/receipt_lookup.py` (ledger query). These stay the
  offline/authored path; the Studio is the live path that produces the same JSON shape.

## Scope: the Robin tenant + a reusable counterpart tenant
The goal is the loop, not another hardcode. Louisville's route pins `TENANT="jeben"` /
`BRAND="louisvillebrands"` as constants. **Do not fork the file per counterpart.** Generalize:

1. **Parameterize the tenant.** Extract the Louisville handler into a tenant-agnostic core
   (`src/app/api/receipts/studio/route.ts` or a shared `lib/receipt-studio.ts`) that takes
   `{tenant, brand}` from a small server-side registry keyed by host/path, not a literal. Louisville
   becomes registry row #1; **`robin`** becomes row #2 (tenant `robin`, brand `zensai`). Same caps,
   same `PUBLIC_SELECT`, same lineage rule. One code path, N tenants (build-reusable-by-default).
2. **The bet form == the ex-ante receipt.** The Studio's create fields already ARE the forge receipt's
   `ex_ante` shape (bet + falsifier + score-back date + predictions in `payload`). Wire the
   `<name>-receipt.html` "file a bet" affordance to `POST` a sealed row; render sealed bets back via
   `GET ?sessionId=`. The forge page stays the *view*; the Studio adds the *write*.
3. **Close = score against reality.** Add a close action (`PATCH`/second POST with `parentId`) that
   records the observed outcome per prediction and flips `status` to CLOSED — the same
   predicted-before vs actual-after the static renderer shows, but captured live. Reuses
   `src/app/api/receipts/[receiptId]/outcome/route.ts` semantics (the debrief close-the-loop already
   shipped, ADR-040).
4. **Portable JSON is the contract.** `GET` already returns the exact fields the forge SSOT consumes.
   A sealed+closed Studio session should export to a `<name>-receipt.json` the static renderer can
   render verbatim — so the interactive and authored paths converge on one artifact (interoperable, D6).

## Air-gap / deferral (D6, hold the line)
- **Now:** data-driven render + JSON export + anon session write. Portable, no per-tenant isolation beyond
  the tenant/brand scope + `PUBLIC_SELECT` field allowlist.
- **Deferred to engagement-live:** stateful **RLS-isolated per-tenant** storage (a real Robin tenant with
  row-level security, not just a scoped column). Gate this behind an actual engagement, per D6 and
  [[supabase-rls-hides-rows-from-new-roles]]. Internal scoring (NCI, conviction values, kinematics) never
  crosses into the Studio's `PUBLIC_SELECT`.

## Cost + verify discipline
- One route, registry-driven; no per-counterpart file. Local iteration; one deploy from the main worktree.
- The Studio write path touches auth + schema + an external DB, so it goes through **ciso-review +
  sre-review** before ship (per the ADR conformance checklist). The static forge path does not.

## Acceptance
File a bet on `robin-receipt.arcs.care` interactively, seal it, close it against the real Call-3 outcome,
export the JSON, and render it through `forge_counterpart.py --surface receipt` to the identical page.
That round-trip (interactive -> JSON -> static render) proves the two paths are one artifact.

Related: [[counterpart-forge-pipeline]], [[recoil-brief-ssot-cli]], blueprint sec 7 + D6,
`_PATTERNS/counterpart-artifact-family-blueprint.md`.
