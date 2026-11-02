#!/usr/bin/env python3
"""voice_gate.py: fail counterpart-facing copy that speaks in the royal "we".

WHY: Zach's solo practice writes to counterparts in the first person singular. The rule
lived only in memory (feedback-counterpart-text-first-person-singular-no-royal-we) and he
still had to correct a royal "we" in the My Ally proposal (dreaming pass 1, 2026-11-02, B1).
Memory did not fire, so this is the mechanical stop (AGENTS.md gotcha 15).

Flags every we / our / ours / us / ourselves / we're / we've / we'll / we'd / let's in
VISIBLE text (HTML script, style and comments are skipped). A truly joint "we" (Zach plus
the counterpart) is kept by marking it, never by loosening the gate:
  HTML   wrap it in an element with data-voice="joint"
  text   end the line with  <!-- joint -->  (Markdown hides it; strip it from a plain-text email)
  any    --allow REGEX (repeatable), e.g. --allow "we agree"

USAGE
  python3 scripts/voice_gate.py FILE [FILE ...]      # .html .htm .md .txt, or - for stdin
  python3 scripts/voice_gate.py --self-test
EXIT  0 clean · 1 at least one unmarked hit · 2 bad input
"""
import argparse
import html.parser
import re
import sys

WORDS = re.compile(r"\b(we|we're|we've|we'll|we'd|our|ours|ourselves|us|let's)\b", re.I)
# "US" in capitals is the country or a unit, not the pronoun
COUNTRY_US = re.compile(r"\bUS\b")
JOINT_LINE = re.compile(r"<!--\s*joint\s*-->")


class Visible(html.parser.HTMLParser):
    """Collect (line, text) for visible text, dropping script/style and joint-marked subtrees."""

    SKIP = {"script", "style", "noscript", "template"}
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
            "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []  # (tag, hidden)
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            return
        hidden = (tag in self.SKIP or dict(attrs).get("data-voice") == "joint"
                  or bool(self.stack and self.stack[-1][1]))
        self.stack.append((tag, hidden))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if not (self.stack and self.stack[-1][1]) and data.strip():
            self.chunks.append((self.getpos()[0], data))


def segments(name, text):
    if name.endswith((".html", ".htm")) or text.lstrip()[:15].lower().startswith(("<!doctype", "<html")):
        p = Visible()
        p.feed(text)
        return p.chunks
    return [(i, l) for i, l in enumerate(text.splitlines(), 1) if not JOINT_LINE.search(l)]


def scan(name, text, allow=()):
    hits = []
    for line, seg in segments(name, text):
        for m in WORDS.finditer(seg):
            if m.group(0) == "US" and COUNTRY_US.match(seg, m.start()):
                continue
            ctx = seg[max(0, m.start() - 40): m.end() + 40].replace("\n", " ").strip()
            if any(re.search(a, ctx, re.I) for a in allow):
                continue
            hits.append((line, m.group(0), ctx))
    return hits


def self_test():
    bad = "<!doctype html><p>We will build your roadmap and our team ships it.</p>"
    good = ("<!doctype html><p>I will build your roadmap.</p><script>let we = 1</script>"
            "<p data-voice=\"joint\">We agree the route together.</p><p>Based in the US.</p>")
    cases = [
        ("bad html fails", len(scan("a.html", bad)) == 2),
        ("good html passes", scan("a.html", good) == []),
        ("bad text fails", len(scan("a.md", "Here is our plan.\nLet's talk.")) == 2),
        ("joint line passes", scan("a.md", "We agree the scope. <!-- joint -->") == []),
        ("--allow passes", scan("a.txt", "we agree the scope", allow=["we agree"]) == []),
    ]
    for name, ok in cases:
        print(("ok   " if ok else "FAIL ") + name)
    return 0 if all(ok for _, ok in cases) else 1


def main():
    ap = argparse.ArgumentParser(description="Fail counterpart copy written in the royal we.")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--allow", action="append", default=[], help="regex; a hit whose context matches is kept")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.files:
        ap.error("give at least one FILE, or - for stdin")
    failed = 0
    for f in a.files:
        try:
            text = sys.stdin.read() if f == "-" else open(f, encoding="utf-8", errors="replace").read()
        except OSError as e:
            print(f"voice-gate: cannot read {f}: {e}", file=sys.stderr)
            return 2
        hits = scan(f, text, a.allow)
        print(f"{'✖' if hits else '✓'} voice-gate: {f}" + (f" ({len(hits)} royal-we hit(s))" if hits else ""))
        for line, word, ctx in hits:
            print(f"    line {line}: \"{word}\" in: {ctx}")
        failed += bool(hits)
    if failed:
        print("voice-gate: write it in \"I\"; mark a truly joint we (data-voice=\"joint\" or <!-- joint -->)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
