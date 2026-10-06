# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec file for Local Subtitler Pro (v0.2.0)
Collects all binary dependencies and assets for faster-whisper, ctranslate2 and PyQt6.
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# 收集 faster_whisper、ctranslate2 的核心动态链接库与 tokenizers 数据
datas_fw, binaries_fw, hidden_fw = collect_all('faster_whisper')
datas_ct2, binaries_ct2, hidden_ct2 = collect_all('ctranslate2')

all_datas = datas_fw + datas_ct2
all_binaries = binaries_fw + binaries_ct2
all_hidden = hidden_fw + hidden_ct2 + [
    'video_subtitler',
    'requests',
    'numpy',
    'tqdm',
    'huggingface_hub',
    'tokenizers',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
]

a = Analysis(
    ['gui_app.py'],
    pathex=['.'],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'IPython',
        'unittest',
        'test',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LocalSubtitlerPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # 无命令行黑框，原生 Windows GUI 模式
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='LocalSubtitlerPro',
)
