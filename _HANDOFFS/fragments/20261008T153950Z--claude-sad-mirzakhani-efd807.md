<!--
session: claude-sad-mirzakhani-efd807
branch: claude/sad-mirzakhani-efd807
head: 5ecd5c61
created_at: 2026-10-08T15:39:50Z
-->
> Night-moves scoped to reusable assets, then a hyperstition cut of a draft scope-of-work scaffold for My Ally LD. Draft only; nothing sent, priced or run through Question Compass.
## Goal
Give structure and graded evidence to an itemized SOW for the My Ally LD prospect, ready for Zach to adapt once the NDA, codebase and build spec arrive.
## Changed
- Added `_ARTIFACTS/sow-scaffold-2026-10-08/` (asset map, graded scaffold, 16 draft assumptions asm-015 to asm-030 (adds charter hypothesis asm-028 and two UNSUPPORTED judgments) that validate against `scripts/assumptions.py`, cost-baseline template). PR open, not merged; no merge receipt yet.
## State
- Nothing received from the prospect (Gmail search 2026-10-08): items depending on the codebase and spec are GRAIN or DEGRADED.
- Repo has no SOW template, no premortem asset, no redaction test harness (gaps listed in file 01).
- External cites: Anthropic API retention and HIPAA page, Lovable terms, FTC COPPA summary, HHS developer-guidance summary. Supabase plan eligibility is UNCONFIRMED; OpenAI terms not read.
## Decisions
- Redaction item changed from deterministic-only to deterministic plus mandatory parent review (deterministic rules miss names in prose).
- Zach's recalled liability figure and any HIPAA/COPPA/BAA applicability claim are excluded; routed to counsel (L.2).
## Open
1. Zach: whose entity pays and on whose paper; which vendors are on a card; is cost visibility an outcome; disclose the recording; NDA status; meaning of "by manana"; may Phase 0 use Question Compass on real material after the NDA.
2. Zach: yes/no to append asm-015..030 to the live ledger.
3. Zach: whether to run `counterpart-gauntlet` on the scaffold (multi-agent cost).
## Next action
When the NDA, codebase and build spec arrive, read them and regrade P0.A1 to P0.A4 and B.3 in 02-sow-scaffold.md.
## Cold-start
`_ARTIFACTS/sow-scaffold-2026-10-08/02-sow-scaffold.md` first; `python3 scripts/assumptions.py check` for the ledger; transcript is INTERNAL (Granola note a6466859-0214-45f2-ba1b-892a30d5028b), recording-consent question open.
