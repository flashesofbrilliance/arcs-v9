# Harness — agentic composition layer over ARCS operators

`harness/` is the composition/runtime layer that *consumes* `operators/`,
not an extension of it. It owns: orchestration by JTBD, delegation to
operator capabilities, RAG + model routing, JIT compile-from-entry-point,
sealed-environment and external-dependency integration, multi-tenant
isolation (user0 state must not bleed into net-new tenant), and artifact
rendering (ziggeraut/russian-doll, UA/player schema, ticket outputs).

`operators/` remains the atomic component catalog only. Nothing in
`harness/` changes that taxonomy.

**Public contract (what `harness/` may pin to):**

- *TODO: enumerate stable harness-facing operator entry points here once
  the first harness file commits.*

**Halt condition:** if an operator module holds process-global or
module-level mutable state that would leak tenant state, flag it as
`harness-blocking` and either refactor or scope per-tenant at the caller,
before it's wired into harness flow.
