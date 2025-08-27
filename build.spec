# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller spec file for TaleKeeper Desktop
Builds a single Windows executable with all dependencies bundled.

To build manually:
pyinstaller build.spec

Output will be in dist/TaleKeeper.exe

INTEGRATION STATUS:
- PyQt6 UI widgets are complete and functional (character_sheet/, equipment_layout/, etc.)
- Main integration with GameEngine is in progress
- See PYQT6_INTEGRATION_PLAN.md for full implementation plan
- Once integration is complete, remove Tkinter imports and dependencies
"""

import os
from pathlib import Path

# Get the directory containing this spec file
SPEC_DIR = Path(SPECPATH).parent
DATA_DIR = SPEC_DIR / 'data'
CONFIG_DIR = SPEC_DIR / 'config' 
ASSETS_DIR = SPEC_DIR / 'assets'

# Data files to include
datas = []

# Add data directory (races, classes, monsters, etc.)
if DATA_DIR.exists():
    datas.append((str(DATA_DIR), 'data'))

# Add config directory (settings, keybindings)
if CONFIG_DIR.exists():
    datas.append((str(CONFIG_DIR), 'config'))
else:
    # Create minimal config directory
    CONFIG_DIR.mkdir(exist_ok=True)
    
# Add assets directory (fonts, images, icons)  
if ASSETS_DIR.exists():
    datas.append((str(ASSETS_DIR), 'assets'))

# Hidden imports - modules that PyInstaller might miss
hiddenimports = [
    # PyQt6 UI Framework (replacing Tkinter)
    'PyQt6',
    'PyQt6.QtWidgets',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.sip',
    # Legacy Tkinter (remove after PyQt6 migration complete)
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    # Database
    'sqlalchemy',
    'sqlalchemy.engine',
    'sqlalchemy.sql',
    'sqlalchemy.orm',
    'sqlalchemy.ext.declarative',
    'sqlalchemy.dialects.sqlite',
    # Core modules
    'loguru',
    'uuid',
    'json',
    'pathlib',
    'datetime',
    'typing',
    'enum',
    'dataclasses',
    're',
    'random',
    'os',
    'sys',
]

# Collect all SQLAlchemy modules
collect_all_imports = [
    'sqlalchemy',
]

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(SPEC_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude modules we don't need to reduce size
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'PyQt5',  # Exclude old PyQt5
        'PySide2',
        'PySide6',
        'wx',
        'tornado',
        'flask',
        'django',
        'requests',
        'urllib3',
        'certifi',
        # NOTE: PyQt6 is now included (removed from excludes)
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TaleKeeper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Temporarily disabled to avoid antivirus false positive
    version_file=None,
)