# /faq-eval

> Cold-reader ATG-FAQ coverage eval for a README (or any public-facing artifact). Simulates a
> developer landing COLD and scores whether the doc answers the questions an adopter has — the ATG
> tributary set. Read-only: reports a punch-list, edits nothing. Billing tier: SUBSCRIPTION.

> **Standard source of truth:** ADR-055 (Tier-B+ ATG-FAQ criterion) · seed `seed-readme-faq-eval`.

## When to use
- Standing up or leveling a public repo README (Tier-B+ conformance gate).
- Any public artifact where "does this answer what a newcomer actually asks?" matters.
- Before shipping a connector page (`<tool>.arcs.care`, ADR-056).

## How it works
Spawn a **cold reader** (a subagent with NO prior context — isolation matters; the author already
knows the answers, so they can't run this honestly themselves). It judges ONLY what the README (and
top-level docs it links) actually says — not the code, and not charitably.

## The ATG-FAQ set (base tributaries)
1. **How do I use it?** — concrete install + first-run command from zero.
2. **Why is it different than ___?** — names a nearest alternative and why pick this. *(Highest-leverage
   line; empirically the weakest axis across the family — most READMEs never name a rival.)*
3. **What problem does it actually solve?** — concrete pain, not abstract.
4. **Who is it for?** — explicit audience.
5. **How does it relate to the family / ecosystem?** — placed in context.

ATG may add **repo-specific tributaries** — the need-to-hear question an adopter has but won't ask
(e.g. a data tool: "is my data sent anywhere?"). Surface 0–2 of these per repo.

## Steps
1. Take the target(s): a repo path / README path (default: argument, else ask).
2. Spawn one cold-reader subagent per batch of READMEs (isolated, no repo context). Prompt it to score
   each FAQ **ANSWERED / PARTIAL / MISSING** from the README alone, with the one-line gap, plus the
   single highest-value fix per repo.
3. Return per repo: a table (FAQ | verdict | gap), a coverage score (X/5 ANSWERED), the top fix.
4. Cross-repo (if >1): which axis is weakest across all, which repo is in worst shape.
5. If run in the arcs-v9 context, append a `faq-eval` receipt per repo to `_SEEDS/ledger.jsonl`
   (ts · seed · event:faq-eval · conformance:"X/5" · gaps[] · receipt). Do NOT edit the READMEs —
   the punch-list is the output; fixes are a separate, reviewed pass.

## Output contract
A punch-list, not a rewrite. Positioning fixes ("why different than X") are GTM decisions — flag, don't author.
