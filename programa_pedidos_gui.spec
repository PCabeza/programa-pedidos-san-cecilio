# -*- mode: python -*-
a = Analysis(['hospital\\programa_pedidos_gui.py'],
             pathex=['C:\\Users\\PortatilPablo\\Desktop\\documents-export-2014-08-15'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          [('icon.ico', 'icon.ico', 'DATA')],
          a.zipfiles,
          a.datas,
          name='programa_pedidos.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False ,
          icon='icon.ico')

# dist = COLLECT(exe, a.binaries, name="dist")
