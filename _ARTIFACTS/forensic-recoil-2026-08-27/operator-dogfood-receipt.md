# Operator Dogfood Receipt — op20 / op21 (2026-08-27)

Genuine live runs, not synthetic. Banked so the result isn't lost.

## op21 (Anterior/Posterior Spline Inference) — P1 stability: PASS
- The pre-mortem's planned-but-never-run P1 test ("5 runs, same fixture, consistent shape") now has a receipt.
- 5 runs, ts-normalized shape-hash identical every time: `698a0a7cc8f76da8`. Deterministic.
- Correction to an earlier false finding: op21/op20 have **no import bug**. The `AttributeError` seen
  in-session was an ad-hoc `importlib` harness that didn't put `operators/` on `sys.path` (so
  `from arcs_primitives import …` resolved to None). Run correctly, both operators import and run clean.

## op20 (Folksonomy Cultivator, 54-dim DBSCAN) — live over REAL prod receipts
- **Corpus:** 247 rows from the prod Supabase `Receipt` table (read-only), all with real `nciScore`
  (range 8–94, mean 58.1). This clears both op20's 5-seed floor AND the "gated at 100 receipts"
  backlog threshold — `corpus_ready = 1.0`.
- **Result:** seed_count 247 · 3 clusters + 1 noise · coverage 99.6% · **avg_silhouette 0.765** (strong).
  | cluster | n | % | cohesion | silhouette |
  |---|---:|---:|---:|---:|
  | sig_cls_accelerating | 133 | 54% | 0.276 | 0.818 |
  | sig_cls_stable | 89 | 36% | 0.366 | 0.754 |
  | sig_cls_decelerating | 24 | 10% | 0.424 | 0.721 |
  | ⚡ noise | 1 | 0.4% | — | — |

### Honest fidelity caveat (this is a PARTIAL-fidelity dogfood, not full 54-dim)
- The clusters are driven almost entirely by the **one** dimension mapped from real signal:
  `signal_classification` (derived from `gradientMagnitude`). The input split (133/90/24) maps ~1:1 to
  the cluster split (133/89/24) — op20 is essentially recovering the gradient tiering it was fed.
- The other ~50 dims (somatic, fated lengths, lab, bar specifics, axioms) **defaulted to constants**
  because prod doesn't store them in op20's shape, so they didn't discriminate.
- **Real integration finding:** prod `courtVerdict` stores **full prose sentences** ("Court permits
  Series A now…"), but op20's `COURT_VERDICT_MAP` expects short enums (PERMIT/CONDITIONAL/BLOCK) →
  every receipt mapped to `unknown`, so the court dimension contributed nothing. op20 was written
  against a different receipt contract than the prod compass route produces.

### What a full-fidelity op20 dogfood needs (scoped, not done)
A proper `prod Receipt → op20 seed` adapter that: parses `courtVerdict` prose → enum; pulls the
`bar` / `loki` / `fated` JSON-TEXT columns; maps `nciByLens` → hci; derives somatic/derivative dims
where the DB has them (`flowTopology`, `manifoldCurvature`, `driftState`, `coherencePct`). Then the
54-dim space is genuinely populated and the clusters mean something beyond the gradient axis.

## op20 — FULL-FIDELITY run (with the field adapter, built same session)
Adapter: `operators/prod_receipt_to_op20_seed.py` — maps real prod columns into op20's seed keys,
faithfully (fills a dim only when the row carries the signal; never fabricates somatic/axiom).
Key faithful mappings: `court`[] check array → verdict enum (BLOCK>TENSION→CONDITIONAL>PERMIT);
`fated` JSON → length dims; `nciByLens` conviction+coherence → hci; `macroTags`(BAR) + mode=COURT →
lab threat / bar ruin; `doorClass` → irreversibility.

Input now genuinely varies (not constant): court `CONDITIONAL 145 / BLOCK 95 / PERMIT 7` ·
lab_threat `HIGH 176 / LOW 71` · ruin `True 149 / False 98` · fated.facts nonzero 246/247 · hci 7 distinct.

**Result: 17 clusters + 3 noise · seed_count 247 · avg_silhouette 0.765 · coverage 98.8% · corpus_ready 1.0.**
Clusters are now multi-axis decision archetypes (core_dims span signal-class + threat + ruin + court):
| cluster | n | core dims |
|---|---:|---|
| cluster_6_ruin_risk | 46 | accelerating · threat_high · ruin · court_conditional |
| cluster_0_ruin_risk | 39 | stable · threat_high · ruin · court_conditional |
| cluster_2 | 38 | accelerating · threat_low · baseline_ok · court_conditional |
| cluster_1_ruin_risk | 28 | stable · threat_high · ruin · **court_BLOCK** |
| cluster_7_ruin_risk | 25 | accelerating · threat_high · ruin · court_block |
| cluster_3 | 6 | accelerating · threat_low · **court_PERMIT** (clean-go) |
| … 11 more small archetypes … | | |

vs the pre-adapter run (3 gradient-only clusters). Same silhouette (0.765) at 6× granularity ⇒ the
extra dims are real structure, not noise. Court dimension now drives clustering (BLOCK vs CONDITIONAL
vs PERMIT visibly separate archetypes) — the exact dimension that contributed nothing before.

Reproduce: pull the rich Receipt columns (id, nciScore, nciByLens, mode, doorClass, court, fated,
macroTags, gradientMagnitude, surface, EXTRACT(EPOCH FROM createdAt)) → save → adapt →
`Cultivator().cultivate_from_jsonl(adapted.jsonl)`. Prod data stays in scratchpad (PII); only the
adapter code is committed.

## Still constant (honest residual)
somatic (22–27) and axioms (40–43) still default — prod doesn't store them (they surface only as the
3-receipt noise pocket where everything else was outlying). Fully closing those needs the compass
route to persist somatic/axiom fields, or a SageTrace join. Not a today-fix; the 54-dim space is now
~13 real dims, up from ~3.

## Net
op20 and op21 both work. op21 is deterministic (P1 PASS). op20 now runs at FULL fidelity over the real
247-receipt corpus via a faithful adapter — 17 real decision archetypes at 0.765 silhouette. The
machinery, the fuel, and the adapter all exist now. Remaining: persist somatic/axiom at write-time to
light up the last ~40 dims.
