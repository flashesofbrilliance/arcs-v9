# ADR-032 — Zero-Trust Posture (governing)

**Status:** ACCEPTED · GOVERNING · 2026-07-19
**Y:** GREEN / HIGH / STABLE
**Supersedes nothing; governs everything after it.**

## Context

Extensibility keeps enlarging the attack surface: new public surfaces (subdomains,
`/api/*`), a multi-agent workflow fleet, multiple concurrent sessions on `main`, MCP
servers that reconnect under changing identities, third-party OSS agents/skills, and a
**public** repo whose commit/PR text is attacker-writable. This session's own threat
assessment found our two hardening passes — least-privilege and cost-delegation —
pointing *opposite directions* at the untrusted-input boundary (weakest model, broadest
egress, on the most hostile input). That is exactly the kind of unforeseen threat-factor
that poisons an extensible base. We need a standing posture, not per-incident fixes.

## Decision

**Zero-trust is governing law for every architectural and implementation decision.**
It is native to ARCS, not bolted on: "affect proposes, receipt disposes" already says
*trust nothing until verified*; RLS deny-all already applies it at the database. We
extend it to the whole stack.

### Principles

1. **Never trust, always verify.** Every input is untrusted until validated — user text,
   external content (email/web/transcripts), MCP tool results, *another agent's output*,
   and *a model's own prior output*. No source is privileged by origin.
2. **Assume injection / assume breach.** Design as if any single component is already
   compromised; the job of the architecture is to bound the blast radius, not to prevent
   every compromise.
3. **Least privilege, deny by default.** Every agent, route, tool grant, and role gets
   the minimum. Start from nothing and add only what the stage provably needs.
4. **Explicit trust boundaries; quarantine at ingest.** Untrusted content is wrapped and
   handled as **data, never instructions.** Instructions found inside ingested content
   are a *signal to report*, never a directive to follow.
5. **Egress is a control, not just ingress.** Outbound channels — `WebFetch`, `Bash`,
   MCP calls, any network — are exfiltration paths. **Read-only ≠ safe.** Scope egress
   explicitly; never let a component fetch a URL *derived from* untrusted content.
6. **Trust-of-input drives model tier — risk-calibrated, never blanket.** Tier is a
   function of `difficulty × trust-of-input × blast-radius`, chosen to **balance risk and
   reward against cost** — not to inflate spend. Spend a robust model *only* where
   untrusted input meets an egress channel or a real consequence; keep the cheapest viable
   model where input is trusted (your own calendar/transcripts) **or** blast-radius is
   already bounded (interior no-tools reasoners that can't exfil even if poisoned).
   Compute efficiency is a first-class constraint: the security budget is concentrated at
   the few genuine trust boundaries, not smeared across the fleet.
7. **Verify provenance, not just plausibility.** Verification must catch *tampering and
   injection*, not only epistemic error. A plausible claim built on poisoned signals must
   still fail.
8. **The supply chain is untrusted.** Third-party agents, skills, plugins, MCP servers,
   and OSS are dependencies: vet, pin, scope, and never grant on trust. (The OSS vetting
   and secrets-inventory ADRs this session are conformant instances.)
9. **Anti-fragile.** Every detected attack or injection attempt is logged to the immune
   ledger (`arcs-immune-system`) and hardens the next iteration. The system should get
   *stronger* from being probed, not merely survive.
10. **Authenticate deterministically where you can; keep intent probabilistic.**
   Cryptography — including ZKPs — deterministically proves *identity, provenance,
   integrity, and capability*. It does **not** prove *intent*: there is no proof that
   given content is non-malicious, because malice is semantic, not a statement about a
   known secret. So split every "trusted vs bad actor" decision:
   - **Deterministic (crypto):** *who / what / where / did-this-arrive-unmodified.* Use
     signed git commits from known keys (`githubCommitVerification`), Sigstore, mTLS,
     W3C Verifiable Credentials, transparency/Merkle logs for receipts, and TEE remote
     attestation for *environment* trust. **ZKPs specifically** earn their cost only for
     *privacy-preserving* proofs — selective disclosure (BBS+), proving key ∈ allowlist
     without revealing which, or verifiable computation across a trust boundary. For most
     actor/provenance checks a plain signature is deterministic and near-free; do **not**
     reach for a SNARK where a signature suffices (Principle 6 — cost discipline).
   - **Probabilistic (defense-in-depth):** *is this content an injection / is this intent
     hostile.* Not provable — keep the untrusted-data framing, boundary-robust model, and
     provenance-verify. Crypto **shrinks** this surface (a cryptographically-authenticated
     channel needn't be re-litigated for identity) but never eliminates it.

   Net rule: authenticate the actor/channel/provenance with deterministic crypto, then
   apply behavioral checks only to *content*. Never let a cryptographically-valid signature
   imply the *payload* is safe — a trusted actor can still relay a poisoned input.

### Conformance checklist (every ADR + non-trivial implementation must answer)

- [ ] **Inputs classified** by trust level (trusted / external-untrusted / cross-agent / self-prior)?
- [ ] **Least privilege** — minimum scope, deny by default?
- [ ] **Egress enumerated** and scoped (not just writes)?
- [ ] **Untrusted content wrapped** as data-not-instructions?
- [ ] **Model tier ≥ trust of input** at each boundary?
- [ ] **Verification screens provenance/tampering**, not just plausibility?
- [ ] **Blast radius** if this component is fully compromised — bounded and stated?
- [ ] **Attack/failure path logged** for anti-fragile learning?

An ADR that cannot check a box must state the residual risk explicitly (naming the gap is
conformant; hiding it is not).

## Operational patterns

**Skeptic Sentinel (bidirectional intent + premise screen).** A dedicated adversarial
operator that questions content *before* it enters reasoning and *after* the output is
produced — the operational form of P4/P7/P9. Three modes:
1. **Threat vector / form factor** — classify injection attempts (imperative-override,
   role/jailbreak, exfil-lure, tool-coercion, delimiter-escape, homoglyph/obfuscation).
2. **False premise / wolf-in-sheep's** — well-formed, plausible content whose *framing*
   smuggles a hostile or unearned assumption. Ancient-Cynic "question the premise, deface
   the currency" (the same lens used in the Chan Suh work). Not a scanner for *what is
   said* but for *what is assumed*.
3. **Provenance** — does the signal match its source's declared trust level?
Primed by the *past* — the pathogen taxonomy in the immune ledger (`pathogen_log` /
`immune_sessions`), so it recognizes known forms; each new form it catches is logged and
primes the next screen (anti-fragile). Runs as no-tools reasoners (bounded blast radius),
model risk-calibrated (Sonnet pre-screen, Opus post-gate). **Implemented** in
`recoil-report.mjs` (`skeptic:pre`, `skeptic:post`).

**Dual-control handshake (M-of-N sign-off).** No single agent's output commits a
consequential action unilaterally — a *proposer* and an independent *confirmer* must both
sign off, like a multisig caller/receiver handshake. Generalizes the existing
`/dual-bar-raiser` (architect + implementer). Two flavors by actor type (per P10):
- **Agent↔agent:** deterministic — the confirmer verifies an HMAC/signature over the
  proposer's action, ideally on a *different model* so one compromised model can't self-approve.
- **Human-in-the-loop:** a step-up auth challenge (below) gates the commit. Reserve for
  genuinely consequential/irreversible actions; "run-of-the-mill" gets the cheap agent↔agent
  form so it doesn't become friction.

**Step-up authentication roadmap (the human factor for dual-control).** Not a wallet; one
standard, phased — cheapest-already-owned first, phishing-resistant endgame last.
**Decision (2026-07-19):** go with the option we already have logic for — the **email
magic-link** as the primary human sign-off factor — and add a **TOTP authenticator app**
(not RSA; RS256 is the JWT signing alg Auth.js already uses) as an optional layer only if
needed. WebAuthn/passkeys remain the eventual endgame.
1. **Now — email magic-link** (Auth.js v5 + Resend, already built): possession of the inbox
   is a real second factor. Reuse it for human sign-off; zero new dependency.
2. **Easy add — TOTP** (`otplib`, RFC 6238) or **SMS OTP** (Twilio Verify) for non-interactive
   step-up. SMS is the *weakest* link (SIM-swap; NIST-deprecated as primary) — prefer TOTP.
   Never use a low-entropy identifier (tax ID, phone number) *as the secret*.
3. **Endgame — WebAuthn / FIDO2 passkeys**: one API that covers **Touch ID / Face ID**
   (platform authenticators), **YubiKey** (roaming/biometric hardware), and passkeys —
   phishing-resistant MFA. This is the single answer to "MFA / passkey / YubiKey / Touch ID /
   Face ID," not five services.

**Chronos-sequencer discipline (general — not just recoil specs).** Any point-in-time
artifact that a later reader consumes as *current state* — handoff, snapshot, ADR, canon
stratum, memory log, any append-only ledger — becomes **dead state wearing a live face** the
moment work continues past it. A chronological/prefix reader (next session, token-truncated
LLM read, human skim) will serialize the superseded version. Originally caught in recoil
multi-pass reports; it is **general**. This is P1 (never trust, always verify) applied to
*time*: recency and position are not currency. Every such artifact must carry:
1. a **current-state header first** (readOrder — authority order, not chronological);
2. in-place **`[SUPERSEDED — see X]`** markers on overturned strata (never silently leave
   dead text looking live);
3. a **freshness/provenance stamp** so a reader can tell how stale it is before trusting it
   (the "data as of" fix on the Live Pulse is the same principle at the UI layer).
Fork Lineage (J17) is the *provenance* half of the remedy; readOrder is the *ordering* half.
Proven live this session: the handoff drifted the instant work continued past it — which is
why state-sync must be a *gated final step*, not a remembered one.

## Consequences

- ADR authoring gains the checklist above; the `/ultrareview` gate should enforce it.
- Some cost increase (robust models at trust boundaries) — accepted, per Principle 6.
- First application (same session): the recoil-report workflow is re-scoped —
  trust-of-input axis added to the delegation policy, gather stages split so only the git
  reader holds a shell, gathered content wrapped as untrusted data, and the verify stage
  told to screen for injection. Residual gap named: MCP-source gatherers still reach their
  server via a read-only built-in that includes `Bash` until per-tool MCP allowlisting is
  validated.

## Changelog
- 2026-07-19 — v1.0 — doctrine established (post threat-assessment, this session).
