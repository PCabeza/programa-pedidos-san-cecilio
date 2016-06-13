#! /usr/bin/python
import argparse, os, shutil
from subprocess import call

parser = argparse.ArgumentParser()
parser.add_argument('target',type=unicode,nargs='?')
parser.add_argument('-m','--make-spec',action='store_true',default=False)
parser.add_argument('-s','--spec-file',action='store_true',default=False)
parser.add_argument('-c','--clean',action='store_true', default=False)
args = parser.parse_args()

baseprogram = "c:\\Python27\\Scripts\\pyi-makespec" if args.make_spec else "c:\\Python27\\Scripts\\pyinstaller.exe"
arguments = ['noconsole', 'onefile','icon=hospital-icon.ico']
arguments = ['--'+a for a in arguments]


if args.clean:
    for f in ['build','programa_pedidos_hospital.egg-info']:
        if os.path.exists(f): shutil.rmtree(f)
    exit(0)

if args.target == 'programa_pedidos':
	script = "hospital\\programa_pedidos_gui.py"
	spec = "programa_pedidos_gui.spec"
elif args.target == 'lista_compra':
	script = "hospital\\lista_compra_gui.py"
	spec = "lista_compra_gui.spec"
else: #elif args.target == 'cruces':
	script = "hospital\\hospital_gui.py"
	spec = "hospital_gui.spec"


command = [baseprogram]+(arguments+[script] if not args.spec_file else [spec])

print ' '.join(command)
call(command)

# c:\\Python27\\Scripts\\pyinstaller.ex --noconsole --onefile --icon=hospital-icon.ico hospital_gui.spec
