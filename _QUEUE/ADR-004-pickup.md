# Claude Code Pickup — ADR-004: mcp.arcs.care DNS Fix

> **Status:** READY — manual step only, no code  
> **Generated from:** `_DECISIONS/ADR-004-mcp-arcs-care-dns.md`  
> **Horizon:** TODAY | **Conviction:** GREEN / HIGH / STABLE

---

## What needs to happen

`mcp.arcs.care` returns 404. The `perplexity-mcp` Vercel project is READY but the custom domain has never been added.

## Steps (10 minutes, manual)

1. **Vercel dashboard** → `perplexity-mcp` project → Settings → Domains
2. Add domain: `mcp.arcs.care`
3. Vercel will show a CNAME record — copy it
4. Go to your DNS registrar for `arcs.care`
5. Add CNAME: `mcp` → `cname.vercel-dns.com` (Vercel will specify the exact value)
6. Vercel dashboard will show green checkmark when propagated (~5 min)
7. Verify: `curl -I https://mcp.arcs.care` → HTTP 200

## After DNS is live

- [ ] Update `arcs-rom-manifest.md` Tier 2: add `mcp.arcs.care` row, deployment ID `dpl_6JUGdNvCEhDPvz9pDmXYBcQnW62b`, status READY
- [ ] Update `~/.claude/CLAUDE.md` P2 row: add `mcp.arcs.care` as canonical URL alongside `perplexity-mcp-kohl.vercel.app`
- [ ] Update `_QUEUE/PENDING.md`: ADR-004 → DONE, ADR-003 → unblock (remove DNS blocker note)

## No code required

This is a Vercel dashboard + DNS registrar operation only.
