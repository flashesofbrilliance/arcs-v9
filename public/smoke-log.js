/**
 * smoke-log.js — tiny log harness for the MUI CDN smoke test.
 * ES module: exports write(msg) which writes timestamped lines to #log.
 */
export function write(msg) {
  const logEl = document.getElementById('log');
  if (!logEl) return;
  const ts = new Date().toISOString().slice(11, 23);
  const line = `[${ts}] ${msg}`;
  logEl.textContent = (logEl.textContent ? logEl.textContent + '\n' : '') + line;
  logEl.scrollTop = logEl.scrollHeight;
}

export function flush() {
  // no-op: write() already flushes immediately
}
