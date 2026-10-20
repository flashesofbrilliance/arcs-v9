# JTBD graph pre-registration, amendment 1 (2026-10-18)

Amends `_PATTERNS/2026-10-18-jtbd-graph-preregistration.md`. No threshold number changes. Written
after a claims-skeptic check of Sprint 0 and before Sprint 1 merged.

## Corrections
1. **"The 6 known tool duplicates"** (s1 section) is withdrawn. A recount of
   `runtime/specs/tool-catalog.json` finds 0 duplicates by (kind, name). One name, `recoil-report`,
   appears under three kinds (command, workflow, package); their namespaced ids differ, so it is not
   a duplicate. s1 reconciles against the real counts.
2. **Wildcard-host surfaces.** Five surface rows have host `*`. Zach decided (2026-10-18) the host is
   written as `any`: `tool:surface:any/<path>`. Schema key note updated; fixtures cover both the
   legal `any` form and the illegal `*` form.
3. **Memory "missing key 0"** in ADR-089 was false when written: `project_yuri_kleban_google.md` has
   no top-of-file front matter (first `---` at line 139). s1 counts such files as unresolved job
   sources and reports them; it does not invent a key.

## Disclosure
The two s1 conditions added to the original file in commit `cd4ffbf4` (operator design-dep rule,
memory reproducibility caveat) were an in-place edit, not a dated amendment. No s1 count existed
then, so the failure condition was not triggered, but they should have been here. They stand.
