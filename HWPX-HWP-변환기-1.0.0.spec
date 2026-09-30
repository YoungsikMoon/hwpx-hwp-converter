# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/hwpx_hwp_app/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('runtime', 'runtime'),
        ('vendor/hwp-converter', 'vendor/hwp-converter'),
        ('vendor/rhwp', 'vendor/rhwp'),
        ('licenses', 'licenses'),
        ('assets', 'assets'),
        ('README.md', '.'),
        ('CHANGELOG.md', '.'),
        ('LICENSE', '.'),
        ('THIRD_PARTY_NOTICES.md', '.'),
    ],
    hiddenimports=['hwpx_hwp_app.about_dialogs'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='HWPX-HWP-변환기-1.0.0',
    version='version_info.txt',
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
)
