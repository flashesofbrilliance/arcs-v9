// Recording Prisma stub: every model call is logged; reads return null/[], writes return a fake row.
export const calls: Array<{ model: string; op: string }> = []
const WRITE = /^(create|createMany|update|updateMany|upsert|delete|deleteMany)$/
export const isWrite = (op: string) => WRITE.test(op)
const model = (name: string) =>
  new Proxy({}, {
    get: (_t, op: string) => async () => {
      calls.push({ model: name, op })
      if (isWrite(op)) return { id: `fake_${name}` }
      return op.startsWith("findMany") ? [] : op === "count" ? 0 : null
    },
  })
export const prisma: any = new Proxy({}, {
  get: (_t, name: string) => (name.startsWith("$") ? async () => [] : model(name)),
})
export default prisma
