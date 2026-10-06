// Returns a canned, well-formed compass JSON so the route runs end to end offline.
export const CANNED = {
  true_north: "Test bearing", why: "Because.", nci_score: 72, coherence_pct: 70,
  decision_mode: "PLAN", door_class: "TWO_WAY",
  tributaries: [{ type: "meta", text: "a" }, { type: "challenge", text: "b" }, { type: "adjacent", text: "c" }],
  reasoning: { court: [], paths: [], fated: {} },
}
// One-shot failure injection: the next create() throws this instead of answering.
let pending: unknown = null
export function failNext(e: unknown) { pending = e }
const create = async () => {
  if (pending) { const e = pending; pending = null; throw e }
  return ok()
}
const ok = () => ({
  content: [{ type: "text", text: JSON.stringify(CANNED) }],
  usage: { input_tokens: 1, output_tokens: 1 },
  stop_reason: "end_turn",
})
export default class Anthropic {
  messages = { create }
  beta = { messages: { create } }
}
