"""Build invented fund test files in several formats. Stdlib + reportlab only. All text is fictional."""
import os, sys, zipfile
from xml.sax.saxutils import escape as x
OUT = sys.argv[1]
HEAD = ["EXAMPLE GROWTH FUND II, L.P.", "LIMITED PARTNERSHIP AGREEMENT (EXCERPT)",
        "Issued: January 15, 2026 | Fictional sample document written for this test"]
SEC = "SECTION 8 - FEES AND EXPENSES (pp. 41-44)"
CL = [("8.1", "Management Fee.", "During the Commitment Period the Partnership shall pay the Manager an annual Management Fee equal to 2.0% of aggregate Capital Commitments."),
      ("8.2", "Fee Offset.", "80% of Transaction Fees received by the Manager shall offset the Management Fee."),
      ("8.3", "Organizational Expenses.", "The Partnership shall bear Organizational Expenses up to $1,500,000; any excess is borne by the Manager.")]
def w(p, s):
    open(os.path.join(OUT, p), "w").write(s)

# 1 txt control, 2 same text with .md extension, 3 idiomatic markdown
plain = "\n".join(HEAD + ["=" * 64, SEC, "=" * 64] + ["%s %s %s" % c for c in CL]) + "\n"
w("01_lpa.txt", plain)
w("02_lpa_plain.md", plain)
w("03_lpa_idiomatic.md", "# Example Growth Fund II, L.P.\n\n*Limited Partnership Agreement (excerpt). Fictional.*\n\n## Section 8 - Fees and Expenses (pp. 41-44)\n\n"
  + "\n\n".join("**%s %s** %s" % c for c in CL) + "\n\n~~2.0%~~ 1.75% *(proposed in Amendment No. 1)*\n")

# 4 legal features in plain text: Article heading, defined term, cross reference, sub-clauses, footnote marker
w("04_lpa_legal_features.txt", "\n".join(HEAD + [
  "ARTICLE I - DEFINITIONS",
  "Section 1.1 \"Management Fee Rate\" means 1.75% per annum.",
  "ARTICLE VIII - FEES AND EXPENSES",
  "Section 8.1 Management Fee. The Partnership shall pay the Manager an annual Management Fee equal to the Management Fee Rate multiplied by aggregate Capital Commitments.[1]",
  "Section 8.3 Organizational Expenses.",
  "(a) The Partnership shall bear Organizational Expenses up to $1,500,000.",
  "(b) Any excess shall be borne by the Manager, except that",
  "(i) placement fees are borne by the Manager in full; and",
  "(ii) the cap in Section 8.3(a) increases to $2,000,000 if the Partnership holds a Final Closing after December 31, 2026.",
  "[1] Subject to the fee offset in Section 8.2."]) + "\n")

# docx helpers
CT = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
      '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
      '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
      '<Override PartName="/word/comments.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>'
      '<Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/></Types>')
RELS = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
DRELS = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
         '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
         '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments" Target="comments.xml"/>'
         '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/></Relationships>')
NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
NUM = ('<?xml version="1.0" encoding="UTF-8"?><w:numbering %s><w:abstractNum w:abstractNumId="0">'
       '<w:lvl w:ilvl="0"><w:start w:val="8"/><w:numFmt w:val="decimal"/><w:lvlText w:val="SECTION %%1 -"/></w:lvl>'
       '<w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%%1.%%2"/></w:lvl>'
       '</w:abstractNum><w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>') % NS
COM = ('<?xml version="1.0" encoding="UTF-8"?><w:comments %s><w:comment w:id="0" w:author="Fund Counsel" w:date="2026-06-20T10:00:00Z">'
       '<w:p><w:r><w:t>Investor A side letter caps this at 1.50%%; confirm before signing.</w:t></w:r></w:p></w:comment></w:comments>') % NS
FN = ('<?xml version="1.0" encoding="UTF-8"?><w:footnotes %s><w:footnote w:id="1"><w:p><w:r><w:t>Reduced to 1.25%% after the fifth anniversary.</w:t></w:r></w:p></w:footnote></w:footnotes>') % NS
def run(t, extra=""):
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (("<w:rPr>%s</w:rPr>" % extra) if extra else "", x(t))
def para(runs, num=None):
    ppr = '<w:pPr><w:numPr><w:ilvl w:val="%d"/><w:numId w:val="1"/></w:numPr></w:pPr>' % num if num is not None else ""
    return "<w:p>%s%s</w:p>" % (ppr, "".join(runs))
def docx(name, body):
    doc = '<?xml version="1.0" encoding="UTF-8"?><w:document %s><w:body>%s</w:body></w:document>' % (NS, body)
    with zipfile.ZipFile(os.path.join(OUT, name), "w", zipfile.ZIP_DEFLATED) as z:
        for p, s in [("[Content_Types].xml", CT), ("_rels/.rels", RELS), ("word/_rels/document.xml.rels", DRELS),
                     ("word/document.xml", doc), ("word/numbering.xml", NUM), ("word/comments.xml", COM), ("word/footnotes.xml", FN)]:
            z.writestr(p, s)
head_p = "".join(para([run(h)]) for h in HEAD)

# 5 docx, typed numbers (clean)
docx("05_lpa_typed.docx", head_p + para([run(SEC)]) + "".join(para([run("%s %s %s" % c)]) for c in CL))
# 6 docx, Word automatic numbering: no typed "8.1" in the text
docx("06_lpa_autonumber.docx", head_p + para([run("FEES AND EXPENSES (pp. 41-44)")], 0) + "".join(para([run("%s %s" % c[1:])], 1) for c in CL))
# 7 docx with tracked changes, a comment, a footnote, and a manual (untracked) strike/underline redline
DEL = '<w:del w:id="1" w:author="Fund Counsel" w:date="2026-06-20T10:00:00Z"><w:r><w:delText>2.0%</w:delText></w:r></w:del>'
INS = '<w:ins w:id="2" w:author="Fund Counsel" w:date="2026-06-20T10:00:00Z"><w:r><w:t>1.75%</w:t></w:r></w:ins>'
p81 = para([run("8.1 Management Fee. During the Commitment Period the Partnership shall pay the Manager an annual Management Fee equal to "),
            '<w:commentRangeStart w:id="0"/>', DEL, INS, '<w:commentRangeEnd w:id="0"/><w:r><w:commentReference w:id="0"/></w:r>',
            run(" of aggregate Capital Commitments."), '<w:r><w:rPr><w:vertAlign w:val="superscript"/></w:rPr><w:footnoteReference w:id="1"/></w:r>'])
p82 = para([run("8.2 Fee Offset. 80% of Transaction Fees received by the Manager shall offset the Management Fee.")])
p83 = para([run("8.3 Organizational Expenses. The Partnership shall bear Organizational Expenses up to "),
            run("$1,500,000", '<w:strike/><w:color w:val="FF0000"/>'), run(" "), run("$2,000,000", '<w:u w:val="single"/><w:color w:val="0000FF"/>'),
            run("; any excess is borne by the Manager.")])
docx("07_lpa_tracked_changes.docx", head_p + para([run(SEC)]) + p81 + p82 + p83)

# 8 text PDF with running header/footer and a page break inside 8.2; 9 compare-style redline PDF; 10 image-only scan
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
def page_furniture(c, n):
    c.setFont("Helvetica", 8); c.drawString(72, 750, "CONFIDENTIAL - EXAMPLE GROWTH FUND II LPA"); c.drawString(500, 40, "Page %d" % n)
def lines(c, y, text, width=90):
    import textwrap
    for l in textwrap.wrap(text, width):
        c.drawString(72, y, l); y -= 14
    return y
c = canvas.Canvas(os.path.join(OUT, "08_lpa_text.pdf"), pagesize=letter)
page_furniture(c, 41); c.setFont("Helvetica", 10); y = 720
for h in HEAD + ["=" * 64, SEC, "=" * 64]:
    c.drawString(72, y, h); y -= 14
y = lines(c, y, "%s %s %s" % CL[0])
c.drawString(72, y, "8.2 Fee Offset. 80% of Transaction Fees received by the"); c.showPage()
page_furniture(c, 42); c.setFont("Helvetica", 10); y = 720
c.drawString(72, y, "Manager shall offset the Management Fee."); y -= 14
lines(c, y, "%s %s %s" % CL[2]); c.save()

c = canvas.Canvas(os.path.join(OUT, "09_lpa_compare_redline.pdf"), pagesize=letter)
c.setFont("Helvetica", 10); y = 720
for h in HEAD + ["=" * 64, SEC, "=" * 64]:
    c.drawString(72, y, h); y -= 14
pre = "8.1 Management Fee. The Partnership shall pay an annual Management Fee equal to "
c.drawString(72, y, pre); xx = 72 + c.stringWidth(pre, "Helvetica", 10)
c.setFillColorRGB(1, 0, 0); c.drawString(xx, y, "2.0%"); wd = c.stringWidth("2.0%", "Helvetica", 10)
c.setStrokeColorRGB(1, 0, 0); c.line(xx, y + 3, xx + wd, y + 3)
c.setFillColorRGB(0, 0, 1); c.drawString(xx + wd + 3, y, "1.75%"); w2 = c.stringWidth("1.75%", "Helvetica", 10)
c.setStrokeColorRGB(0, 0, 1); c.line(xx + wd + 3, y - 2, xx + wd + 3 + w2, y - 2)
c.setFillColorRGB(0, 0, 0); c.drawString(xx + wd + w2 + 6, y, "of aggregate Capital Commitments."); y -= 14
c.drawString(72, y, "%s %s %s" % CL[1]); c.save()
print("built", sorted(os.listdir(OUT)))
