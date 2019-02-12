# -*- mode: python -*-

block_cipher = None

options = [('W ignore', None, 'OPTION')]
a = Analysis(['timekeeper.py'],
             pathex=['C:\\Users\\ghaag\\Programming\\Python Projects\\Time Logger'],
             binaries=[],
             datas=[],
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
          name='TimeKeeper',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
		  icon='timetable.ico',
          console=False , version='version.rc')
