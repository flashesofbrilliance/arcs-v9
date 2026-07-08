# Decision Receipt — Schema v1.1

> The audit trail of the ARCS reasoning system. Updated May 11 2026: added `receipt_deficit` field.

## Schema

```json
{
  "question": "The actual question being decided",
  "horizon": "today | this_week | this_quarter | 1_3_years",
  "stakes": "low | medium | high",
  "mode": "QUICKMOVE | PLAN | COURT",
  "clarity_mode": "SIMPLE | RICH | DEEP",
  "drift_state": "on_track | drifting | recovered",
  "macros_used": ["BAR", "KKL", "LAB"],
  "lenses_applied": ["stoic", "munger", "aristotle", "systems"],
  "true_north": "Single recommended action",
  "why": ["Reason 1", "Reason 2", "Reason 3"],
  "loki_test_passed": true,
  "receipt_deficit": "none | interface_layer | core",
  "kintsugi_flags": [],
  "timestamp": "ISO-8601",
  "session_id": "uuid"
}
```

## Macro Definitions

### BAR (Risk Scan)
- **B**est case if right
- **A**verage case
- **R**isk case if wrong

### KKL (Time Scan)
- **K**now now
- **K**now later
- **L**earn only by doing

### LAB (Adversarial Scan)
- **L**oki test — how does this fail?
- **A**dvisor test — what would a trusted advisor say?
- **B**ayes test — what would change my confidence?

## Compounding Logic

Receipts compound. A session with 3 receipted decisions > 10 unreceipted ones.
The vault is the equity. The receipts are the shares.

## Notion
[Artifact Vault entry](https://www.notion.so/35dd5422179681bb837ee4c74c18fb39)
