// phosphor_engine.mjs: run any Phosphor check on another browser engine without editing it.
//   PHOSPHOR_BROWSER=webkit node --import ./scripts/lib/phosphor_engine.mjs scripts/phosphor_<name>_check.mjs <page.html>
// WebKit is the engine behind every iPhone and iPad browser, so it is the closest stand-in for the real device we can run here.
// Chromium launch flags (autoplay policy) are dropped for other engines; Chromium-only features (CDP sessions) fail honestly.
import { createRequire } from 'node:module'
const pw = createRequire('/Users/zharris/arcs-v9/package.json')('playwright')
const eng = process.env.PHOSPHOR_BROWSER
if (eng && eng !== 'chromium') {
  if (!pw[eng]) throw new Error('unknown engine ' + eng)
  pw.chromium.launch = (o = {}) => pw[eng].launch({ ...o, args: [] })
}
