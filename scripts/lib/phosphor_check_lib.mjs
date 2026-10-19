// phosphor_check_lib.mjs: the part every Phosphor check script repeated. A check prints one line per assertion and the script exits 1 if any failed.
// Usage in a check script:  import { check, failed } from './lib/phosphor_check_lib.mjs'  ...  process.exit(failed() ? 1 : 0)
let bad = 0
export const check = (ok, msg) => { console.log(`${ok ? '✓' : '✗'} ${msg}`); if (!ok) bad++ }
export const failed = () => bad
