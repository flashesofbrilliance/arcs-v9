import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { AMMO_COOKIE, ammoUnlocked } from '@/lib/ammo-gate'
import { CIA_GATE, DIOPTRA_GATE, MONDAY_GATE, MYALLY_GATE, gateUnlocked } from '@/lib/passcode-gate'

const SUBDOMAIN_MAP: Record<string, string> = {
  'resume':       '/resume.html',
  'schriner-ext': '/schriner-ext.html',
  // honest.arcs.care: "Check it before you say it", the in-browser front door to
  // arcs-verb-eval (tools/arcs-verb-eval). Static; every check runs client-side.
  'honest':       '/honest.html',
  // dj.arcs.care: Phosphor, the family audio instrument. Static, built from _ARTIFACTS/phosphor-src by scripts/phosphor_build.py; noindex.
  'dj':           '/dj.html',
  // NOTE: 'recruithaus' is handled explicitly below (it has a gated /ammo
  // sub-surface), so it is intentionally NOT in this simple one-to-one map.
}

// Hosts with a gated /ammo companion tier, sharing the recruithaus ammo-gate
// infra (one passcode, one cookie) rather than each inventing its own gate.
// Keyed by subdomain; each entry names its ammo file and its locked-state
// gate page. Adding a new gated host is one line here.
const AMMO_HOSTS: Record<string, { ammoFile: string; gateFile: string }> = {
  'schriner':  { ammoFile: '/schriner-ammo.html',  gateFile: '/schriner-gate.html' },
  'autopilot': { ammoFile: '/autopilot-ammo.html', gateFile: '/autopilot-gate.html' },
  // vico intentionally un-gated (2026-09-23): its /ammo "deeper case" is now
  // open, routed by the ungated MULTI_PATH_MAP['vico'] entry below. vico-gate.html
  // was deleted from public/ on 2026-10-07 (unrouted public-file audit).
}

// Hosts with more than one static destination (a reserved sub-path plus a
// default). Checked before SUBDOMAIN_MAP. Added 2026-07-13: todd-call.arcs.care
// /teardown and julia.arcs.care /runtime were previously declared only in
// next.config.ts + vercel.json rewrites. Root cause of the bug this fixes:
// platform-level rewrites are re-applied AFTER this middleware runs, and the
// host's wildcard rule was re-catching the REWRITTEN destination filename
// (e.g. "/todd-teardown.html" contains "teardown" but doesn't start with it,
// so a prefix-only exclusion let the wildcard re-match it on the second pass
// and overwrite this middleware's rewrite back to the default page) — fixed
// in next.config.ts by excluding the substring anywhere, not just as a
// prefix. This middleware entry is kept as the primary, deterministic
// mechanism; next.config.ts's fix is the belt-and-suspenders backstop.
// Agent-readable discovery paths (2026-10-29). On a catch-all host these must never answer
// with the host's HTML page (a soft 404 an agent reads as content). A host's own llms.txt is
// mapped here or in its MULTI_PATH_MAP entry (concourse); robots.txt and sitemap.xml serve the
// shared public/ files; anything else is a real 404. Gate: tests/unit/llms-routes.test.ts.
const MACHINE_PATH = /^\/(llms\.txt|index\.md|robots\.txt|sitemap\.xml)$/
const HOST_LLMS: Record<string, string> = {
  'good':   '/good-llms.txt',
  'resume': '/resume-llms.txt',
}

const MULTI_PATH_MAP: Record<string, Record<string, string>> = {
  // myally.arcs.care: one tabbed hub (Proposal, Timeline, Primer, Debrief). Every page path opens the hub,
  // which picks its tab from the path (bare host and unknown paths open Debrief; /mnda-edits lands on Proposal). The Oct 15 plan (myally.html) is retired and no longer routed.
  // The signed PDF maps to itself so the default rewrite does not swallow it. Gated end to end by the
  // myally passcode block in proxy() before this map is consulted.
  'myally':    { '/proposal': '/myally-hub.html', '/timeline': '/myally-hub.html', '/mnda-edits': '/myally-hub.html', '/primer': '/myally-hub.html', '/debrief': '/myally-hub.html', '/myally-mnda-signed.pdf': '/myally-mnda-signed.pdf', default: '/myally-hub.html' },
  // saul.arcs.care — interview bundle (2026-09-03): root = prep, /followup = forked battle cards, /resume = viewer.
  // Asset paths are mapped to themselves so the default-page rewrite does not swallow the PDFs/txt.
  'saul':      { '/followup': '/saul-followup.html', '/resume': '/saul-resume-viewer.html', '/saul-resume.pdf': '/saul-resume.pdf', '/saul-cover.pdf': '/saul-cover.pdf', '/saul-resume-ats.txt': '/saul-resume-ats.txt', default: '/saul.html' },
  // monstro.arcs.care — AI Marketing Engineer bundle (2026-09-08): root = candidate pitch (counterpart-safe, noindex), /resume + /cover = viewers, PDFs mapped to themselves so the default-page rewrite does not swallow them.
  'monstro':   { '/full': '/monstro-full.html', '/resume': '/monstro-resume.html', '/cover': '/monstro-cover.html', '/monstro-resume.pdf': '/monstro-resume.pdf', '/monstro-cover.pdf': '/monstro-cover.pdf', default: '/monstro.html' },
  // success-academy.arcs.care — AI Product Manager bundle (2026-09-24): OPEN (ungated), noindex. root = positioning brief + fit score, /resume = viewer. Asset paths mapped to themselves so the default-page rewrite does not swallow the PDF/txt.
  // claritai.arcs.care: Head of Operational Excellence & AI Systems bundle (2026-09-28): OPEN (ungated), noindex, for Jeff Kronisch (Harris Allied) to forward to Seth Merrin. root = brief + objections + history; PDF mapped to itself.
  // concourse.arcs.care: Concourse FDE bundle (2026-10-19): OPEN (ungated), noindex. root = candidate page (bet, record, role shape, gaps, kickoff card, ledger), /sara = recruiter brief, /plan = 90-day plan + pre-mortem (draft 2026-10-19), /llms.txt + /candidate.json = agent-readable claims with read-only checks. External cuts only; no counterpart profile content.
  // monday.arcs.care: RET RFP submission guide for the monday.com FDE panel (2026-10-26). Gated end to end by MONDAY_PASSCODE above; noindex. root = guide; /monday-guide-rc46.zip = the submitted ZIP (sha256 matches dist/submission-rc46.zip.sha256), mapped to itself so the default rewrite does not swallow it.
  // cia.arcs.care: candidate brief for the Culinary Institute of America architect role (2026-10-29). Gated by CIA_PASSCODE; noindex.
  'cia':       { '/resume.pdf': '/cia-brief-resume.pdf', default: '/cia-brief.html' },
  // dioptra.arcs.care: candidate brief for the Dioptra Staff PM role (2026-10-29). Gated by DIOPTRA_PASSCODE; noindex.
  'dioptra':   { default: '/dioptra-brief.html' },
  'monday':    { '/monday-guide-rc46.zip': '/monday-guide-rc46.zip', default: '/monday-guide.html' },
  'concourse': { '/sara': '/concourse-sara.html', '/plan': '/concourse-plan.html', '/llms.txt': '/concourse-llms.txt', '/candidate.json': '/concourse-candidate.json', default: '/concourse.html' },
  'claritai': { '/claritai-resume.pdf': '/claritai-resume.pdf', default: '/claritai.html' },
  'success-academy': { '/resume': '/success-academy-resume-viewer.html', '/success-academy-resume.pdf': '/success-academy-resume.pdf', '/success-academy-resume-ats.txt': '/success-academy-resume-ats.txt', default: '/success-academy.html' },
  // conduit.arcs.care — Conduit Health PM, Patient Experience bundle (2026-09-28): OPEN (ungated), noindex, for Annie Wasserman (HappyPath) to forward to co-founder Rocky Seftel. root = positioning brief, /resume = viewer. Asset paths mapped to themselves so the default-page rewrite does not swallow the PDF/txt.
  'conduit': { '/resume': '/conduit-resume-viewer.html', '/conduit-resume.pdf': '/conduit-resume.pdf', '/conduit-resume-ats.txt': '/conduit-resume-ats.txt', '/conduit-brief.pdf': '/conduit-brief.pdf', '/conduit-case-study.pdf': '/conduit-case-study.pdf', '/case-study': '/conduit-case-study.html', default: '/conduit.html' },
  // squad.arcs.care — Squad (gosquad.ai) Product Engineer bundle (2026-09-24): OPEN (ungated), noindex. root = positioning brief + fit score (the thesis mirror aimed at founder Ignacio García León), /resume = print-ready HTML resume (technical cut, leadership scope kept), + ATS txt. Asset paths mapped to themselves so the default-page rewrite does not swallow the resume/txt.
  'squad':     { '/resume': '/squad-resume.html', '/squad-resume.html': '/squad-resume.html', '/squad-resume-ats.txt': '/squad-resume-ats.txt', '/card': '/squad-battlecard.html', '/squad-battlecard.html': '/squad-battlecard.html', default: '/squad.html' },
  // fun.arcs.care — Fun.xyz Senior Product Marketing Manager bundle (2026-09-24): OPEN (ungated), noindex. root = positioning brief (Grayscale-led, crypto/regulated-finance forward, honest payments gap stated), /resume = viewer. Asset paths mapped to themselves so the default-page rewrite does not swallow the PDF/txt.
  'fun': { '/resume': '/fun-resume-viewer.html', '/fun-resume.pdf': '/fun-resume.pdf', '/fun-resume-ats.txt': '/fun-resume-ats.txt', default: '/fun.html' },
  // schriner.arcs.care — Oxenham Group recruiter bundle (2026-09-14): root = candidate pitch
  // for Joe (plain-language, non-technical recruiter register), /resume = viewer, PDF + ATS
  // text mapped to themselves so the default-page rewrite does not swallow them.
  'schriner':  { '/resume': '/schriner-resume-viewer.html', '/schriner-resume.pdf': '/schriner-resume.pdf', '/schriner-resume-ats.txt': '/schriner-resume-ats.txt', '/ammo': '/schriner-ammo.html', '/vico': '/schriner-vico.html', default: '/schriner.html' },
  // autopilot.arcs.care + vico.arcs.care — dedicated per-company subdomains
  // (2026-09-17), split out of schriner.arcs.care per the actual commitment
  // made live on the Joe follow-up call ("I can change the subdomain for you,
  // Joe, where one will just be Autopilot and the other will be Veeqo").
  // schriner.arcs.care is left live and unchanged so any link Joe already has
  // keeps working; these are additive, not a migration.
  'autopilot': { '/resume': '/autopilot-resume-viewer.html', '/autopilot-resume.pdf': '/autopilot-resume.pdf', '/autopilot-resume-ats.txt': '/autopilot-resume-ats.txt', '/ammo': '/autopilot-ammo.html', default: '/autopilot.html' },
  'vico':      { '/resume': '/vico-resume.html', '/ammo': '/vico-ammo.html', default: '/vico.html' },
  'todd-call': { '/teardown': '/todd-teardown.html', default: '/todd-call.html' },
  'julia':     { '/runtime': '/julia-runtime.html', default: '/julia.html' },
  'ahmed-ext': { '/report': '/ahmed-ext.html', '/evening': '/ahmed-evening.html', '/seed': '/ahmed-seed.html', default: '/ahmed.html' },
  // lewoof.arcs.care (2026-10-07): root = the Le Woof playbook, /invoicing = the deal-intake
  // and invoice builder that used to be the whole host. The host is gated, see the
  // lewoof block in proxy() below.
  'lewoof':    { '/invoicing': '/lewoof-intake.html', default: '/lewoof-playbook.html' },
  // prl.arcs.care/status/<seg> status-page family (2026-08-17).
  'prl':       { '/status/catchup': '/prl-status-catchup.html', '/status/crm': '/prl-status-crm.html', '/status/troubleshooting': '/prl-status-troubleshooting.html', '/status/build': '/prl-status-build.html', '/status/tidio': '/prl-status-tidio.html', '/status/progress': '/prl-status-progress.html', '/status/atlas': '/prl-status-atlas.html', '/status/receipt': '/prl-status-receipt.html', '/status/runbook': '/prl-status-runbook.html', '/checkpoint': '/prl-checkpoint.html', '/checkpoint.pdf': '/prl-checkpoint.pdf', default: '/todd-call.html' }, // root = overview (masked); status pages ride under /status/<seg>
  // good.arcs.care/blog/nftt/<slug> — Notes from the Trenches long-form posts (2026-08-18).
  // Rendered via scripts/blog_render.py from _ARTIFACTS/blog/*.md; default stays the goods gallery.
  // Three depth tiers per post, water-fountain first: bare slug = 90-second exec (default depth),
  // /brief = operational, /full = surgical. Firehose is opt-in, one click deeper.
  'good':      { '/blog/nftt/post-1': '/blog-nftt-post-1.html', '/blog/nftt/post-1/brief': '/blog-nftt-post-1.html', '/blog/nftt/post-1/full': '/blog-nftt-post-1.html', '/blog/nftt/post-2/full': '/blog-nftt-post-2.html', '/blog/nftt/post-2': '/blog-nftt-post-2.html', '/blog/nftt/post-3/full': '/blog-nftt-post-3.html', '/blog/nftt/post-3': '/blog-nftt-post-3.html', '/blog/nftt/post-4/full': '/blog-nftt-post-4.html', '/blog/nftt/post-4': '/blog-nftt-post-4.html', '/blog/nftt/take-home-trap': '/blog-nftt-take-home-trap.html', '/blog/nftt/take-home-trap/full': '/blog-nftt-take-home-trap.html', '/blog/nftt/take-home-trap/dossier': '/blog-nftt-take-home-trap-dossier.html', '/blog/nftt/any-stranger-can-be-a-bar-raiser': '/blog-nftt-any-stranger-can-be-a-bar-raiser.html', '/blog/nftt/any-stranger-can-be-a-bar-raiser/full': '/blog-nftt-any-stranger-can-be-a-bar-raiser.html', '/blog/nftt/confirmed-not-my-bug': '/blog-nftt-confirmed-not-my-bug.html', '/blog/nftt/confirmed-not-my-bug/full': '/blog-nftt-confirmed-not-my-bug.html', '/blog/nftt/the-question-that-found-the-outage': '/blog-nftt-the-question-that-found-the-outage.html', '/blog/nftt/the-question-that-found-the-outage/full': '/blog-nftt-the-question-that-found-the-outage.html','/blog/nftt/assets-and-liabilities': '/blog-nftt-assets-and-liabilities.html', '/blog/nftt/assets-and-liabilities/full': '/blog-nftt-assets-and-liabilities.html', '/blog/nftt/cheapest-edit-is-a-diff': '/blog-nftt-cheapest-edit-is-a-diff.html', '/blog/nftt/cheapest-edit-is-a-diff/full': '/blog-nftt-cheapest-edit-is-a-diff.html', '/blog/nftt/probably-confirmation-bias': '/blog-nftt-probably-confirmation-bias.html', '/blog/nftt/probably-confirmation-bias/full': '/blog-nftt-probably-confirmation-bias.html', '/blog/nftt/light-at-thirty-eight-miles-an-hour': '/blog-nftt-light-at-thirty-eight-miles-an-hour.html', '/blog/nftt/light-at-thirty-eight-miles-an-hour/full': '/blog-nftt-light-at-thirty-eight-miles-an-hour.html', '/blog/nftt/light-at-thirty-eight-miles-an-hour/research': '/blog-nftt-light-at-thirty-eight-miles-an-hour-research.html', '/blog/nftt/the-video-that-said-too-much': '/blog-nftt-the-video-that-said-too-much.html', '/blog/nftt/the-video-that-said-too-much/full': '/blog-nftt-the-video-that-said-too-much.html', '/instruments': '/good-instruments.html', '/audit': '/good-agent-receipts-audit.html', '/fears': '/good-fears.html', '/copypasta': '/good-copypasta.html', '/good-copypasta-og.png': '/good-copypasta-og.png', '/good-fears-og.png': '/good-fears-og.png', '/cases': '/good-case-six-week-outage.html', '/cases/six-week-outage': '/good-case-six-week-outage.html', '/cases/reader-who-remembered': '/good-case-reader-who-remembered.html', '/blog/nftt/the-loop-closes': '/blog-nftt-the-loop-closes.html', '/blog/nftt/the-loop-closes/full': '/blog-nftt-the-loop-closes.html', '/blog/nftt/the-loop-closes/hud': '/blog-nftt-loop-hud.html', '/blog/nftt/the-factory-on-itself': '/blog-nftt-the-factory-on-itself.html', '/blog/nftt/the-factory-on-itself/full': '/blog-nftt-the-factory-on-itself.html', '/blog/nftt/schematic-scaffolds': '/blog-nftt-schematic-scaffolds.html', '/blog/nftt/schematic-scaffolds/full': '/blog-nftt-schematic-scaffolds.html', '/blog/nftt/ledger-not-story': '/blog-nftt-ledger-not-story.html', '/blog/nftt/ledger-not-story/full': '/blog-nftt-ledger-not-story.html', '/blog/nftt/pulp-governance': '/blog-nftt-pulp-governance.html', '/blog/nftt/pulp-governance/full': '/blog-nftt-pulp-governance.html', '/blog/nftt/second-pass': '/blog-nftt-second-pass.html', '/blog/nftt/second-pass/full': '/blog-nftt-second-pass.html', '/blog/nftt/the-instinct-before-it-had-a-name': '/blog-nftt-the-instinct-before-it-had-a-name.html', '/blog/nftt/the-instinct-before-it-had-a-name/full': '/blog-nftt-the-instinct-before-it-had-a-name.html', '/blog/nftt/four-dates-one-thesis-three-confirmations': '/blog-nftt-four-dates-one-thesis-three-confirmations.html', '/blog/nftt/four-dates-one-thesis-three-confirmations/full': '/blog-nftt-four-dates-one-thesis-three-confirmations.html', '/blog/nftt/the-pre-mortem-that-asked-to-be-wrong': '/blog-nftt-the-pre-mortem-that-asked-to-be-wrong.html', '/blog/nftt/the-pre-mortem-that-asked-to-be-wrong/full': '/blog-nftt-the-pre-mortem-that-asked-to-be-wrong.html', '/blog/nftt/the-same-rigor-applied-to-slang': '/blog-nftt-the-same-rigor-applied-to-slang.html', '/blog/nftt/the-same-rigor-applied-to-slang/full': '/blog-nftt-the-same-rigor-applied-to-slang.html', '/blog/nftt/the-method-that-was-already-built': '/blog-nftt-the-method-that-was-already-built.html', '/blog/nftt/the-method-that-was-already-built/full': '/blog-nftt-the-method-that-was-already-built.html', '/blog/nftt/closing-the-loop-receipts': '/blog-nftt-closing-the-loop-receipts.html', '/blog/nftt/closing-the-loop-receipts/full': '/blog-nftt-closing-the-loop-receipts.html', '/blog/nftt/tuning-into-the-distortion-field': '/blog-nftt-tuning-into-the-distortion-field.html', '/blog/nftt/tuning-into-the-distortion-field/full': '/blog-nftt-tuning-into-the-distortion-field.html', '/blog/nftt/the-lock-that-was-already-there': '/blog-nftt-the-lock-that-was-already-there.html', '/blog/nftt/a-draft-is-not-a-verb': '/blog-nftt-a-draft-is-not-a-verb.html', '/blog/nftt/a-draft-is-not-a-verb/full': '/blog-nftt-a-draft-is-not-a-verb.html', '/blog/nftt/the-cold-reconstruction': '/blog-nftt-the-cold-reconstruction.html', '/blog/nftt/the-cold-reconstruction/full': '/blog-nftt-the-cold-reconstruction.html', '/blog/nftt/the-control-and-the-experiment': '/blog-nftt-the-control-and-the-experiment.html', '/blog/nftt/the-control-and-the-experiment/full': '/blog-nftt-the-control-and-the-experiment.html', '/blog/nftt/the-cold-reconstruction/report': '/blog-nftt-recon-report-cold-1.html', '/blog/nftt/the-control-and-the-experiment/report/cold-1': '/blog-nftt-recon-report-cold-1.html', '/blog/nftt/the-control-and-the-experiment/report/cold-2': '/blog-nftt-recon-report-cold-2.html', '/blog/nftt/the-control-and-the-experiment/report/warm-relaxed': '/blog-nftt-recon-report-warm-relaxed.html', '/blog/nftt/the-control-and-the-experiment/report/warm-matched': '/blog-nftt-recon-report-warm-matched.html', '/blog/nftt/receipts-or-it-didnt-happen': '/blog-nftt-receipts-or-it-didnt-happen.html', '/blog/nftt/receipts-or-it-didnt-happen/full': '/blog-nftt-receipts-or-it-didnt-happen.html', '/blog/nftt/the-lock-that-was-already-there/full': '/blog-nftt-the-lock-that-was-already-there.html', '/blog-nftt-tuning-into-the-distortion-field-hero.jpg': '/blog-nftt-tuning-into-the-distortion-field-hero.jpg', '/blog-nftt-the-instinct-before-it-had-a-name-hero.jpg': '/blog-nftt-the-instinct-before-it-had-a-name-hero.jpg', '/blog-nftt-the-method-that-was-already-built-hero.jpg': '/blog-nftt-the-method-that-was-already-built-hero.jpg', '/blog-nftt-closing-the-loop-receipts-hero.jpg': '/blog-nftt-closing-the-loop-receipts-hero.jpg', '/blog/nftt/notomation': '/blog-nftt-notomation.html', '/blog/nftt/notomation/full': '/blog-nftt-notomation.html', '/blog/nftt/seven-calls-seven-falsifiers': '/blog-nftt-seven-calls-seven-falsifiers.html', '/blog/nftt/seven-calls-seven-falsifiers/full': '/blog-nftt-seven-calls-seven-falsifiers.html', '/blog/nftt': '/blog-nftt-index.html', '/series/receipts': '/good-series-receipts.html', '/series/lore': '/good-series-lore.html', '/series/lore/the-gap': '/good-series-lore-the-gap.html', '/blog/til': '/blog-til-index.html', '/blog/til/one-day-99-merges': '/blog-til-one-day-99-merges.html', '/blog/til/apple-openai': '/blog-til-apple-openai.html', '/blog/til/apple-openai.pdf': '/blog-til-apple-openai.pdf', '/blog/til/zim': '/blog-til-zim.html', '/blog/til/closing-the-loop': '/blog-til-closing-the-loop.html', '/blog/til/a-draft-is-not-a-verb': '/blog-til-a-draft-is-not-a-verb.html', default: '/good.html' },
}

// App icon set shared by every host (src/app metadata files + public/icon-*.png).
// favicon.ico is already excluded by the matcher below.
const SHARED_ICON_PATH = /^\/(icon(-\d+)?\.(svg|png)|apple-icon\.png|manifest\.webmanifest|opengraph-image\.png)$/

export default async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  // --- Recruiter ammo-tier gate (host-independent) ---------------------------
  // Any /recruithaus-ammo* asset (the gated viewer + PDFs holding comp logic and
  // the founder-lens objection-handling battle cards) requires the unlock cookie
  // on EVERY host. This is deliberate: the recruithaus subdomain rewrite alone is
  // not a gate, because a public/ file is directly fetchable via app.arcs.care/<file>.
  // Checking the cookie here, before host routing, closes that bypass. The gate
  // page itself (/recruithaus-gate.html) uses a different prefix, so it stays open.
  const matchedAmmoHost = Object.values(AMMO_HOSTS).find((h) => pathname.startsWith(h.ammoFile.replace(/\.html$/, '')))
  if (pathname.startsWith('/recruithaus-ammo') || matchedAmmoHost) {
    const ok = await ammoUnlocked(
      request.cookies.get(AMMO_COOKIE)?.value,
      process.env.RECRUITHAUS_AMMO_PASSWORD,
    )
    if (!ok) {
      const url = request.nextUrl.clone()
      url.pathname = matchedAmmoHost ? matchedAmmoHost.gateFile : '/recruithaus-gate.html'
      return NextResponse.rewrite(url)
    }
    return NextResponse.next()
  }

  // Recoil identity gate is now enforced per-route via Auth.js session +
  // ADMIN_EMAILS (src/lib/admin.ts) on every /recoil surface:
  //   /recoil, /recoil/[reportId], /recoil/figma-r001 (server-wrapped),
  //   /recoil/html/[slug]. That is the real gate: per-user, revocable,
  //   fail-closed. The old shared RECOIL_PASSWORD cookie gate was a coarser
  //   second lock (and sat disclosed in git history), so it was removed here,
  //   along with the now-dead /recoil/unlock + /api/recoil/unlock endpoints.
  //   Gates are fail-closed (NODE_ENV !== "development"), matching /warroom.

  const hostname = request.headers.get('host') || ''
  const sub = hostname.split('.')[0]

  // --- lewoof.arcs.care: whole host behind the shared passcode ----------------
  // The playbook holds partner deal terms and the intake page holds a
  // counterparty's contact details, so (1) every Le Woof file (/lewoof-*,
  // /lewoof.html) is locked on EVERY host, because public/ files are directly
  // fetchable at app.arcs.care/<file>, and (2) the lewoof host itself is locked
  // end to end, not just a sub-path. Same passcode, same cookie and same
  // fail-closed helper as the ammo tiers (an unset RECRUITHAUS_AMMO_PASSWORD
  // keeps the host locked). The gate page (/lewoof-gate*) and /api (the unlock
  // route) stay open.
  if (pathname.startsWith('/lewoof-gate')) return NextResponse.next()
  const lewoofFile = pathname === '/lewoof.html' || pathname.startsWith('/lewoof-')
  const lewoofHostOpen =
    pathname.startsWith('/_next') ||
    pathname.startsWith('/_vercel') ||
    pathname.startsWith('/api') ||
    pathname === '/robots.txt' ||
    SHARED_ICON_PATH.test(pathname)
  if (lewoofFile || (sub === 'lewoof' && !lewoofHostOpen)) {
    const ok = await ammoUnlocked(
      request.cookies.get(AMMO_COOKIE)?.value,
      process.env.RECRUITHAUS_AMMO_PASSWORD,
    )
    if (!ok) {
      const url = request.nextUrl.clone()
      url.pathname = '/lewoof-gate.html'
      return NextResponse.rewrite(url)
    }
  }
  // lewoof.arcs.care/desk (2026-10-20): short link to the Le Woof Daily Desk
  // artifact, the single tracker (PR 1719's in-app desk was discarded). Sits
  // after the gate, so the link itself stays behind the passcode.
  if (sub === 'lewoof' && (pathname === '/desk' || pathname === '/desk/')) {
    return NextResponse.redirect('https://claude.ai/artifact/EN1E3113GZGsrc2UobDyvM', 302)
  }

  // --- cia.arcs.care: candidate brief for the CIA architect role -------------
  // Same shape as the monday gate, own secret (CIA_PASSCODE) and cookie.
  if (pathname.startsWith('/cia-gate')) return NextResponse.next()
  const ciaFile = pathname.startsWith('/cia-brief')
  const ciaHostOpen =
    pathname.startsWith('/_next') ||
    pathname.startsWith('/_vercel') ||
    pathname.startsWith('/api') ||
    pathname === '/robots.txt' ||
    SHARED_ICON_PATH.test(pathname)
  if (ciaFile || (sub === 'cia' && !ciaHostOpen)) {
    const ok = await gateUnlocked(
      CIA_GATE.ns,
      request.cookies.get(CIA_GATE.cookie)?.value,
      process.env[CIA_GATE.env],
    )
    if (!ok) {
      const url = request.nextUrl.clone()
      url.pathname = '/cia-gate.html'
      return NextResponse.rewrite(url)
    }
  }

  // --- dioptra.arcs.care: candidate brief for the Dioptra Staff PM role -----
  // Same shape as the cia gate, own secret (DIOPTRA_PASSCODE) and cookie.
  if (pathname.startsWith('/dioptra-gate')) return NextResponse.next()
  const dioptraFile = pathname.startsWith('/dioptra-brief')
  const dioptraHostOpen =
    pathname.startsWith('/_next') ||
    pathname.startsWith('/_vercel') ||
    pathname.startsWith('/api') ||
    pathname === '/robots.txt' ||
    SHARED_ICON_PATH.test(pathname)
  if (dioptraFile || (sub === 'dioptra' && !dioptraHostOpen)) {
    const ok = await gateUnlocked(
      DIOPTRA_GATE.ns,
      request.cookies.get(DIOPTRA_GATE.cookie)?.value,
      process.env[DIOPTRA_GATE.env],
    )
    if (!ok) {
      const url = request.nextUrl.clone()
      url.pathname = '/dioptra-gate.html'
      return NextResponse.rewrite(url)
    }
  }

  // --- monday.arcs.care: submission guide for the monday.com FDE panel -------
  // Same shape as the myally gate, own secret (MONDAY_PASSCODE) and cookie.
  // /monday-guide* is locked on every host; the gate page and /api stay open.
  if (pathname.startsWith('/monday-gate')) return NextResponse.next()
  const mondayFile = pathname.startsWith('/monday-guide')
  const mondayHostOpen =
    pathname.startsWith('/_next') ||
    pathname.startsWith('/_vercel') ||
    pathname.startsWith('/api') ||
    pathname === '/robots.txt' ||
    SHARED_ICON_PATH.test(pathname)
  if (mondayFile || (sub === 'monday' && !mondayHostOpen)) {
    const ok = await gateUnlocked(
      MONDAY_GATE.ns,
      request.cookies.get(MONDAY_GATE.cookie)?.value,
      process.env[MONDAY_GATE.env],
    )
    if (!ok) {
      const url = request.nextUrl.clone()
      url.pathname = '/monday-gate.html'
      return NextResponse.rewrite(url)
    }
    // Past the gate: log ZIP downloads (a person with the passcode, not a mail scanner). No IP.
    if (pathname === '/monday-guide-rc46.zip') {
      console.log('monday_access', JSON.stringify({ event: 'zip_download', country: request.headers.get('x-vercel-ip-country'), city: request.headers.get('x-vercel-ip-city'), ua: request.headers.get('user-agent')?.slice(0, 120) }))
    }
  }

  // --- myally.arcs.care: whole host behind its OWN passcode -----------------
  // Proposal for a counterpart team (names, scope, internal context). Same shape
  // as the lewoof gate, but a separate secret (MYALLY_PASSCODE) and cookie, so
  // this passcode opens nothing else. /myally.html and /myally-* are locked on
  // EVERY host (public/ files are fetchable at app.arcs.care/<file>); the gate
  // page and /api stay open. Unset env var = locked.
  if (pathname.startsWith('/myally-gate')) return NextResponse.next()
  const myallyFile = pathname === '/myally.html' || pathname.startsWith('/myally-')
  const myallyHostOpen =
    pathname.startsWith('/_next') ||
    pathname.startsWith('/_vercel') ||
    pathname.startsWith('/api') ||
    pathname === '/robots.txt' ||
    SHARED_ICON_PATH.test(pathname)
  if (myallyFile || (sub === 'myally' && !myallyHostOpen)) {
    const ok = await gateUnlocked(
      MYALLY_GATE.ns,
      request.cookies.get(MYALLY_GATE.cookie)?.value,
      process.env[MYALLY_GATE.env],
    )
    if (!ok) {
      const url = request.nextUrl.clone()
      url.pathname = '/myally-gate.html'
      return NextResponse.rewrite(url)
    }
  }

  // /ammo on any AMMO_HOSTS subdomain — the gated companion to that host's open
  // pitch. Reuses the recruithaus ammo-gate infra (same shared passcode, same
  // cookie) rather than inventing a second gate mechanism per host; each host's
  // own /*-ammo* asset prefix is already covered by the host-independent check
  // above.
  if (AMMO_HOSTS[sub] && (pathname === '/ammo' || pathname === '/ammo/')) {
    const ok = await ammoUnlocked(
      request.cookies.get(AMMO_COOKIE)?.value,
      process.env.RECRUITHAUS_AMMO_PASSWORD,
    )
    const url = request.nextUrl.clone()
    url.pathname = ok ? AMMO_HOSTS[sub].ammoFile : AMMO_HOSTS[sub].gateFile
    return NextResponse.rewrite(url)
  }

  if ((MULTI_PATH_MAP[sub] || SUBDOMAIN_MAP[sub]) && MACHINE_PATH.test(pathname)) {
    const own = MULTI_PATH_MAP[sub]?.[pathname] ?? (pathname === '/llms.txt' ? HOST_LLMS[sub] : undefined)
    if (own) {
      const url = request.nextUrl.clone()
      url.pathname = own
      return NextResponse.rewrite(url)
    }
    if (pathname === '/robots.txt' || pathname === '/sitemap.xml') return NextResponse.next()
    return new NextResponse('Not found', { status: 404, headers: { 'content-type': 'text/plain; charset=utf-8' } })
  }

  const multiPaths = MULTI_PATH_MAP[sub]
  if (multiPaths) {
    if (
      pathname.startsWith('/_next') ||
      pathname.startsWith('/api') ||
      // AEO discovery files must serve the real public/ static files on these
      // hosts, not the host's catch-all `default` page. Without this passthrough
      // good.arcs.care/robots.txt and /sitemap.xml were being rewritten to
      // /good.html (200, but garbage as robots/sitemap), so the sitemap the
      // NFTT robots.txt advertises was unreachable on its own host.
      pathname === '/robots.txt' ||
      pathname === '/sitemap.xml' ||
      // Shared app icons, manifest and OG card must reach these hosts too,
      // not their catch-all default page.
      SHARED_ICON_PATH.test(pathname)
    ) {
      return NextResponse.next()
    }
    const dest = multiPaths[pathname] ?? multiPaths.default
    if (pathname.startsWith(dest)) {
      return NextResponse.next()
    }
    const url = request.nextUrl.clone()
    url.pathname = dest
    return NextResponse.rewrite(url)
  }

  // --- recruithaus.arcs.care ------------------------------------------------
  // Root = the open candidate-positioning pitch (recruithaus.html). /ammo = the
  // gated tier: unlocked -> the ammo viewer; locked -> the passcode gate page.
  // Everything else on the host collapses to the pitch. Asset files under
  // /recruithaus-ammo* are already gated by the host-independent check above.
  if (sub === 'recruithaus') {
    if (
      pathname.startsWith('/_next') ||
      pathname.startsWith('/_vercel') ||
      pathname.startsWith('/api') ||
      SHARED_ICON_PATH.test(pathname)
    ) {
      return NextResponse.next()
    }
    if (pathname === '/ammo' || pathname === '/ammo/') {
      const ok = await ammoUnlocked(
        request.cookies.get(AMMO_COOKIE)?.value,
        process.env.RECRUITHAUS_AMMO_PASSWORD,
      )
      const url = request.nextUrl.clone()
      url.pathname = ok ? '/recruithaus-ammo.html' : '/recruithaus-gate.html'
      return NextResponse.rewrite(url)
    }
    if (pathname.startsWith('/recruithaus-gate.html') || pathname.startsWith('/recruithaus.html')) {
      return NextResponse.next()
    }
    const url = request.nextUrl.clone()
    url.pathname = '/recruithaus.html'
    return NextResponse.rewrite(url)
  }

  // --- jobs.arcs.care ------------------------------------------------------
  // The Alert Swipe Board, an app route (src/app/jobs) rather than a static
  // page: the host collapses to /jobs, while the API, auth, and the magic-link
  // sign-in page (/compass, where the gated page redirects) pass through so the
  // sign-in round trip does not loop back into the rewrite.
  if (sub === 'jobs') {
    if (
      pathname.startsWith('/jobs') ||
      pathname.startsWith('/compass') ||
      pathname.startsWith('/_next') ||
      pathname.startsWith('/_vercel') ||
      pathname.startsWith('/api') ||
      SHARED_ICON_PATH.test(pathname)
    ) {
      return NextResponse.next()
    }
    const url = request.nextUrl.clone()
    url.pathname = '/jobs'
    return NextResponse.rewrite(url)
  }

  const dest = SUBDOMAIN_MAP[sub]

  if (dest) {
    const { pathname } = request.nextUrl
    if (
      pathname.startsWith(dest) ||
      pathname.startsWith('/_next') ||
      pathname.startsWith('/_vercel') ||
      pathname.startsWith('/api') ||
      SHARED_ICON_PATH.test(pathname)
    ) {
      return NextResponse.next()
    }
    const url = request.nextUrl.clone()
    url.pathname = dest
    return NextResponse.rewrite(url)
  }

  return NextResponse.next()
}

export const config = {
  // fonts/ is excluded so self-hosted font files are never rewritten: on a multi-path
  // host (good.arcs.care, vico.arcs.care) the catch-all `default` page otherwise answered
  // /fonts/*.woff2 with HTML, and next.config.ts caches /fonts/* as immutable for a year,
  // so the wrong answer stuck. Found live 2026-10-03.
  matcher: ['/((?!_next/static|_next/image|favicon.ico|fonts/).*)'],
}
