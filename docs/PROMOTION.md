# Branch policy & CI promotion — receipts that learn from drift

The point of this gate is not "tests pass." It is to **turn architecture decay into
receipts you can learn from**. Drift, crift, and tech debt accrete by blight and neglect —
a copy forked instead of extending the SSOT, an internal name left on a public page, a
dead link no one re-curled. Each gate below is a detector; each **failure is a receipt**.

## Branch policy

- `main` is protected and always deployable. No direct pushes (the one sanctioned exception
  is the content-only, build-excluded path in AGENTS.md, pushed `--no-verify` from a
  main-tracking worktree). All code lands via PR.
- Feature work happens on `claude/*` branches (or a worktree), opened as a PR into `main`.
- Before committing to `main` from a shared worktree, `git rev-list HEAD..origin/main` MUST
  be `0` (the write-lock; pull first). Concurrent sessions coordinate on this.

## The promotion gates (drift detectors → receipts)

| Gate | When | Detects (the decay) | The receipt on failure |
|---|---|---|---|
| **Family Tripwire** | PR touching `public/**` / `next.config.ts` | prospect-safety drift: real name, dead `claude.ai/code` link, or insider jargon leaked to a public page (air-gap eroding) | red required check → merge blocked; the diff is the receipt |
| **ci** | every PR | build / typecheck / unit regressions | red check |
| **Deploy Verify** | Vercel production `deployment_status: success` | live decay: API smoke + `tests/family.spec.ts` (routes, console errors, a real head-mount + filter toggle) fail on prod | **auto-rollback to last READY + a GitHub Issue** — the durable learning receipt |

## PR documentation criteria (the body IS the receipt)

Every PR uses `.github/pull_request_template.md`. A merge requires:
1. **What & why** — the decision, not the diff.
2. **Drift/tech-debt receipt** — debt added or paid, SSOT respected (ADR-031), air-gap held.
   Knowingly adding debt is allowed; leaving it **unnamed** is the drift.
3. **Verification** — tripwire clean + live/E2E evidence.

A thin body on a risky change is itself a drift signal and a reason to request changes.

## Required status checks (set once, by a human with admin)

```bash
gh api -X PUT repos/flashesofbrilliance/arcs-v9/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  -f 'required_status_checks[strict]=true' \
  -f 'required_status_checks[contexts][]=Family Tripwire (prospect-safety gate) / tripwire' \
  -f 'required_status_checks[contexts][]=ci' \
  -F 'enforce_admins=false' \
  -F 'required_pull_request_reviews[required_approving_review_count]=0' \
  -F 'restrictions=null'
```

## Feeding the learning loop

Deploy-Verify Issues and blocked-tripwire diffs are the raw receipts. Promote the recurring
ones into ADRs / DEWY receipts via the ADR/DEWY candidate watcher (`scripts/adr_dewy_watch.py`)
so the same decay is caught by construction next time — the gate teaches the generator.
