# /teardown

> Given a person's website + a bio/LinkedIn PDF, produces two gauntlet-hardened artifacts: a
> private internal pre-call brief and an external-facing gift teardown addressed directly to
> them — both deployed live to a password-gated `*.arcs.care` subdomain. This skill exists
> because the Danny Quick / Kiko session (2026-07-15/16) built this pipeline by hand across
> ~15 iterations, most of them *fixing things that should never have shipped* — a first-pass
> homepage-only scan produced two flatly wrong claims about the subject's own site. This skill
> encodes the fix: verify before you draft, not after.

**Usage:** `/teardown <website-url> <path-to-bio-pdf-or-notes>`

If either input is missing, ask for it — don't proceed on a partial brief.

## Step 0 — Relationship register (ask, don't guess)

Before writing a word of copy, determine: is this person a **friend/warm contact** or a
**cold intro** (Boardy-style, met through a connector, first real conversation)? This changes
both artifacts' tone completely — compare `danny.html`/`kiko.html` (friend register: "figured
this'd be more useful than a good-luck text," casual, no self-introduction) against
`daniel.html`/`labella.html` (cold-intro register: formal opener, "prepared for," explicit
value-prop framing). If it's not obvious from context, use `AskUserQuestion`. Getting this
wrong is the single fastest way for either artifact to misfire — a formal cold-outreach
opener sent to a friend reads as bizarre.

## Step 1 — Primary-source research (PDF/bio)

Read the provided PDF/notes file directly (`Read` tool) — this is ground truth for the
person's own track record, never paraphrase it from a web search. Extract: current role(s)
(check for *multiple concurrent roles* — a founder running two things at once is a real
signal, not noise), prior ventures with real specifics (backers, duration, outcome),
education, any first-person "why I built this" framing already in their own words if present.

**Do not supplement with WebSearch results and present them with the same confidence as the
primary source.** If WebSearch surfaces something the PDF doesn't confirm, either verify it
against a live, checkable page in Step 2, or mark it `UNCONFIRMED` and keep it out of any
table labeled "verbatim" or "evidence."

## Step 2 — Live technical + content scan (the step that was skipped and caused every real error)

**Do not scan only the homepage.** The single largest failure in the Danny Quick session was
treating a homepage-only `get_page_text` as the whole site — the founder bio, the trust/safety
copy, and the real pricing all lived on subpages the homepage never linked to, and a
homepage-only pass concluded (wrongly) that none of it existed.

1. Load the homepage with the Browser tool. Run `javascript_tool` to extract every `<a href>`
   on the page (`Array.from(document.querySelectorAll('a')).map(a=>a.getAttribute('href'))`)
   — that's your subpage crawl list, not guesswork.
2. Visit every internal link found (skip external/social links). Capture full page text for
   each with `get_page_text` or `javascript_tool` (`document.body.innerText`) if the visible
   text is longer than the default char cap — check `document.body.innerText.length` first.
3. Fetch response headers directly (`javascript_tool`: `fetch('/', {method:'GET'}).then(r=>{...})`
   collecting the `Headers` object) — check for missing `Content-Security-Policy`,
   `X-Frame-Options`/`frame-ancestors`, and any stray wildcard `Access-Control-Allow-Origin`
   on the HTML document itself. This is the "favor" section's usual source material.
4. Check `/robots.txt` and `/sitemap.xml` resolve (SSR/SEO health signal).
5. Scan for live forms (`document.forms`) to confirm/deny actual self-serve checkout —
   pricing copy without a wired signup form is a real, common finding.
6. If a `/compare` or competitor-benchmarking page exists, treat its claims as **the
   subject's own unverified marketing**, not fact — cross-check the 2-3 most checkable claims
   (usually pricing) against the named competitor's own public pricing page via `WebSearch`
   + a direct page visit, the same way this session caught the IZEA pricing mismatch on
   Kiko's `/compare` page. Report contradictions found; don't silently pass them through.

## Step 3 — Draft both artifacts

### 3a. Internal pre-call brief (private, never sent)

Single-file HTML, ARCS dark-cockpit tokens (see palette below), password-gated with a
memorable single word (surname or similar), marked `PRIVATE · ZACH INTERNAL ONLY · DO NOT
FORWARD` in a gold notice banner. Sections: track record (from Step 1, cite what's confirmed
vs. what the resume shape implies), site teardown (what's working / what to probe, from
Step 2), a stated-vs-revealed question bank (5-6 questions, each with a "LISTEN FOR" line —
see `public/danny.html` §"Stated vs. Revealed" for the template), and a proposed call agenda
with a stop-loss condition. Register per Step 0 — if it's a friend, the question bank's
"listen for" lines should not read like vetting a stranger.

### 3b. External-facing gift teardown (addressed directly to them)

Single-file HTML, same token palette, password-gated with their first name. Structure
(mirrors `public/kiko.html` / `public/daniel.html`):

```
00 · The favor       — one cheap, real fix (usually the header/security finding from Step 2.3)
01 · Evidence         — verbatim copy inventory, ONLY content directly observed in Step 2.
                        A table row claiming "verbatim" that traces to a WebSearch summary
                        instead of a page you actually read is exactly the failure this skill
                        exists to prevent.
02 · Gap analysis      — ranked findings, most important first. Frame gaps about content that
                        exists-but-isn't-linked as "buried/discoverability" issues, not
                        "doesn't exist" — verify absence, don't infer it from an incomplete
                        scan (see Step 2).
03 · [non-prescriptive label] — NOT "the site you should have." Something collaborative —
                        "GTM quick wins" or similar, offered as ideas not a directive
                        (NOTOMATION: scaffold their judgment, don't compress it).
04 · Interlock hypotheses — only if pre-call / no real conversation has happened yet: label
                        this section explicitly as hypotheses to test live, and DO NOT
                        fabricate quotes attributed to the person. If a real call transcript
                        exists, real quotes with attribution are fine (see daniel.html).
05 · Next              — concrete next steps, single-column cards (not a 2-col grid — cards
                        should span the full content width).
```

Style rules, non-negotiable (all caught the hard way this session):
- En-dashes (`–`), not em-dashes (`—`), throughout.
- No `max-width: NNch` caps on `p`, `.sub`, or `li` — let them fill the 860px column.
- No `text-wrap: balance` on headings — let them wrap naturally to full width.
- `.sechead > div` (the flex wrapper around each section's label+h2) needs `flex:1;
  min-width:0` or the h2 won't fill the row.
- A pill nav (anchor links to each numbered section) belongs right below the header's
  `.meta` line, not floating elsewhere.
- Never narrate the editing/correction process at the reader ("correction from an earlier
  pass," "the way I just checked yours") — see Funhouse gate below. They see the final draft.

## Step 4 — The gauntlet (run BEFORE calling either draft final, not after)

This is the step that was, in the actual session, run reactively across three separate user
prompts after the artifact was already deployed. Running it proactively here is the entire
point of turning this into a skill. Apply each lens explicitly and record the verdict:

- **BAR (Bayesian / Adversarial / Ruin)** — *Bayesian*: for every claim, could you point to
  the exact page/header/quote it came from? If not, it's not evidence, it's a prior. Update
  or cut. *Adversarial*: actively try to find the claim that's wrong — don't just re-read
  approvingly. *Ruin*: what's the actual cost if this specific claim is wrong and the subject
  catches it? Rate low/med/high; higher-ruin claims need harder verification before shipping.
- **LAB (Loki / Advisors / Bayesian)** — *Loki*: try to break your own artifact adversarially,
  the way a trickster would. *Advisors*: would a skeptical third party sign off, or would they
  find the same gaps you'd rather not look for?
- **KKL (Known-Known / Known-Unknown / Loki)** — write the explicit epistemic map before
  calling it done: what's confirmed (cite the source), what's an open question (say so on the
  page, don't silently omit), and what's a residual blind spot you have no way to check from
  outside (e.g., whether an apparent gap is actually deliberate). Never let a Known-Unknown
  masquerade as a Known-Known.
- **COURT (constitutional / NOTOMATION)** — does the artifact scaffold the subject's own
  judgment or compress/replace it? Section 04's hypothesis framing is the main test. Also:
  apply the *same* verification bar to any claim about **you** (Zach) in the interlock
  section that you just applied to the subject — an unverified stat about yourself sitting
  next to a fact-checked page is a fairness failure, not a neutral one.
- **Funhouse (self-flattery / distortion check)** — read every sentence and ask "does this
  inform the reader, or does it perform rigor at them?" Cut anything in the second category.
  This includes meta-narration of your own drafting/correction process (see Step 3b's style
  rules) and overclaiming your own credentials with the same confidence as fact-checked
  content about someone else.

Report the gauntlet result as a short table (lens → verdict → what was fixed) before treating
either artifact as final — either to the user in chat, or in a scratch note, but not baked
into the shipped page itself (that's Funhouse's job to prevent).

## Step 5 — Deploy

1. Work in the **main worktree**, not a feature branch (`git worktree list`, find the one on
   `main` — as of this session, `/Users/zharris/arcs-v9/.claude/worktrees/frosty-kepler-b69f51`,
   but re-verify, this drifts across sessions).
2. `public/<name>.html` (internal) and `public/<name-or-topic>.html` (external) — pick a
   short, memorable external slug if the person's first name is already taken by another
   engagement (this session moved `danny-ext.arcs.care` → `kiko.arcs.care` for exactly this
   reason).
3. Add two `beforeFiles` rewrite entries to `next.config.ts` (see existing entries for the
   exact pattern — `{ source: "/:path*", destination: "/<file>.html", has: [{ type: "host",
   value: "<subdomain>.arcs.care" }] }`).
4. Commit, push, then `bash scripts/deploy-prod.sh` — this handles main-worktree enforcement
   and (attempts) domain auto-assignment.
5. **Verify domain assignment manually** — the pre-flight script has not reliably
   auto-added new domains in practice this session. Check via the Vercel MCP/API
   (`get_deployment` or a direct `GET .../domains`) and `POST` the domain if missing:
   ```
   curl -X POST "https://api.vercel.com/v9/projects/<PROJECT_ID>/domains?teamId=<TEAM_ID>" \
     -H "Authorization: Bearer $VERCEL_TOKEN" -H "Content-Type: application/json" \
     -d '{"name": "<subdomain>.arcs.care"}'
   ```
6. Confirm both URLs return 200, and that the password gate actually unlocks with the
   intended word (test via the Browser tool, not just `curl` — the gate is client-side JS).

## Design tokens (reuse verbatim)

```
--bg:#020408  --surface:#0d1117  --surface2:#111827  --border:#1e293b
--text:#e2e8f0  --muted:#8b9bb0  --dim:#64748b
--cyan:#00F0FF  --green:#00FF9D  --gold:#FFD700  --red:#FF4D6D  --steel:#94a3b8
```
Full CSS reference implementation: `public/kiko.html`.

## What this skill is not

Not a replacement for judgment on Step 0 (relationship register) or on which gauntlet
findings are worth surfacing to the subject vs. keeping internal — those are calls the
session should make explicitly, the way this one did, not something to automate away.
