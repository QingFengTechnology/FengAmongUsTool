# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for FengAmongUsTool
# Requirements: PyInstaller >= 5.8  (contents_directory support)
# Build:  pyinstaller FengAmongUsTool.spec
# Output layout:
#   dist/FengAmongUsTool/FengAmongUsTool.exe   <- only the launcher EXE
#   dist/FengAmongUsTool/app/                  <- all DLLs / .pyc / data files

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # qfluentwidgets ships its own i18n translations & theme assets
        *collect_data_files('qfluentwidgets'),
        # qframelesswindow ships platform blur libs
        *collect_data_files('qframelesswindow'),
    ],
    hiddenimports=[
        # ── app package ──────────────────────────────────────────────
        'app.common.resource',
        'app.common.config',
        'app.common.icon',
        'app.common.setting',
        'app.common.signal_bus',
        'app.common.style_sheet',
        'app.common.servers_downloader',
        'app.view.main_window',
        'app.view.private_server_interface',
        'app.view.setting_interface',
        'app.view.utility_interface',
        # ── fluent widgets ────────────────────────────────────────────
        *collect_submodules('qfluentwidgets'),
        # ── PyQt6 extras not auto-detected ────────────────────────────
        'PyQt6.QtSvg',
        'PyQt6.QtSvgWidgets',
        'PyQt6.QtPrintSupport',
        'PyQt6.QtMultimedia',
        # ── async networking (aiohttp + deps) ─────────────────────────
        'aiohttp',
        'aiosignal',
        'aiohappyeyeballs',
        'frozenlist',
        'multidict',
        'yarl',
        'propcache',
        # ── optional image / color helpers ────────────────────────────
        'colorthief',
        'darkdetect',
        # ── Windows APIs ──────────────────────────────────────────────
        'win32api',
        'win32con',
        'win32gui',
        'pywintypes',
    ],
    hookspath=[],
    hooksconfig={
        'PyQt6': {
            'qt_plugins': ['platforms', 'styles', 'imageformats', 'iconengines'],
        },
    },
    runtime_hooks=[],
    # strip build-only tools from the bundle
    excludes=[
        # build-only tools
        'nuitka', 'ruff', 'pip', 'setuptools', 'wheel', 'distutils',
        # exclude PyQt5 entirely — conflicts with PyQt6 at pack time
        'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
        'PyQt5.QtNetwork', 'PyQt5.QtSvg', 'PyQt5.QtMultimedia',
        'PyQt5.QtPrintSupport', 'PyQt5.QtOpenGL', 'PyQt5.sip',
        # exclude PySide2/PySide6 for the same reason
        'PySide2', 'PySide6',
    ],
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
    exclude_binaries=True,          # onedir: keep all DLLs out of the EXE
    name='FengAmongUsTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                  # no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/resource/images/logo.ico',
    # ─── KEY: redirect all dependencies into app/ subfolder ───────────
    # Requires PyInstaller >= 5.8
    contents_directory='app',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    # Don't compress these DLLs — UPX can corrupt them
    upx_exclude=[
        'vcruntime140.dll',
        'vcruntime140_1.dll',
        'msvcp140.dll',
        'Qt6Core.dll',
        'Qt6Gui.dll',
        'Qt6Widgets.dll',
        'Qt6Network.dll',
        'Qt6OpenGL.dll',
    ],
    name='FengAmongUsTool',
)
