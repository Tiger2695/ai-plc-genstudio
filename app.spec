# -*- mode: python ; coding: utf-8 -*-
import streamlit
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Streamlit ki metadata aur data files ko properly collect karne ke liye
streamlit_datas = collect_data_files('streamlit', include_py_files=True)

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=streamlit_datas,  # <-- Yahan updated variable daal diya
    hiddenimports=['streamlit', 'httpx', 'pandas'] + collect_submodules('streamlit'),
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI_PLC_Delta_Studio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # True rakha hai taaki console logs dikhte rahein
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    icon='NONE'
)