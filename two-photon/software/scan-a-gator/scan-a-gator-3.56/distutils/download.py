#
# SCAN-A-GATOR - AUTOMATIC VERSION CONTROL
#
# Run this file (Requires Python3.x) to automatically download
# and extract the latest version of this software.
#
# change: changed demoData.zip folder
# change: forced pause if executing download.py from distutils folder
# change: deleted a LOT of extra TIFs from demoData.zip and will rely completely on imgdata.npy
import sys
if sys.version_info[0]<3:
  raise Exception("REQUIRES PYTHON 3")
import os
import zipfile
import urllib.request
if os.path.basename(os.path.abspath('./'))=="distutils":
  input("dont run this script inside './distutils/', silly!")
  quit()
print("pulling version list")
f = urllib.request.urlopen("http://swharden.com/version/SAG/?C=M;O=D")
chunks=str(f.read()).split("href")
versions=[]
for chunk in chunks:
  if not ".zip" in chunk: continue
  if not "Scan-A-Gator" in chunk: continue
  chunk=chunk.split('"')[1]
  versions.append(chunk)
print("%d versions avilable."%len(versions))
print("selecting the most recent.")
fname=versions[0]
pretty=fname.replace("%20"," ")
f.close()
if os.path.exists(pretty.replace(".zip",'')):
  print("you already have the latest version!")
  exit()
print("downloading [%s]"%pretty)
g = urllib.request.urlopen("http://swharden.com/version/SAG/"+fname)
with open(pretty, 'b+w') as f:
    f.write(g.read())
g.close()
print("download complete\ndecompressing")
z = zipfile.ZipFile(pretty)
z.extractall(pretty.replace(".zip",''))
z.close()
print("clearning up")
os.remove(pretty)
print("This program is now ready to use.")
if os.path.exists("./dummyData/"):
  input()
  quit()
else:
  input("\n\nIf you want to download 8MB of demo data, press ENTER...")
fname="demoData.zip"
print("Downloading demoData.zip ... (this may take a while)")
g = urllib.request.urlopen("http://swharden.com/version/SAG/"+fname)
with open(fname, 'b+w') as f:
    f.write(g.read())
g.close()
print("download complete\ndecompressing")
z = zipfile.ZipFile(fname)
z.extractall('./')
z.close()
print("clearning up")
os.remove(fname)
print("This program is now ready to use.")
input()