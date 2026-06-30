"""
ARCS backup — AES-256-GCM encrypted snapshot to iCloud Drive.

Triggered semantically (not on a timer):
  - Decision receipt written
  - Template promoted to canonical
  - Session closed

Key is stored in macOS Keychain. Encryption uses Python cryptography (AESGCM).
Backup is written atomically (tmp file + os.replace).
All operations run in a daemon thread — never block the receipt write path.

Receipts and gap log writes are always persisted regardless of battery mode.
"""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import threading
import urllib.request
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

GIGI_BASE = os.environ.get("GIGI_URL", "http://localhost:3142")
ICLOUD_DIR = os.path.expanduser(
    "~/Library/Mobile Documents/com~apple~CloudDocs"
)
BACKUP_PATH = os.path.join(ICLOUD_DIR, "arcs-gigi.enc")
KEYCHAIN_SERVICE = "arcs-gigi-backup"
KEYCHAIN_ACCOUNT = "arcs-gigi-key"

# Bundles to snapshot on each backup
_BACKUP_BUNDLES = ["arcs_templates", "arcs_gap_log"]


def _get_or_create_key() -> bytes:
    """Return 32-byte key from Keychain; create and store one if absent."""
    result = subprocess.run(
        [
            "security", "find-generic-password",
            "-a", KEYCHAIN_ACCOUNT,
            "-s", KEYCHAIN_SERVICE,
            "-w",
        ],
        capture_output=True, text=True, timeout=5,
    )
    if result.returncode == 0:
        return bytes.fromhex(result.stdout.strip())

    key = secrets.token_bytes(32)
    subprocess.run(
        [
            "security", "add-generic-password",
            "-a", KEYCHAIN_ACCOUNT,
            "-s", KEYCHAIN_SERVICE,
            "-w", key.hex(),
        ],
        check=True, timeout=5,
    )
    return key


def _export_bundles() -> dict:
    """Pull all records from each ARCS bundle via GIGI REST export."""
    snapshot: dict = {}
    for name in _BACKUP_BUNDLES:
        try:
            req = urllib.request.Request(
                f"{GIGI_BASE}/v1/bundles/{name}/export", method="GET"
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read())
            snapshot[name] = data.get("records", [])
        except Exception as e:
            snapshot[name] = {"_export_error": str(e)}
    return snapshot


def _do_backup(reason: str) -> None:
    """Encrypt GIGI bundle snapshots and write to iCloud Drive."""
    try:
        key = _get_or_create_key()
        payload = json.dumps({
            "reason": reason,
            "bundles": _export_bundles(),
        }).encode()
        nonce = secrets.token_bytes(12)
        ciphertext = AESGCM(key).encrypt(nonce, payload, None)

        os.makedirs(ICLOUD_DIR, exist_ok=True)
        tmp = BACKUP_PATH + ".tmp"
        with open(tmp, "wb") as f:
            f.write(nonce + ciphertext)
        os.replace(tmp, BACKUP_PATH)
    except Exception as e:
        print(f"[arcs_backup] backup failed ({reason}): {e}")


def trigger_backup(reason: str = "receipt_written") -> None:
    """Non-blocking: fire backup in background daemon thread."""
    threading.Thread(target=_do_backup, args=(reason,), daemon=True).start()


def restore_backup(dest_path: Optional[str] = None) -> dict:
    """
    Decrypt the iCloud backup and return the bundle snapshot dict.
    Optionally write the restored JSON to dest_path.
    """
    if not os.path.exists(BACKUP_PATH):
        raise FileNotFoundError(f"No backup found at {BACKUP_PATH}")

    key = _get_or_create_key()
    with open(BACKUP_PATH, "rb") as f:
        raw = f.read()

    nonce, ciphertext = raw[:12], raw[12:]
    payload = AESGCM(key).decrypt(nonce, ciphertext, None)
    data = json.loads(payload)

    if dest_path:
        with open(dest_path, "w") as f:
            json.dump(data, f, indent=2)

    return data
