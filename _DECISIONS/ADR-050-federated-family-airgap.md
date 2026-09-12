# ADR-050 — The federated family + the SSOT/front-end air-gap

**Status:** Accepted · 2026-08-11

## Context
The canon/product artifacts (polyform, four-cores, playground, monolith, performers) lived only as
private claude.ai artifacts, plus internal SSOTs (meta-audit, Tao, status) that name real clients.
Shipping them publicly risks leaking the cross-client book.

## Decision
Two layers with an enforced air-gap. **SSOT layer** (meta-audit · Tao · status · registry) is the
internal truth — rich, unredacted, gated. **Public layer** (forge · forge-cut · playground(+4) ·
monolith) are prospect-safe *faces*, generated from the SSOTs with all real names, dead claude.ai
links, and insider jargon stripped. The Meta-Audit head is dropped from public (it enumerates the
client portfolio); it stays SSOT. Hosted on arcs.care subdomains via next.config host rewrites.

## Consequences
Prospects get the abstract engine; clients' names never cross the gap. The gap is guarded by the
tripwire (ADR-051). Per-tenant field-truth pages are the future client-facing counterpart.
