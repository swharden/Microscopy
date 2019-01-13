import numpy as np
import pylab

def plotFreeHand(fname):
  f=open(fname)
  raw=f.readlines()
  f.close()
  xs,ys=[],[]
  for line in raw:
    if not "PVFreehand" in line:
      continue
    line=line.split('"')
    xs.append(float(line[1]))
    ys.append(1-float(line[3]))

  pylab.figure(figsize=(5,5))
  pylab.plot(xs,ys)
  pylab.axis([0,1,0,1])
  pylab.grid()
  pylab.show()

#plotFreeHand("ess.xml")
#plotFreeHand("smallSpiral.xml")
plotFreeHand("out.xml")