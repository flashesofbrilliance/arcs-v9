// Unit tests for src/document/adapters/warroomToRecoilReport.ts (pure mapper,
// war-room SSOT -> RecoilReport props). Inline fixtures pin each field-map row;
// the corpus test sweeps the real SSOTs for invariants only, so editing an
// engagement file never breaks this suite.
import { test } from "node:test"
import assert from "node:assert/strict"
import fs from "node:fs"
import path from "node:path"
import { warroomToRecoilReport as adapt } from "../../src/document/adapters/warroomToRecoilReport.ts"

const both = { audience: "both" }
const internal = { audience: "internal" }

function ssot(over: Record<string, unknown> = {}) {
  return {
    meta: {
      date: "2026-09-15",
      counterpart: "Pat Example",
      segments: 4,
      gate: { internal: "secret-pass" },
      provenance: { ...both, load_bearing_quote: "the line &#183; that mattered" },
    },
    opportunity: { ...internal, y_state: "GREEN", engagement_type: "client" },
    insights: [
      { ...both, plane: "idea", title: "Shared insight", text: "Safe to share." },
      { ...internal, plane: "counterpart", title: "Private read", text: "Never external." },
    ],
    beliefs: [{ ...internal, id: "P1", verdict: "FALSIFIED", claim: "A claim", evidence: "The evidence", inference: "EXP" }],
    next_steps: [
      { ...internal, owner: "Zach", text: "First step" },
      { ...internal, owner: "Zach", text: "Second step" },
    ],
    page: {
      header: { title: "Pat &#183; Example Co", sub: "<strong>Client</strong> &amp; partner" },
      blocks: [
        {
          tab: "recoil", type: "keyvalue", ...internal, h2: "Receipt closed &#183; ex-ante vs actual",
          rows: [{ k: "Predicted", v: "p" }, { k: "Actual", v: "It landed." }, { k: "Fork hit", v: "Upgrade." }],
        },
        {
          tab: "recoil", type: "keyvalue", ...internal, h2: "Receipt closed · follow-up call (2026-09-17)",
          rows: [{ k: "Actual (call 2)", v: "Second close." }],
        },
        {
          tab: "wargame", type: "list", ...internal, h2: "The gauntlet",
          items: [
            { dot: "", html: "<strong>BAR (ruin):</strong> the exposed edge" },
            { dot: "", html: "<strong>LAB &#183; Loki:</strong> the skeptic" },
            { dot: "", html: "<strong>COURT:</strong> no overclaim" },
            { dot: "g", html: "<strong>LAB &#183; Advisor:</strong> an ally" },
          ],
        },
        {
          tab: "wargame", type: "table", ...internal, h2: "ATG pre-mortem &#183; assume dead in 90 days",
          columns: ["Node", "Their objection", "Failure mode", "Handling"],
          rows: [
            ["1. Send", "'too long'", "Ignored", "One page"],
            ["2. Call &#183; <strong>BOTTLENECK</strong>", "-", "Stalls", "Force an answer"],
          ],
        },
      ],
    },
    ...over,
  }
}

test("cover: header title/sub decoded, y_state badge, meta line", () => {
  const o = adapt(ssot())
  assert.deepEqual(o.cover, {
    actions: [],
    title: "Pat · Example Co",
    subtitle: "Client & partner",
    badges: ["War Room", "GREEN"],
    meta: "2026-09-15 · 4 segments · client",
  })
  // No SSOT field is a call to action: an explicit [] hides the screen's inert defaults.
})

test("load-bearing quote from meta.provenance, attributed to counterpart + date", () => {
  assert.deepEqual(adapt(ssot()).loadBearingQuote, { text: "the line · that mattered", attribution: "Pat Example · 2026-09-15" })
})

test("signal threads: insights first, then beliefs with verdict accent and inference note", () => {
  const t = adapt(ssot()).signalThreads!
  assert.deepEqual(t.map((x) => x.title), ["Shared insight", "Private read", "A claim"])
  assert.equal(t[2].label, "P1 · FALSIFIED")
  assert.equal(t[2].body, "The evidence")
  assert.equal(t[2].note, "Inference: EXP")
  assert.notEqual(t[2].accent, t[0].accent, "falsified belief is not the default accent")
})

test("protocol: next_steps in order, owner as title, only the first active", () => {
  const p = adapt(ssot()).protocol!
  assert.deepEqual(p.map((s) => [s.label, s.title, s.body, !!s.active]), [
    ["Next 01", "Zach", "First step", true],
    ["Next 02", "Zach", "Second step", false],
  ])
})

test("callWalk: one step per receipt close, date from h2 else meta.date", () => {
  const w = adapt(ssot()).callWalk!
  assert.deepEqual(w, [
    { label: "2026-09-15", title: "Ex-ante vs actual", body: "It landed. Fork hit: Upgrade." },
    { label: "2026-09-17", title: "Follow-up call", body: "Second close." },
  ])
  assert.ok(w.every((s) => s.peak === undefined), "closes are never ranked")
})

test("riskFlags: gauntlet lens -> label and variant", () => {
  assert.deepEqual(adapt(ssot()).riskFlags!.map((f) => [f.variant, f.label, f.body]), [
    ["warning", "BAR (ruin)", "the exposed edge"],
    ["caution", "LAB · Loki", "the skeptic"],
    ["info", "COURT", "no overclaim"],
    ["success", "LAB · Advisor", "an ally"],
  ])
})

test("riskFlags: recoil-tab Kairos list follows the gauntlet; other recoil lists ignored", () => {
  const base = ssot()
  const o = adapt({
    ...base,
    page: {
      ...base.page,
      blocks: [
        ...base.page.blocks,
        {
          tab: "recoil", type: "list", ...internal, h2: "Kairos, quiet signals &amp; risks",
          items: [
            { dot: "", html: "<strong>Kairos:</strong> the window" },
            { dot: "g", html: "<strong>Quiet signal:</strong> he reads it" },
            { dot: "", html: "<span style='color:var(--red)'>Risk:</span> comp band" },
            { dot: "gold", html: "an unlabeled read" },
          ],
        },
        { tab: "recoil", type: "list", ...internal, h2: "Next steps (internal)", items: [{ dot: "", html: "<strong>Send it</strong> now" }] },
      ],
    },
  })
  assert.deepEqual(o.riskFlags!.slice(4).map((f) => [f.variant, f.label, f.body]), [
    ["info", "Kairos", "the window"],
    ["success", "Quiet signal", "he reads it"],
    ["warning", "Risk", "comp band"],
    ["caution", "Recoil read", "an unlabeled read"],
  ])
  assert.equal(o.riskFlags!.length, 8, "the Next steps list is not a risk source")
})

test("protocol: ex-ante commitments lead, reconstructed receipts are labelled, next steps stay active", () => {
  const base = ssot()
  const receipt = (h2: string) => ({
    tab: "exante", type: "receipt", ...internal, h2,
    fields: [
      { label: "D &#183; Sharpened question", value: "not a step" },
      { label: "Pre-committed move", value: "Send once, then wait" },
      { label: "Falsifier", value: "He asks again" },
      { label: "Kill line", value: "{{unfilled}}" },
    ],
  })
  const withReceipt = (h2: string) => adapt({ ...base, page: { ...base.page, blocks: [...base.page.blocks, receipt(h2)] } }).protocol!
  assert.deepEqual(withReceipt("Exhibit 1 &#183; Ex-Ante Decision Receipt").map((s) => [s.label, s.title, s.body, !!s.active]), [
    ["Ex-ante", "Pre-committed move", "Send once, then wait", false],
    ["Ex-ante", "Falsifier", "He asks again", false],
    ["Next 01", "Zach", "First step", true],
    ["Next 02", "Zach", "Second step", false],
  ])
  assert.equal(withReceipt("Exhibit 1 (reconstructed - no filed pre-call receipt)")[0].label, "Ex-ante (reconstructed)")
  assert.equal(withReceipt("Reconstructed pre-call receipt (post-hoc, unscoreable)")[0].label, "Ex-ante (reconstructed)")
})

test("preCallContext: Pre-Call keyvalue rows verbatim, duplicates kept, internal stays internal", () => {
  const base = ssot()
  const raw = {
    ...base,
    page: {
      ...base.page,
      blocks: [
        ...base.page.blocks,
        { tab: "pre", type: "keyvalue", ...internal, h2: "Context", rows: [
          { k: "Build", v: "Tidio &#8594; Zapier" }, { k: "Trigger", v: "surgery Friday" },
          { k: "Trigger", v: "second row" }, { k: "Owner", v: "{{who}}" },
        ] },
        { tab: "recoil", type: "keyvalue", ...internal, h2: "Not context", rows: [{ k: "X", v: "y" }] },
      ],
    },
  }
  assert.deepEqual(adapt(raw).preCallContext, { Build: "Tidio \u2192 Zapier", Trigger: "surgery Friday", "Trigger (2)": "second row" })
  assert.equal(adapt(raw, { audience: "external" }).preCallContext, undefined)
})

test("preCallIntel: Intel items verbatim as 'Lead-in: body', unlabeled items keep their body only", () => {
  const base = ssot()
  const raw = {
    ...base,
    page: {
      ...base.page,
      blocks: [
        ...base.page.blocks,
        { tab: "pre", type: "list", ...internal, h2: "Intel", items: [
          { dot: "g", html: "<strong>Todd</strong> : engaged, has edit access" },
          { dot: "", html: "<strong>Genuine fan.</strong> Reached out unprompted" },
          { dot: "", html: "Holding company, three brands to ten" },
          { dot: "", html: "<strong>Owner:</strong> {{who}}" },
        ] },
        { tab: "pre", type: "list", ...internal, h2: "Questions &amp; landmines", items: [{ dot: "", html: "not intel" }] },
      ],
    },
  }
  assert.deepEqual(adapt(raw).preCallIntel, [
    "Todd: engaged, has edit access",
    "Genuine fan. Reached out unprompted",
    "Holding company, three brands to ten",
  ])
  assert.equal(adapt(raw, { audience: "external" }).preCallIntel, undefined)
})

test("Questions & landmines: landmines become riskFlags, everything else preCallQuestions", () => {
  const base = ssot()
  const raw = {
    ...base,
    page: {
      ...base.page,
      blocks: [
        ...base.page.blocks,
        { tab: "pre", type: "list", ...internal, h2: "Questions &amp; landmines", items: [
          { dot: "", html: "Is the req real? &#183; look for: a named owner" },
          { dot: "", html: "<strong>Close:</strong> offer a written read" },
          { dot: "", html: "<span style='color:var(--gold)'>Landmine (unresolved):</span> priority unknown" },
          { dot: "r", html: "<strong>Landmine: comp.</strong> Do not raise it." },
          { dot: "", html: "Landmines hit: two air-gap breaches" },
          { dot: "", html: "<span style='color:var(--red)'>Landmine:</span> {{what to avoid}}" },
        ] },
      ],
    },
  }
  const o = adapt(raw)
  assert.deepEqual(o.preCallQuestions, [
    "Is the req real? \u00b7 look for: a named owner",
    "Close: offer a written read",
    "Landmines hit: two air-gap breaches",
  ])
  assert.deepEqual(o.riskFlags!.slice(-2).map((f) => [f.variant, f.label, f.body]), [
    ["warning", "Landmine (unresolved)", "priority unknown"],
    ["caution", "Landmine: comp.", "Do not raise it."],
  ])
  assert.equal(o.riskFlags!.length, 6, "4 gauntlet + 2 landmines; the {{slot}} landmine is absent")
  const ext = adapt(raw, { audience: "external" })
  assert.equal(ext.preCallQuestions, undefined)
  assert.equal(ext.riskFlags, undefined)
})

test("preCallTrueNorth: True North paragraphs verbatim, qualifier kept, ordered first in strata", () => {
  const base = ssot()
  const withProse = (h2: string, p: string[]) => adapt({
    ...base,
    page: { ...base.page, blocks: [
      { tab: "pre", type: "keyvalue", ...internal, h2: "Context", rows: [{ k: "Build", v: "x" }] },
      { tab: "pre", type: "prose", ...internal, h2, p },
      { tab: "pre", type: "prose", ...both, h2: "Pre-Call &#183; orient before contact", p: ["method, not a bearing"] },
    ] },
  })
  const o = withProse("True North", ["Land the build.", "Then step back."])
  assert.equal(o.preCallTrueNorth, "Land the build.\n\nThen step back.")
  const keys = Object.keys(o)
  assert.ok(keys.indexOf("preCallTrueNorth") < keys.indexOf("preCallContext"), "bearing renders before context")
  assert.equal(withProse("True North (reconstructed post-hoc)", ["Reconnect."]).preCallTrueNorth, "(reconstructed post-hoc) Reconnect.")
  assert.equal(withProse("True North", ["{{one-sentence bearing}}"]).preCallTrueNorth, undefined)
  assert.equal(adapt({ ...base, page: { blocks: [{ tab: "pre", type: "prose", ...internal, h2: "True North", p: ["x"] }] } }, { audience: "external" }).preCallTrueNorth, undefined)
})

test("Forge claim adjudication: rows become signal threads after beliefs, columns found by name", () => {
  const base = ssot()
  const forge = (columns: string[], rows: string[][]) => adapt({
    ...base,
    page: { ...base.page, blocks: [{ tab: "forge", type: "table", ...internal, h2: "Claim adjudication", columns, rows }] },
  }).signalThreads!
  const t = forge(["Claim", "Ruling", "Source force"], [
    ["Bill gets the mis-routes", "GROUNDED", "'those others will just go to Bill'"],
    ["Priority is high", "struck", "Never answered"],
    ["{{claim}}", "GROUNDED", "{{verbatim}}"],
  ])
  assert.deepEqual(t.slice(3).map((x) => [x.label, x.title, x.body]), [
    ["Forge \u00b7 GROUNDED", "Bill gets the mis-routes", "'those others will just go to Bill'"],
    ["Forge \u00b7 STRUCK", "Priority is high", "Never answered"],
  ])
  assert.notEqual(t[3].accent, t[4].accent, "grounded and struck are told apart")
  // brooks orders Claim, Evidence, Ruling
  const b = forge(["Claim", "Evidence", "Ruling"], [["He asked for an audit", "'where are you?'", "INFERENCE"]])
  assert.deepEqual([b[3].label, b[3].body], ["Forge \u00b7 INFERENCE", "'where are you?'"])
  const c = forge(["Claim", "Ruling", "Why"], [["Cold intro", "INFERENCE (cold start GROUNDED; 'test' motive unobserved)", "x"]])
  assert.deepEqual([c[3].label, c[3].note], ["Forge \u00b7 INFERENCE", "cold start GROUNDED; 'test' motive unobserved"])
})

test("scenarios: pre-mortem fills worst only, bottleneck becomes the note", () => {
  const s = adapt(ssot()).scenarios!
  assert.equal(s.best, undefined)
  assert.equal(s.base, undefined)
  assert.equal(s.worst?.title, "ATG pre-mortem · assume dead in 90 days")
  assert.equal(s.worst?.body, "1. Send, dies if: Ignored, move: One page / 2. Call, dies if: Stalls, move: Force an answer")
  assert.equal(s.worst?.note, "Bottleneck: 2. Call")
})

test("no-source props stay undefined; empty or garbage input yields only the hidden-actions cover", () => {
  const bare = { cover: { actions: [] } }
  assert.deepEqual(adapt({}), bare)
  assert.deepEqual(adapt(null), bare)
  assert.deepEqual(adapt("not json"), bare)
  assert.deepEqual(adapt([1, 2]), bare)
})

test("entities decode: smart quotes, ellipsis, arrows, accents, numeric refs", () => {
  const o = adapt(ssot({ meta: { provenance: { ...both, load_bearing_quote: "&ldquo;it&rsquo;s Ma&ntilde;ana&hellip;&rdquo; &rarr; &#8594; &#x2192;" } } }))
  assert.equal(o.loadBearingQuote?.text, "\u201cit\u2019s Ma\u00f1ana\u2026\u201d \u2192 \u2192 \u2192")
})

test("TEXT-string arrays and objects parse; malformed JSON strings are ignored", () => {
  const base = ssot()
  const o = adapt({ ...base, insights: JSON.stringify(base.insights), next_steps: "[not json" })
  assert.equal(o.signalThreads!.filter((t) => t.label === "idea").length, 1)
  assert.equal(o.protocol, undefined)
  assert.equal(adapt(JSON.stringify(base)).cover?.title, "Pat · Example Co", "whole SSOT as a TEXT string")
})

test("unfilled {{placeholders}}, TBD markers and redaction spans read as absent", () => {
  const o = adapt(ssot({
    insights: [{ ...both, plane: "idea", title: "{{title}}", text: "{{text}}" }],
    beliefs: [],
    next_steps: [{ ...internal, owner: "Zach", text: "TBD" }],
    page: {
      blocks: [
        { tab: "recoil", type: "keyvalue", h2: "Receipt closed", rows: [{ k: "Actual", v: "PENDING" }, { k: "Fork hit", v: "TBD" }] },
        {
          tab: "wargame", type: "table", h2: "Pre-mortem", columns: ["Node", "Failure mode", "Handling"],
          rows: [["1", '<span style="background:#1e293b;color:#1e293b;">their real objection</span>', "{{your move}}"]],
        },
      ],
    },
  }))
  assert.equal(o.signalThreads, undefined)
  assert.equal(o.protocol, undefined)
  assert.equal(o.callWalk, undefined)
  assert.equal(o.scenarios, undefined)
})

test("external audience: only nodes tagged `both`; untagged and internal fail closed", () => {
  const o = adapt(ssot(), { audience: "external" })
  assert.deepEqual(Object.keys(o).sort(), ["cover", "loadBearingQuote", "signalThreads"])
  assert.deepEqual(o.signalThreads!.map((t) => t.title), ["Shared insight"])
  assert.deepEqual(o.cover, { actions: [], meta: "2026-09-15 · 4 segments" }, "untagged header and internal opportunity dropped")
  const internalQuote = ssot()
  internalQuote.meta.provenance.audience = "internal"
  assert.equal(adapt(internalQuote, { audience: "external" }).loadBearingQuote, undefined)
})

test("gate passcode never appears in the output", () => {
  for (const audience of ["internal", "external"] as const) {
    assert.ok(!JSON.stringify(adapt(ssot(), { audience })).includes("secret-pass"))
  }
})

test("corpus: every real SSOT adapts without leaks or placeholders", () => {
  const dir = path.join(process.cwd(), "runtime", "recoil", "generated")
  let n = 0
  for (const f of fs.readdirSync(dir).filter((x) => x.endsWith(".json"))) {
    let raw: any
    try { raw = JSON.parse(fs.readFileSync(path.join(dir, f), "utf-8")) } catch { continue }
    n++
    for (const audience of ["internal", "external"] as const) {
      const out = JSON.stringify(adapt(raw, { audience }))
      assert.ok(!out.includes("{{"), `${f} (${audience}) leaks a template slot`)
      assert.ok(!/"(TBD|TODO|PENDING)"/.test(out), `${f} (${audience}) leaks a TBD marker`)
      assert.ok(!/<\/?[a-z][^>]*>/i.test(out), `${f} (${audience}) leaks an HTML tag`)
      assert.ok(!/&(#\d+|#x[0-9a-f]+|[a-z]+);/i.test(out), `${f} (${audience}) leaks an undecoded HTML entity`)
      const gate = raw?.meta?.gate
      for (const v of gate && typeof gate === "object" ? Object.values(gate) : []) {
        if (typeof v === "string" && v.length > 4) assert.ok(!out.includes(v), `${f} (${audience}) leaks the gate passcode`)
      }
    }
    // External output must be a subset of what the internal cut shows.
    const ext = adapt(raw, { audience: "external" })
    const int = adapt(raw)
    for (const t of ext.signalThreads ?? []) assert.ok(int.signalThreads?.some((x) => x.title === t.title), `${f}: external thread not in internal`)
  }
  assert.ok(n > 10, `expected the SSOT corpus, read ${n} files`)
})
