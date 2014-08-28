# -*- mode: python -*-
a = Analysis(['hospital\\hospital_gui.py'],
             pathex=['Z:\\shared_folder\\hospital-pkg'], 
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          [('icon.ico', 'compile/icon.ico', 'DATA')],
          a.zipfiles,
          a.datas,
          name='programa_cruces.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False ,
          icon='compile/icon.ico')
