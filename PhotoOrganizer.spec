# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/shape_predictor_5_face_landmarks.dat', 'face_recognition_models/models'),
        ('resources/shape_predictor_68_face_landmarks.dat', 'face_recognition_models/models'),
        ('resources/mmod_human_face_detector.dat', 'face_recognition_models/models'),
        ('resources/dlib_face_recognition_resnet_model_v1.dat', 'face_recognition_models/models'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PhotoOrganizer',
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
    icon=['resources/icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PhotoOrganizer',
)
app = BUNDLE(
    coll,
    name='PhotoOrganizer.app',
    icon='resources/icon.icns',
    bundle_identifier=None,
)
