# PRL normalization + recognition layer (1.3 backbone, SSOT)
_2026-08-07 · Deterministic (no LLM) canonicalization + recognition over PRL's own data. Turns free-text lead
input into a canonical PRL grade / material family / competitor-equivalent. **Recognition only — never emits a
spec, price, or UL status** (those route to a human; the anti-fabrication rule holds here too)._

## Files
| File | What |
|---|---|
| `normalize.py` | The engine: `norm()` canonicalizer + `recognize(text)` + `normalize_state()`. Runnable self-test. |
| `grade-dictionary.json` | 150 PRL grades → family + description + aliases (dash/space/slash/suffix variants) |
| `material-synonyms.json` | Family/chemistry aliases (PC↔polycarbonate, PA66↔nylon 6/6↔polyamide 66…) + the modifier/suffix decode grammar |
| `competitor-to-prl.json` | 895 keys: competitor grade (bare + brand-qualified + maker-qualified) → PRL equivalent(s) |
| `field-normalization.json` | `location_c` state map (full name → USPS), lead_source canonical set |

## What it does (recognition precedence)
`recognize(text)` scans 1–3-word grams of the normalized text and returns matches:
1. **Exact PRL grade** (`PC-GP1-D`, `pc gp1`) → `prl_grade`.
2. **Competitor grade → PRL equivalent** (`Lexan 141` → PC-GP2-D) → `competitor_equiv`.
3. **Material family** (`polycarbonate`, `PA66`, `nylon 6/6`) → `family` (then route to a specialist for the
   exact grade — never guess the grade from a family).
4. Nothing → empty → handoff.

Self-test: **10/10** including the real audit inputs (`PA66 for fiber extrusion` → NY66; `Lexan 141` →
PC-GP2-D). Run `python3 normalize.py`.

## Known limitations (honest; these are the eval's job to track)
- **`6/6` splits.** "nylon 6/6" currently matches NY6, not NY66, because `/` tokenizes. Fix: pre-map
  `6/6`,`6,6`→`66` before gramming. Tracked; low-harm (still surfaces nylon + routes to specialist).
- **Bare competitor numbers are ambiguous.** "3105" alone can map to >1 PRL grade (35 such collisions);
  brand-qualified input ("Makrolon 3105") disambiguates. When only a bare number is given, return all
  candidates and let the specialist confirm — never auto-pick.
- **Recognition ≠ recommendation.** Surfacing "you mean our PC family" is allowed; asserting "use PC-GP2-D" is
  a specialist call. The bot recognizes and routes; it does not spec.

## How this feeds the deterministic eval + the bot
- **1.3 recognition:** the bot runs `recognize()` on the inquiry to tag intent + pre-fill the lead
  `description` (e.g. "family: NY66; competitor ref: Lexan 141") — improving routing without stating specs.
- **Routing/coverage eval (next):** each `(audience × trigger × condition)` case asserts the expected
  `recognize()` output + expected surface (KB answer / starter / handoff). Deterministic pass/fail — extends
  `firewall-test-prompts.md` from "must refuse" to "must recognize + surface exactly this."
- **Data quality:** `normalize_state()` fixes the audit-found `location_c` inconsistency (New Jersey vs TX).
  **Write-format is still gated** — existing Unbounce→Sugar zaps use FULL state names, so confirm the target
  format with Todd before any normalization write.

## Regenerating
The dictionaries are generated from `../../prl-kb/prl-product-catalog-2025.json` (grades + nomenclature) and
`../../prl-kb/competitor-intel/cross-reference-map.csv`. Re-run the generator when those change.
