# Brooks walkthrough video: plan (DRAFT, nothing recorded or uploaded)

**Job:** a short video, sent alongside the email, so Brooks hears Zach's voice once more and gets the page in about a minute
without reading it. **The page is the ceiling:** the video says nothing that is not on
`_ARTIFACTS/brooks-audit-onepager.html` (R2, `_PATTERNS/2026-10-30-readme-to-video-resonance-rules.md`).

**Ahmed order, carried into time:** the takeaway first, one number, three reasons, the asks, the one question back. Depth
(the 7-item checklist) stays on the page, not in the video ("nobody wants depth front").

## Production: recommend A

| | A. Live recording (recommended) | B. readme-to-video pipeline |
|---|---|---|
| Voice | Zach, live, one take | ElevenLabs clone of Zach (paid; hard stop 1 in the skill) |
| Picture | Screen recording of the kit page, scrolled one section per beat; webcam bubble optional | Cards rendered from the page with Playwright, timed to takes |
| Cost | $0 | Credits per character, plus build time |
| Time | About 20 minutes including two or three takes | Hours (nine stages, three gates) |
| Fit | Warmth is the point after one cold call; a real voice carries it | Polished, but a cloned voice to a counterpart he has met once risks reading as synthetic if he notices |

The tool: Loom (free tier) or QuickTime screen recording. **Loom shows who watched and how far**, which is a human signal the
email opens cannot give (the Mixmax opens were scanners). Unlisted YouTube is the fallback (the monday panel video precedent).

## Before recording

1. Fill **[START]** on the page and in the script. The close says the date out loud.
2. Open the page at `localhost:8791/brooks-audit-onepager.html` (or the final hosted copy), browser zoom so the title, the
   verdict and the $5,000 card fill the first screen. Close other tabs; hide bookmarks; notifications off.
3. Leave the checklist folded. Do not open it on camera.

## Storyboard and script

Pace target 2.4 to 2.8 words a second (R8 band is 1.8 to 3.4). Spoken forms, no symbols (R6). No em-dashes (R9). First
person singular (R7); "your team" for Louisville. MOQ is his own word, said as letters.

| # | On screen | Say (spoken form) | Words | About |
|---|---|---|---|---|
| 1 | Top of page: title, the summary line, the three numbers | Hi Brooks, it's Zach. On our call you mentioned looking for an outside audit of your AI build. Here's what that looks like, in about a minute. Five thousand dollars, two weeks, and about three hours of your team's time. You can stop after this and keep everything. | 48 | 18 s |
| 2 | Scroll to "What I heard on our call" | Here's what I heard. You don't want to get stuck with twenty thousand dollars of bags because you didn't see an early indicator. Volume-based indicators can miss a signal that's still rising. And when a customer simulation misses, either the data was bad or the hypothesis was wrong. So I'd check whether your tools can tell a flavor that has peaked from one that's still rising, and for one simulation that missed, which one broke. | 75 | 29 s |
| 3 | Scroll to the adobo section, then "Your questions" | I'd test it on the adobo flavor you mentioned. Your criteria scores it with me watching, and I write down what it says before the order. From your side, it's three meetings, about three hours. No customer data. You get one page: where you are on the build, what's least efficient, which hypotheses aren't holding up, and three next steps, each with a number for success and a date to check it. | 72 | 28 s |
| 4 | Scroll to the closing question; hold | One question. Has adobo gone out yet, or is the minimum order still ahead? Either way works. Tell me which, and I'll send two start dates. Thanks, Brooks. | 28 | 11 s |

Total: 223 words (counted), **about 86 seconds** at 2.6 words a second; a calmer pace runs closer to 100. To hit 60 seconds, cut beat 2's third reason and beat 3's
last sentence (about 165 words, 65 seconds). Recommendation: keep the full script. 90 seconds is still short, and the cut
lines are the two that answer "why not do it ourselves" and "what does this commit me to."

## Script checks (redone 2026-11-04 after the gauntlet)

- **R2, no new figures.** Said: five thousand, two weeks, three hours, twenty thousand, three next steps.
  All on the page. No "sixty days", no "bets".
- **R5, the limit travels.** "You can stop after this and keep everything" is said in beat 1. "No customer
  data" in beat 3.
- **R6 / R9.** No digits or symbols in the narration column; no em-dashes.
- **R7 voice.** No royal we; "our call" is joint. "You mentioned looking for an audit" (not "you asked for")
  matches his hedged line 92.
- **Not said on purpose:** the checklist, the Step 2 options, the proof link, payment terms, Justin, Jeben,
  earlier prices, ARCS terms.

## Delivery

- **In the email:** one line under the cover note, above the page: "If it's easier to watch than read, here's a ninety-second
  walkthrough: [link]." The page stays inline below it, so the email works with or without the video.
- **Thumbnail:** the first screen (title, verdict, $5,000), not a face. It reads as the page, not a pitch.
- **No captions file yet** (the skill lists `.vtt` as NEXT). Loom auto-captions; check them once for "M O Q" and the date.

## Hard stops

- Recording, upload and the link are Zach's. Nothing here records, uploads or edits the Gmail draft.
- If path B is chosen: the ElevenLabs step needs Zach's explicit yes after seeing the character count and credit cost.
