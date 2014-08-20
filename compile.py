#! /usr/bin/python
import argparse, os, shutil
from subprocess import call

parser = argparse.ArgumentParser()
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

script = "hospital\\programa_pedidos_gui.py"
spec = "programa_pedidos_gui.spec"

command = [baseprogram]+(arguments+[script] if not args.spec_file else [spec])

print ' '.join(command)
call(command)
