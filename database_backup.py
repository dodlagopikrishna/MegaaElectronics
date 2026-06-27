"""Local database backup for MEGAA Electronics.

Creates timestamped SQLite snapshots and copies them into a backup folder.
On Windows, ``config.json`` may override the destination; otherwise snapshots
are stored in ``DatabaseBackups`` beside the live database file.
"""

from __future__ import annotations

import os
import shutil
import sqlite3
from datetime import datetime

from app_config import get_backup_sync_dir
from database_setup import APP_DATA_DIR, DB_PATH, get_connection
from store_config import STORE_DB_FILENAME

METADATA_LAST_SYNC = "backup_last_sync"
METADATA_LAST_FILE = "backup_last_file"
METADATA_DEST_PATH = "backup_dest_path"

LEGACY_METADATA_KEYS = {
    "google_drive_last_sync": METADATA_LAST_SYNC,
    "google_drive_last_file": METADATA_LAST_FILE,
}


def _snapshot_filename() -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = STORE_DB_FILENAME.rsplit(".", 1)[0]
    return f"{base}_{ts}.db"


def create_database_backup() -> str:
    """Create a consistent SQLite snapshot from the live DB path."""
    if not os.path.isfile(DB_PATH):
        raise FileNotFoundError(f"Database file not found at {DB_PATH}")
    filename = _snapshot_filename()
    dest = os.path.join(APP_DATA_DIR, filename)
    src = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        dst = sqlite3.connect(dest)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()
    return dest


def get_backup_dir() -> str:
    """Resolved backup directory (installer override or DatabaseBackups beside live DB)."""
    configured = get_backup_sync_dir().strip()
    if configured:
        return configured
    return os.path.join(os.path.dirname(DB_PATH), "DatabaseBackups")


def get_backup_destination() -> str:
    return get_backup_dir()


def is_backup_configured() -> bool:
    path = get_backup_dir()
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        return False
    return os.path.isdir(path) and os.access(path, os.W_OK)


def copy_snapshot_to_folder(local_path: str, dest_dir: str) -> str:
    """Copy a snapshot file into dest_dir; returns the destination file path."""
    os.makedirs(dest_dir, exist_ok=True)
    if not os.access(dest_dir, os.W_OK):
        raise PermissionError(f"Cannot write to backup folder: {dest_dir}")
    filename = os.path.basename(local_path)
    dest_path = os.path.join(dest_dir, filename)
    shutil.copy2(local_path, dest_path)
    return dest_path


def _get_metadata(key: str) -> str:
    conn = get_connection()
    row = conn.execute("SELECT value FROM app_metadata WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else ""


def _set_metadata(key: str, value: str) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO app_metadata (key, value) VALUES (?, ?)",
        (key, value),
    )
    conn.commit()
    conn.close()


def migrate_backup_metadata() -> None:
    """Copy legacy google_drive_* metadata keys to backup_* keys."""
    for old_key, new_key in LEGACY_METADATA_KEYS.items():
        value = _get_metadata(old_key)
        if value and not _get_metadata(new_key):
            _set_metadata(new_key, value)


def get_last_backup_info() -> dict:
    return {
        "last_sync": _get_metadata(METADATA_LAST_SYNC),
        "last_file": _get_metadata(METADATA_LAST_FILE),
        "dest_path": _get_metadata(METADATA_DEST_PATH) or get_backup_dir(),
    }


def save_last_backup_info(filename: str, dest_path: str | None = None) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _set_metadata(METADATA_LAST_SYNC, now)
    _set_metadata(METADATA_LAST_FILE, filename)
    if dest_path:
        _set_metadata(METADATA_DEST_PATH, dest_path)


def run_folder_backup() -> dict:
    """Backup DB_PATH as a new timestamped snapshot in the backup folder."""
    result = {
        "success": False,
        "message": "",
        "filename": "",
        "db_path": DB_PATH,
        "dest_path": "",
    }
    dest_dir = get_backup_dir()

    local_backup = None
    try:
        local_backup = create_database_backup()
        dest_file = copy_snapshot_to_folder(local_backup, dest_dir)
        filename = os.path.basename(dest_file)
        save_last_backup_info(filename, dest_dir)
        result["success"] = True
        result["filename"] = filename
        result["dest_path"] = dest_dir
        result["message"] = f"Snapshot saved to backup folder: {filename}"
    except FileNotFoundError as exc:
        result["message"] = str(exc)
    except PermissionError as exc:
        result["message"] = str(exc)
    except Exception as exc:
        result["message"] = f"Backup failed: {exc}"
    finally:
        if local_backup and os.path.isfile(local_backup):
            try:
                os.remove(local_backup)
            except OSError:
                pass
    return result
