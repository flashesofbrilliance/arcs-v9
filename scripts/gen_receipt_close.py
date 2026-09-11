#!/usr/bin/env python3
"""
gen_receipt_close.py -- scaffold a receipt-close SSOT by scoring an ex-ante
receipt against its recoil (blueprint sec 7 companion to forge_counterpart.py).

The receipt-close is the crispest proof (blueprint sec 9): a bet filed BEFORE,
scored AFTER against reality. This scaffolder does the mechanical half so the
synthesis stage never fabricates:

  - It lifts the ex-ante bet + predictions from the ex-ante receipt block.
  - It seeds close.scorecard from the recoil's belief-update table, so every
    scored row is GROUNDED in a verbatim line the counterpart actually said
    ("the line that moved it" column), never invented.
  - It seeds close.net_new from the recoil's "threads that crossed" list.
  - It leaves the narrative-synthesis fields (waveform, reverse_listening,
    kairos_lock, posterior) as explicit TODO stubs for the synth stage. The
    forge honesty gate (forge_counterpart.honesty_and_attribution) then refuses
    to ship any row without an observed outcome + verbatim quote.

Attribution discipline (blueprint sec 0/D1): Me = Zach (the predictions),
Them = counterpart (the verbatim lines that moved the belief). Predictions are
Zach's; every 'observed' quote is the counterpart's own words.

Usage:
  python3 scripts/gen_receipt_close.py \
      --recoil runtime/recoil/generated/2026-07-23-kleban-recoil.json \
      --out    runtime/recoil/generated/2026-07-23-kleban-receipt.json \
      [--ex-ante runtime/recoil/generated/2026-07-23-kleban.json]

Then hand-enrich the TODO fields and render:
  python3 scripts/forge_counterpart.py --surface receipt --data <out> --out public/<name>-receipt.html
"""
import argparse, json, sys


def load(p):
    with open(p) as f:
        return json.load(f)


def find_blocks(page, btype):
    return [b for b in page.get("blocks", []) if b.get("type") == btype]


def scaffold(recoil, ex_ante=None):
    m = recoil["meta"]
    page = recoil["page"]

    # --- ex-ante bet + predictions -----------------------------------------
    # Prefer an explicit 'receipt' block in the recoil (the "filed before" card);
    # fall back to the ex-ante war-room SSOT if provided.
    bet = "TODO: the one-line bet, filed before the call"
    predictions = []
    receipt_blocks = find_blocks(page, "receipt")
    src = None
    if receipt_blocks:
        src = receipt_blocks[0]
    elif ex_ante:
        ea_page = ex_ante.get("page", {})
        ea_receipts = [b for b in ea_page.get("blocks", []) if b.get("type") == "receipt"]
        src = ea_receipts[0] if ea_receipts else None
    if src:
        for f in src.get("fields", []):
            lab = f["label"].lower()
            if "pre-committed" in lab or "move" in lab:
                bet = f["value"]
            # every ex-ante field becomes a candidate prediction; the synth stage
            # assigns honest confidences and prunes. Seeded at 50 (uncertain).
            predictions.append({"pct": 50, "claim": f["value"], "meta": f'ex-ante &middot; {f["label"]}'})

    # --- scorecard from the belief-update table ----------------------------
    # A 3-col table [before, line-that-moved(their words), after] is the canonical
    # recoil belief-update shape (see kleban-recoil.json). Each row -> one scored
    # scorecard row, GROUNDED in the verbatim middle column.
    scorecard = []
    for t in find_blocks(page, "table"):
        cols = [c.lower() for c in t.get("columns", [])]
        if any("before" in c or "believed" in c for c in cols) and len(t.get("columns", [])) >= 3:
            for row in t["rows"]:
                scorecard.append({
                    "verdict": "TODO",           # HIT / MISS / PARTIAL -- synth decides
                    "predicted": row[0],
                    "observed": row[1],          # the verbatim line that moved it (their words)
                    "delta": row[2] if len(row) > 2 else "",
                })

    # --- net-new from the "threads that crossed" list ----------------------
    net_new = []
    for lst in find_blocks(page, "list"):
        if "cross" in lst.get("h2", "").lower() or "thread" in lst.get("h2", "").lower():
            for it in lst["items"]:
                net_new.append({"signal": "TODO: one-line signal", "quote": "TODO: verbatim quote", "update": it.get("html", "")})

    skeleton = {
        "meta": {
            "report_id": m["report_id"].replace("-recoil", "") + "-receipt",
            "date": m["date"],
            "counterpart": m["counterpart"],
            "company": m.get("company", ""),
            "call_label": "TODO: e.g. First call / Call 3",
            "doc_title": f'{m["counterpart"]} · Receipt Close',
            "glyph": "&#20214;",
            "badges": ["Receipt Close", "Ex-Ante Scored", "Priors Updated"],
            "meta_lines": [
                f'RECEIPT: {m["report_id"].replace("-recoil","")}-RECEIPT · STATUS AT OPEN: TODO · STATUS AT CLOSE: TODO',
                f'CALL: {m["date"]} · SOURCE: {m.get("provenance",{}).get("captured","TODO")} · MODE: EX-ANTE SCORED',
                "EX-ANTE FILED: TODO",
            ],
            "resolution": {"level": "full", "caveat": "TODO"},
            "gate": m.get("gate", {}),
        },
        "lede_cover": "TODO: cover lede -- what this is, whose prediction is scored (Zach's), grounded in their words.",
        "ex_ante": {
            "lede": "TODO: the bet as it stood before the call, not hindsight.",
            "bet": bet,
            "predictions": predictions or [{"pct": 50, "claim": "TODO", "meta": "TODO"}],
            "kairos_pre": "TODO: what the bet said in advance the call would turn on.",
        },
        "waveform": {
            "label": "TODO: call, date",
            "points": [{"key": "open", "label": "open", "v": 45, "tip": "TODO"},
                       {"key": "kairos", "label": "kairos", "v": 82, "kairos": True, "tip": "TODO: the moment the read moved"},
                       {"key": "close", "label": "close", "v": 60, "tip": "TODO"}],
            "caption": "TODO: read the shape of the call.",
        },
        "reverse_listening": {
            "lede": "TODO: read from the close backward, resolution spent on the signal.",
            "beats": [{"tag": "KAIROS", "dilation": "dilated", "label": "TODO", "quote": "TODO verbatim", "read": "TODO"}],
        },
        "kairos_lock": {"label": "TODO", "quote": "TODO verbatim", "prose": "TODO: why this is write-locked."},
        "close": {
            "status": "CLOSED",
            "status_note": "TODO: one line on how the bet scored.",
            "scorecard": scorecard or [{"verdict": "TODO", "predicted": "TODO", "observed": "TODO verbatim", "delta": ""}],
            "net_new": net_new,
            "posterior": {"wedge": "TODO", "status": "TODO", "register": "TODO (their frame, their words)", "note": "TODO"},
        },
        "foot": f'ARCS &middot; FIELD OS &middot; RECEIPT CLOSE &middot; {m["counterpart"].upper()}<br><b>FILE THE BET &middot; SCORE AGAINST REALITY &middot; LET THE RECEIPT TEACH YOU THE WEDGE</b>',
        "_scaffold_note": ("Generated by gen_receipt_close.py. Fields marked TODO require synthesis. "
                           "Scorecard 'observed' + net_new quotes must stay verbatim (their words); "
                           "the forge honesty gate rejects ungrounded rows. Delete this key when done."),
    }
    return skeleton


def main():
    ap = argparse.ArgumentParser(description="Scaffold a receipt-close SSOT from a recoil (+ optional ex-ante).")
    ap.add_argument("--recoil", required=True, help="the recoil SSOT (belief-updates, filed-before receipt)")
    ap.add_argument("--ex-ante", help="optional ex-ante war-room SSOT for the bet/predictions")
    ap.add_argument("--out", help="write scaffold here (default: stdout)")
    a = ap.parse_args()
    recoil = load(a.recoil)
    ex_ante = load(a.ex_ante) if a.ex_ante else None
    sk = scaffold(recoil, ex_ante)
    text = json.dumps(sk, indent=2, ensure_ascii=False)
    if a.out:
        with open(a.out, "w") as f:
            f.write(text + "\n")
        n_todo = text.count("TODO")
        print(f"wrote {a.out} ({len(sk['close']['scorecard'])} scorecard rows seeded from recoil, "
              f"{n_todo} TODO fields to synthesize)", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()
