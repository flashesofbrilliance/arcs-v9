# ARCS

**ARCS helps you think through one hard decision.** You type the question. It gives back one next step, the reasons for it, three follow-up questions, and a label for how settled the answer is (GREEN when it holds up; YELLOW, FORK or another warning label when it does not). Each run is saved as a receipt you can come back to.

It does not make the decision for you: the answer is a next step to weigh, and the final call stays yours.

**Check one thing yourself (no API keys or database needed):**

```bash
npm install
node --experimental-strip-types --import ./tests/unit/register.mjs --test tests/unit/ygate.test.ts
```

That runs the 17 tests for the part that labels how settled an answer is (`src/lib/ygate.ts`). All 17 pass on `main`. Needs Node 22.6 or later.

**Try it:** open [app.arcs.care](https://app.arcs.care) and choose **Open the compass**. No account is needed (anonymous use is allowed by `_DECISIONS/ADR-016-arcs-v9-auth-model.md`, limited to 10 questions a minute). The home page also links an example brief. Wider access opens in stages through a waitlist on that page.

---

## What happens when you ask

1. You type a question. Optionally you add prep: the stakes, the time window, what you are protecting, and how sure you already are (`src/app/api/prep/route.ts`).
2. The app makes **one** Claude call with a prompt that walks six steps, L0 to L5 (`src/app/api/compass/route.ts`, the `PIPELINE` block):
   - L0: is this a real decision?
   - L1: the strongest objections.
   - L2: what evidence and prior odds bear on it.
   - L3: is it built on a false premise, or overconfident?
   - L4: an honest confidence score from 0 to 100.
   - L5: one next step and up to three reasons.
3. The answer comes back with exactly three follow-up questions: the deeper question underneath, the uncomfortable one, and a reframe from another field.
4. Plain code, not the model, then labels how settled the answer is (`src/lib/ygate.ts`, below).
5. The result is saved as a **receipt**, one database row per run (`prisma.receipt.create` in the compass route), and can be read back as a brief at `/brief/<id>`.

### The labels (the "Y-gate")

| Label | When the code sets it |
|---|---|
| GREEN | No warning fired and confidence is 65 or more. |
| YELLOW | A caution fired, or confidence is under 65. |
| FORK | Two or more workable paths. |
| PARADOX | Paths exist but none is clearly better. |
| DELTA | Ruin risk was found, or your confidence moved since the last run. |
| SCRATCH | Confidence is under 40, or you said you feel lost. |

The gate runs 10 numbered checks (1 to 6, 8, 9, 10 and 12 in `src/lib/ygate.ts`). The receipt page draws each label at a matching sharpness, grainy when unsettled and sharp when settled (`src/app/receipt/[receiptId]/page.tsx`).

### Words you will see

- **DEWY**: the four parts of a receipt. **D**ecision (the sharpened question), **E**ntity (who else is involved), **W**indow (the time horizon), **Y** (how settled it is). Schema: `runtime/specs/dewy-receipt-schema-v1.json`.
- **Receipt**: the saved record of one run.
- **Brief**: the readable page made from a receipt.
- **ADR**: architecture decision record, a short note on one design choice. 93 of them are in `_DECISIONS/`.

## What is proven, and what is not

| Claim | Where to check |
|---|---|
| The labeling code works as described | `tests/unit/ygate.test.ts`, 17 tests passing |
| The wider unit suite | `npm run test:unit` runs the 20 test files in `tests/unit/` |
| The app is live | [arcs.care](https://arcs.care) and [app.arcs.care](https://app.arcs.care) |
| Each run is saved | `src/app/api/compass/route.ts`, the `prisma.receipt.create` call |
| A reader with no memory rebuilt 17 of 19 parts (about 90%) of one incident from the repo history alone | `runtime/audit/cold-1.json`; one incident, not the whole repo |
| This README was itself read cold and checked claim by claim | `runtime/audit/readme-cold-1.json`, rendered to `_ARTIFACTS/audit-report/readme-cold-1.html` |

**Not built, or not what it may sound like:**

- The canon describes eight layers, L0 to L7 (`_CANON/book-ii/part-ii-rom-axioms.md`). The app runs L0 to L5.
- The **Observatory** (`/observatory`, `src/app/observatory/page.tsx`) is a demo that replays a fixed dataset about this build's own history. It does not replay your decisions.
- `operators/` is a reference library of Python modules. Its own README says it is not wired into the live compass.

## Run it locally

You need Node 22.6 or later and a Postgres database. There is no SQLite option: both development and production use Postgres (`prisma.config.ts`).

```bash
npm install                 # also runs prisma generate
# create .env.local (it is git-ignored) with:
#   DATABASE_URL=postgres://...      required (src/lib/db.ts throws without it)
#   ANTHROPIC_API_KEY=...            required for the compass to answer
#   AUTH_SECRET=...                  for sign-in sessions
#   AUTH_RESEND_KEY=...              for magic-link sign-in email (src/lib/auth.ts)
npm run db:push             # create the tables
npm run dev                 # http://localhost:3000, compass at /dashboard
npm run build               # typecheck and production build
```

### The Python CLI

`scripts/arcs_cli.py` uses only the Python standard library. It runs five steps over network-scan JSON files (analyze, assess, evaluate, synthesize, recapitulate; `run` does all five). The repo does not ship sample scan files, so bring your own; the input shape is in the script's docstring.

```bash
python3 scripts/arcs_cli.py run --inputs scan1.json scan2.json --out dewy_receipt.md
```

`scripts/score_me.py` is a demo: it applies fixed weights to a name, title, company and year, and reads no data.

## Where things live

| Path | What lives there |
|---|---|
| `src/app/` | The web app: compass (`/dashboard`), briefs, Observatory demo, API routes |
| `src/lib/ygate.ts` | The labeling code |
| `src/app/api/compass/route.ts` | The prompt and the single Claude call |
| `prisma/schema.prisma` | Database models, including User, PrepSession, Receipt, Brief and Outcome |
| `runtime/specs/` | Receipt schema and other machine-readable specs |
| `_DECISIONS/` | ADRs |
| `_CANON/` | Long-form writing on the ideas behind ARCS |
| `operators/` | Reference Python library, not wired into the live app |
| `CLAUDE.md`, `AGENTS.md`, `WORLD.md` | Written for coding agents working in this repo, not for first-time readers |

**Stack:** Next.js 16, Prisma 7 on Postgres, Auth.js v5 magic links, the Anthropic SDK (`package.json`). Components use inline styles; `src/app/globals.css` is the one stylesheet.

**License:** source-available for evaluation and reference; all rights reserved (`LICENSE`). This repository is private.
