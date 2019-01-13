# -*- coding: utf-8 -*-
"""
1.) delete ../build/*
2.) copy everything from ../*.* into ../build/
      - exclude *.pyc
      - exclude anything starting with an underscore (_)
      - exclude folders (maybe later? images/icons?)
3.) compile .py -> .pyc
4.) delete all .py files
5.) zip it all
6.) upload the zip
"""
#change: created automated 'build' script which compiles PYCs, copies them with necessary supporting files, and zips it all up - ready to run (from bytecode)
import os
import glob
import shutil
import time
import py_compile
import zipfile

def moveIt(fname):
  fname=os.path.abspath(fname)
  A,B=os.path.split(fname)
  print("copying",B)
  shutil.copy(fname,A+"/build/"+B)
  
if os.path.exists('../build/'):
  for fname in glob.glob('../build/*'):
    if os.path.isdir(fname):
      shutil.rmtree(fname)
    else:
      os.remove(fname)
else:
  os.mkdir('../build/')
for fname in glob.glob('../build/*'):
  print('deleting',fname)
  os.remove(fname)
  
#MOVE ALL PYTHON SOURCES
for fname in glob.glob('../*.py'):
  if os.path.basename(fname)[0]=="_": 
    continue
  moveIt(fname)
  
#MANUALLY MOVE SOME THINGS
moveIt("../defaults.ini")
moveIt("../cmd.cmd")
moveIt("../dmidecode.exe")
moveIt("../LAUNCH.bat")
moveIt("../license.txt")

#COMPILE THINGS
for fname in glob.glob('../build/*.py'):
  py_compile.compile(fname)
  os.remove(fname)
  
#__pycache__ pull back
if os.path.exists('../build/__pycache__'):
  for fname in glob.glob('../build/__pycache__/*.pyc'):
    shutil.move(fname,'../build/'+os.path.basename(fname).replace(".cpython-33",''))
    
  shutil.rmtree('../build/__pycache__')
  
print("DONE MOVING EVERYTHING")

buidfname='build %s.zip'%time.strftime("%y.%m.%d %H.%M",time.localtime())

zipf = zipfile.ZipFile(buidfname, 'w', zipfile.ZIP_DEFLATED)
for fname in glob.glob("../build/*"):
  print("ZIPPING",os.path.basename(fname))
  zipf.write(fname,os.path.basename(fname))
zipf.close()

print("ZIPPED into: ",buidfname)