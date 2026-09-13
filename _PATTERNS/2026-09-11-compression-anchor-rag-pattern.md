# Pattern: Compression-Anchor RAG (Witness-to-Spec Invariant Ladder)

> **Pattern ID:** `PAT-RAG-COMPRESSION-ANCHOR-001`  
> **Status:** BANKED (2026-09-11)  
> **Origin:** Jogged instant recall of the complete 2026-09-08 ARCS-on-ARCS living-system architecture (heartbeat, OT canary, mutual attestation, self-serve atlas scan, carrier signal normalization) from a single fragment of conversation.

---

## The Problem
Standard semantic retrieval / vector search across large heterogeneous codebases and multi-session logs often fails in two opposite directions:
1. **Shallow keyword matches** retrieve noisy, flat references (mentions of words without conceptual altitude).
2. **Generic LLM summarization** dilutes the exact load-bearing idioms, metaphorical geometry, and critical architectural invariants that human partners anchor their cognition on.

## The Retrieval Architecture (What Made It Snap)

Instead of a generic text similarity query, retrieval was executed along a **4-rung compression ladder**:

```
[ LEVEL 1: Epistemic Anchor (Tension/Metaphor) ]
   Query: "pulse should check the oracle" (from human memory)
   Target: _STATE/witness/*.jsonl (High-altitude human/agent dialogue anchors)
            │
            ▼
[ LEVEL 2: Operational Proof (The OT Layer) ]
   Target: scripts/pulse.py (The actual executable clock)
   Verification: python3 scripts/pulse.py status (Check live beats vs genesis)
            │
            ▼
[ LEVEL 3: Forward Specification (The Generative Spec) ]
   Target: _SPECS/self-serve-atlas-scan-v1.md (The architectural intent)
            │
            ▼
[ LEVEL 4: Grounded Diagnostic (The Seam/Gap) ]
   Comparison: What was specified vs. what was wired into pulse.json
```

### Why This Works (The Mechanics)

1. **The Witness Register as High-Fidelity Lossless Compression:**
   `_STATE/witness/*.jsonl` stores verbatim quotes paired with structural context (`context` + `gut` + `load-bearing flash`). This preserves the **semantic coordinates** of a breakthrough in 2-3 sentences without thousands of tokens of chat fluff.
2. **Cross-Referencing the Twin (Logical ⇄ Temporal):**
   Searching for the *interaction* between primitives (`pulse` $\leftrightarrow$ `oracle`) immediately filtered out hundreds of generic "heartbeat" or "pulse" occurrences across node_modules and UI CSS keyframes.
3. **Immediate Operational Grounding:**
   The retrieval did not stop at reading markdown: it executed `python3 scripts/pulse.py status` to ground the historical concept in live reality (Beat 3, 2026-09-08 genesis).

---

## When to Invoke This Retrieval Sequence

When a partner asks "where did we leave off with X" or references a deep architectural concept:
1. **Search `_STATE/witness/*.jsonl`** first with exact metaphorical/relational tokens.
2. **Trace from the witness entry to the corresponding spec in `_SPECS/` or `_DECISIONS/`**.
3. **Run the tool or inspect the operational code in `scripts/` or `operators/`** to see where the physical implementation stopped short of the spec.
4. **Synthesize the gap as a sharp diagnostic**, not a sprawling summary.
