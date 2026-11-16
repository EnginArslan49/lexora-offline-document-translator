# -*- mode: python ; coding: utf-8 -*-
# ============================================================
# Lexora — PyInstaller Spec
# ============================================================
# onedir modu kullanıyoruz (onefile değil) — Argos'un paket dizini
# yazılabilir olmalı; onefile modu sys._MEIPASS kullanır ve
# alt süreçlerde sorun çıkarabilir. Ayrıca LGPL uyumu için
# PySide6 .dll'lerinin ayrı kalması daha güvenlidir.
# ============================================================

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

hiddenimports = (
    collect_submodules("argostranslate")
    + collect_submodules("lingua")
    + collect_submodules("ctranslate2")
    + collect_submodules("sentencepiece")
    + collect_submodules("stanza")
    + ["docx", "lxml.etree"]
)

datas = collect_data_files("argostranslate")
datas += collect_data_files("lingua")
datas += [("resources", "resources")]

a = Analysis(
    ["app.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "tkinter", "matplotlib", "IPython", "pytest",
        "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets",
        "PySide6.Qt3DCore", "PySide6.QtMultimedia", "PySide6.QtQuick3D",
        "torch", "torchvision", "torchaudio", "tensorboard"
    ],
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Lexora",
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon="resources/icons/app.ico",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="Lexora",
)