# https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
# https://docs.python.org/2/distutils/setupscript.html#installing-scripts
# https://caremad.io/blog/setup-vs-requirement/
# http://guide.python-distribute.org/creation.html

# TODO refactor everything to comply with pep8 style
# TODO refactor compile.py to make it more more understadable (change it to pyinstaller-compile.py)


from setuptools import setup

setup(
    name='programa-pedidos-hospital',
    version='1.1',
    author='Pablo Cabeza',
    author_email='josepablocg@gmail.com',
    packages=['hospital'],
    package_data={"hospital": ["data/icon.ico"]},

    entry_points={
        "console_scripts": ["programa_pedidos=hospital.hospital_gui:main"],
    },
    description='Programa para hospital de Granada',

    install_requires=[
        "xlrd",
        "xlsxwriter",
        "pyttk",
        "Pillow",
        # 'pywin32',
        # 'pyinstaller'
        # "chardet"
    ],
)
