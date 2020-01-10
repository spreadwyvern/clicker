# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['clicker_recorder.py'],
             pathex=['C:\\Users\\user\\PycharmProjects\\clicker'],
             binaries=[],
             datas=[('500hz_cont_10s.wav', '.'), ('iso8201_lf_10s.wav', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='clicker_recorder',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
