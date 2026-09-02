---story---
{
  "slug": "take-home-trap",
  "tier": "full",
  "eyebrow": "NOTES FROM THE TRENCHES // when the take-home is the trap",
  "threads": [
    {"id":"red",   "hex":"#FF4D6D", "name":"red · the exploit", "shape":"diamond"},
    {"id":"cyan",  "hex":"#00F0FF", "name":"cyan · the echo",   "shape":"circle"},
    {"id":"green", "hex":"#00FF9D", "name":"green · the ship",  "shape":"square"}
  ],
  "arc": {"caption":"the arc of one week in the trenches", "stops":[
    {"label":"a recruiter's take-home", "thread":"red"},
    {"label":"is any of this ours?", "thread":"cyan"},
    {"label":"the opposite-sign echo", "thread":"cyan"},
    {"label":"ship the control", "thread":"green"},
    {"label":"the eval said no edge", "thread":"green"}
  ]}
}
---/story---

# NOTES FROM THE TRENCHES // when the take-home is the trap

## The recruiter's repo, and the question that made it ours

*A North Korean crew ships malware disguised as a job interview. We wrote the defensive dossier, and then asked the question that actually mattered: is any of this ours? Three threads run through what happened next. Red is the exploit, the recruiter's repo that runs the instant you open it. Cyan is the echo, the move that found something a threat report cannot hold. Green is the ship, a finding that ended as a running control instead of a paragraph.*

## The take-home is the trap

The lure is a job. A recruiter reaches out, the vibe is real, and there is a coding assignment: clone this repo, get the dev server running before our next call. That is the whole attack. This is the DPRK "Contagious Interview" campaign, MITRE tracks it as G1052, and it targets engineers because engineers open repos for a living.

— *Red: opening the folder is the exploit. A hidden VS Code task detonates on folder-open, and an npm install hook detonates on install, so the careful reviewer who avoids one still trips the other.*

>> The payload is not in the code you review. It arrives after, from a server, and runs before you have decided anything.

The mechanics are ugly and clever. A beacon ships your entire environment to a server and then runs whatever the server sends back. Your secrets are the prize, and the machine is now someone else's.

[[ARC]]

## Is any of this ours?

We built a clean dossier for it. Kill chain, ATT&CK mapping, detection rules, an incident runbook. Good work. Then we stopped and asked the uncomfortable question: is any insight in here actually ours, or is it competent restatement of what Unit 42 and Microsoft already published?

Honest answer: none of the threat facts are ours, and that is correct.

— *Cyan: on a threat dossier, a unique insight would be a liability, not a feature. Inventing a novel attribution nobody else has is exactly the confabulation we gate against.*

*In plain terms: an orthogonal echo is when two things from unrelated worlds turn out to share the same underlying shape. ARCS goes looking for them on purpose, because the shared shape is usually the transferable lesson.*

## The opposite-sign echo

So we ran the echo detector against our own decision corpus. Strip the malware off the malware and it is a five-move shape: a trusted-looking channel delivers something that runs before review, executes code fetched live, and drains your ambient secrets. Where else does that shape live?

It lives all over our own notes, at the opposite sign. Never run what a parallel process hands you without checking it in version control. Never trust a forged speaker. Gate anything that auto-triggers. Treat your durable records as sovereign and the engines that touch them as revocable tenants. Four unrelated rules, one invariant underneath.

— *Cyan: the campaign is a single principle violated five ways. Our corpus is the same principle defended, independently, in four domains that never knew about each other.*

>> Provenance before execution. The reflex that blocks a forged attestation is the same reflex that blocks eval of a C2 response. Same move, opposite sign.

That correspondence is the part that is ours. Not the malware facts, the shape they share with how we already decide.

## Ship the control

A finding that ends as a paragraph gets re-derived at full cost the next time. So this one did not stop at insight. The malware's reusable patterns became a read-only scanner: it reads an untrusted repo and flags the seven trigger patterns without ever installing, running, or phoning anything, which is the only safe way to inspect the very thing whose danger is that it runs.

It shipped as a skill, packaged with a matched pair of test repos, and registered in the seed bank as a public-good candidate. It is on a pull request, not a wish list.

— *Green: a finding that ends as a reusable control, not a paragraph. That is the intended shape of the work.*

## The eval that said no edge

Then we benchmarked it honestly, and the benchmark was unflattering. On small, blatant test repos, a capable agent catches the malware with or without the scanner. Pass-rate delta: zero. Cost: a wash.

We wrote that down exactly as it was.

— *Green: measure the right thing, and report it straight even when the number is not the one you wanted.*

Because the eval also showed where the value actually is. Without the tool, one agent quietly rebuilt a scanner from scratch to answer a CI question, which is the reuse the tool exists to prevent. The scanner's edge is not verdict accuracy on a three-file toy. It is determinism, a CI exit code that blocks a merge every time, and coverage on real repos where reading by hand does not scale.

>> The eval that says "no edge here" is the one worth keeping. It tells you, precisely, where the value is not.

One week. A recruiter's trap became a dossier, the dossier became an honest question, the question found an invariant, the invariant became a tool, and the tool told us the truth about itself. That is the trench, and that is the whole job.

The full field dossier, kill chain through detections through the ARCS layer, is at good.arcs.care/blog/nftt/take-home-trap/dossier.
