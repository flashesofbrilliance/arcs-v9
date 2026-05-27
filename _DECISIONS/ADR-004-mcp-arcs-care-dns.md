# ADR-004 — mcp.arcs.care DNS: Wire Custom Domain to perplexity-mcp

> **Status:** DECIDED  
> **Date:** 2026-05-27  
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** How should `mcp.arcs.care` be routed, and what is the fix for the current 404?

---

## E — Entity / System

- Vercel project `perplexity-mcp` (`prj_BOLubU4LLun9jadQZJTkBiXtaHzF`)
- Current domains on project: `perplexity-mcp-kohl.vercel.app` only — `mcp.arcs.care` is NOT listed
- DNS registrar for `arcs.care` domain
- `arcs-rom-manifest.md` Tier 2 table

---

## W — Window

**Horizon:** TODAY  
**Revisit trigger:** After domain is added and propagation confirmed.

---

## Context

**Audit finding (2026-05-27):** `mcp.arcs.care` returns HTTP 404. The Vercel project `perplexity-mcp` is READY (`dpl_6JUGdNvCEhDPvz9pDmXYBcQnW62b`) but the custom domain has never been added to the project. The domain is not in the project's domain list.

`arcs.care` root domain is on `arcs-care` project — DNS is likely managed through Vercel or the registrar. Adding `mcp.arcs.care` as a subdomain requires:
1. Adding the domain to `perplexity-mcp` project on Vercel
2. Vercel will provide a DNS record (CNAME) to add at the registrar
3. Once propagated, `mcp.arcs.care` → `perplexity-mcp-kohl.vercel.app`

---

## Decision

**Chosen:** Add `mcp.arcs.care` as a custom domain on the `perplexity-mcp` Vercel project.

**Steps:**
1. Vercel dashboard → `perplexity-mcp` project → Settings → Domains → Add `mcp.arcs.care`
2. Copy the CNAME record Vercel provides
3. Add CNAME at DNS registrar: `mcp` → `cname.vercel-dns.com` (or whatever Vercel specifies)
4. Wait for propagation (~5 min on Vercel's edge, up to 24h for global)
5. Verify: `curl -I https://mcp.arcs.care` → 200

---

## Y — Conviction

**Polarity:** GREEN  
**Conviction:** HIGH  
**Stability:** STABLE

**Loki test:** None — this is a mechanical DNS fix, not an architectural decision.

---

## Consequences

- `mcp.arcs.care` becomes the canonical MCP endpoint URL
- Update `arcs-rom-manifest.md` Tier 2 table: add `mcp.arcs.care` row with deployment ID `dpl_6JUGdNvCEhDPvz9pDmXYBcQnW62b`
- Update `~/.claude/CLAUDE.md` P2 row: `perplexity-mcp` → add `mcp.arcs.care` as canonical URL
- ADR-003 COCD API docs can reference `mcp.arcs.care` once live

**Implementation pointer:** Vercel dashboard (no code change required)

---

## Linked receipts / ADRs

- ADR-003 — COCD weave (blocked on this for API docs)
