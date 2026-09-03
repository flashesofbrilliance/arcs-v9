# LinkedIn companion: "With Life, and Without It"

Draft-first. Post the teaser to the feed; paste the article into LinkedIn's article
editor. Both carry the hardened framing: the legitimate recruiter is fully anonymized,
the hostile caller is dissolved into its threat vector, specific indicators are withheld
on a public feed, and the animacy tell is framed as a prompt to verify, never a verdict.

---

## 1. Teaser post (feed)

Two recruiters called me an hour apart on the same rainy Wednesday. One of them had no one home.

The first was a job that was really a trap. A DPRK crew running the "Contagious Interview" scam, where the "coding assignment" they want you to clone is the malware. I had written about the mechanics before. What I had not felt before was the tell that comes first, before any analysis.

The caller had the shape of a person and none of the presence. He looped "can you hear me" after I had answered. He could not take an unscripted question. A second voice prompted him from off mic. His camera stayed off the whole time. It was a conversation with the life removed.

An hour later a real recruiter called. She interrupted and got interrupted, digressed, admitted she needed to check something, named her client up front, and asked me to run nothing. The contrast was total.

I wrote the whole thing up: the three tells, why the felt one matters (and why it is a prompt to verify, never a verdict on a stranger), and the one line worth keeping.

Protect your watch, your wallet, and your keys. Your time, your money, your access. That is all this kind of caller is ever reaching for.

I left the first call ten minutes early. I stayed on the second ten minutes late.

Full piece in the comments.

#infosec #DPRK #socialengineering #ContagiousInterview

> Link to drop in the first comment: https://good.arcs.care/blog/nftt/take-home-trap

---

## 2. Article (paste into LinkedIn's article editor)

**With Life, and Without It**

*A field account of the morning a threat vector called, and the honest recruiter who called an hour later.*

**Two calls**

They came an hour apart, through the same thin pane of a video window. Two recruiters, two roles, two voices. By the end of the day I understood I had been handed something rare: a matched pair, a control and its opposite, the same experiment run twice with one variable changed. The variable was whether anyone was home.

**The first caller had no one behind it**

The first call opened in static. Not the ordinary fumbling of a bad connection, but something stranger, a loop that would not resolve. Can you hear me. Hello. Hello. I answered, clearly, three times, and still the question came back unchanged. Turn off your camera, he said, it is better. His own was already dark.

I have been on more calls than I can count. The body keeps a register the mind is slow to consult, and mine was already filling with a low, specific unease. When I offered a small human aside, half a joke, the sentence broke against him. He could not take an unscripted turn. When I asked an idle question, there was a beat, a stall, a retrieval, and then a recited answer. He did not converse so much as advance, plowing his lines regardless of mine, and every so often a second voice surfaced to prompt him. No, no, no. We guide you.

I want to be precise about what I felt, because it is the whole of it. It was not that he was foreign, or nervous, or reading from a script. Many honest people are all three. It was that there was no one there. The words had the shape of a person and none of the pressure of one. The life had been subtracted, and I could hear the hollow where it had been.

**What it wanted**

What it wanted was simple, and it was patient about it. Clone the project, it said. Open it in your editor. It had a repository ready and a custom development tool it wanted me inside of, and it kept returning to the ask the way water returns to the low point of a floor. I said I would run a security review first. No, it said, for security you do not need to run the code. Only review it in your editor. Do not run or install anything.

That sentence is the tell inside the tell. It is true, in the narrow way that traps are true. On an editor set to trust the folder, merely opening it can be enough, because the trap is not in the running, it is in the opening. Keep your editor set to distrust unknown folders and the trigger does not fire, which is exactly the protection the caller was talking me out of. I glanced at the repository's page, not cloning it, and saw a single squashed commit. No history, no life of its own there either. I declined, and I left the call.

**What it actually was**

Stripped of the borrowed name and the invented company, this is a known thing:

- A DPRK-nexus, financially motivated operation, the campaign widely tracked as "Contagious Interview."
- Reported under many overlapping cluster names: Famous Chollima, DeceptiveDevelopment, and others. Its lineage to Lazarus is an analytic judgment, not settled consensus.
- A trojanized "assessment" repository that triggers on folder-open and on install, harvests your environment, and pulls a second stage.

One honest note on evidence. The behavioral tells above are what I saw and heard on the call. The deeper infrastructure is known campaign reporting, not something I observed from this contact. I keep those two apart on purpose.

**The second caller was alive**

An hour later a second recruiter called about a different role, and within ten seconds the contrast was total. We interrupted each other and neither of us minded. I was the one who digressed, and caught myself, and apologized, and digressed again, and she made room for all of it. She admitted, out loud and without embarrassment, that a detail was escaping her, and went to look it up while I waited. She named her client before I could ask, and she offered numbers I could check, and at no point, not once, did she ask me to run anything at all.

Her name, her firm, her client, the number she quoted: all of it real, and all of it withheld here. She is a living person doing honest work, and the reward for being real should not be to be catalogued.

**With life, and without it**

There are three axes you can read a stranger's call on, and they fire in order.

- **Animacy.** Is anyone home. The old phrase for it is vox animus, the animating voice, the sign of a living presence behind the words. This is the one you feel first. But it is a prompt to verify, never a verdict on a stranger. Plenty of honest people are nervous, on a bad line, private with a camera, or speaking a second language. The felt absence is a reason to slow down, not a conviction.
- **Provenance.** Did they give me something checkable, or hide it. The living one offered hers freely. The vector hid its own and would not even claim its own code.
- **Execution.** Are they pushing me to run, clone, or open something, now, on this call. The living one asked me to run nothing. The vector wanted the trap opened while assuring me I was safe.

The feeling only pointed. Provenance and execution are what turned it into a finding.

**Protect your watch, your wallet, and your keys**

Here is the version you can keep in a sentence. Protect your watch, your wallet, and your keys. Your watch is your time and your attention. Your wallet is your money. Your keys are your access, the credentials that quietly open everything else. That is the whole of what the caller was reaching for, all three at once, dressed as an opportunity.

And the last tell was in the clock. I left the first call ten minutes early, because some part of me could not get out of the room fast enough. I stayed on the second ten minutes late, because I did not want to go. The hollow ones you cannot leave soon enough. The living ones you lose track of the time.

*The full illustrated version, with the operational detail and a defensive dossier, is at good.arcs.care/blog/nftt/take-home-trap.*
