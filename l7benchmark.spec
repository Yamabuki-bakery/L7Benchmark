# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['l7benchmark.py'],
    pathex=[],
    binaries=[],
    # 包含 profiles 目录和必要的隐藏导入
    datas=[
        ('profiles/*.py', 'profiles'),
       # ('config.py', '.'),
       # ('mytypes.py', '.')
    ],
    hiddenimports=[
        'aiohttp',
        'aiohttp.client',
        'aiohttp.http_parser',
        'aiohttp.helpers',
        # 這裏疑似需要把內置的 profile 加到 hidden imports 裏面
        'profiles.default',
        'profiles.aozoracafe',
        'profiles.test'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'unittest', 'pytest', 'numpy', 'pandas',  # 明确排除不需要的库
        'tkinter', 'PyQt5', 'matplotlib'  # 常见可排除项
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
    name='l7benchmark',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True  # PyInstaller 6.0+ 可能需要此参数
)