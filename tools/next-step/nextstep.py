#!/usr/bin/env python3
"""nextstep: did a call end with a named next step? Counts only; no model judgment.

Reads a Granola transcript with timestamps ("[m:ss] Microphone: ..." or
"[h:mm:ss] System audio (Name): ..."). Looks at the last WINDOW seconds.
A next step is NAMED when one line holds both a date expression and a
commitment phrase. Otherwise VERIFY if a line asks for identity proof,
else NONE. Microphone is Zach; any System audio is the other side.

Usage:
  nextstep.py TRANSCRIPT.txt [...]   one line per call: verdict, who, the cue words
  nextstep.py --self-test
Stdlib only. Prints cue words, never the transcript text.
"""
import re
import sys

WINDOW = 180  # seconds: "the last 3 minutes"

DATE = re.compile(
    r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow"
    r"|tonight|next week|this week|end of (the )?(day|week)|eod|eow|later today"
    r"|in (a|one|two|three|\d+) (days?|weeks?)"
    r"|(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{1,2}"
    r"|\d{1,2}(st|nd|rd|th))\b")
COMMIT = re.compile(
    r"\b(i'll|i will|we'll|we will|you'll|let's|let me|i'm going to"
    r"|can you|could you|schedule|send|follow up|set up|book|intro)\b")
VERIFY = re.compile(
    r"\b(company (email|address)|work email|verify|verification"
    r"|confirm (your|who))\b")
LINE = re.compile(r"^\[(\d+):(\d+)(?::(\d+))?\] (Microphone|System audio)[^:]*: (.*)")


def secs(a, b, c):
    return int(a) * 60 + int(b) if c is None else \
        int(a) * 3600 + int(b) * 60 + int(c)


def lines(text):
    for raw in text.splitlines():
        m = LINE.match(raw.strip())
        if m:
            a, b, c, src, said = m.groups()
            yield secs(a, b, c), "zach" if src == "Microphone" else "them", said.lower()


def verdict(text):
    ls = list(lines(text))
    if not ls:
        return "NO-TIMESTAMPS", "", ""
    end = max(t for t, _, _ in ls)
    tail = [l for l in ls if l[0] >= end - WINDOW]
    for t, who, said in tail:
        d, c = DATE.search(said), COMMIT.search(said)
        if d and c:
            return "NAMED", who, f"{c.group(0)} / {d.group(0)}"
    for t, who, said in tail:
        v = VERIFY.search(said)
        if v:
            return "VERIFY", who, v.group(0)
    return "NONE", "", ""


def self_test():
    def call(*body):
        return "\n\n".join(body)
    # Shapes of the four hand-labeled calls (paraphrased, not transcript text).
    cases = {
        "NONE": call("[58:00] System audio (A): we stack those into a library",
                     "[61:32] System audio (A): hope we get to catch up soon. Have a great day.",
                     "[61:44] Microphone: Thanks so much. Bye."),
        "NONE ": call("[33:33] System audio: next I talk to my founder and schedule a virtual call",
                      "[34:22] Microphone: here's what my first 30 days could look like",
                      "[36:03] System audio: Have a great one."),
        "NAMED them": call("[83:01] System audio: want to schedule a time to talk next week?",
                           "[84:30] Microphone: All right, cheers. Bye."),
        "NAMED zach": call("[35:00] Microphone: I will follow up with that on Monday",
                           "[35:20] System audio: Anytime. Thanks."),
        "VERIFY zach": call("[1:02:10] Microphone: could you send that from your company email?",
                       "[1:03:00] System audio: Sure."),
    }
    for want, text in cases.items():
        got, who, _ = verdict(text)
        assert f"{got} {who}".strip() == want.strip(), (want, got, who)
    # Outside the window does not count.
    old = call("[10:00] Microphone: I'll send it Monday", "[20:00] System audio: Bye now.")
    assert verdict(old)[0] == "NONE", "a line 10 minutes before the end is not the close"
    print("self-test ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--self-test"]:
        self_test()
    elif a:
        for p in a:
            v, who, cue = verdict(open(p).read())
            print(f"{p}\t{v}\t{who}\t{cue}")
    else:
        sys.exit(__doc__)
