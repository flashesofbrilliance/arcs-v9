# DYOR — Blacksmith recon (internal)

_Private. For Zach's records + interview prep. Never served (air-gapped). Provenance tagged:
**[verified]** = read directly this session; **[memory]** = from prior verified session/memory;
**[re-verify]** = used inline but not re-confirmed here — check before relying in a room._

## What they are
- **Blacksmith** — "Secure GitHub Actions." Faster GitHub Actions CI: managed runners on their own
  bare-metal hardware, plus a build-cache layer. The pitch is speed + the economics of owning the
  execution layer. **[verified — homepage]**
- YC **W24**; the role is **Staff Product Engineer** for AI-native developer tooling. **[memory]**

## Funding / stage
- ~**$58.5M** total. **Series B $45M led by Peak XV** at ~**$550M** valuation (~Aug 12 2026);
  **GV** led Seed + Series A. **[memory — do NOT cite a hard ARR number publicly]**
- Reading: well-capitalized, past product-market fit, scaling. Hiring "all before year end" and the
  "more about maturity than size of company" note both fit a Series-B scale-up. **[memory / recoil]**

## Security posture (their own words) **[verified — blacksmith.sh/security, read this session]**
- **Compliance:** SOC 2 Type 2, GDPR, ISO 27001 data centers; a Trust Center; answers security
  questionnaires.
- **GitHub integration:** least-privilege app; **just-in-time (JIT) tokens** scoped per job, expire
  after 1 hour; login exclusively via GitHub SSO; no direct access to org/repo secrets.
- **Isolation:** jobs run in **Firecracker microVMs** on bare metal behind a private VPN; never share
  kernels; microVM + state destroyed after each job.
- **Cache:** artifacts on **MinIO + Ceph** clusters on the same fleet; encrypted, isolated by org,
  authenticated + audited.
- **Adversarial:** **quarterly external pen-tests.**
- **Values that read off this page:** least-privilege · fail-closed · isolation boundaries ·
  adversarial testing as routine. (This is the honest hook the cover letter nods to.)

## The moat (positioning, worth arguing in-room)
- Not "a faster runner" as a feature — it's owning **bare metal + storage + the utilization curve**,
  each layer paying for the next. The strategic question to raise: *is the durable win the coding
  agent, or the execution layer underneath everyone's agents?* **[verified — synthesized from homepage
  + cover letter thesis]**

## Customers / stack signals **[re-verify]**
- The bundle domain-map pairs their customer/adjacency space with Zach's shipped domains
  (fintech ↔ Mercury/Finch/Expensify · AI-native infra ↔ Exa/Chroma/Clerk/Supabase · media ↔
  Descript/VEED/Plex). Treat the specific named logos as **illustrative of the space**, not a
  confirmed Blacksmith customer list — re-verify any specific logo before asserting it to them.

## Hiring context **[recoil / memory]**
- Process: 3 stages (was 4) — two short screens (~30 + ~60 min), then on-site; ~1-day turnaround.
- One prior candidate rejected: ex-AWS, "too corporate." Zach's scrappy-operator framing is the
  deliberate anti-profile.
- Reports into founders (recruiter believes so; **[re-verify]**). On-site vs hybrid unconfirmed.

## Gaps to close before a live round
1. Confirm the current customer logos (their site / case studies) rather than relying on the domain-map.
2. Confirm reporting line + on-site expectation.
3. Read their docs/changelog for the newest surface (their "next products" = where the agent story lives).

_Seeded by the recoil ([[recruiter-recoil-report.md]]); feeds the founder gauntlet
([[founder-gauntlet.md]]) and the cover-letter security nod._
