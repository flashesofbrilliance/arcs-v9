// Node resolve hook for stdlib unit tests (no test-framework dependency).
// Maps the "@/..." path alias to src/, adds .ts/.tsx extension resolution, and
// swaps side-effecting modules for recording stubs in tests/unit/stubs/.
import { existsSync, statSync } from "node:fs"
import { fileURLToPath, pathToFileURL } from "node:url"
import path from "node:path"

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..")
const STUBS = {
  "@/lib/db": "tests/unit/stubs/db.ts",
  "@/lib/auth": "tests/unit/stubs/auth.ts",
  "@anthropic-ai/sdk": "tests/unit/stubs/anthropic.ts",
  "resend": "tests/unit/stubs/resend.ts",
  "next/cache": "tests/unit/stubs/next-cache.ts",
}

function withExt(p) {
  for (const c of [p, `${p}.ts`, `${p}.tsx`, path.join(p, "index.ts")]) {
    if (existsSync(c) && statSync(c).isFile()) return c
  }
  return null
}

export async function resolve(spec, ctx, next) {
  if (STUBS[spec]) return { url: pathToFileURL(path.join(ROOT, STUBS[spec])).href, shortCircuit: true }
  if (spec.startsWith("@/")) {
    const f = withExt(path.join(ROOT, "src", spec.slice(2)))
    if (f) return { url: pathToFileURL(f).href, shortCircuit: true }
  }
  if ((spec.startsWith("./") || spec.startsWith("../")) && ctx.parentURL?.startsWith("file:")) {
    const f = withExt(path.resolve(path.dirname(fileURLToPath(ctx.parentURL)), spec))
    if (f) return { url: pathToFileURL(f).href, shortCircuit: true }
  }
  try {
    return await next(spec, ctx)
  } catch (e) {
    // CJS packages without an exports map (e.g. next/server) need the .js suffix under ESM.
    if (e?.code === "ERR_MODULE_NOT_FOUND" && !spec.startsWith(".") && !path.extname(spec)) return next(`${spec}.js`, ctx)
    throw e
  }
}
