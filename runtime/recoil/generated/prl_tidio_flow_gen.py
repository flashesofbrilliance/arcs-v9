#!/usr/bin/env python3
"""
Generate an importable Tidio Flow JSON for the PRL Resins Phase-1 lead-capture chatbot.

Tidio's flow format uses a dual-id system that this generator wires automatically:
  - payload.id      : small sequential canvas id (1,2,3...)  -> used in connections + decision routes
  - id / dbNodeId   : big unique node id                      -> used in button.destination, getUserInput.passedNode, edges
  - edges[]         : big-id from->to pairs, each with a routeId (uuid)

Model: define nodes in a graph (each node names its next node[s] by key); a build pass assigns
ids and emits connections + edges + passedNode + button destinations consistently.

Node kinds:
  trigger  -> onFirstVisit
  message  -> sendChatMessagesToVisitor         (next=key)
  input    -> getUserInput (saves to a variable) (next=key, optional validation)
  decision -> decisionCardMessages (short title + buttons) (buttons=[(label, next_key)...])

Learned limits: decision card TITLE and button labels are short-only; long copy goes in message nodes.
"""
import json, uuid, argparse


class FlowBuilder:
    def __init__(self, name, category="generate_leads"):
        self.name = name
        self.category = category
        self.specs = []          # ordered list of node specs (dicts)
        self.by_key = {}
        self._edge_id = 300000000

    # ---- graph definition API ----
    def trigger(self, key, nxt, ttype="onFirstVisit", extra=None):
        self._add(key, "trigger", next=nxt, ttype=ttype, extra=extra or {})

    def message(self, key, text, nxt=None):
        self._add(key, "message", text=text, next=nxt)

    def ask(self, key, message, variable, nxt, validation="none", error=None, save_property=False):
        # save_property=True binds to a contact property (must exist; use only for built-ins
        # name/email/phone/company). False => answer kept as a session variable only, so no
        # custom property needs to pre-exist (clears Tidio's "Can't be empty" binding error).
        self._add(key, "input", message=message, variable=variable, next=nxt,
                  validation=validation, error=error, save_property=save_property)

    def decision(self, key, title, buttons):
        # buttons: list of (label, next_key)
        self._add(key, "decision", title=title, buttons=buttons)

    def _add(self, key, kind, **kw):
        spec = {"key": key, "kind": kind}
        spec.update(kw)
        self.specs.append(spec)
        self.by_key[key] = spec

    # ---- build ----
    def build(self, first_trigger="onFirstVisit"):
        # assign ids by declaration order
        small = {}
        big = {}
        for i, s in enumerate(self.specs):
            small[s["key"]] = i + 1
            big[s["key"]] = 200000001 + i

        nodes = []
        edges = []
        # layout helpers
        depth = {}
        # simple layout: y grows with index, x staggers by column hint
        def pos(i):
            return (10000 + (i % 4) * 340, 700 + i * 150)

        # pre-create node dicts with empty connections
        node_by_key = {}
        for i, s in enumerate(self.specs):
            x, y = pos(i)
            payload = {"id": small[s["key"]], "x": x, "y": y, "customName": "",
                       "connections": {"top": [], "left": [], "right": [], "bottom": []}}
            node = {"id": big[s["key"]], "dbNodeId": big[s["key"]],
                    "type": None, "payload": payload}
            node_by_key[s["key"]] = node
            nodes.append(node)

        def add_edge(frm_key, to_key):
            self._edge_id += 1
            edges.append({"from_node_id": big[frm_key], "to_node_id": big[to_key],
                          "id": self._edge_id, "dbEdgeId": self._edge_id,
                          "routeId": str(uuid.uuid4())})

        def add_top(to_key, frm_key):
            node_by_key[to_key]["payload"]["connections"]["top"].append(
                {"nodeId": small[frm_key], "direction": "to"})

        for s in self.specs:
            node = node_by_key[s["key"]]
            p = node["payload"]
            k = s["kind"]

            if k == "trigger":
                node["type"] = s.get("ttype", "onFirstVisit")
                for kk, vv in (s.get("extra") or {}).items():
                    p[kk] = vv
                nxt = s["next"]
                p["connections"]["bottom"].append({"nodeId": small[nxt], "direction": "from"})
                add_top(nxt, s["key"]); add_edge(s["key"], nxt)

            elif k == "message":
                node["type"] = "sendChatMessagesToVisitor"
                p["messages"] = [{"type": "text", "content": s["text"]}]
                if s.get("next"):
                    nxt = s["next"]
                    p["connections"]["bottom"].append({"nodeId": small[nxt], "direction": "from"})
                    add_top(nxt, s["key"]); add_edge(s["key"], nxt)

            elif k == "input":
                node["type"] = "getUserInput"
                nxt = s["next"]
                p.update({
                    "message": s["message"],
                    "failedNode": None,
                    "passedNode": big[nxt],
                    "validation": s.get("validation", "none"),
                    "error_message": s.get("error") or "Sorry, that doesn't look right. Mind trying again?",
                    "variable_name": s["variable"],
                    "number_of_repeats": 1,
                    "answer_to_variable": bool(s.get("save_property", False)),
                })
                p["connections"]["bottom"].append({"route": "success", "nodeId": small[nxt], "direction": "from"})
                add_top(nxt, s["key"]); add_edge(s["key"], nxt)

            elif k == "decision":
                node["type"] = "decisionCardMessages"
                buttons = []
                for i, (label, tkey) in enumerate(s["buttons"]):
                    buttons.append({"id": i + 1, "type": "action", "title": label,
                                    "destination": big[tkey]})
                    p[f"1_{i+1}Node"] = small[tkey]
                    p["connections"]["bottom"].append(
                        {"route": f"1_{i+1}", "nodeId": small[tkey], "direction": "from"})
                    add_top(tkey, s["key"]); add_edge(s["key"], tkey)
                p["cards"] = [{
                    "id": 1, "url": "", "imageUrl": "", "subtitle": "",
                    "title": s["title"], "buttons": buttons,
                    "showTitleIndicator": True, "dataSyncedWithStore": False,
                }]
                p["transferToOperatorMessageActive"] = False

        return {
            "name": self.name, "category": self.category,
            "firstTrigger": first_trigger, "template": "", "sandbox": 0,
            "color": "", "draftFromTemplate": 0, "type": "conversationAutomation",
            "nodes": nodes, "edges": edges, "sessionVariables": [],
        }


def build_full():
    fb = FlowBuilder("PRL Resins - Lead Capture")

    fb.trigger("t", "hello")
    fb.message("hello",
        "Hi, thanks for stopping by. Looking for a resin, a spec match, or an alternative to "
        "what you're running now? I'll get you to the right person fast.", nxt="menu")
    fb.decision("menu", "What brings you in?", [
        ("I know what I need", "a1"),
        ("Help me choose", "b1"),
        ("Have someone call me", "cb1"),
        ("Guides and resources", "res1"),
        ("Something else", "c1"),
    ])

    # Resources path (C-in-menu): clickable links to real prlresins.com resources
    fb.message("res1",
        "Here are some quick resources:\n"
        "- Product Selection Guide: https://prlresins.com/polymer-product-catalog/\n"
        "- Browse our resins: https://prlresins.com/products/\n"
        "- Quality guarantee: https://prlresins.com/quality-guarantee/\n"
        "- Find us / contact: https://prlresins.com/contact/", nxt="res2")
    fb.message("res2",
        "Prefer to talk to a person? Call 1-800-243-5176, or head back and pick "
        "'Have someone call me' and we'll reach out fast.")

    # Branch A - knows what they need
    fb.ask("a1", "Great. Which resin or spec are you after?", "desired_resin_or_spec", "a2")
    fb.decision("a2", "Are you replacing a resin you run now?", [
        ("Yes", "a2y"), ("No", "a3")])
    fb.ask("a2y", "What are you using today?", "current_resin", "a3")
    fb.ask("a3", "What are you making with it?", "application", "a4")
    fb.ask("a4", "Any must-hit specs? Temperature, flame rating, color, or a regulatory listing.",
           "requirements", "cap_name")

    # Branch B - help me choose
    fb.ask("b1", "No problem, that's what we're here for. What are you making?", "application", "b2")
    fb.ask("b2", "What matters most? For example heat, impact, UV for outdoor, chemical resistance, "
           "color, or cost.", "requirements", "b3")
    fb.decision("b3", "Running a resin now you'd want to match or improve on?", [
        ("Yes", "b3y"), ("No", "cap_name")])
    fb.ask("b3y", "What are you running now?", "current_resin", "cap_name")

    # Branch C - something else
    fb.ask("c1", "Happy to help. What can I point you to?", "question", "c_ask")
    fb.decision("c_ask", "Want someone to follow up?", [
        ("Yes, please", "cap_name"), ("No thanks", "c_end")])
    fb.message("c_end", "No problem. You can reach us anytime at (800) 243-5176.")

    # Callback path - fast human  (all session variables -> carried in webhook, no property binding)
    fb.ask("cb1", "You got it. What's your name?", "name", "cb2")
    fb.ask("cb2", "Best number to reach you?", "phone", "cb3", validation="phone")
    fb.ask("cb3", "When's a good time to reach you? (optional)", "requirements", "cb_end")
    fb.message("cb_end", "Done. Someone from our team will call you shortly, usually within a "
               "few hours. No phone trees.")

    # Shared contact capture (A, B, and C-yes converge here)
    # All capture fields are session variables (carried in webhook). Contact-property binding
    # is avoided because Tidio's system properties (name) enforce validation rules and non-system
    # names (company) don't exist -> both cause activation errors. Add Update-contact-property
    # nodes later if we want name/email/phone on the Tidio record itself.
    fb.ask("cap_name", "Last thing and you're set. Who should we get this to?", "name", "cap_email")
    fb.ask("cap_email", "Best email?", "email", "cap_phone", validation="email",
           error="Hmm, that doesn't look like an email. Mind trying again?")
    fb.ask("cap_phone", "Phone? (optional)", "phone", "cap_company", validation="phone")
    fb.ask("cap_company", "And your company?", "company", "cap_terr")
    fb.ask("cap_terr", "What state or region are you in?", "territory", "cap_close")
    fb.message("cap_close", "Thanks! One of our resin specialists will reach out shortly, usually "
               "within a few hours. A real person, no phone trees.")

    return fb.build()


# The five SEM onramps scoped in the build spec. Each is triggered by its own URL slug,
# so they never collide with each other or with the onFirstVisit main flow.
SEM_ONRAMPS = {
    "sabic": dict(
        slug="sabic-alternatives",
        label="SABIC alternatives",
        hello="Looking to move off a SABIC grade? Tell me which one you're running (Lexan, "
              "Ultem, Noryl, Valox) and I'll get you to a specialist who can match it.",
        ask="Which SABIC grade are you replacing?"),
    "lexan": dict(
        slug="lexan",
        label="Lexan / Makrolon polycarbonate",
        hello="Need a Lexan-class polycarbonate? We compound PC to match. Tell me the grade "
              "or the spec you have to hit.",
        ask="Which polycarbonate grade are you running today?"),
    "ultem": dict(
        slug="ultem",
        label="Ultem PEI",
        hello="Looking for an Ultem-class PEI? Tell me the grade or the spec and I'll get you "
              "to someone who can match it.",
        ask="Which PEI grade or spec are you working to?"),
    "noryl": dict(
        slug="noryl",
        label="Noryl modified PPE",
        hello="Need a Noryl-class PPE? Tell me the grade or what the part has to do.",
        ask="Which Noryl grade are you replacing?"),
    "valox": dict(
        slug="valox",
        label="Valox PBT",
        hello="Replacing a Valox PBT? Tell me the grade or the requirement driving it.",
        ask="Which Valox grade are you running today?"),
}


def build_sem_onramp(key="sabic"):
    """URL-triggered onramp for a paid-search landing page (Unbounce).

    Fires when the visitor is on a URL containing this onramp's slug, opens with a
    competitor-specific greeting, and captures a high-intent replacement lead. All fields are
    session variables, so they ride the webhook exactly like the main flow.

    NOTE: the Unbounce landing pages sit on the LIVE prlresins.com domain. Adding the Tidio
    snippet there is a production change and needs Todd's go-ahead. The flow itself is safe to
    import and leave inactive until then.

    NOTE: these ask for the grade and conditions but deliberately never offer a match. Per the
    Aug 3 audit the cross-reference tables are page images, so nothing can look up an
    equivalent yet. The onramp's job is to capture intent and route, not to answer.
    """
    cfg = SEM_ONRAMPS[key]
    fb = FlowBuilder(f"PRL Resins - SEM Onramp ({cfg['label']})")

    fb.trigger("t", "hello", ttype="onUrlOpened",
               extra={"url": cfg["slug"], "match": "partial", "frequency": "once24"})
    fb.message("hello", cfg["hello"], nxt="s1")
    fb.ask("s1", cfg["ask"], "current_resin", "s2")
    fb.ask("s2", "What are you making with it?", "application", "s3")
    fb.ask("s3", "What does the part have to stand up to? Temperature range, outdoor exposure, "
           "chemicals, or a listing you need to hold.", "requirements", "cap_name")
    fb.ask("cap_name", "Great. Who should we put this together for?", "name", "cap_email")
    fb.ask("cap_email", "Where should we send it?", "email", "cap_phone", validation="email",
           error="Hmm, that doesn't look like an email. Mind trying again?")
    fb.ask("cap_phone", "Best number to reach you?", "phone", "cap_company", validation="phone")
    fb.ask("cap_company", "And your company?", "company", "cap_terr")
    fb.ask("cap_terr", "What state or region are you in?", "territory", "cap_close")
    fb.message("cap_close",
        "Thanks. A PRL resin specialist will follow up shortly with a match for your "
        "conditions, usually within a few hours. A real person, no phone trees.")

    return fb.build(first_trigger="onUrlOpened")


def build_ai_handoff():
    """AI -> flow delivery bridge (v2, added 2026-08-03 after the Lyro purchase).

    WHY THIS EXISTS
    ---------------
    On the Jul 31 call Daniel confirmed a hard product boundary: the FLOW-level webhook
    works on any plan, but the AI (Lyro) pushing a captured lead to SugarCRM on its own
    requires the higher Tidio+ tier. PRL bought Flows + Lyro, NOT Tidio+.

    So with Lyro enabled, a visitor who converses only with the AI is qualified and then
    goes nowhere: no Sugar lead is created. That is a lead-loss path, the exact failure
    this project exists to prevent.

    This flow closes it. Lyro's job ends at HANDOFF, not at capture. The AI answers and
    qualifies, then steers the visitor into this short flow, whose webhook delivers the
    lead through the already-proven flow path. The rep also has the full AI transcript in
    the Tidio inbox, so this only needs to capture what SugarCRM structurally requires.

    TRIGGER: must be set in the Tidio UI. The correct trigger-type string for a keyword or
    quick-reply match was NOT verified against a Tidio export, so it is deliberately left
    as onFirstVisit here and MUST be changed after import, or it will collide with the main
    flow. Confirm the mechanism with Tidio support: whether Lyro can hand off to a flow
    directly, or whether it must steer the visitor to click a quick reply.

    NOTE ON PHONE: kept required, not optional. The SugarCRM audit (2026-08-03) found
    phone_work is a required field on Leads, filled on 100/100 live records. If Todd
    decides to allow blank phones, relax this here AND in build_full()/build_sem_onramp().
    """
    fb = FlowBuilder("PRL Resins - AI Handoff (lead delivery bridge)")

    fb.trigger("t", "hello")  # <-- CHANGE TRIGGER IN TIDIO UI BEFORE ACTIVATING
    # VALUE EXCHANGE, not a form ask. The side-by-side PRL gates behind qualification is the
    # single best thing to trade for contact details, and the trade self-qualifies: someone
    # who gives an email to receive a named-grade comparison has told us what they run, that
    # they are actively evaluating, and that they are serious. That is Todd's own qualifier
    # ("a real lead names a resin PRL sells") arriving for free.
    # It also asks for CONDITIONS, which is the field a specialist most needs and the one a
    # generic form never captures.
    fb.message("hello",
        "Good news, we compound an equivalent to that. Our specialists can put a side by side "
        "in front of you, tested against the conditions your part actually sees.", nxt="h_need")
    fb.ask("h_need", "Which grade are you running today, and what does the part have to stand "
           "up to? Temperature range, outdoor exposure, chemicals, any listing you need to hold.",
           "desired_resin_or_spec", "cap_name")
    fb.ask("cap_name", "Great. Who should we put this together for?", "name", "cap_email")
    fb.ask("cap_email", "Where should we send it?", "email", "cap_phone", validation="email",
           error="Hmm, that doesn't look like an email. Mind trying again?")
    fb.ask("cap_phone", "Best number, in case a question comes up while they build it?",
           "phone", "cap_company", validation="phone")
    fb.ask("cap_company", "And your company?", "company", "cap_terr")
    fb.ask("cap_terr", "What state or region are you in?", "territory", "cap_close")
    fb.message("cap_close",
        "Done. A PRL resin specialist will send that over shortly, usually within a few "
        "hours. A real person, no phone trees.")

    return fb.build()


def build_full_ai():
    """Main flow, AI-forward variant (v2, 2026-08-03). Non-destructive: build_full() is
    untouched and remains what is live.

    WHY
    ---
    v1 funnels every visitor through the rigid decision tree, so Lyro is only reached by
    people who escape it. That inverts the value of the Flows + Lyro purchase: the
    improvisation capability is the reason for the upgrade, and almost nobody would meet it.

    The split below keeps a rigid path where SPEED wins and hands to the AI where JUDGMENT
    wins. Someone who already knows their grade wants four questions and out. Someone
    describing a part and its requirements is having a conversation, and a three-question
    form is the wrong instrument for that.

    MECHANISM
    ---------
    Per Daniel (Jul 31): the flow runs first and Lyro takes over when the flow ends or is
    interrupted. So "hand to AI" is implemented as ending the flow on an open invitation,
    not as a special node type. Lyro then picks up the conversation.

    DELIVERY
    --------
    AI-path visitors do NOT pass through the capture form, so their lead reaches SugarCRM
    only via build_ai_handoff(). That makes the handoff mechanism load-bearing in this
    variant. Do not activate this variant until the handoff is verified working, or
    "Help me choose" becomes a lead-loss path.
    """
    fb = FlowBuilder("PRL Resins - Lead Capture (AI-forward)")

    fb.trigger("t", "hello")
    fb.message("hello",
        "Hi, thanks for stopping by. Looking for a resin, a spec match, or an alternative to "
        "what you're running now? I'll get you to the right person fast.", nxt="menu")
    fb.decision("menu", "What brings you in?", [
        ("I know what I need", "a1"),        # rigid: speed
        ("Help me choose", "ai_choose"),     # AI: judgment
        ("Have someone call me", "cb1"),     # rigid: pure capture
        ("Guides and resources", "res1"),
        ("Something else", "ai_open"),       # AI: open ended
    ])

    # --- AI handoff points: flow ends, Lyro takes over ---
    fb.message("ai_choose",
        "Happy to help you narrow it down. Tell me what you're making and what the part has "
        "to stand up to. Heat, impact, outdoor exposure, chemicals, a regulatory listing, "
        "whatever matters most. I'll work through it with you.")
    fb.message("ai_open",
        "Go ahead and ask. If it's something I can't answer I'll get you to a specialist.")

    # Resources path
    fb.message("res1",
        "Here are some quick resources:\n"
        "- Product Selection Guide: https://prlresins.com/polymer-product-catalog/\n"
        "- Browse our resins: https://prlresins.com/products/\n"
        "- Quality guarantee: https://prlresins.com/quality-guarantee/\n"
        "- Find us / contact: https://prlresins.com/contact/", nxt="res2")
    fb.message("res2",
        "Anything you want to dig into, just ask. Or call 1-800-243-5176 to reach a person.")

    # Branch A - knows what they need (rigid, unchanged from v1)
    fb.ask("a1", "Great. Which resin or spec are you after?", "desired_resin_or_spec", "a2")
    fb.decision("a2", "Are you replacing a resin you run now?", [
        ("Yes", "a2y"), ("No", "a3")])
    fb.ask("a2y", "What are you using today?", "current_resin", "a3")
    fb.ask("a3", "What are you making with it?", "application", "a4")
    fb.ask("a4", "Any must-hit specs? Temperature, flame rating, color, or a regulatory listing.",
           "requirements", "cap_name")

    # Callback path (rigid, unchanged)
    fb.ask("cb1", "You got it. What's your name?", "name", "cb2")
    fb.ask("cb2", "Best number to reach you?", "phone", "cb3", validation="phone")
    fb.ask("cb3", "When's a good time to reach you? (optional)", "requirements", "cb_end")
    fb.message("cb_end", "Done. Someone from our team will call you shortly, usually within a "
               "few hours. No phone trees.")

    # Shared contact capture
    fb.ask("cap_name", "Last thing and you're set. Who should we get this to?", "name", "cap_email")
    fb.ask("cap_email", "Best email?", "email", "cap_phone", validation="email",
           error="Hmm, that doesn't look like an email. Mind trying again?")
    fb.ask("cap_phone", "Best number to reach you?", "phone", "cap_company", validation="phone")
    fb.ask("cap_company", "And your company?", "company", "cap_terr")
    fb.ask("cap_terr", "What state or region are you in?", "territory", "cap_close")
    fb.message("cap_close", "Thanks! One of our resin specialists will reach out shortly, usually "
               "within a few hours. A real person, no phone trees.")

    return fb.build()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="prl-chatbot-flow.json")
    ap.add_argument("--flow", choices=["full", "full-ai", "sem", "ai"] + [f"sem:{k}" for k in SEM_ONRAMPS], default="full")
    args = ap.parse_args()
    if args.flow.startswith("sem:"):
        data = build_sem_onramp(args.flow.split(":", 1)[1])
    else:
        data = {"sem": build_sem_onramp, "ai": build_ai_handoff,
                "full-ai": build_full_ai, "full": build_full}[args.flow]()
    with open(args.out, "w") as f:
        json.dump(data, f, indent=2)
    print(f"wrote {args.out}: {len(data['nodes'])} nodes, {len(data['edges'])} edges")
