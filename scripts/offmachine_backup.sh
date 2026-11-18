#!/usr/bin/env bash
# offmachine_backup.sh: weekly off-machine backup (rollback and DR plan, _PROPOSALS/2026-11-17-rollback-dr-plan.md, gap 1).
#
# Writes, per run (DATE = today):
#   1. arcs-memory-DATE.bundle.enc   git bundle --all of the Claude memory corpus, AES-256-CBC / PBKDF2 600k
#                                    (same format and passphrase as the 2026-09-26 backup; restore per README-RESTORE.txt)
#   2. arcs-v9-refs-DATE.bundle      git bundle of every arcs-v9 ref on origin (main, branches, tags), NOT encrypted:
#                                    same private code as the GitHub repo (the 2026-10-06 choice); a copy if GitHub loses it
# Each lands in iCloud ARCS/_backups/ with a .sha256; the encrypted memory bundle also goes up as a release asset on the
# private repo flashesofbrilliance/arcs-memory-backup. Each bundle is verified before it is copied anywhere.
#
# The passphrase is read from the login Keychain (item arcs-memory-backup) straight into openssl's env, never printed.
# Usage: scripts/offmachine_backup.sh [--no-release] [--keep N]   (--keep: newest N of each kind kept in iCloud, default 8)
# Weekly: launchd agent ~/Library/LaunchAgents/care.arcs.offmachine-backup.plist (Sundays 20:00) runs origin/main's copy;
# log at ~/Library/Logs/arcs-offmachine-backup.log.
set -euo pipefail

MEM="$HOME/.claude/projects/-Users-zharris-arcs-v9/memory"
REPO="${ARCS_REPO:-$(cd "$(dirname "$0")/.." && pwd)}"   # launchd pipes main's copy in and sets ARCS_REPO
DEST="$HOME/Library/Mobile Documents/com~apple~CloudDocs/ARCS/_backups"
RELEASE_REPO="flashesofbrilliance/arcs-memory-backup"
DATE="$(date +%Y-%m-%d)"
RELEASE=1
KEEP=8
while [ $# -gt 0 ]; do
  case "$1" in
    --no-release) RELEASE=0 ;;
    --keep) KEEP="$2"; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done

[ -d "$DEST" ] || { echo "offmachine_backup: iCloud folder missing: $DEST" >&2; exit 1; }
WORK="$(mktemp -d "${TMPDIR:-/tmp}/offmachine-backup.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

# 1. memory corpus, encrypted
git -C "$MEM" bundle create -q "$WORK/memory.bundle" --all
git bundle verify -q "$WORK/memory.bundle" >/dev/null
MEMENC="arcs-memory-$DATE.bundle.enc"
ARCS_BK_PASS="$(security find-generic-password -s arcs-memory-backup -w)" \
  openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -salt -pass env:ARCS_BK_PASS \
  -in "$WORK/memory.bundle" -out "$WORK/$MEMENC"
# round-trip proof: decrypt and verify before anything leaves the machine
ARCS_BK_PASS="$(security find-generic-password -s arcs-memory-backup -w)" \
  openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 -pass env:ARCS_BK_PASS \
  -in "$WORK/$MEMENC" -out "$WORK/memory.check.bundle"
cmp -s "$WORK/memory.bundle" "$WORK/memory.check.bundle" || { echo "offmachine_backup: memory decrypt round-trip differs" >&2; exit 1; }
echo "memory: $(git -C "$MEM" rev-list --all --count) commits, round-trip ok"

# 2. arcs-v9 refs, plain bundle from a fresh mirror of origin (worktree-independent)
git clone -q --mirror "$(git -C "$REPO" remote get-url origin)" "$WORK/arcs-v9.git"
REFS="arcs-v9-refs-$DATE.bundle"
git -C "$WORK/arcs-v9.git" bundle create -q "$WORK/$REFS" --all
git -C "$WORK/arcs-v9.git" bundle verify -q "$WORK/$REFS" >/dev/null
echo "arcs-v9: $(git -C "$WORK/arcs-v9.git" for-each-ref | wc -l | tr -d ' ') refs, main $(git -C "$WORK/arcs-v9.git" rev-parse --short main)"

for f in "$MEMENC" "$REFS"; do
  (cd "$WORK" && shasum -a 256 "$f" > "$f.sha256")
  cp "$WORK/$f" "$WORK/$f.sha256" "$DEST/"
  echo "icloud: $f ($(wc -c < "$WORK/$f" | tr -d ' ') bytes)"
done

if [ "$RELEASE" = 1 ]; then
  TAG="backup-$DATE"
  if gh release view "$TAG" -R "$RELEASE_REPO" >/dev/null 2>&1; then
    gh release upload "$TAG" -R "$RELEASE_REPO" --clobber "$WORK/$MEMENC" "$WORK/$MEMENC.sha256"
  else
    gh release create "$TAG" -R "$RELEASE_REPO" --title "Memory corpus $DATE" \
      --notes "Encrypted git bundle of the memory corpus. Restore: README-RESTORE.txt in iCloud ARCS/_backups." \
      "$WORK/$MEMENC" "$WORK/$MEMENC.sha256"
  fi
  echo "release: $RELEASE_REPO $TAG"
fi

# prune iCloud: keep the newest $KEEP of each kind this script writes (older hand-made backups untouched)
for pat in 'arcs-memory-*.bundle.enc' 'arcs-v9-refs-*.bundle'; do
  # shellcheck disable=SC2012
  ls -1t "$DEST"/$pat 2>/dev/null | tail -n +"$((KEEP + 1))" | while read -r old; do
    case "$old" in *2026-09-26*) continue ;; esac   # the first hand-made memory backup stays
    rm -f "$old" "$old.sha256"; echo "pruned: $(basename "$old")"
  done
done
echo "offmachine_backup: done $DATE"
