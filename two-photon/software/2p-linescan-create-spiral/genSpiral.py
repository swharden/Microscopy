
import matplotlib
matplotlib.use('TkAgg') # <-- THIS MAKES IT FAST!

import numpy as np
import pylab
import os

def genSpiral(turns=10,points=100):
  step=turns/points
  ts=np.arange(0,turns,step)*2*np.pi
  ts=np.sqrt(ts*ts[-1])
  dist=np.arange(len(ts))
  xs=np.sin(ts)*dist
  ys=np.cos(ts)*dist
  return xs,ys

def genCircleShift(turns=10,dist=3,shift=None,pointsPerTurn=50):
  """Create a circle with 'turns' rotations and 'points' number of total dots."""
  points=pointsPerTurn*turns
  step=turns/points
  if shift==None:
    shift=dist/50
  ts=np.arange(0,turns,step)*2*np.pi
  xs=np.sin(ts)*dist
  ys=np.cos(ts)*dist
  xs=xs+np.arange(len(xs))*shift
  print("PIXELS:",len(ys))
  return xs,ys

def plotIt(xs,ys):
  pylab.plot(xs,ys,'b-',alpha=.2)
  pylab.plot(xs,ys,'b.')

def saveLS(xs,ys,name,turns,dist,shift):
  xs/=256
  ys/=256
  # center it
  xs=xs-min(xs)
  xs=xs-max(xs)/2+.5
  ys=ys-min(ys)
  ys=ys-max(ys)/2+.5

  # save it
  out='<?xml version="1.0" encoding="utf-8"?>\n'
  out+='<PVLinescanDefinition mode="freeHand">\n'
  for i in range(len(xs)):
    out+='  <PVFreehand x="%f" y="%f" />\n'%(xs[i],ys[i])
  out+='</PVLinescanDefinition>\n'
  bn="X:/Users_Public/Scott/2p linescan coordinates/"+name+"/"
  if not os.path.exists(bn):
    os.mkdir(bn)
  f=open(bn+"/coords.xml",'w')
  f.write(out)
  f.close()
  print('Saved',bn+"/coords.xml")

  msg=bn+"\n"
  msg+='points: %d\n'%len(ys)
  msg+='1000 ms @ 7.2 dwell =  %d linescans\n'%(1000/len(ys)*100)

  msg+='turns: %d\n'%turns
  msg+='dist: %d\n'%dist
  msg+='shift: %.03f'%shift


  # plot it
  pylab.figure(figsize=(10,10))
  pylab.plot(xs,ys,'k-',alpha=.2)
  pylab.plot(xs,ys,'k.',ms=1)
  pylab.axis([0,1,0,1])
  pylab.grid()
  pylab.text(0+.01,1-.01,msg,ha='left',va='top')
  pylab.tight_layout()
  #pylab.show()
  pylab.savefig(bn+"/coords.png",dpi=120)
  pass


#turns,dist,shift,name= 10, 10, 1/10, 'test'
#xs,ys=genCircleShift(turns,dist,shift)
#saveLS(xs,ys,name,turns,dist,shift)

turns,dist,shift,name= 10, 5, 1/15, 'SHLS-2'
xs,ys=genCircleShift(turns,dist,shift)
saveLS(xs,ys,name,turns,dist,shift)

turns,dist,shift,name= 20, 5, 1/15, 'SHLS-3'
xs,ys=genCircleShift(turns,dist,shift,20)
xs=np.arange(len(xs))/5
saveLS(xs,ys,name,turns,dist,shift)

print("DONE")