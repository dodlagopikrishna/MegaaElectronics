# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for MEGAA Electronics — Windows 64-bit build.
#
# Build command (run from the project root on a Windows x64 machine):
#     pyinstaller megaa.spec
#
# Output:  dist/MEGAA Electronics/MEGAA Electronics.exe
#
# Prerequisites:
#     pip install -r requirements.txt -r requirements-build.txt

import sys
from pathlib import Path

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_submodules,
    copy_metadata,
)

block_cipher = None

# ---------------------------------------------------------------------------
# Data files — NiceGUI ships its own JS/CSS that must be bundled.
# ---------------------------------------------------------------------------
nicegui_datas = collect_data_files("nicegui")
nicegui_datas += copy_metadata("nicegui")

# ---------------------------------------------------------------------------
# Hidden imports — modules that PyInstaller cannot discover statically.
# ---------------------------------------------------------------------------
hidden = (
    collect_submodules("nicegui")
    + collect_submodules("webview")
    + [
        # Application modules (loaded via dicts / late imports)
        "views.login",
        "views.dashboard",
        "views.products",
        "views.clients",
        "views.quotes",
        "views.invoices",
        "views.maintenance",
        "views.user_management",
        "views.change_password",
        "views.transaction_builder",
        "app_config",
        "store_config",
        "database_setup",
        "login_manager",
        "models",
        "pdf_generator",
        "whatsapp_share",
        "country_phone_codes",
        "ui_theme",
        # Stdlib / third-party that NiceGUI or pywebview might need at runtime
        "engineio.async_drivers.threading",
        "bcrypt",
        "PIL",
        "fpdf",
    ]
)

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("assets", "assets"),
    ]
    + nicegui_datas,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MEGAA Electronics",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                     # Windowed app, no terminal
    icon="assets/megaa_electronics_logo.ico" if Path("assets/megaa_electronics_logo.ico").exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="MEGAA Electronics",
)
