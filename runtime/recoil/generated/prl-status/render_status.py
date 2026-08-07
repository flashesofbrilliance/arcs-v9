#!/usr/bin/env python3
"""Render the PRL daily exec-status update from board.json.

Outputs an email-client-safe HTML body, a plain-text fallback, and a content
signature used to send ONLY when something changed since the last update.

Usage:
  render_status.py --html out.html --text out.txt         # write both bodies
  render_status.py --sig                                   # print content signature
  render_status.py --changed-since last-sent.json          # exit 0 if changed, 3 if same
  render_status.py --subject                               # print the subject line

No third-party deps (stdlib only). Business-level content only; no PII.
"""
import argparse, hashlib, html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD = os.path.join(HERE, "board.json")

# email-safe: light card, colored chips (dark-theme email clients are unreliable)
STATUS = {
    "not_started":       ("Not started",        "#334155", "#ffffff"),
    "in_progress":       ("In progress",         "#0284c7", "#ffffff"),
    "troubleshooting":   ("Troubleshooting",     "#d97706", "#ffffff"),
    "pending_review":    ("Pending your review", "#ca8a04", "#ffffff"),
    "acceptance_testing":("Acceptance testing",  "#7c3aed", "#ffffff"),
    "done":              ("Done",                "#059669", "#ffffff"),
}
ORDER = ["done", "acceptance_testing", "in_progress", "troubleshooting", "pending_review", "not_started"]


def load():
    with open(BOARD) as f:
        return json.load(f)


def signature(b):
    """Stable hash of only the meaningful fields, so cosmetic edits don't trigger a send."""
    parts = []
    for ph in b["phases"]:
        for it in ph["items"]:
            parts.append("|".join([
                ph["phase"], it["name"], it["status"],
                "R" if it.get("refinement_needed") else "",
                it.get("note", ""),
            ]))
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()


def counts(b):
    c = {}
    for ph in b["phases"]:
        for it in ph["items"]:
            c[it["status"]] = c.get(it["status"], 0) + 1
    return c


def subject(b):
    c = counts(b)
    done = c.get("done", 0)
    total = sum(c.values())
    pend = c.get("pending_review", 0)
    tail = f" // {pend} need you" if pend else ""
    return f"PRL chatbot // daily status ({done}/{total} done){tail}"


def chip_html(status, refine):
    label, bg, fg = STATUS[status]
    if refine and status == "acceptance_testing":
        label += " &middot; refinement needed"
    return (f'<span style="display:inline-block;padding:3px 9px;border-radius:11px;'
            f'background:{bg};color:{fg};font-size:12px;font-weight:600;'
            f'white-space:nowrap;font-family:Arial,Helvetica,sans-serif">{label}</span>')


def render_html(b):
    c = counts(b)
    summary = " &nbsp;&middot;&nbsp; ".join(
        f'{c[s]} {STATUS[s][0].lower()}' for s in ORDER if c.get(s))
    rows = []
    for ph in b["phases"]:
        rows.append(
            f'<tr><td colspan="2" style="padding:18px 0 6px;font:600 13px Arial,Helvetica,sans-serif;'
            f'color:#0f172a;letter-spacing:.02em;text-transform:uppercase">{html.escape(ph["phase"])}</td></tr>')
        for it in ph["items"]:
            note = html.escape(it.get("note", ""))
            rows.append(
                '<tr>'
                '<td style="padding:8px 12px 8px 0;vertical-align:top;border-top:1px solid #e2e8f0;'
                'font:400 14px Arial,Helvetica,sans-serif;color:#0f172a">'
                f'<div style="font-weight:600">{html.escape(it["name"])}</div>'
                f'<div style="color:#475569;font-size:13px;margin-top:2px">{note}</div>'
                '</td>'
                '<td style="padding:8px 0;vertical-align:top;border-top:1px solid #e2e8f0;text-align:right;white-space:nowrap">'
                f'{chip_html(it["status"], it.get("refinement_needed"))}</td>'
                '</tr>')
    return f"""<div style="max-width:620px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;color:#0f172a">
  <p style="font-size:15px;line-height:1.5;margin:0 0 4px">Hi Todd &ndash;</p>
  <p style="font-size:15px;line-height:1.5;margin:0 0 16px">Quick visual status on the chatbot program. Anything marked <b>pending your review</b> is waiting on a call from you.</p>
  <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px;margin:0 0 8px;font-size:13px;color:#334155">{summary}</div>
  <table cellpadding="0" cellspacing="0" width="100%" style="border-collapse:collapse">{''.join(rows)}</table>
  <p style="font-size:13px;color:#64748b;margin:18px 0 0">Full detail and the per-stage logic live at prl.arcs.care. Reply any time and I will adjust.</p>
  <p style="font-size:14px;margin:14px 0 0">With gratitude,<br>Zach</p>
</div>"""


def render_text(b):
    c = counts(b)
    lines = ["Hi Todd -", "",
             "Quick visual status on the chatbot program. Anything marked 'pending your review' is waiting on a call from you.", ""]
    lines.append(" | ".join(f"{c[s]} {STATUS[s][0].lower()}" for s in ORDER if c.get(s)))
    for ph in b["phases"]:
        lines += ["", ph["phase"].upper()]
        for it in ph["items"]:
            label = STATUS[it["status"]][0]
            if it.get("refinement_needed") and it["status"] == "acceptance_testing":
                label += " - refinement needed"
            lines.append(f"  [{label}] {it['name']}")
            if it.get("note"):
                lines.append(f"      {it['note']}")
    lines += ["", "Full detail and the per-stage logic live at prl.arcs.care. Reply any time and I will adjust.",
              "", "With gratitude,", "Zach"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html")
    ap.add_argument("--text")
    ap.add_argument("--sig", action="store_true")
    ap.add_argument("--subject", action="store_true")
    ap.add_argument("--changed-since")
    ap.add_argument("--mark-sent", help="write {signature,sent} snapshot to this path")
    ap.add_argument("--sent-date", default="", help="date stamp to record with --mark-sent")
    a = ap.parse_args()
    b = load()

    if a.mark_sent:
        with open(a.mark_sent, "w") as f:
            json.dump({"signature": signature(b), "sent": a.sent_date}, f)
        print("marked"); return
    if a.sig:
        print(signature(b)); return
    if a.subject:
        print(subject(b)); return
    if a.changed_since:
        cur = signature(b)
        prev = None
        if os.path.exists(a.changed_since):
            with open(a.changed_since) as f:
                prev = json.load(f).get("signature")
        if cur == prev:
            print("unchanged"); sys.exit(3)
        print("changed"); return
    if a.html:
        with open(a.html, "w") as f:
            f.write(render_html(b))
    if a.text:
        with open(a.text, "w") as f:
            f.write(render_text(b))
    if not (a.html or a.text):
        print(render_html(b))


if __name__ == "__main__":
    main()
