# RET take-home: recoil across release candidates (T0 2026-10-10 10:11 to 2026-10-12 15:23)

Internal note. Not shipped.

## Record
| Phase | RCs | What happened | ZIP |
|---|---|---|---|
| The build | rc1 (10-10 21:05) | 143 commits: product, tests, deck | 5.40 MB |
| Polishing the argument | rc2-rc11 (10-10 21:27-23:00) | 10 cuts in 2 h, 1-4 commits each, mostly deck features | 5.4 to 6.2 |
| The surface grows | rc12-rc14 (10-11 am) | bench rework, deck interactions, history bundle | 6.2 to 8.6 |
| Honesty and reasoning | rc15-rc17 (10-12 am) | claims audit (4 false, 16 overstated); How we got here x3 | 8.6 to 8.8 |
| Back to the product | rc18-rc22 (10-12 pm) | 4 real product defects found and fixed | 8.8 to 9.4 |

Since rc1: 66 commits; by scope deck 18, bench 11, reasoning 9, release 4.

Product defects that mattered most, and what found them:
- K55 new amendment needed a code change: brief line-by-line trace
- K56 question 101+ never answered (no cursor): brief trace
- K57 Claude key not read from .env: first live rehearsal question
- K58 poller could die mid-demo: independent code review

## Lessons
1. Simulation measured what we built; rehearsal and the brief trace measured what they will ask. 3,072 scenarios caught none of K55-K58.
2. The claims audit was the highest-value meta-work; most other meta-work added surface that then needed its own gates.
3. Cut cadence is a signal: 10 RCs in 2 h is reflex, not decision. The size cap forced batching, and batching produced better RCs.

## Landing
Centre of gravity (brief): "a modest build that proves you listened". Video: not a perfect answer; structure ambiguity,
trade-offs, use the data, communicate reasoning, own perspective.
Pulls toward it: amendment rules (Doug), figure check (Nina), what-leaves-RET (Sam), boards (Elena), ranked outcomes,
mistakes log, claims audit.
Pulls away if led with: grading machinery, scenario counts, seven tiles, depth control. Have them; do not present them.

## Shavasana
- Let go: more pages, gates, video cuts, RCs. rc23 is the last unless rehearsal breaks something.
- Keep: three-part run of show, two timed rehearsals, three unseen live questions.
- The one thing: lead with Doug's November 13 to December 4 story, Elena's three tests, and the live question.
