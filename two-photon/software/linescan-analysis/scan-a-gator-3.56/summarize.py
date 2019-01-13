import sys
import glob
import os
import numpy as np

if not sys.version_info[0]>2:
  print("RUN THIS ONLY ON PYTHON 3+")
else:
  print("your python version is ok...")

def csv2npy(fname):
  data = np.loadtxt(open(fname,'rb'),delimiter=",",dtype=object)
  for y in range(len(data)):
    for x in range(len(data[y])):
      data[y][x]=data[y][x][2:-1]
  return data


analysisName = "a"
search=r"X:\Data\2P01\projects\2014-07-22 mouse PVN MCN TGOT"
structure="a"
LSincludeL = 704
LSincludeH = 721
mustMatch="08032014" # or "-" for anything

csvs=[]
for root, dirs, files in os.walk(search, topdown=True):
  for name in sorted(files):
    if not name[-4:] == ".csv":
      continue
    if not mustMatch in root:
      continue
    tag = os.path.basename(os.path.split(root)[0])
    if not "LineScan" in tag:
      continue
    num = int(tag.split("-")[-1])
    if num<LSincludeL or num > LSincludeH:
      #print(" -- EXCLUDING %d BECAUSE OUTSIDE RANGE"%num)
      continue
    if name[-5]==structure:
      csvs.append(os.path.join(root,name))
      print("adding %d"%num)
csvs=sorted(csvs)
print("found %d scans..."%len(csvs))

### ANALYSIS ###

nums=[]
Gs=[]
dGRs=[]
msPerPx=None
for fname in csvs:
  num=os.path.basename(os.path.split(os.path.split(fname)[0])[0]).split("-")[-1]
  nums.append("LS-"+num)
  print("ANALYZING",num)
  data = csv2npy(fname)
  thisMs = data[1][np.where(data[0]=='msPerPx')[0][0]]
  if msPerPx==None:
    msPerPx=thisMs
  if not msPerPx == thisMs:
    print("WARNING!!! Different ms/px")
  Gs=np.append(Gs,data[1:,0])
  dGRs=np.append(dGRs,data[1:,3])
Gs = np.reshape(Gs,(len(nums),len(Gs)/len(nums)))
dGRs = np.reshape(dGRs,(len(nums),len(dGRs)/len(nums)))

out='TIME,'+",".join(nums)+"\n"
for y in range(len(Gs[0])):
  out+=str(float(msPerPx)*y)+","+",".join(Gs[:,y])+"\n"
f=open('./analysis/%s-G.csv'%analysisName,'w')
f.write(out)
f.close()

out='TIME,'+",".join(nums)+"\n"
for y in range(len(dGRs[0])):
  out+=str(float(msPerPx)*y)+","+",".join(dGRs[:,y])+"\n"
f=open('./analysis/%s-dGR.csv'%analysisName,'w')
f.write(out)
f.close()

os.system('explorer.exe "%s"'%(os.path.abspath('./analysis/')))
print("DONE")