# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

added_files = [
    ('frontend/dist', 'frontend/dist'),
    ('backend', 'backend'),
]

hidden_imports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'webview',
    'clr',
    'clr_loader',
    'pythonnet',
    'bottle',
    'proxy_tools',
    'numpy',
    'scipy',
    'scipy.special',
    'scipy.fft',
    'scipy.signal',
    'scipy.ndimage',
    'scipy.spatial',
    'scipy.linalg',
    'scipy.sparse',
    'scipy.optimize',
    'scipy.integrate',
    'sklearn',
    'sklearn.utils._typedefs',
    'soundfile',
    'sigmf',
    'commpy',
    'reedsolo',
    'pyldpc',
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'alembic',
    'pydantic',
    'pydantic_settings',
    'backend.main',
]

a = Analysis(
    ['desktop_app.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'celery', 'redis'],
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
    name='DrishtiRF',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='DrishtiRF.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DrishtiRF',
)
