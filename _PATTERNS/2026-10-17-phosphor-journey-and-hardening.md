# Phosphor: customer journey, stated against revealed, and the hardening plan (2026-10-17)

Written for Zach. Evidence base, stated up front because it limits every claim below: Phosphor sends nothing anywhere, so there is no usage data, and no child or outside parent has used it in front of us. The only revealed behaviour on record is Zach's own, across this build session (what he asked for, what he said did not work, what he did on his phone), plus the check suites. Everything about kids is a hypothesis.

## 1. The journey, by user story

Two stories the product states: "a baby DJ that grows with you" (a kid plays, a parent grows into decks and synths) and "co-creating a family song, craft or ritual together." Stages, with what exists today and the open edge.

| Stage | Kid (pads, simple faders) | Parent (decks, synths, patch boards) | Edge found |
|---|---|---|---|
| Discover and open | Opens a shared link on a phone or tablet | Same link, on a laptop | Link is a private artifact; the viewer needs an account. No public page yet. |
| First sound | Tap Play on a loaded song, or a pad | Load a file, press Play | No sample song preloaded: a blank page with nothing to hear. This is the decision fatigue he named. |
| Play | Pads, Wobble, presets, Song/Sing switch | Decks, mixer, MIDI in | Parent surfaces appear only after a 1.5 s hold, good; Kid visuals were too subtle to notice. |
| Shape | Six one-tap Glitch presets, Picture strength | Mix tray with min and max per effect, tempo map | Kid cannot hear what a thing does before using it. Presets now describe themselves. |
| Keep and share | None for the child | Waypoint text, session recording, pins | Nothing a kid can hand to a grandparent. |
| Return and grow | Remembered settings | Pins, waypoints, limits | No sign of progress or a next thing to try; the "grows with you" story has no mechanism yet. |
| Safety | Eject lock, volume ceiling, flash limit | Parent hold | Kid on a phone can still exit by browser gestures; headphone loudness untested. |

## 2. How coherent are the goals against the stated preference

Stated, in his words across the session: simplify, touch first, less is more, kid pads and simple faders, a separate parent track, and fewer decisions.

Coherent: the Kid and Parent split, the hold gate, the presets, the Eject lock, the flash limit, the volume ceiling, the offline claim.

Incoherent or untested: (a) "less is more" against a backlog of about 140 open rows and a steady stream of new capability requests; (b) "touch first for the kid" against a test suite built on mouse emulation and synthetic songs; (c) "grows with you" with no progression mechanism; (d) the zero-network claim, which is true for the saved file and not for the artifact viewer, which loads the page from a host.

## 3. Stated against revealed, and the root cause of the gap

| Stated | Revealed in this session | Gap |
|---|---|---|
| Simple, less is more | Asked for many controller types, MIDI, a tray with min and max per effect, an iPad remote, a laser-mouse input | The builder wants depth and range for himself. |
| Kid first | Every defect he reported came from using it on his own phone (undraggable bump, dead picture effects) | The tested user is the builder acting as parent. |
| Fewer decisions | Same session: "decision fatigue ... lack of knowledge of what something sounds like" | He wants guided entry points (presets) and depth behind them. These two do not conflict. |
| Many glitch features | Said Sweep is the best one; the picture effects were barely visible | He values effects he can hear or see at once over feature count. |

Root cause, in order of weight:
1. Different people. The stated preferences describe an imagined child; the revealed ones come from a parent who is also the builder. One person is playing three roles.
2. Different contexts. Stated in design mode at a desk, revealed in use mode on a phone, where emulation had shown no defect.
3. No observation channel. The product is deliberately offline, so nothing reveals behaviour except Zach telling us.
4. The tests prove that what was built works, not that it is felt. Synthetic songs and measured pixel counts passed while the picture effects felt dead.
5. Accretion is the default answer to a new idea, so stated simplicity loses to each interesting addition.

## 4. How to correct it, and the blind spots to solve for

1. Make revealed behaviour observable without breaking the offline promise: an opt-in, local-only event log a grown-up can read or export (the backlog already has an event-log row). Record time to first sound, which controls are touched, preset against manual use, and where a session stops.
2. Put real people in front of it: five short sessions with a child and a parent each, screen and hands recorded locally, on the actual phone. Count what they do, not what they say.
3. Turn each stated goal into a revealed metric before building more: a child with no instructions makes a sound within 5 seconds; a parent changes a limit within 60 seconds; a kid session reaches a second preset unprompted.
4. Spend a cut for every add: each new capability has to retire or hide something, and the Kid surface is capped.
5. Test on the real device class on every change that touches touch, not only emulation.
Blind spots the review exposed: phone Safari audio start, no Web MIDI on iPhone or iPad, storage blocked in the artifact viewer, headphone loudness, screen reader and one-handed use, a child leaving the page by gesture, sharing a link that carries a private account requirement, and the page analysing only the first 24 seconds of a song.

## 5. The hardening plan

Deterministic code review (mechanical, runs on every commit): the build check that the page equals its sources, the static review of the sources (ids that do not exist, duplicate ids, labels with no control, storage outside a try, debug leftovers, dashes in text), the kit token sync, the component and token gates, the wrap lint, and the page gate on the full browser matrix.

Regression testing: 35 check suites run one at a time, each paired with a mutation that must fail it. Add a flake ledger: run the whole set three times in a row, record any check that changes result, and treat a changing check as a defect until explained (the silent-audio fault and the clock check are the known two).

Abductive hardening, anterior (before shipping a change): for each change write the three most likely ways it fails in the hands of a child, a parent and a bad network, name the cheapest observation that would show each, and run it. Posterior (after a failure): from each defect found, infer the class it belongs to and add a gate for the class, not the instance. Done so far this way: a size trim altered the inlined design tokens and the sync check failed silently (now blocked at commit); two buttons shared an id so the strip zoom buttons were dead (now a static rule plus a behaviour check); a name collision with the DJ mixer state broke the first tray build (caught by the page-error check, class now covered by the static review growing a collision rule next).

Voice-of-customer gauntlet, from the customer's seat. Scripted walkthroughs on an emulated phone and tablet, scored on the revealed metrics above: a four-year-old (taps anything, ignores text), an eight-year-old (wants to make a beat with a friend), a parent DJ (wants decks and limits), a grandparent (large targets, no jargon), a teacher (one song for a class, needs a lock), a screen reader user, a one-handed user, and a skeptical reviewer (looks for a claim the page cannot back). Each persona gets a pass or fail per metric and a list of blockers. These are scripted stand-ins, not people; they find defects in the path, and real sessions in section 4 are still the test of whether it is wanted.

## 6. What the first pass already found
- Two elements shared the ids for zoom in and zoom out, so the Zoom buttons under the strip did nothing (fixed, with a check that fails on the old page).
- A trimmed comment inside the design tokens had been failing the token sync check unnoticed (restored; the commit hook now blocks it).
- Ten suites failed once on silent audio and passed on rerun; the cause is still undiagnosed and is the first thing the flake ledger should explain.
