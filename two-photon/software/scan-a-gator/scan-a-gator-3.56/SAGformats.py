import pylab
import glob
import numpy as np
import pylab
import time
from PIL import Image
import os
from scipy.ndimage import gaussian_filter

#14.01.13-22.52: started a class for projection (and depth coding) of Zseries folders.

def debug(msg):
  print(msg)
stopwatch=0
def timeThis():
  global stopwatch
  stopwatch=time.time()
def timeTook(msg):
  took=time.time()-stopwatch
  if took<1:
    debug("%.3f ms for %s"%((took)*1000.0,msg))
  else:
    debug("%.03f s for %s"%(took,msg))

def getImageDimensions(fname):
  im=Image.open(fname)
  return im.size

def ar2im(ar):
  #do max stuff like this: np.max(self.images[0,60:70].astype(np.uint8),axis=0)
  return Image.fromarray(ar)

def npContrast(a,minimum=0.0,maximum=255.0):
  """return the array stretched between min/max. contrast adjustment."""
  #debug("auto-contrasting the Numpy way.")
  #14.01.02-21.11: implimented numpy contrast rather than ImageChops for LS preview.
  r=maximum-minimum #range
  a=a-np.min(a) # start at zero
  a=a/np.max(a) # now span 0-1
  a=a*r #now span correct range
  a=a+minimum #now go from minimum to maximum
  return a

def rgbGen1(f,rev=True):
  """given a fraction (0-1), return a uniuqe color code. R,G,B fraction."""
  if rev:
    f=1.0-f
  #R,G,B,A=pylab.cm.jet(f)
  R,G,B,A=pylab.cm.rainbow(f) # little brighter than jet

  return [R,G,B]

def plotRGB(n=1024):
  Rs,Gs,Bs=[],[],[]
  for i in range(n):
    r,g,b=rgbGen1(i/n)
    Rs.append(r)
    Bs.append(b)
    Gs.append(g)
  pylab.figure()
  pylab.plot(Rs,'r-',alpha=.5,lw=3)
  pylab.plot(Gs,'g-',alpha=.5,lw=3)
  pylab.plot(Bs,'b-',alpha=.5,lw=3)
  #pylab.grid()
  pylab.axis([-50,n+50,-.1,1.1])
  pylab.show()

class ZSeries:
  """Zseries"""

  def __init__(self,path):
    self.path=path
    self.loadImageData()

    #self.images[0]=self.images[0]

    self.genPics()

    im=self.zproject(self.images[0])
    im.save(self.path+"/SAG/CH1z.png")

    if len(self.images[1])>0:
      im=self.zproject(self.images[1])
      im.save(self.path+"/SAG/CH2z.png")

  def zproject(self,data,axis=0):
    #todo: axis rotation
    debug("PROJECTING")
    data=data.astype(np.uint8)
    R=np.empty(data.shape)
    G=np.empty(data.shape)
    B=np.empty(data.shape)
    for Z in range(data.shape[0]):
      nR,nG,nB=rgbGen1(float(Z)/data.shape[0])
      R[Z]=data[Z]*nR
      G[Z]=data[Z]*nG
      B[Z]=data[Z]*nB
    Rp=np.max(R.astype(np.uint8),axis=axis)
    Gp=np.max(G.astype(np.uint8),axis=axis)
    Bp=np.max(B.astype(np.uint8),axis=axis)
    im=self.makeRGB(Rp,Gp,Bp)
    return im

  def genPics(self):
    """create CH1.png, CH2.png, and GB.png."""

    Rp=self.project(0,axis=0)
    imR=Image.fromarray(Rp.astype(np.uint8))
    imR.save(self.path+"/SAG/CH1.png")

    try:
      Gp=self.project(1,axis=0)
      imG=Image.fromarray(Gp.astype(np.uint8))
      imG.save(self.path+"/SAG/CH2.png")

      imRGB=self.makeRGB(Rp,Gp,Rp)
      imRGB.save(self.path+"/SAG/RGB.png")

    except:
      print("NO GREEN CHANNEL FOUND. EXITING.")
      return




  def makeRGB(self,R=None,G=None,B=None):
    """must all be same shape."""
    data=np.zeros((R.shape[0],R.shape[1],3))
    if not R==None: data[:,:,0]=R[:,:] #RED
    if not G==None: data[:,:,1]=G[:,:] #GREEN
    if not B==None: data[:,:,2]=B[:,:] #BLUE
    im=Image.fromarray(data.astype(np.uint8),mode="RGB")
    return im

  def project(self,channel=0,startAt=0,endAt=-1,image=False,axis=0):
    """all arguments are index values."""
    timeThis()
    data=np.max(self.images[channel,startAt:endAt].astype(np.uint8),axis=axis)
    if image:
      im=Image.fromarray(data.astype(np.uint8))
      timeTook("projection to image")
      return im
    else:
      timeTook("projection to NPY array")
      return data

  def loadImageData(self,force=False):
    """start and end are file numbers starting with 1."""
    timeThis()
    if not os.path.exists(self.path+"/SAG/"):
      os.mkdir(self.path+"/SAG/")
    if os.path.exists(self.path+"/SAG/imgdata.npy") and force==False:
      self.images=np.load(self.path+"/SAG/imgdata.npy")
      timeTook("loading data from NPY")
      return
    # must create our own NPY from TIF data
    CH1list=sorted(glob.glob(self.path+"/*CurrentSettings_Ch1*"))
    L=1
    CH2list=[]
    if glob.glob(self.path+"/*CurrentSettings_Ch2*"):
      CH2list=sorted(glob.glob(self.path+"/*CurrentSettings_Ch2*"))
      L=2
    Z=max(len(CH1list),len(CH2list))
    X,Y=getImageDimensions(CH1list[0])
    self.images=np.empty((L,Z,Y,X),dtype=np.int8)
    debug("filling array of shape: "+str(self.images.shape))
    for z in range(len(CH1list)):
      self.images[0,z]=pylab.imread(CH1list[z])/2**4 # 12-bit -> 8-bit
    for z in range(len(CH2list)):
      self.images[1,z]=pylab.imread(CH2list[z])/2**4 # 12-bit -> 8-bit
    # now it's time to save the NPY to disk
    np.save(self.path+"/SAG/imgdata.npy",self.images)
    timeTook("generated and saved NPY file")


def projectAllFolders(path):
  """for each Zseries in a path, project each one."""
  for fname in glob.glob(path+"/ZSeries-*"):
    print("\n\nPROCESSING:",fname)
    try:
      ZS=ZSeries(fname)
      del ZS
      print("COMPLETE")
    except:
      print("COULD NOT DO IT")

if __name__ == "__main__":
  #ZS=ZSeries(r'X:\Data\2P01\2013\12-2013\2013-12-16\cell02\ZSeries-12032013-1549-361')
  #ZS=ZSeries(r'C:\Users\SHarden\Desktop\ZSeries-01202014-1403-404')
  #print("DONE")
  #projectAllFolders(r'X:\Data\2P01\2014\2014-01\2014-01-18 CRH')

  path=r"X:\Data\2P01\2013\06-2013\06-10-2013-HC\ZSeries-06102013-1508-449"
  ZS=ZSeries(path)
  ZS.project()