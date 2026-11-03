// Ledger DEL-023 — regression test for trust contract §3: "account deletion removes
// your receipts, outcomes, uploaded files and personal data". Runs the REAL
// /api/account/delete handler against an in-memory table store, seeds the
// signed-in user AND a bystander with a row in every user-keyed table, and
// asserts the user ends with zero rows while the bystander keeps every row.
import { test, beforeEach, afterEach } from "node:test"
import assert from "node:assert/strict"
import { setImpl } from "./stubs/db.ts"
import { setSession } from "./stubs/auth.ts"

type Row = Record<string, unknown>
type Where = Record<string, unknown>

const matches = (row: Row, where: Where = {}) =>
  Object.entries(where).every(([k, cond]) => {
    if (cond && typeof cond === "object" && "in" in cond) return (cond as { in: unknown[] }).in.includes(row[k])
    if (cond && typeof cond === "object" && "equals" in cond) {
      const c = cond as { equals: string; mode?: string }
      return c.mode === "insensitive"
        ? String(row[k]).toLowerCase() === c.equals.toLowerCase()
        : row[k] === c.equals
    }
    return row[k] === cond
  })

function fakeDb(tables: Record<string, Row[]>) {
  const model = (name: string) => {
    const t = () => (tables[name] ??= [])
    return {
      findMany: async ({ where }: { where?: Where } = {}) => t().filter((r) => matches(r, where)),
      findUnique: async ({ where }: { where: Where }) => t().find((r) => matches(r, where)) ?? null,
      updateMany: async ({ where, data }: { where: Where; data: Row }) => {
        const hit = t().filter((r) => matches(r, where))
        hit.forEach((r) => Object.assign(r, data))
        return { count: hit.length }
      },
      deleteMany: async ({ where }: { where: Where }) => {
        const before = t().length
        tables[name] = t().filter((r) => !matches(r, where))
        return { count: before - tables[name].length }
      },
      delete: async ({ where }: { where: Where }) => {
        const row = t().find((r) => matches(r, where))
        if (!row) throw new Error(`${name} not found`)
        tables[name] = t().filter((r) => r !== row)
        return row
      },
    }
  }
  const db: Record<string, unknown> = new Proxy({} as Record<string, unknown>, {
    has: () => true,
    get: (_t, name: string) =>
      name === "$transaction" ? async (fn: (tx: unknown) => unknown) => fn(db) : model(name),
  })
  return db
}

// Every user-keyed table the route is responsible for, seeded for one owner.
const seed = (u: string, email: string): Record<string, Row[]> => ({
  user: [{ id: u, email }],
  prepSession: [{ id: `${u}-prep`, userId: u }],
  receipt: [{ id: `${u}-r`, userId: u, prepId: `${u}-prep`, parentId: null }],
  brief: [{ id: `${u}-b`, receiptId: `${u}-r` }],
  sageTrace: [{ id: `${u}-st`, receiptId: `${u}-r` }],
  prepGuide: [{ id: `${u}-pg`, receiptId: `${u}-r` }],
  outcome: [{ id: `${u}-o`, receiptId: `${u}-r` }],
  annotation: [{ id: `${u}-a`, receiptId: `${u}-r`, userId: u }],
  scanSignal: [{ id: `${u}-ss`, userId: u, parentSignalId: null }],
  scanFeedback: [{ id: `${u}-sf`, signalId: `${u}-ss` }],
  sessionReceipt: [
    { id: `${u}-sr1`, userId: u, parentId: null, bet: "b", outcome: "o", lesson: "l", payload: {} },
    { id: `${u}-sr2`, userId: u, parentId: `${u}-sr1`, bet: "b2" },
  ],
  jobSwipe: [{ jobid: `${u}-job`, userId: u, direction: "r" }],
  lead: [{ id: `${u}-lead`, email }],
})

const owned = (tables: Record<string, Row[]>, u: string) =>
  Object.entries(tables).flatMap(([name, rows]) =>
    rows.filter((r) => JSON.stringify(r).includes(u)).map((r) => `${name}:${String(r.id ?? r.jobid)}`),
  )

let tables: Record<string, Row[]>
beforeEach(() => {
  const a = seed("u1", "U1@example.com")
  const b = seed("u2", "u2@example.com")
  tables = Object.fromEntries(Object.keys(a).map((k) => [k, [...a[k], ...b[k]]]))
  // Cross-user lineage: the bystander's session receipt was seeded from u1's.
  tables.sessionReceipt.push({ id: "u2-sr-child", userId: "u2", parentId: "u1-sr1" })
  setImpl(fakeDb(tables))
})
afterEach(() => { setImpl(null); setSession(null) })

test("account delete leaves zero rows for the user in every table, incl. SessionReceipt and JobSwipe", async () => {
  setSession({ user: { id: "u1", email: "u1@example.com" } })
  const { POST } = await import("../../src/app/api/account/delete/route.ts")
  const res = await POST()
  assert.equal(res.status, 200)
  assert.deepEqual(owned(tables, "u1"), [])
  assert.equal(tables.sessionReceipt.filter((r) => r.userId === "u1").length, 0)
  assert.equal(tables.jobSwipe.filter((r) => r.userId === "u1").length, 0)
})

test("bystander rows survive, and cross-user lineage is detached, not orphaned", async () => {
  const bystanderBefore = owned(tables, "u2").filter((k) => k !== "sessionReceipt:u2-sr-child")
  setSession({ user: { id: "u1", email: "u1@example.com" } })
  const { POST } = await import("../../src/app/api/account/delete/route.ts")
  await POST()
  const child = tables.sessionReceipt.find((r) => r.id === "u2-sr-child")
  assert.ok(child)
  assert.equal(child.parentId, null)
  assert.deepEqual(owned(tables, "u2").filter((k) => k !== "sessionReceipt:u2-sr-child"), bystanderBefore)
})

test("anonymous request deletes nothing", async () => {
  const before = JSON.stringify(tables)
  const { POST } = await import("../../src/app/api/account/delete/route.ts")
  const res = await POST()
  assert.equal(res.status, 401)
  assert.equal(JSON.stringify(tables), before)
})
