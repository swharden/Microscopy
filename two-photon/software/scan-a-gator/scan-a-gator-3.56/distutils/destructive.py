msg="""\n\n     ### THIS PROGRAM IS DANGEROUS! ###\n
It contains scripts which will permanently modify or delete data.
Do not use this unless you know EXACTLY what you are doing.
No further warnings will be given.\n\n
   Press ENTER to continue ..."""
#input(msg)
   
#change: implimented destructive (administrative) functions in a new ./distutils/destructive.py script.
   
import glob
import os
import sys
sys.path.append('../')
import linescan

def destructive_delete(fname):
  """delete something without a warning. echo to console."""
  print("DELETING:",fname)
  os.remove(fname)

def destructive_cleanLinescanFolder(folder):
  """given a linescan folder, delete the fluffy stuff."""
  print("CLEANING",folder)
  for fname in glob.glob(folder+"/*source.tif"):
    destructive_delete(fname)
  fnames=glob.glob(folder+"/References/*.tif")
  for i in range(len(fnames)):
    if "Ch2" in fnames[i]:
      destructive_delete(fnames[i])
    if i>=2: 
      destructive_delete(fnames[i])
    
def destructive_removeTIFdata(folder):
  """given a linescan folder, create numpy arrays for images, then delete the originals."""
  LS=linescan.LineScan(folder)
  LS.project()
  for fname in glob.glob(folder+"/*CurrentSettings*.tif"):
    destructive_delete(fname)
  for fname in glob.glob(folder+"/SAG/*"):
    if ".ini" in fname: continue
    if "imgdata.npy" in fname: continue
    destructive_delete(fname)
    

if __name__ == "__main__":
  print("EXECUTING.")
  for folder in glob.glob(r"C:\scott\jason\demoData2\LineScan*"):
    destructive_cleanLinescanFolder(folder)
    destructive_removeTIFdata(folder)