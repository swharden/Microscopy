import linescan
from PIL import Image
import numpy as np
import pylab
import os
import glob
#14.01.13-15.39: started compare.py to allow experimental comparison of multiple linescan experiments

def reportSummaryLS(paths,stName,CH="dGR",show=True):
  pylab.figure(figsize=(12,10))
  for i in range(len(paths)):
    c=float(i)/(len(paths)+1)
    color=pylab.cm.jet(c)
    path=paths[i]
    if "*" in path:
      path=glob.glob(path)[0]
    LS=linescan.LineScan(path)
    LS.project()
    ID=path.split("-")[-1]
    ID+=" ("+LS.config["timeFirst"].split(" ",1)[1]+")"
    for structure in LS.structures:
      if not stName==structure:
        continue
      for y in range(len(LS.structures[structure][CH])):
        pylab.plot(LS.Xs,LS.structures[structure][CH][y],color=color,alpha=.2)
      pylab.plot(LS.Xs,np.average(LS.structures[structure][CH],axis=0),label=ID,color=color,alpha=1,lw=2)
  if CH=='dGR':
    LS.prettyFormat(r"Average ($\Delta$G)/R",legendSize=12,maxmin=False)
  else:
    LS.prettyFormat(r"Raw PMT Intensity [CH=%s]"%CH,legendSize=12,rawPMT=True,maxmin=False)
  if show:
    pylab.show()


if __name__=="__main__":

  analyze="722,723,724,725,726,727,728,729"

  parent=r'X:\Data\2P01\2014\2014-01\2014-01-11 SH rat HPC stability/'
  testPaths=[]
  for item in analyze.split(","):
    testPaths.append(parent+'*-'+item)
  reportSummaryLS(testPaths,'s1','G',False)
  reportSummaryLS(testPaths,'s1','R',False)
  reportSummaryLS(testPaths,'s1','dG',False)
  reportSummaryLS(testPaths,'s1','dR',False)
  reportSummaryLS(testPaths,'s1','dGR',False)
  pylab.show()