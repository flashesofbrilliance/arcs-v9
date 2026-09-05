# Call-stage tells: the DPRK "Contagious Interview" lure before the repo

The repo scanner (`sbom-payload-scan`) covers the payload. This file covers the stage before it:
the recruiter call that tries to get you to clone. Grounded in a real, side-by-side pair on
2026-09-02: an actual Contagious Interview lure ("Richard Stein", richardstein692@gmail.com, fake
company "Cryptis", repo "Jackpot") at 11:00, and a genuine executive recruiter call at 12:00. The
contrast is the reference set.

## The three axes, in the order the body reads them

Read a suspicious call on three axes. They fire in this order, and the first is the leading indicator.

### 1. Animacy (vox animus) — is anyone actually home?
The scam is a front-man relaying from a handler and, likely, a real-time AI translation/voice layer.
That destroys spontaneity, and the destruction is audible.
- Non-responsive loops: repeated "Hello? Hello? Can you hear me?" after you have clearly answered.
- Off-script utterances break them: a simple human aside ("was it robotic?") gets "What do you mean?"
- A second voice prompts the front man (handler chorus: "No no no," "we guide you").
- Retrieval lag on spontaneous questions ("What part of France?" → stumble → "uh, Paris").
- Uninterrupted, non-yielding flow: they plow the script; a living conversant overlaps and adapts.
- Camera kept off; possible pitch/TTS artifacts (the "robotic" quality).
> The felt absence of a living presence fires before the conscious analysis does. Trust it, then
> confirm with axes 2 and 3. The legit call had the opposite: overlapping speech, real digressions,
> real-time "let me double-check, it's escaping me" gaps. That friction is the animus.

### 2. Provenance — did they give me something checkable, or hide it?
- Scam: refuses provenance. Asked for his GitHub handle → "I'm not a contributor." Vague company
  ("Cryptis", France, 2017, 6 members), buzzword-salad product, camera off.
- Legit: offers provenance unprompted. Named the client up front, gave checkable numbers (funding,
  ARR, headcount, named open roles), real identity and platform.

### 3. Execution — are they pushing me to run/clone/open something, now, on this call?
- Scam: "you can clone the projects in your code editor" live, with urgency, refusing "send a
  follow-up email." The tell within the tell: **"for security, you don't need to run the code...
  only review it in your editor."** That is true and malicious: opening the folder triggers the
  `.vscode/tasks.json` `folderOpen` task. Do not conflate "review" with "open in an editor."
- Legit: asked you to run nothing. The entire ask was your background and sharing your links.

## The 30-second field test
1. Did they give me provenance I can check, or hide it?
2. Are they pushing me to run/clone/open something, right now, on this call?
Legit trends toward (gave provenance, asked me to run nothing). Scam trends toward (hid provenance,
wants me to execute now). And before either: did it feel like anyone was home?

## If you got further than a near-miss
If you cloned or opened the repo in an editor, or ran `npm install`, treat it as compromise and go to
the dossier's §05 IR runbook: isolate, rotate every reachable credential, hunt outbound to port 1224,
reimage. Merely being on the call and refusing to clone (the 2026-09-02 outcome) is a clean near-miss.

## Safe handling
Never clone/open an untrusted "assessment" repo on the call or on your daily-driver machine. If you
must inspect it, use `sbom-payload-scan` (read-only) first, then a disposable VM with no network, no
real credentials, and `npm config set ignore-scripts true`.
