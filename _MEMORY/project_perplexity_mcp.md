---
name: perplexity-mcp-build-deploy-state
description: Live MCP server at perplexity-mcp-kohl.vercel.app; wired in ~/.claude/mcp.json; 3 tools (search/reason/chat)
metadata: 
  node_type: memory
  type: project
  originSessionId: 2e051b4c-6ed0-47b9-ba6a-e789e4866d88
---

**Last verified:** 2026-05-28

## Status: LIVE ✅

- **Local:** `~/perplexity-mcp`
- **GitHub:** `flashesofbrilliance/perplexity-mcp` (private)
- **Vercel:** Live at `perplexity-mcp-kohl.vercel.app`
- **Wired in:** `~/.claude/mcp.json` as `perplexity` MCP server

## 3 tools (v1)

| Tool | Model | Purpose |
|---|---|---|
| `search` | `sonar` | Real-time web search + citations |
| `reason` | `sonar-reasoning-pro` | Chain-of-thought over live web |
| `chat` | `r1-1776` | Offline reasoning, no web |

## Key files
- `app/[transport]/route.ts` — MCP handler (GET/POST/DELETE)
- `lib/perplexity.ts` — fetch-based Perplexity client, appends citation block
- Package: `mcp-handler` v1.1.0 (NOT `@vercel/mcp-adapter` — old name, superseded)

## Notes
- `sonar-deep-research` deferred to v2 (expensive, avoid accidental calls)
- Not wired into arcs-v9 compass route — standalone personal Claude Code tool
