# -*- mode: python -*-
import logging
from pkgutil import get_data


icon_dst = "build/icon.ico"
logging.info("saving icon from hospital package-data into %s" % icon_dst)
with file(icon_dst, "w") as f: f.write(get_data('hospital', 'data/icon.ico'))


a = Analysis(['scripts\\programa-pedidos.py'],
             hiddenimports=['Tkinter'],
             hookspath=None,
             runtime_hooks=None)
a.datas += [('hospital/data/icon.ico', icon_dst, 'DATA')]

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='programa_cruces.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False ,
          icon=icon_dst)
