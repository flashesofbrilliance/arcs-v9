#!/usr/bin/env python3
"""
STAGED end-to-end lead walk-through (DRY-RUN — no CRM writes).
Pushes sample inquiries through the REAL recognizer (normalize.py) + the 1.1 capture-field
contract (prl-tidio-capture-flow-spec.md) + the territory map, and prints:
  (1) what the bot SAYS vs ROUTES per ADR-PRL-001 (governed answering), and
  (2) the exact SugarCRM Leads payload the Zapier Create-Record step would send.
Nothing is written anywhere. This is the most faithful sim available pre-sandbox.
"""
import sys, os, csv, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "normalization"))
import normalize as N  # recognize(), normalize_state()

# --- territory map (state -> primary rep) -------------------------------------
TERR = {}
with open(os.path.join(HERE, "..", "prl-territory-map.csv")) as f:
    for r in csv.DictReader(f):
        TERR[r["state"].strip().lower()] = (r["primary"].strip(), r.get("secondary", "").strip())

def route(state_full):
    prim, sec = TERR.get((state_full or "").strip().lower(), ("", ""))
    if prim.lower() == "distribution":
        return f"Distribution channel (state has no direct rep) -> secondary {sec or 'SM'}", sec or "Sales Manager"
    if not prim:
        return "no territory match -> Sales Manager (MVP fielding inbox)", "Sales Manager"
    return f"{prim} (primary rep for {state_full})", prim

def split_name(full):
    parts = (full or "").split()
    if len(parts) == 0: return ("", "")
    if len(parts) == 1: return (parts[0], "(none)")   # single-word fallback
    return (parts[0], " ".join(parts[1:]))

# --- the bot's governed-answer decision (ADR-PRL-001) -------------------------
def governed_reply(recog, inquiry):
    txt = inquiry.lower()
    cert = any(k in txt for k in ["ul94", "ul 94", "yellow card", "certification", "flame rating", "rti", "agency"])
    spec = any(k in txt for k in ["hdt", "heat deflection", "tensile", "modulus", "°f", "deg f", "specific gravity", "mfr"])
    comp = any(m["type"] == "competitor_equiv" for m in recog)
    fam  = any(m["type"] in ("family", "prl_grade") for m in recog)
    if cert:
        return "HARD ROUTE. Cert/UL not grounded (yellow-card data not in KB). Bot: offers the official data sheet + connects a specialist; captures the lead."
    if spec:
        return "ROUTE (governed-answer OFF until eval green). Bot: does NOT state the value; offers the official data sheet + a specialist; captures the lead."
    if comp:
        g = next(m for m in recog if m["type"] == "competitor_equiv")
        return (f"RECOGNIZE pre-capture ({g['brand']} -> PRL {g['prl_grade']}). Per Aug-5 decision the equivalence is "
                f"delivered AFTER contact capture (lead magnet + screens fishing). Bot: 'We very likely match that "
                f"- share your details and a specialist confirms the exact grade.'")
    if fam:
        f = recog[0]
        return f"ANSWER (safe capability level): recognizes {f.get('family_name', f.get('family'))}; helps generally, captures, routes for the specific grade."
    return "No recognition -> capture + route to a specialist (never guess)."

# --- sample leads (raw captured inputs) ---------------------------------------
LEADS = [
    {"scenario":"A. Molder, competitor cross-ref (short path)",
     "inquiry":"Do you have an equivalent to Lexan 141? Need a quote for an injection molding job.",
     "name":"Maria Gonzalez","company":"Precision Molding LLC","phone":"(203) 555-0142",
     "email":"m.gonzalez@precisionmolding.com","state":"Texas","market":"injection molder"},
    {"scenario":"B. OEM, application (help-me-choose)",
     "inquiry":"Designing an under-hood connector, need a high-temp glass-filled nylon that can take heat.",
     "name":"David Chen","company":"Deere & Company","phone":"309-555-0177",
     "email":"chend@johndeere.com","state":"Illinois","market":"OEM"},
    {"scenario":"C. Spec/cert question (governed -> route), Distribution state",
     "inquiry":"What is the UL94 flame rating and HDT of your PC-G30 grade?",
     "name":"Sam","company":"Bayline Devices","phone":"415-555-0199",
     "email":"sam@bayline.io","state":"California","market":"OEM"},
]

def build_payloads():
    """Return [{scenario, decision, routing, assignee, payload}] built from the REAL recognizer +
    capture-field contract + territory map. Reusable by the off-cloud delivery smoke (mock-sugar)."""
    out = []
    for L in LEADS:
        recog = N.recognize(L["inquiry"])
        fn, ln = split_name(L["name"])
        st_abbrev = N.normalize_state(L["state"])
        desc_route, assignee = route(L["state"])
        payload = {
            "first_name": fn, "last_name": ln, "account_name": L["company"],
            "phone_work": L["phone"], "email1": L["email"],
            # NOTE: live records use FULL state names (CRM audit) -> write full, keep abbrev as ref
            "location_c": L["state"], "location_c_abbrev_ref": st_abbrev,
            "lead_source": "Chatbot", "status": "New",
            "description": L["inquiry"], "market": L["market"],
            "assigned_user_hint": assignee,
            "recognizer": [ {k:v for k,v in m.items() if k in ("type","prl_grade","family_name","brand")} for m in recog ],
            "source_url": "https://prlresins.com/products/", "captured_at": "<stamped at write>",
        }
        out.append({"scenario": L["scenario"], "decision": governed_reply(recog, L["inquiry"]),
                    "routing": desc_route, "assignee": assignee, "payload": payload})
    return out


def main():
    print("="*88)
    print("STAGED LEAD WALK-THROUGH  (DRY-RUN — nothing written to Tidio, Zapier, or SugarCRM)")
    print("="*88)
    for row in build_payloads():
        payload = row["payload"]
        print(f"\n### {row['scenario']}")
        print(f"Visitor said: \"{payload['description']}\"")
        print(f"BOT DECISION: {row['decision']}")
        print(f"ROUTING:      {row['routing']}")
        print("SUGAR LEADS PAYLOAD (staged, not sent):")
        print(json.dumps(payload, indent=2))
        req = ["first_name","last_name","account_name","phone_work","location_c","lead_source"]
        missing = [k for k in req if not payload.get(k)]
        print(f"REQUIRED-FIELD GATE: {'PASS (all 6 present)' if not missing else 'FAIL missing '+str(missing)}")

    print("\n" + "="*88)
    print("Notes: (1) location_c written as FULL name to match live Unbounce->Sugar records (audit).")
    print("       (2) NY/PA split by sub-region (Rob W / Howard E) needs city/zip, not just state.")
    print("       (3) The only step NOT exercised here is the live Create-Record write — needs the sandbox.")
    print("="*88)


if __name__ == "__main__":
    main()
