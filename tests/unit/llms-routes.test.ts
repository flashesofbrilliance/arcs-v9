// Agent-readable discovery paths (2026-10-29). Catch-all hosts used to answer /llms.txt and
// /index.md with their HTML page (200, a soft 404 agents read as content). Two layers can do
// that: src/proxy.ts host maps and next.config.ts host catch-all rewrites. This gate fails if
// either layer sends a machine path on a catch-all host to an .html page.
import { test } from "node:test"
import assert from "node:assert/strict"
import { readFileSync } from "node:fs"
import { NextRequest } from "next/server"

const { default: proxy } = await import("../../src/proxy.ts")
const req = (host: string, path: string) => new NextRequest(`https://${host}${path}`, { headers: { host } })
const rewritten = (res: Response) => {
  const h = res.headers.get("x-middleware-rewrite")
  return h ? new URL(h).pathname : null
}
const MACHINE = ["/llms.txt", "/index.md", "/robots.txt", "/sitemap.xml"]

test("proxy: open catch-all hosts never rewrite a machine path to HTML", async () => {
  for (const host of ["good.arcs.care", "resume.arcs.care", "claritai.arcs.care", "saul.arcs.care", "honest.arcs.care"]) {
    for (const path of MACHINE) {
      const dest = rewritten(await proxy(req(host, path)))
      assert.ok(!dest?.endsWith(".html"), `${host}${path} -> ${dest}`)
    }
  }
})

test("proxy: hosts with their own llms.txt serve it; unknown machine paths 404", async () => {
  assert.equal(rewritten(await proxy(req("good.arcs.care", "/llms.txt"))), "/good-llms.txt")
  assert.equal(rewritten(await proxy(req("resume.arcs.care", "/llms.txt"))), "/resume-llms.txt")
  assert.equal((await proxy(req("good.arcs.care", "/index.md"))).status, 404)
  assert.equal((await proxy(req("dj.arcs.care", "/llms.txt"))).status, 404)
})

// next.config.ts: every host catch-all `/:path((?!...).*)` for these hosts must exclude the
// machine paths (and the llms.txt destination it rewrites to).
test("next.config: catch-all rewrites exclude machine paths", () => {
  const src = readFileSync(new URL("../../next.config.ts", import.meta.url), "utf8")
  for (const host of ["status.arcs.care", "resume.arcs.care", "good.arcs.care"]) {
    const rules = [...src.matchAll(/\{ source: "\/:path\(\(\?!(.*?)\)\.\*\)", destination: "([^"]+\.html)", has: \[\{ type: "host", value: "([^"]+)" \}\] \}/g)]
      .filter((m) => m[3] === host)
    assert.ok(rules.length > 0, `no catch-all found for ${host}`)
    for (const [, look] of rules) {
      const re = new RegExp(`^(?!${look.replace(/\\\\/g, "\\")}).*$`)
      for (const p of ["llms.txt", "index.md", "robots.txt", "sitemap.xml", "status-llms.txt", "resume-llms.txt", "good-llms.txt"]) {
        assert.ok(!re.test(p), `${host} catch-all would answer /${p} with HTML`)
      }
    }
  }
})

// resume.arcs.care/proof (2026-10-30): the proxy sends the proof ledger's paths to their files, and the
// next.config resume catch-all must not re-catch those destinations and serve resume.html instead.
test("resume.arcs.care/proof: proxy routes the ledger and the catch-all lets it through", async () => {
  assert.equal(rewritten(await proxy(req("resume.arcs.care", "/proof"))), "/proof.html")
  assert.equal(rewritten(await proxy(req("resume.arcs.care", "/proof/claims.json"))), "/proof-claims.json")
  assert.equal(rewritten(await proxy(req("resume.arcs.care", "/index.md"))), "/resume-index.txt")
  assert.equal(rewritten(await proxy(req("resume.arcs.care", "/anything"))), "/resume.html")
  const src = readFileSync(new URL("../../next.config.ts", import.meta.url), "utf8")
  const m = src.match(/\{ source: "\/:path\(\(\?!(.*?)\)\.\*\)", destination: "\/resume\.html", has: \[\{ type: "host", value: "resume\.arcs\.care" \}\] \}/)
  assert.ok(m, "resume catch-all not found")
  const re = new RegExp(`^(?!${m[1].replace(/\\\\/g, "\\")}).*$`)
  for (const p of ["proof.html", "proof-claims.json", "resume-index.txt"]) assert.ok(!re.test(p), `resume catch-all would re-catch /${p}`)
})

// good.arcs.care (2026-10-30): section indexes and AGENTS.md are generated files, never the HTML catch-all.
test("good.arcs.care: section llms.txt and AGENTS.md route to their generated files", async () => {
  assert.equal(rewritten(await proxy(req("good.arcs.care", "/blog/nftt/llms.txt"))), "/good-nftt-llms.txt")
  assert.equal(rewritten(await proxy(req("good.arcs.care", "/blog/til/llms.txt"))), "/good-til-llms.txt")
  assert.equal(rewritten(await proxy(req("good.arcs.care", "/AGENTS.md"))), "/good-agents.txt")
  assert.equal(rewritten(await proxy(req("good.arcs.care", "/agents.md"))), "/good-agents.txt")
  const src = readFileSync(new URL("../../next.config.ts", import.meta.url), "utf8")
  const m = src.match(/\{ source: "\/:path\(\(\?!(.*?)\)\.\*\)", destination: "\/good\.html", has: \[\{ type: "host", value: "good\.arcs\.care" \}\] \}/)
  assert.ok(m, "good catch-all not found")
  const re = new RegExp(`^(?!${m[1].replace(/\\\\/g, "\\")}).*$`)
  for (const p of ["good-nftt-llms.txt", "good-til-llms.txt", "good-agents.txt"]) assert.ok(!re.test(p), `good catch-all would re-catch /${p}`)
})
