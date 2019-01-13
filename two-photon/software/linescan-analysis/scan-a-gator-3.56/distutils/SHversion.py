import sys
if sys.version_info[0]<3:
  raise Exception("REQUIRES PYTHON 3")

import ftplib
import glob
import os
#import urllib.request
import zipfile
import time
from changelog import *

def versionBundle():
  """compress ../* into a zip with a filename according to the time."""
  foldersToIgnore=["versions","__pycache__"]
  def zipdir(path, zip):
    basepath=path
    for root, dirs, files in os.walk(path):
      for file in files:
        if os.path.basename(root) in foldersToIgnore:
          continue #IGNORE BACKUPS
        elif ".pyc" in file:
          continue #IGNORE COMPILED FILES
        else:
          absPath=os.path.join(root, file)
          relPath=absPath.replace(basepath,"")
          zip.write(absPath,relPath)
  fname="Scan-A-Gator "
  fname+=time.strftime("%y.%m.%d %H.%M",time.localtime())
  if os.path.exists("C:/computername.txt"):
    with open("C:/computername.txt") as f:
      fname+=" "+f.read().strip()
  fname="./versions/"+fname+".zip"
  if not os.path.exists('./versions/'):
    os.mkdir('./versions')
  print("ZIPPING TO:",fname)
  zipf = zipfile.ZipFile(fname, 'w', zipfile.ZIP_DEFLATED)
  zipdir(os.path.abspath("../"), zipf)
  zipf.close()
  print("DONE")

def versionUpload():
  """upload the most recent compressed version to the internet. """
  fname=sorted(glob.glob("./versions/*.zip"))[-1]
  print('uploading "%s" ...'%fname)
  username='swhardenbackup'
  password='makeBackups13!'
  session = ftplib.FTP('ftp.swharden.com',username,password)
  session.cwd("SAG")
  file = open(fname,'rb')
  session.storbinary('STOR '+os.path.basename(fname), file)
  file.close()

  file = open('changelog.html','rb')
  session.storbinary('STOR '+'changelog.html', file)
  file.close()

  print("DONE")
  session.quit()

if __name__ == "__main__":
  updateCangelog()
  versionBundle()
  input("\n\npush ENTER to upload this version ...")
  versionUpload()
  input("DONE")