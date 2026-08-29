# The Invariant Envelope — one schema, many fluid surfaces

> "Invariant fluidity": the *shape* is fixed, the *render* is free. Every durable ARCS
> object — a memory file, a tenant SSOT (`runtime/recoil/generated/*.json`), a published
> Claude artifact — conforms to the same six-field envelope. Everything else is a surface.
>
> This generalizes the existing memory frontmatter (`name` / `description` / `metadata.type`)
> and the `[[name]]` memory link. `name` → `id`. `metadata.type` → `type`. `[[name]]` → an
> entry in `associations[]`. Nothing already written breaks; the envelope is a superset.

## The envelope

```jsonc
{
  "id":       "kebab-slug-or-artifact-uuid",   // stable identity (was memory `name:`)
  "type":     "memory | ssot | artifact | adr | dewy | canon | proverb",
  "tenant":   "user0 | <counterpart-slug>",    // user0 = Zach = tenant zero
  "provenance": "how this object came to exist (tool, script, hand, session)",
  "updated":  "YYYY-MM-DD",                     // last-known-true, NOT live state
  "associations": [                             // was the [[name]] link, now typed + cross-type
    { "rel": "generated-from | renders | memory | sibling | supersedes | tenant-of | echo",
      "ref": "<id | file-path | url>" }
  ]
}
```

Type-specific surfaces hang additional fields off the envelope (an `artifact` row adds
`url`, `title`, `source_file`; a `proverb` adds `aspect`, `verb`, `source_adr`). The six
fields above are the invariant every row shares.

## Tenancy

- **user0** — Zach. Canon, product architecture, self-reflective artifacts, infra.
- Each counterpart is a **tenant**: `todd-prl`, `yuri-kleban`, `robin-daniels`,
  `louisville-brands`, `christopher-skinner`, `tribe-ai`, `assemblyai`, `prospect` (teardowns
  of non-engaged targets). A tenant's SSOTs, artifacts, and memories share `tenant`.

## Association relations

| rel | meaning |
|---|---|
| `generated-from` | this object is rendered from ref (artifact ← its repo SSOT) |
| `renders` | inverse: ref is rendered from this object |
| `memory` | ref is a memory file that grounds/explains this object |
| `sibling` | same tenant + same surface family (the Kleban 6-surface set) |
| `supersedes` | this object replaces ref (older artifact version) |
| `tenant-of` | ref is the tenant root this belongs to |
| `echo` | Orthogonal-Echo: cross-domain kinematic isomorphism to ref (ATG/#4 spice) |

## The gap this closes

Published artifacts had **no repo index** and many **no repo SSOT** — they live only as
hosted HTML, violating ADR-031 ("extend the single source of truth"). The registry
(`_STATE/artifact-registry.jsonl`) is the index; `source_file: null` rows are the
back-prop backlog (chief among them the Tao of ARCS — see `_CANON/tao-proverbs.jsonl` plan).

## Governance (NOTOMATION)

The machine fills **mechanical** fields (`id`, `url`, `title`, `updated`) and **proposes**
associations. Zach owns `tenant`, `source_file`, and confirmed `associations`. Re-seeding
(`scripts/artifact_registry.py`) merges by `id` and never overwrites a human-set field.
