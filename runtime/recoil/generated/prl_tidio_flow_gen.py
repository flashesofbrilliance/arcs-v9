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
    def trigger(self, key, nxt):
        self._add(key, "trigger", next=nxt)

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
                node["type"] = "onFirstVisit"
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


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="prl-chatbot-flow.json")
    args = ap.parse_args()
    data = build_full()
    with open(args.out, "w") as f:
        json.dump(data, f, indent=2)
    print(f"wrote {args.out}: {len(data['nodes'])} nodes, {len(data['edges'])} edges")
