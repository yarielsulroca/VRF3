# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

BASE_DIR = Path(SPECPATH).resolve()
ICON_PATH = BASE_DIR / 'assets' / 'icon.ico'
icon_arg = str(ICON_PATH) if ICON_PATH.exists() else None

a = Analysis(
    [str(BASE_DIR / 'run_app.py')],
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pandas',
        'openpyxl',
        'customtkinter',
        'PIL',
        'watchdog',
        'tkinter',
        'tkinter.ttk',
        *collect_submodules('src'),
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy.testing',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'sphinx',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VRF2_Libro_Compras',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_arg,
    version_file='version_info.txt',
)