# _ARTIFACTS — redundant knowledge bank (self-contained explorer sources)

Committed 2026-07-11 per the Alexandria fire-test finding: these five interactive
explorers were published to claude.ai but their sources lived only in a session
scratchpad — single-copy scrolls by our own census. Now git-distributed.

Each file is fully self-contained (inline CSS/JS, embedded data — no network needed
to open): open directly in any browser, forever, offline. Data source of truth:
`runtime/specs/knowledge-lattice-v1.json` (explorers embed a compact copy at publish).

| File | What it is | Published at |
|---|---|---|
| arcs-meta-audit-roadmap.html | Meta-audit + roadmap (fidelity ladder, resolution dial, kairos timeline, inchworm log) | claude.ai/code/artifact/cc787dbb-… |
| arcs-knowledge-lattice.html | Abductive-web explorer (81 nodes, 5 domain meta-nodes, 720° protocol, phase gauge) | claude.ai/code/artifact/7ec96669-… |
| arcs-12d-orbital.html | 12D phase space (keyboard nav, metronome ×5, invariants, satoshi, entanglement) | claude.ai/code/artifact/ef9e90f9-… |
| arcs-moire-mobius.html | Moiré/Möbius generative study — PARADOX topology, horizon through fog | claude.ai/code/artifact/53dc557c-… |
| arcs-alexandria.html | Library-of-Alexandria rotunda + fire test | claude.ai/code/artifact/4c3ccb93-… |

Update law: when an explorer is republished, re-copy its source here in the same
commit (sentry checks for drift between _ARTIFACTS/ and the lattice JSON epoch).
