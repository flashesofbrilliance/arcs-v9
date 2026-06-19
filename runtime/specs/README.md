---
name: runtime-specs-index
description: Runtime specifications, ROM documents, and schema definitions for ARCS v9
version: 1.0.0
category: runtime/specifications
---

# ARCS v9 Runtime Specifications

This directory contains all **schema definitions**, **ROM (Rules of Motion) documents**, and **engineering specifications** that govern ARCS v9 runtime behavior.

## Organization

### Schema & Data Model

| File | Purpose | Type | Status |
|------|---------|------|--------|
| `dewy-receipt-schema-v1.json` | DEWY receipt data model (JSON Schema Draft 07) | Machine-readable | ✅ ACTIVE |
| `dewy-receipt-schema-v1.md` | DEWY receipt fields — human-readable companion | Documentation | ✅ ACTIVE |

### Motion Rules & Attribution

| File | Purpose | Type | Status |
|------|---------|------|--------|
| `time-quality-attribution-rom.json` | W-field inference rules, Kairos Lock, phase-band governors | ROM v0.1.0 | ✅ ACTIVE |
| `lattice-pressure-rom.json` | Superionic goal lattice pressure model, edge-decay, calcification guards | ROM v0.1.0 | ✅ ACTIVE |
| `ARCS-v9-ROM.md` | Complete Rule of Motion reference document | Reference | ✅ ACTIVE |

### Engineering Specifications

| File | Purpose | Type | Status |
|------|---------|------|--------|
| `arcs-v9-engineering-spec-v1.md` | Full stack architecture, API routes, data flow | Spec v1 | ✅ ACTIVE |
| `arcs-v9-consolidated-design-v1.md` | Consolidated design patterns and UI architecture | Reference | 🟡 REFERENCE |

## Key Integration Points

### Prisma Schema Alignment
The Prisma schema in `prisma/schema.prisma` must conform to `dewy-receipt-schema-v1.json`:
- All DEWY fields present in schema: D, E, W, Y, tributaries, nci_score, reasoning, etc.
- JSON arrays stored as TEXT (SQLite compat)
- Enums use canonical polarity/conviction/stability values

### Compass Route (src/app/api/compass/route.ts)
The compass pipeline expects:
- L0–L5 Claude call returns JSON matching DEWY schema structure
- Y-gate computation uses enums from `dewy-receipt-schema-v1.json`
- Time attribution follows `time-quality-attribution-rom.json` rules
- Lattice inference respects `lattice-pressure-rom.json` governors

### ADR Cross-References

| ADR | Expects | File(s) |
|-----|---------|---------|
| ADR-002 | Database split (dev SQLite / prod Postgres) | `arcs-v9-engineering-spec-v1.md` |
| ADR-023 | Observability as superionic goal lattice | `lattice-pressure-rom.json` |
| ADR-020 | Operators library validates against spec | (operators/ directory) |
| ADR-019 | DEWY schema completeness | `dewy-receipt-schema-v1.*` |

## Version History

### v1.0.0 (Current)
- DEWY receipt schema finalized (9 canonical fields)
- Time Quality Attribution ROM locked (W-field, cadence NCI, macro triggers)
- Lattice Pressure ROM locked (edge-decay, contrarian-injection, calcification-guard)
- Engineering spec comprehensive (L0–L5 pipeline, routes, DB schema)

### Deprecated / Archived
Older specification versions are kept in `archive/specs/deprecated-versions/` for reference only.

## How to Use This Directory

**If updating the schema:**
1. Modify both `.json` (machine-readable) and `.md` (documentation)
2. Update `prisma/schema.prisma` to stay in sync
3. Run `npx prisma migrate dev --name <description>`
4. Update this README with new file entries

**If adding a new ROM or specification:**
1. Add to appropriate subsection (Schema / Motion Rules / Engineering)
2. Include version number in filename (e.g., `my-spec-v1.json`)
3. Add ADR reference if this spec validates an ADR
4. Link from this README

**If deprecating a spec:**
1. Move to `archive/specs/deprecated-versions/`
2. Update this README status to 🟢 ARCHIVED
3. Document why it was deprecated (if non-obvious)

## Reading Order

**For new contributors:**
1. Start with `arcs-v9-engineering-spec-v1.md` (overview)
2. Read `dewy-receipt-schema-v1.md` (data model)
3. Consult specific ROM documents as needed (time-quality, lattice-pressure)
4. Reference `ARCS-v9-ROM.md` for complete motion rules

**For implementation:**
1. Check `dewy-receipt-schema-v1.json` before modifying Receipt model
2. Consult appropriate ROM before changing decision logic
3. Update this README if you add or remove specifications
