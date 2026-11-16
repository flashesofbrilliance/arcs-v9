#!/usr/bin/env python3
"""floorlight: a floor-time traffic light for live calls (v0, no LLM, no network).

Zach holds the floor from the moment he starts speaking until the other side
says something real. A backchannel ("mm-hmm", "yeah", "okay") does not take
the floor back. The light shows how long he has held it:
green under YELLOW seconds, yellow under RED seconds, red after.

Two ways to tell "something real" from a backchannel:
  transcript mode: the other side's block has more than 3 words
  voice mode:      the other side spoke for at least RESET_SECS in one go
                   (about how long 4 words take; used by the live capture)

Usage:
  floorlight.py replay CALL.txt [CALL.txt ...]   turn lengths from past calls
  floorlight.py --self-test

CALL.txt lines are "m:ss SRC": M = Zach's mic, S = them (>3 words),
s = them (<=3 words, a backchannel), END = where the excerpt stops.
Stdlib only. Stores nothing.
"""
import statistics
import sys

YELLOW = 40.0
RED = 60.0
RESET_WORDS = 4
RESET_SECS = 1.2


class FloorClock:
    def __init__(self, yellow=YELLOW, red=RED):
        self.yellow, self.red = yellow, red
        self.mine_since = None  # when Zach took the floor; None = not his

    def me(self, t):
        if self.mine_since is None:
            self.mine_since = t

    def them(self, t, words=None, secs=None):
        real = (words is not None and words >= RESET_WORDS) or \
               (secs is not None and secs >= RESET_SECS)
        if real:
            held, self.mine_since = self.held(t), None
            return held  # how long Zach's turn ran, or None
        return None

    def held(self, now):
        return None if self.mine_since is None else now - self.mine_since

    def color(self, now):
        h = self.held(now)
        if h is None:
            return "off"  # their floor: nothing to watch
        return "green" if h < self.yellow else \
               "yellow" if h < self.red else "red"


def parse(path):
    for line in open(path):
        line = line.split("#")[0].strip()
        if line:
            ts, src = line.split()
            m, s = ts.split(":")
            yield int(m) * 60 + int(s), src


def turns(path):
    """Zach's floor holds: list of (seconds, finished?)."""
    clock, out, last = FloorClock(), [], 0
    for t, src in sorted(parse(path), key=lambda e: e[0]):
        last = t
        if src == "M":
            clock.me(t)
        elif src in ("S", "s"):
            h = clock.them(t, words=RESET_WORDS if src == "S" else 1)
            if h is not None:
                out.append((h, True))
    h = clock.held(last)
    if h is not None:
        out.append((h, False))  # still talking when the excerpt ends
    return out


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p * (len(xs) - 1))))]


def replay(paths):
    every = []
    for p in paths:
        ts = turns(p)
        every += ts
        secs = [h for h, _ in ts]
        print(f"{p}: {len(ts)} turns, longest {max(secs):.0f}s, "
              f">=40s {sum(h >= 40 for h in secs)}, "
              f">=60s {sum(h >= 60 for h in secs)}")
    secs = [h for h, _ in every]
    cut = sum(not done for _, done in every)
    print(f"\nall: n={len(secs)} turns ({cut} cut off by the excerpt end, "
          f"so their true length is longer)")
    print(f"median {statistics.median(secs):.0f}s  p75 {pct(secs, .75):.0f}s"
          f"  p90 {pct(secs, .90):.0f}s  max {max(secs):.0f}s")
    print(f"share >=40s {sum(h >= 40 for h in secs) / len(secs):.0%}  "
          f"share >=60s {sum(h >= 60 for h in secs) / len(secs):.0%}")


def self_test():
    c = FloorClock()
    assert c.color(0) == "off"
    c.me(0)
    assert c.color(39.9) == "green" and c.color(40) == "yellow"
    assert c.color(59.9) == "yellow" and c.color(60) == "red"
    assert c.them(50, words=1) is None, "backchannel must not reset"
    assert c.them(50, secs=0.5) is None, "short sound must not reset"
    assert c.color(61) == "red"
    assert c.them(62, words=4) == 62, "a real reply ends the turn"
    assert c.color(63) == "off"
    c.me(70)
    assert c.them(75, secs=1.2) == 5 and c.color(76) == "off"
    print("self-test ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--self-test"]:
        self_test()
    elif a[:1] == ["replay"] and a[1:]:
        replay(a[1:])
    else:
        sys.exit(__doc__)
