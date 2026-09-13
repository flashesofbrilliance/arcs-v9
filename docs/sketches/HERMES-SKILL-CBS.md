# HERMES AGENT SKILL: CBS ANTI-SLOP & ZERO-TELEMETRY HARNESS
## Skill Name: `cbs-anti-slop`
## Path: `.hermes/profiles/arcs/skills/arcs/cbs-anti-slop/SKILL.md`

### Definition & Purpose
Hermes operator skill for executing the Consonance-Burstiness-Symmetry (CBS) evaluation engine against prospective content and verifying zero-telemetry routes.

### Standing Invariants (YOAV PROTOCOL):
1. Code lives strictly in `src/lib/cbs.ts` (deterministic, zero-dependency).
2. Public tool mounted at `src/app/tools/anti-slop/page.tsx` runs in-browser RAM (zero telemetry).
3. Do not run multi-model fanouts or foreign LLM calls for scorable regex tasks.

### Execution Routine:
```bash
# Verify implementation compiles clean
npm run build

# Run deterministic audit against staged files
node -e "const { runCBSAnalysis } = require('./src/lib/cbs'); console.log(runCBSAnalysis(process.argv[1]))" "$PROSE_DRAFT"
```
