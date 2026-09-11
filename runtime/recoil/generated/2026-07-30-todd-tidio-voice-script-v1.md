# PRL Resins Chatbot — Voice-Tuned Conversation Script v1

The bot's actual words, tuned to two voices so it sounds like PRL, not a generic widget.

## Voice profile (what we're matching)

**Todd's email voice:** warm, short, plain, human, a little enthusiasm. Opens casually ("Hey,"),
gets to the point, no corporate stiffness, no jargon. Sample tells: "You got it!", "This is
perfect. Thank you!", "I answered these because I know the answers."

**The website voice (prlresins.com):** "Compounding Success," "personal attention to the needs of
each customer," "Straight to the Source," "no phone trees involved," "Would you rather speak with
a human? Call (800) 243-5176," short lead times / speed to market, "Custom Formulating,"
"American Made." Reliability and real relationships over corporate scale.

**Resonance rule:** every bot line should sound like it could sit on the current site or come
from Todd. Short. Human. Fast. Offers a real person quickly. No "I am a virtual assistant" filler.

## Human-first principle (answers the phone question)

The site's own CTA is "no phone trees, straight to the source." So the bot never traps anyone in
a form. Every path can reach a human immediately:
- Greeting always includes a **"Just have someone call me"** option.
- Contact capture always offers **"Prefer to talk now? Call (800) 243-5176."**
- A callback request is tagged `callback-requested` and treated as high priority.

## The script

### Greeting (proactive after ~5s, or on open)
> "Hi, thanks for stopping by. Looking for a resin, a spec match, or an alternative to what
> you're running now? Tell me what you need and I'll get you to the right person fast."

Buttons:
- **I know the resin or spec I need**
- **Help me find the right one**
- **Just have someone call me**  ← fast human path
- **Something else**

### Branch A — knows what they need
1. "Great. Which resin or spec are you after?" → `desired_resin_or_spec`
2. "Are you replacing something you run now?" [Yes / No]
   - Yes: "What are you using today?" → `current_resin`  ·  "Who's your current supplier?
     (optional)" → `current_supplier`
3. "What are you making with it?" → `application`
4. "Any must-hit specs? Temperature, flame rating, color, a regulatory listing. (optional)"
   → `requirements`
5. → Contact capture. Tag `ready-to-spec`.

### Branch B — help me find one
1. "No problem, that's what we're here for. What are you making?" → `application`
2. "What matters most for it? For example heat, impact, UV for outdoor, chemical resistance,
   color, or cost. (optional)" → `requirements`
3. "Running a resin now that you'd want to match or improve on?" [Yes → `current_resin` / No]
4. (Optional smart nudge from the material matrix, for example) "Sounds like outdoor and UV
   matter. ASA and PC/ASA are strong there. I'll flag that for our specialist to confirm."
5. → Contact capture. Tag `needs-help`.

### Branch C — something else
1. "Happy to help. What can I point you to?" → `question`
2. If it matches an FAQ: answer in a line, then "Want me to connect you with someone?"
3. → optional Contact capture. Tag `general`.

### "Just have someone call me" (fast path)
1. "You got it. What's the best name and number, and when's good?" → `name`, `phone`,
   plus a free-text best-time → `requirements`
2. "Done. Someone from our team will call you shortly, usually within a few hours." Tag
   `callback-requested` (high priority).

### Contact capture (shared by A and B)
> "Last thing and you're set. Who should we get this to?"
1. "Name" → `name`
2. "Best email" → `email`
3. "Phone (optional)" → `phone`
4. "Company" → `company`
5. "What state or region are you in?" → `territory`

Always visible here: **"Prefer to talk now? Call (800) 243-5176."**

### Close
> "Thanks, [name]. One of our resin specialists will reach out shortly, usually within a few
> hours. Talking to a real person, no phone trees."

The closing line deliberately echoes the site's "no phone trees / straight to the source."

## SEM landing-page variant (Unbounce, e.g. /sabic-alternatives)
Page-scoped greeting, drops straight into Branch A:
> "Looking to move off a SABIC grade? Tell me which one, Lexan, Ultem, Noryl, Valox, and I'll
> match it to a PRL equivalent and get you to a specialist fast."

## Micro-copy notes
- Prefer "you're running now" / "what are you making" over "utilize" or "requirements gathering."
- One question per message. Never stack.
- Warmth markers used sparingly: "Great," "No problem," "You got it," "you're set."
- Speed promise everywhere: "within a few hours" (matches Todd's ~4-hour target and site speed).

_Version: v1 · 2026-07-30 · voice sources: Todd Hotes emails (Jul 2026) + prlresins.com current
copy. Pairs with branch-logic map v1.3 and the Tidio build sheet v1.1._
