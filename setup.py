# https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
# https://docs.python.org/2/distutils/setupscript.html#installing-scripts
# https://caremad.io/blog/setup-vs-requirement/
# http://guide.python-distribute.org/creation.html

#from distutils.core import setup
from setuptools import setup

setup(
    name='programa pedidos hospital',
    version='1.0',
    author='Pablo Cabeza',
    author_email='josepablocg@gmail.com',
    # packages=['programa_pedidos_bl'],
    # package_dir={'programa_pedidos_bl':'hospital'}

    # scripts=['hospital/programa_pedidos_gui.py'],
    description='Programa para hospital de Granada',

    install_requires=[
       "xlrd",
       "xlsxwriter",
       "pyttk"
	#    'pywin32',
	#    'pyinstaller'
       # "chardet"
    ],
)
