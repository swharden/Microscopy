import sys
import os
sys.path.append('../')
import linescan

masterPath=r"X:\Data\2P01\2013"
for directory, dirnames, filenames in os.walk(masterPath):
  if "LineScan-" in os.path.basename(directory):
    print(directory)
    if not os.path.exists(directory+"/SAG/imgdata.npy"):
      print()
      try:
        LS=linescan.LineScan(directory)
        LS.loadImageData()        
      except:
        print("FAILED?!")
