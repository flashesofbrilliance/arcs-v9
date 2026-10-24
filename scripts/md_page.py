#!/usr/bin/env python3
"""md_page.py: a small, safe Markdown to HTML body converter for the proposal wiki.

Handles what the repo's proposals use: front matter, headings, paragraphs, bold, italic, strike, code spans,
fenced code, blockquotes, rules, tables, bullet and numbered lists with one nested level, task boxes, links.
All text is escaped first, so a stray <script> in a source file is shown, never run.

  python3 scripts/md_page.py --self-test
Stdlib only.
"""
import html, re, sys


def esc(s):
    return html.escape(s, quote=True)


def inline(s):
    s = esc(s)
    codes = []

    def keep(m):
        codes.append("<code>%s</code>" % m.group(1))
        return "\x00%d\x00" % (len(codes) - 1)

    s = re.sub(r"`([^`]+)`", keep, s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" rel="noopener">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"~~([^~]+)~~", r"<del>\1</del>", s)
    s = re.sub(r"(?<![\w*])\*([^*\s][^*]*?)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"(?<![\w_])_([^_\s][^_]*?)_(?![\w_])", r"<em>\1</em>", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], s)


def split_front_matter(text):
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                fm = {}
                for l in lines[1:i]:
                    if ":" in l:
                        k, _, v = l.partition(":")
                        fm[k.strip()] = re.sub(r"\s+#.*$", "", v).strip()
                return fm, "\n".join(lines[i + 1:])
    return {}, text


def _list(items):
    """items: list of (indent, ordered, text). One nested level."""
    out, stack = [], []
    for ind, ordered, txt in items:
        tag = "ol" if ordered else "ul"
        box = ""
        m = re.match(r"\[( |x|X)\]\s+(.*)", txt)
        if m:
            box = "&#9745; " if m.group(1) in "xX" else "&#9744; "
            txt = m.group(2)
        depth = 1 if ind >= 2 else 0
        while len(stack) > depth + 1:
            out.append("</li></%s>" % stack.pop())
        if len(stack) == depth + 1:
            out.append("</li>")
        if len(stack) < depth + 1:
            out.append("<%s>" % tag)
            stack.append(tag)
        out.append("<li>%s%s" % (box, inline(txt)))
    while stack:
        out.append("</li></%s>" % stack.pop())
    return "".join(out)


def md_to_html(text):
    out, lines, i = [], text.split("\n"), 0
    para = []

    def flush():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(x.strip() for x in para)))
            para.clear()

    while i < len(lines):
        l = lines[i]
        if l.strip().startswith("```"):
            flush()
            lang, buf, i = l.strip()[3:], [], i + 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            out.append('<pre tabindex="0"><code>%s</code></pre>' % esc("\n".join(buf)))
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)", l)
        if m:
            flush()
            n = max(2, min(len(m.group(1)), 4))
            out.append("<h%d>%s</h%d>" % (n, inline(m.group(2)), n))
            i += 1
            continue
        if re.match(r"^\s*(---+|\*\*\*+)\s*$", l):
            flush()
            out.append("<hr>")
            i += 1
            continue
        if l.lstrip().startswith(">"):
            flush()
            buf = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>%s</blockquote>" % md_to_html("\n".join(buf)))
            continue
        if l.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            flush()
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], rows[2:]
            out.append('<div class="tw" tabindex="0"><table><tr>%s</tr>%s</table></div>'
                       % ("".join("<th>%s</th>" % inline(c) for c in head),
                          "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in r) for r in body)))
            continue
        lm = re.match(r"^(\s*)([-*]|\d+[.)])\s+(.*)", l)
        if lm:
            flush()
            items = []
            while i < len(lines):
                lm = re.match(r"^(\s*)([-*]|\d+[.)])\s+(.*)", lines[i])
                if lm:
                    items.append((len(lm.group(1)), lm.group(2)[0].isdigit(), lm.group(3)))
                    i += 1
                elif lines[i].strip() and lines[i].startswith("   ") and items:
                    ind, o, t = items[-1]
                    items[-1] = (ind, o, t + " " + lines[i].strip())
                    i += 1
                else:
                    break
            out.append(_list(items))
            continue
        if not l.strip():
            flush()
        else:
            para.append(l)
        i += 1
    flush()
    return "\n".join(out)


def self_test():
    bad = md_to_html("hello <script>alert(1)</script> world")
    assert "<script>" not in bad and "&lt;script&gt;" in bad, "known-bad: raw script must be escaped"
    bad2 = md_to_html("[x](javascript:alert(1))")
    assert "href" not in bad2, "known-bad: javascript: links must not become links"
    good = md_to_html("# T\n\n| a | b |\n|---|---|\n| 1 | **2** |\n\n```\nx < y\n```\n\n- [ ] todo\n  - nested\n- [x] done\n\n> quote\n")
    for needle in ("<h2>T</h2>", "<table>", "<th>a</th>", "<strong>2</strong>", "<pre", "x &lt; y", "&#9744; todo", "<ul><li>", "<blockquote>"):
        assert needle in good, "known-good missing " + needle
    fm, body = split_front_matter("---\nstatus: DRAFT # note\nentry: 1\n---\n# H")
    assert fm == {"status": "DRAFT", "entry": "1"} and body.strip() == "# H"
    assert md_to_html("a\nb") == "<p>a b</p>"
    print("self-test ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        print(__doc__)
