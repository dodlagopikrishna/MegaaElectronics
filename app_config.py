"""Centralized, installer-aware configuration for user-chosen paths.

Reads ``config.json`` from the directory containing the executable (frozen
builds) or the project root (development).  The Inno Setup installer writes
this file with the database and PDF-export directories selected by the user
during installation.  When the file is absent or a key is missing, callers
fall back to their platform defaults so the dev workflow is unchanged.
"""

import json
import os
import sys

_config: dict = {}


def _config_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_PATH = os.path.join(_config_dir(), "config.json")


def load_config() -> None:
    """Load config.json if it exists; safe to call multiple times."""
    global _config
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
            _config = json.load(fh)


def get_db_dir() -> str:
    """Return the configured database directory, or empty string for platform default."""
    return _config.get("db_dir", "")


def get_export_dir() -> str:
    """Return the configured PDF export directory, or empty string for platform default."""
    return _config.get("export_dir", "")
