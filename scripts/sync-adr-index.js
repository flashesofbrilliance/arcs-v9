#!/usr/bin/env node
// scripts/sync-adr-index.js — dry-run diff between _DECISIONS/*.md and _DECISIONS/index.json
//
// Read-only by design: this script never writes to index.json or any .md file.
// It parses what's on disk, compares it to the existing index, and prints a
// JSON diff report for an architect to review and apply by hand. index.json
// is the single machine-readable ADR index (ADR-024/ADR-025 collision + the
// filesystem-vs-index drift below is why this exists instead of a blind
// regenerate — some fields in index.json are already hand-set ground truth
// and must never be silently overwritten).
//
// Invariant enforced here: any entry with a non-null y_state or stability is
// treated as locked. The diff will show it as `locked: true` and will never
// appear as a proposed "update" for those two fields, even if a smarter
// inference were possible.
//
// Usage: node scripts/sync-adr-index.js

const fs = require("fs")
const path = require("path")

const DECISIONS_DIR = path.join(process.cwd(), "_DECISIONS")
const INDEX_PATH = path.join(DECISIONS_DIR, "index.json")

function isRealAdrFile(filename) {
  if (!filename.endsWith(".md")) return false
  if (filename === "_TEMPLATE.md") return false
  if (/^RECOIL-REPORT-/.test(filename)) return false
  return true
}

// Parses id / title / status out of either format seen in the wild:
//   - YAML frontmatter: ---\nid: ADR-008\ntitle: ...\nstatus: ...\n---
//   - Blockquote header: # ADR-001 — Title \n\n> **Status:** DECIDED
function parseAdrFile(filename) {
  const raw = fs.readFileSync(path.join(DECISIONS_DIR, filename), "utf8")

  const idFromFilename = (filename.match(/^(ADR-\d+)/) || [])[1] || null

  const frontmatterMatch = raw.match(/^---\n([\s\S]*?)\n---/)
  if (frontmatterMatch) {
    const fm = frontmatterMatch[1]
    const get = (key) => (fm.match(new RegExp(`^${key}:\\s*(.+)$`, "m")) || [])[1]?.trim().replace(/^"(.*)"$/, "$1")
    return {
      file: filename,
      id: get("id") || idFromFilename,
      title: get("title") || null,
      status: get("status") || null,
      format: "yaml-frontmatter",
    }
  }

  const h1Match = raw.match(/^#\s*(ADR-\d+[:—-]?\s*.*)$/m)
  const statusMatch = raw.match(/\*\*Status:\*\*\s*([A-Z_]+)/)
  return {
    file: filename,
    id: idFromFilename,
    title: h1Match ? h1Match[1].trim() : null,
    status: statusMatch ? statusMatch[1] : null,
    format: "blockquote",
  }
}

function main() {
  const files = fs.readdirSync(DECISIONS_DIR).filter(isRealAdrFile)
  const index = JSON.parse(fs.readFileSync(INDEX_PATH, "utf8"))

  const indexByFile = new Map(index.map((e) => [e.file, e]))
  const seenFiles = new Set()

  const add = []
  const update = []
  const anomalies = []

  // Group parsed files by id to detect collisions (two files, same ADR-NNN).
  const parsedByFile = files.map(parseAdrFile)
  const byId = new Map()
  for (const p of parsedByFile) {
    if (!p.id) continue
    if (!byId.has(p.id)) byId.set(p.id, [])
    byId.get(p.id).push(p)
  }
  for (const [id, group] of byId.entries()) {
    if (group.length > 1) {
      anomalies.push({
        type: "id_collision",
        id,
        files: group.map((g) => ({ file: g.file, status: g.status, title: g.title })),
        note: "Multiple files share this ADR id. File path is the real unique key — do not renumber. Each file's own index.json row (if present) is handled independently below.",
      })
    }
  }

  for (const parsed of parsedByFile) {
    seenFiles.add(parsed.file)
    const existing = indexByFile.get(parsed.file)

    if (!existing) {
      add.push({
        file: parsed.file,
        id: parsed.id,
        title: parsed.title,
        status: parsed.status,
        gate: null, // not derivable from file content alone — architect input
        y_state: null,
        stability: null,
        note: "Missing from index.json. y_state/stability left null — NEEDS_INPUT, not guessed.",
      })
      continue
    }

    const fieldUpdates = {}
    const locked = {}

    // title: only propose a change if the file's parsed title is real and
    // differs from what's currently stored (catches the ADR-008/010 case
    // where index.json.title == filename instead of the human title).
    if (parsed.title && parsed.title !== existing.title) {
      fieldUpdates.title = { from: existing.title, to: parsed.title, reason: `parsed from ${parsed.format}` }
    }
    if (parsed.status && parsed.status !== existing.status) {
      fieldUpdates.status = { from: existing.status, to: parsed.status, reason: `parsed from ${parsed.format}` }
    }

    // y_state / stability are never auto-updated. If already non-null,
    // record them as locked so the architect sees they were seen and
    // deliberately left alone.
    if (existing.y_state !== null && existing.y_state !== undefined) {
      locked.y_state = existing.y_state
    }
    if (existing.stability !== null && existing.stability !== undefined) {
      locked.stability = existing.stability
    }

    if (Object.keys(fieldUpdates).length > 0 || Object.keys(locked).length > 0) {
      update.push({
        file: parsed.file,
        id: existing.id,
        updates: fieldUpdates,
        locked,
      })
    }
  }

  // index.json rows with no matching file on disk (should be empty per Phase 1 findings,
  // but check for real rather than assume).
  for (const entry of index) {
    if (!seenFiles.has(entry.file) && !fs.existsSync(path.join(DECISIONS_DIR, entry.file))) {
      anomalies.push({
        type: "orphan_index_entry",
        file: entry.file,
        note: "index.json references a file that does not exist in _DECISIONS/.",
      })
    }
  }

  const report = { add, update, anomalies }
  console.log(JSON.stringify(report, null, 2))
}

main()
