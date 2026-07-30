#!/usr/bin/env python3
"""
Generate an importable Tidio Flow JSON for the PRL Resins chatbot.

Tidio's flow format uses a dual-id system:
  - payload.id      : small sequential canvas id (1,2,3...)   -> used in connections + decision route nodes
  - id / dbNodeId   : big unique node id                       -> used in button.destination, getUserInput.passedNode/failedNode, edges
  - edges[]         : big-id from->to pairs with a routeId (uuid)
This generator tracks all of that automatically so the ids always line up.

v1 = MINIMAL validation flow: onFirstVisit -> greeting card with 4 buttons -> a short message per button.
Once this imports + renders, we extend to full capture (getUserInput chains).
"""
import json, uuid, argparse

class FlowBuilder:
    def __init__(self, name, category="generate_leads"):
        self.name = name
        self.category = category
        self.nodes = []
        self.edges = []
        self._small = 0
        self._big = 200000000
        self.x = 10000
        self.y = 700

    def _ids(self):
        self._small += 1
        self._big += 1
        return self._small, self._big

    def add(self, ntype, payload, x=None, y=None):
        sid, bid = self._ids()
        payload = dict(payload)
        payload["id"] = sid
        payload["x"] = x if x is not None else self.x
        payload["y"] = y if y is not None else self.y
        payload.setdefault("customName", "")
        payload.setdefault("connections", {"top": [], "left": [], "right": [], "bottom": []})
        node = {"id": bid, "dbNodeId": bid, "type": ntype, "payload": payload}
        self.nodes.append(node)
        return node

    def small(self, node): return node["payload"]["id"]
    def big(self, node):   return node["id"]

    def connect(self, frm, to):
        """Wire a simple top/bottom connection + an edge (big ids)."""
        frm["payload"]["connections"]["bottom"].append({"nodeId": self.small(to), "direction": "from"})
        to["payload"]["connections"]["top"].append({"nodeId": self.small(frm), "direction": "to"})
        self.edges.append({
            "from_node_id": self.big(frm), "to_node_id": self.big(to),
            "id": self._next_edge(), "dbEdgeId": self._edge_last, "routeId": str(uuid.uuid4()),
        })

    _edge_last = 300000000
    def _next_edge(self):
        FlowBuilder._edge_last = getattr(FlowBuilder, "_edge_last") + 1
        self._edge_last = FlowBuilder._edge_last
        return self._edge_last

    def to_dict(self, first_trigger="onFirstVisit"):
        return {
            "name": self.name, "category": self.category,
            "firstTrigger": first_trigger, "template": "", "sandbox": 0,
            "color": "", "draftFromTemplate": 0, "type": "conversationAutomation",
            "nodes": self.nodes, "edges": self.edges, "sessionVariables": [],
        }


def build_minimal():
    fb = FlowBuilder("PRL Resins - Lead Capture (v1 test)")

    trigger = fb.add("onFirstVisit", {}, x=10300, y=700)

    # Greeting as a message node (long text allowed here, unlike the card title)
    hello = fb.add("sendChatMessagesToVisitor", {
        "messages": [{"type": "text",
            "content": "Hi, thanks for stopping by. Looking for a resin, a spec match, or an "
                       "alternative to what you're running now? I'll get you to the right "
                       "person fast."}],
    }, x=10300, y=880)
    fb.connect(trigger, hello)

    # Decision card: SHORT title (has a char limit) + 4 quick-reply buttons
    greeting = fb.add("decisionCardMessages", {
        "cards": [{
            "id": 1, "url": "", "imageUrl": "", "subtitle": "",
            "title": "What brings you in?",
            "buttons": [],
            "showTitleIndicator": True, "dataSyncedWithStore": False,
        }],
        "transferToOperatorMessageActive": False,
    }, x=10300, y=1060)
    fb.connect(hello, greeting)

    # One short message per branch (validation stubs; replaced by full capture in v2)
    # Button labels kept short to respect Tidio's quick-reply length limit.
    msgs = []
    labels = [
        ("I know what I need", "Great. Let's get the details to a specialist."),
        ("Help me choose", "No problem, that's what we're here for."),
        ("Have someone call me", "You got it. We'll grab your number next."),
        ("Something else", "Happy to help. Tell us what you need."),
    ]
    for i, (btn, text) in enumerate(labels):
        m = fb.add("sendChatMessagesToVisitor", {
            "messages": [{"type": "text", "content": text}],
        }, x=10000 + i * 360, y=1320)
        msgs.append(m)
        fb.connect(greeting, m)

    # Fill button destinations (big ids) + decision route small-id map
    card = greeting["payload"]["cards"][0]
    for i, (btn, _) in enumerate(labels):
        card["buttons"].append({"id": i + 1, "type": "action", "title": btn,
                                "destination": fb.big(msgs[i])})
        greeting["payload"][f"1_{i+1}Node"] = fb.small(msgs[i])

    return fb.to_dict()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="prl-chatbot-flow-v1.json")
    args = ap.parse_args()
    data = build_minimal()
    with open(args.out, "w") as f:
        json.dump(data, f, indent=2)
    print(f"wrote {args.out}: {len(data['nodes'])} nodes, {len(data['edges'])} edges")
