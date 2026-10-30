#!/usr/bin/env python3
"""readme_video_check: diff the claims in a source README against a video's narration and card text.

Rules: _PATTERNS/2026-10-30-readme-to-video-resonance-rules.md (R1-R10). Read-only; never calls a voice or
model API. Exit 1 when any FAIL check fires, 0 otherwise (WARN and INFO never fail the run).

Usage:
  python3 scripts/readme_video_check.py --vid <dir with build.cjs, voice/SCRIPT.md, voice/NN.*, out/NN.mp4> \
      --readme <README.md> [--readme <another.md>] [--keep <keep.json>] [--json]

<keep.json> (optional) declares deliberate omissions: {"omit": {"<source atom text>": "<reason>"}}. A source
caveat that is neither carried nor declared there is a FAIL (R1, R5): dropping a caveat is a decision, never a
side effect of cutting for time.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

ONES = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                    "fourteen fifteen sixteen seventeen eighteen nineteen".split())}
TENS = {w: 10 * i for i, w in enumerate("_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()) if w != "_"}
SCALE = {"hundred": 100, "thousand": 1000, "million": 10 ** 6}
# Words that are only numbers in this register when they are not part of a phrase like "one command".
SOFT = {"one"}
ACRONYM_OK = {"I"}  # spoken as-is by any voice
CAVEAT_HEADS = ("honest gaps", "gaps, honestly", "gaps", "limitations", "not claimed")


def words_to_numbers(text):
    """Return the numbers spoken in words ("thirty five thousand dollars" -> 35000)."""
    toks = re.findall(r"[a-z]+", text.lower())
    out, cur, total, seen, i = [], 0, 0, False, 0
    def flush():
        nonlocal cur, total, seen
        if seen:
            out.append(total + cur)
        cur, total, seen = 0, 0, False
    for t in toks:
        if t in ONES or t in TENS:
            if seen and cur % 10 == 0 and t in ONES and cur >= 20:
                cur += ONES[t]
            elif seen and cur and not (t in TENS and cur % 100 == 0):
                flush(); cur = ONES.get(t, TENS.get(t)); seen = True
            else:
                cur += ONES.get(t, TENS.get(t, 0)); seen = True
        elif t in SCALE and seen:
            if SCALE[t] == 100:
                cur *= 100
            else:
                total += cur * SCALE[t]; cur = 0
        elif t == "and" and seen:
            continue
        else:
            flush()
    flush()
    return out


def digit_numbers(text):
    vals = []
    for m in re.findall(r"(?<![A-Za-z§\d.])\d[\d,]*(?:\.\d+)?", text):
        try:
            vals.append(float(m.replace(",", "")))
        except ValueError:
            pass
    return vals


def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s.replace("&nbsp;", " "))).strip()


def parse_build(path):
    src = path.read_text()
    cards = []
    for m in re.finditer(r"\{\s*k:\s*'(.*?)',\s*h:\s*'(.*?)',\s*b:\s*`(.*?)`,\s*v:\s*'(.*?)'\s*\}", src, re.S):
        k, h, b, v = m.groups()
        cards.append({"kicker": k, "head": h, "body": strip_html(b), "v": v,
                      "items": max(len(re.findall(r"<li>", b)), len(re.findall(r"<tr>", b)))})
    return cards


def parse_script(path):
    parts = re.split(r"^## (\d+)\s*$", path.read_text(), flags=re.M)
    return {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts), 2)}


def caveats(readme_text):
    """Bullets under a gaps/limitations heading, keyed by their bold lead or first clause."""
    out, on = [], False
    for line in readme_text.splitlines():
        if line.startswith("#"):
            on = line.lstrip("# ").strip().lower().startswith(CAVEAT_HEADS)
            continue
        if on and line.startswith("- "):
            lead = re.match(r"- \*\*(.+?)\*\*", line)
            out.append((lead.group(1) if lead else line[2:].split(".")[0]).strip().rstrip("."))
    # Caveats that live outside a gaps section: sentences that qualify what the evidence is.
    for m in re.finditer(r"[^.\n|]*\b(?:fictional|not a pass|stand-in)\b[^.\n|]*", readme_text, re.I):
        out.append(m.group(0).strip(" `*"))
    return out


def stems(s):
    stop = set("the a an of in is are and or to for with not no on at by it its this that be as".split())
    return {w[:5] for w in re.findall(r"[a-z]+", s.lower()) if w not in stop and len(w) > 2}


def duration(f):
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                           capture_output=True, text=True, timeout=30)
        return float(r.stdout.strip())
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vid", required=True, type=Path)
    ap.add_argument("--readme", required=True, type=Path, action="append")
    ap.add_argument("--keep", type=Path)
    ap.add_argument("--evidence", type=Path, action="append", default=[],
                    help="extra files a figure may come from (data, run logs); a figure found only here is WARN, not FAIL")
    ap.add_argument("--pad", type=float, default=0.8, help="tail pad build.cjs adds after each take, seconds")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    readme = "\n".join(p.read_text() for p in a.readme)
    omit = json.loads(a.keep.read_text()).get("omit", {}) if a.keep else {}
    cards = parse_build(a.vid / "build.cjs")
    script = parse_script(a.vid / "voice" / "SCRIPT.md")
    rows = []
    def add(level, rule, card, msg):
        rows.append({"level": level, "rule": rule, "card": card, "msg": msg})

    src_nums = set(digit_numbers(readme)) | set(words_to_numbers(readme))
    src_stems = stems(readme)
    ev = "\n".join(p.read_text(errors="ignore") for p in a.evidence)
    ev_nums = set(digit_numbers(ev))
    def unsourced(n, where, i):
        if n in ev_nums:
            add("WARN", "R2", i, f"{where} {n:g}: not in the README, only in evidence files; cite it on the card or add it to the README")
        else:
            add("FAIL", "R2", i, f"{where} {n:g}, which no source states")

    for i, c in enumerate(cards, 1):
        said = script.get(i, "")
        shown = " ".join([c["kicker"], c["head"], c["body"]])
        # R0 one source of narration: SCRIPT.md and build.cjs v must say the same words.
        norm = lambda s: re.sub(r"\b([A-Z]) (?=[A-Z]\b)", r"\1", s).replace(" ", "").lower()
        if not said:
            add("FAIL", "R0", i, "card has no narration in SCRIPT.md")
        elif norm(said) != norm(c["v"]):
            add("WARN", "R0", i, "SCRIPT.md and build.cjs `v` differ beyond acronym spacing; the take may not match the fallback")
        # R2 no new claims: every number spoken or shown must exist in the source.
        for n in set(words_to_numbers(said)) | set(digit_numbers(said)):
            if n not in src_nums:
                unsourced(n, "narration says", i)
        for n in digit_numbers(shown):
            if n not in src_nums and not (1900 < n < 2100 and str(int(n)) in readme):
                unsourced(n, "card shows", i)
        # R3 shown and said agree on every figure.
        shown_n = {n for n in digit_numbers(shown) if not 1900 < n < 2100} | ({float(c["items"])} if c["items"] else set())
        said_n = set(words_to_numbers(said)) - {1} | set(digit_numbers(said))
        for n in sorted(said_n - shown_n):
            if n >= 2:
                add("WARN", "R3", i, f"{n:g} is said but not on the card")
        for n in sorted(shown_n - said_n):
            if n >= 2 and not re.search(rf"\b{int(n)}\.\d", shown):
                add("INFO", "R3", i, f"{n:g} is on the card but not said (fine if it is a label, a section number or a code value)")
        # R6 spoken forms: no digits, symbols or unlexed acronyms in narration.
        for sym in re.findall(r"[\d$%§#&/]", said):
            add("FAIL", "R6", i, f"narration contains '{sym}'; write it as spoken")
        for ac in sorted(set(re.findall(r"\b[A-Z]{2,}s?\b", said)) - ACRONYM_OK):
            add("INFO", "R6", i, f"acronym '{ac}' in narration; confirm the voice says it as letters (lexicon)")
        # R4 one idea per card: a soft ceiling on sentences and words.
        sents = [s for s in re.split(r"(?<=[.?!])\s+", said) if s]
        wc = len(said.split())
        if wc > 60 or len(sents) > 6:
            add("WARN", "R4", i, f"{wc} words, {len(sents)} sentences; more than one idea is likely riding on this card")
        # R9 no em-dashes anywhere.
        if "\u2014" in said + shown:
            add("FAIL", "R9", i, "em-dash present")
        # R8 card time set by narration.
        take = next((f for e in ("m4a", "wav", "mp3", "aiff") for f in [a.vid / "voice" / f"{i:02d}.{e}"] if f.exists()), None)
        seg = a.vid / "out" / f"{i:02d}.mp4"
        if take is None:
            add("WARN", "R8", i, "no recorded take; build falls back to a system voice")
        else:
            td, sd = duration(take), duration(seg) if seg.exists() else None
            if td and sd is not None and abs(sd - (td + a.pad)) > 0.15:
                add("FAIL", "R8", i, f"segment {sd:.2f}s vs take {td:.2f}s + pad {a.pad}s; card time is not the narration")
            elif td and seg.exists() and seg.stat().st_mtime < take.stat().st_mtime:
                add("FAIL", "R8", i, "segment is older than its take; rebuild before shipping")
            if td:
                wps = wc / td
                if not 1.8 <= wps <= 3.4:
                    add("WARN", "R8", i, f"{wps:.2f} words/s; outside a listenable 1.8 to 3.4 range")

    # R1 + R5 every source caveat carried, or declared omitted with a reason.
    said_all = " ".join(script.values()) + " " + " ".join(c["body"] + " " + c["head"] for c in cards)
    have = stems(said_all)
    for cv in caveats(readme):
        st = stems(cv)
        hit = len(st & have) / max(1, len(st))
        if cv in omit:
            add("INFO", "R5", None, f"caveat omitted by decision: '{cv}' ({omit[cv]})")
        elif hit <= 0.5:
            add("FAIL", "R5", None, f"source caveat not carried and not declared omitted: '{cv}'")
    # R2 new vocabulary: content stems in narration that the source never uses.
    novel = sorted(stems(" ".join(script.values())) - src_stems)
    if novel:
        add("INFO", "R2", None, "narration stems absent from the source (check each is wording, not a new claim): " + ", ".join(novel))
    # R10 runtime.
    full = duration(a.vid / "out" / "walkthrough.mp4")
    if full:
        add("INFO", "R10", None, f"walkthrough runs {full:.1f}s across {len(cards)} cards")

    if a.json:
        print(json.dumps(rows, indent=2))
    else:
        for r in rows:
            where = f"card {r['card']:02d}" if r["card"] else "deck"
            print(f"{r['level']:<4} {r['rule']:<3} {where:<7} {r['msg']}")
        n = {l: sum(r["level"] == l for r in rows) for l in ("FAIL", "WARN", "INFO")}
        print(f"\n{n['FAIL']} FAIL, {n['WARN']} WARN, {n['INFO']} INFO")
    return 1 if any(r["level"] == "FAIL" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
