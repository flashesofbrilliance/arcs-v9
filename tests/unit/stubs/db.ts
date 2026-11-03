// Recording Prisma stub: every model call is logged; reads return null/[], writes return a fake row.
export const calls: Array<{ model: string; op: string }> = []
const WRITE = /^(create|createMany|update|updateMany|upsert|delete|deleteMany)$/
export const isWrite = (op: string) => WRITE.test(op)
// A test may swap in a stateful fake (see account-delete.test.ts); null = recording stub.
let impl: Record<string, unknown> | null = null
export const setImpl = (p: Record<string, unknown> | null) => { impl = p }
const model = (name: string) =>
  new Proxy({}, {
    get: (_t, op: string) => async (...args: unknown[]) => {
      if (impl) return (impl[name] as Record<string, (...a: unknown[]) => unknown>)[op](...args)
      calls.push({ model: name, op })
      if (isWrite(op)) return { id: `fake_${name}` }
      return op.startsWith("findMany") ? [] : op === "count" ? 0 : null
    },
  })
export const prisma = new Proxy({} as Record<string, unknown>, {
  get: (_t, name: string) =>
    impl && name in impl ? impl[name] : name.startsWith("$") ? async () => [] : model(name),
})
export default prisma
