# -*- coding: utf-8 -*-
"""
Created on Sat Dec 28 23:40:59 2013

@author: scott

  IMPORTANT THINGS TO REMEMEMBER WHEN CODING THIS PROJECT:

  * the linescan.py script should be completely command driven
    and have zero reliance on any GUI.

  * NEVER modify any file except those inside the /SAG/ folder

  * COMPARTMENTALIZE FUCNTIONALITY - make things as simple as possible

  * minimize the amount of code that goes in the GUI file. Keep that
    limited to things necessary to control UI elements (graying, etc.)

  * intellegently name config variables - prepend with letters?

"""


import numpy as np
import scipy as sp
from scipy.ndimage import gaussian_filter
import pylab
from PIL import Image
from PIL import ImageDraw
from PIL import ImageChops
from PIL import ImageOps
from PIL import ImageEnhance
import glob
import os
import time
import threading
import pickle
import sys
from operator import itemgetter

debugLevel=3 #maximum level to show


def execute(cmd):
  """run a command, intended to be threaded."""
  debug("execute()")
  os.system('"'+cmd+'"')

def launchThreaded(fname):
  """threadedly launch a file."""
  debug("launchThreaded()")
  cmd=os.path.normpath(fname)
  threading.Thread(target=execute,args=(cmd,)).start()

def threadCommand(cmd):
  """threadedly run a command."""
  #14.01.24-14.51: added a function to threadedly execute any dos command
  debug("threadCommand() for command: [%s]"%cmd)
  threading.Thread(target=execute,args=(cmd,)).start()

def epoch2pretty(epoch):
  """takes a float epoch time and returns pretty time."""
  st=epoch2t(epoch)
  return time.strftime("%y-%m-%d %I:%M:%S %p", st)

def epoch2t(epoch):
  """takes a float epoch and returns a time struct."""
  return time.gmtime(epoch)

def timeFormatPretty(msg):
  """Converts 20:03:46.0156250 to 08:03:46 PM"""
  if "." in msg: msg=msg.split(".")[0]
  h,m,s=msg.split(":")
  h24=int(h)
  h,m,s=int(h),int(m),int(s)
  suffix="AM"
  if h>12:
    h=h-12
    suffix="PM"
  #msg="%02d:%02d:%02d %s"%(h,m,s,suffix)
  msg="%02d:%02d:%02d"%(h24,m,s)
  return msg

def XMLpull(line,tag):
  line=line.split(" ",1)[1]
  line=line.split('" ')
  value=None
  for item in line:
    if tag in item:
      item=item.split("=")
      value=item[1].replace('"','')
  return value


def XML_L(xmlfile):
  """parse XML file for useful LINESCAN data. return a dictionary."""

  keysLS=["pixelsPerLine","linesPerFrame","framePeriod","scanlinePeriod",
      "dwellTime","opticalZoom","pmtGain_0","pmtGain_1","laserPower_0",
      "micronsPerPixel_XAxis"]
  d={}
  d["version"]=0 #overwrite this with whatever editor you choose

  # THIS IS WHERE YOU ADD GUI-TYPE THINGS
  d["notes"]=""

  # THIS IS SPECIFIC TO XML TYPE TINGS NOW
  d["sequences"]=0
  d["frames"]=0
  f=open(xmlfile)
  raw=f.readlines()
  f.close()
  for line in raw:
    if "<PVScan " in line:
        if not "timeFirst" in d.keys():
          #14.01.03-16.39: made the browser show linescan date as well as time
          d["timeFirst"]=XMLpull(line,'date')
          d["timeFirst"]=d["timeFirst"][:6]+d["timeFirst"][8:]
    if "<Sequence" in line:
        d["sequences"]=d["sequences"]+1
    if "<Frame" in line:
        d["frames"]=d["frames"]+1
        abstime=XMLpull(line,"absoluteTime")
        try:
          d["absoluteTime"]=float(abstime)
          d["timeSpan"]=float(XMLpull(line,"absoluteTime"))
          if d["timeSpan"]<60:
            d["timeSpan"]="%.01fs"%(d["timeSpan"])
          else:
            d["timeSpan"]="%.01fm"%(d["timeSpan"]/60.0)
        except:
          pass #must be still scanning?
    for key in keysLS:
      if key in line:
        d[key]=float(XMLpull(line,"value"))
  if not "LineScan" in xmlfile:
    return d
  ref=glob.glob(os.path.dirname(xmlfile)+"/References/*Ch1-LinescanRef*.tif")[0]
  d["ref"]=os.path.split(ref)[1]

  # now that we have the basics, let's add some of our own for simplicity
  d["imgX"]=d["linesPerFrame"]
  d["imgY"]=d["pixelsPerLine"]
  d["imgZ"]=d["sequences"]
  d["msPerPx"]=d["framePeriod"]/d["imgX"]*1000
  d["umPerPx"]=d["micronsPerPixel_XAxis"]

  # to make a numpy array of x ticks, do this:
  # np.arange(d["imgX"])*d["msPerPx"]

  # add default GUI settings
  # prepend common things with "gui" to keep them close in alphabetical order
  d["guiSelectedSweeps"]=None
  d["guiValidSweeps"]=None
  #CHANGE: set space and time gaussian default value to 1 (from 0)
  d["guiGaussSpace"]=1 #IN PIXELS
  d["guiGaussTime"]=1 #IN PIXELS
  d["guiBaseline"]=[0,10] #IN PIXELS
  d["guiMeasure"]=[] #IN PIXELS
  d["guiEvents"]=[] #IN PIXELS

  #TODO: MAKE THINGS MS

  d["structures"]=[]
  #d["structures"]=[[10,20,"d1"],[30,37,"s1"],[51,60,"s2"],[65,70,"s3"],[82,89,"d2"]]

  return d

def debug(msg,level=3):
  """use this instead of print() for debug messages.

    * level 3 -- most minimal, not displayed
    * level 2 -- informative, display in statusbar
    * level 1 -- important, perhaps bold?
    * level 0 -- critical, stop the program, pop-up, log to file
  """
  if level<=debugLevel:
    print("-"*(level),msg)

def listFolderScans(parentFolder,atLeast=0,app=None,debugFunc=None,justOne=False):
  """A bit like a directory browser, but returns formatted scan details.

  stars are added if config files are saved
  ! is added if flagged

  EXAMPLES:
    * 06:11:34 PM S 123 (05) 1024x4032       (single image)
    * 06:11:34 PM L 321 (03) 350ms 12min * ! (linescan)
    * 06:11:34 PM T 123 (20) 430x432 1.8s    (time series)
    * 06:11:34 PM Z 123 (55) 1024x1024       (z series)
  """
  #TIP: dont use file modification time, instead read XML
  # this is because the copying to the X-drive messes it up.

  #14.01.02-21.11: adds * to end of folder nickname if scans.pkl exists
  #14.01.02-21.11: adds ! to end of folder nickname if flagged file exists
  #14.01.02-21.11: added functionality to only show folders with 'atLeast' scans

  if justOne:
    #given a single folder to look up
    fnames=[parentFolder]
  else:
    #this path is a folder of folders
    fnames=glob.glob(parentFolder+"/*")
  files=[]
  folders=[]

  #for fldr in fnames:
  for i in range(len(fnames)):
    fldr=fnames[i]
    bn=os.path.basename(fldr) #basename
    nick=bn
    if "-" in nick:
      fileNumber=nick.split("-")[-1]
    else:
      fileNumber="#?#"

    #14.01.13-15.39: using file modification date for files without .XML files
    #st=epoch2t(os.stat(fldr).st_ctime)
    #14.01.13-15.39: relying on ABF modification time, not creation time
    #st=time.gmtime((os.stat(fldr).st_ctime))
    dateFile=fldr #the file to date the folder by
    if os.path.isdir(dateFile):
      if glob.glob(fldr+"/*.*"):
        dateFile=glob.glob(fldr+"/*.*")[0]

    #14.01.13-15.39: file timestamp now in localtime instead of gmtime
    st=time.localtime((os.stat(dateFile).st_mtime))
    nick="%d/%d/%d "%(st.tm_mon,st.tm_mday,st.tm_year)
    #14.01.24-14.51: causing browser to show 24 hour timestamps to help for alphabetical ordering
    nick+="%02d:%02d:%02d"%(st.tm_hour,st.tm_min,st.tm_sec)
    #nick+="%d:%02d:%02d AM"%(st.tm_hour%12,st.tm_min,st.tm_sec)
    #if st.tm_hour>12:
      #nick=nick.replace("AM","PM")

    if "SingleImage-"==bn[:12]:
      #nick+=" S %s [xml]"%(fileNumber)
      x=XML_L(glob.glob(fldr+"/*.cfg")[0])
      x=dictUpdate(x,XML_L(glob.glob(fldr+"/*.xml")[0]))
      #14.01.05-23.57: fixed problem where SingleImages had a " Z " label
      nick+=" S %s (%dx%d)"%(fileNumber,x["pixelsPerLine"],x["linesPerFrame"])
      #nick="???"
      files.append(["S",fldr,nick])

    elif "LineScan-"==bn[:9]:
      if len(glob.glob(fldr+"/*CurrentSettings_Ch2*"))<atLeast:
        #minimum not met
        continue
      try:
        x=XML_L(glob.glob(fldr+"/*.xml")[0])
      except:
        print("NO XML FILE?")
        continue
      try:
        nick+=" L %s (%02d) %s"%(fileNumber,x["sequences"], x["timeSpan"])
      except:
        nick+=" L %s (?) ?"%(fileNumber)
      #14.01.04-18.59: now LS marks * and ! are not exclusive
      if os.path.exists(fldr+"/SAG/scans.pkl"):
        nick+=" *"
      else:
        nick+="  "

      if os.path.exists(fldr+"/SAG/flagged"):
        nick+=" !"
      else:
        nick+="  "

      files.append(["L",fldr,nick])

    elif "TSeries-"==bn[:8]:
      x=XML_L(glob.glob(fldr+"/*.xml")[0])
      #nick+=" T %s [xml]"%(fileNumber)
      try:
        nick+=" T %s (%02d) %s"%(fileNumber,x["sequences"], x["timeSpan"])
      except:
        nick+=" T %s (?) ?"%(fileNumber)
#      if os.path.exists(fldr+"/SAG/"):
#        nick+=" *"
      files.append(["T",fldr,nick])

    elif "ZSeries-"==bn[:8]:
      #nick==epoch2pretty(os.stat(fldr).st_ctime)
      #nick+=" Z %s [xml]"%(fileNumber)
      x=XML_L(glob.glob(fldr+"/*.xml")[0])
      nick+=" Z %s (%02d)"%(fileNumber,x["frames"])
      files.append(["Z",fldr,nick])

    elif ".abf"==bn[-4:]:
      nick+=" A %s %.02fMB"%(bn[-7:],os.stat(fldr).st_size/1000000.0)
      files.append(["A",fldr,nick])

    elif ".tif"==bn[-4:] or ".TIF"==bn[-4:]:
      nick+=" I %s %.02fMB"%(bn,os.stat(fldr).st_size/1000000.0)
      files.append(["I",fldr,nick])

    elif os.path.isfile(fldr)==False:
      nick = "/"+bn+"/"
      folders.append(["/",fldr,nick])

    else:
      nick+=" ? "+bn
      files.append(["X",fldr,nick])


    # this might make it slower, but it will be more resposnive
    if debugFunc:
      debugFunc("PARSING XML DATA - %02d of %02d = %d%%"%(i,len(fnames),100.0*i/float(len(fnames))),1)
    if app:
      app.processEvents()

  if debugFunc:
    debugFunc("Scanning for hidden and flagged files...",1)
  if app:
    app.processEvents()

  #14.01.13-15.39: check if 'hidden' file is in ./sag/ at file population time
  for i in range(len(files)):
    if os.path.isdir(files[i][1]):
      if glob.glob(files[i][1]+"/SAG/hidden"):
        files[i][2]=files[i][2]+" H"

  #14.01.11-17.31: used "sorted(files,key=lambda nick: nick[2])" to sort file browser list by date (as pulled from XML data)
  #14.01.13-15.39: now folder lists are sorted appropriately in the browser
  return sorted(folders)+sorted(files,key=lambda nick: nick[2])
  #return folders+sorted(files)

def dictSave(d,fname=None):
  """format a dictionary to text. If no fname given, just print."""
  out=""
  for k in sorted(d.keys()):
    if type(d[k])==str:
      out+='%s = "%s"\n'%(k,str(d[k]))
    else:
      out+="%s = %s\n"%(k,str(d[k]))

  if fname==None:
    print(out)
  else:
    #debug("writing configuration file")
    f=open(fname,'w')
    f.write(out)
    f.close()
  return out

def dictLoad(fname=None):
  """load an ini-style text file to a dictionary."""
  f=open(fname)
  raw=f.readlines()
  f.close()
  d={}
  for line in raw:
    if line[0]=="#":
      continue
    if not " = " in line:
      continue
    #14.01.02-21.11: fixed bug where backslash in config file would crash eval()
    if "\\" in line:
      line=line.replace("\\","/")
    line=line.split(" = ")
    d[line[0]]=eval(line[1])
  return d

def dictUpdate(original,newer):
  """Combine two dictionaries. If duplicate keys exist,
  use the newer values to overwrite the older ones."""
  for k in newer.keys():
    original[k]=newer[k]
  return original

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


def imFromLSArray(ar,fname=None):
  """assumes input is a 12-bit LS image. returrns 8-bit img."""
  im=Image.fromarray((ar/16).astype(np.uint8))
  if fname==None:
    return im
  else:
    im.save(fname)

def imSave(im,fname,size=None):
    if size:
      sizex,sizey=im.size
      if size[0]: sizex=size[0]
      if size[1]: sizey=size[1]
      im=im.resize((sizex,sizey))
    im.save(fname)


def imFromNumpyArray(ar,fname=None,autoContrast=True):
  """applies automatic contrast to input then returns Image.
  Give it a file name and it will save it too!."""
  if not len(ar.shape)==2:
    print("ERROR: imFromNumpyArray(ar) with shape of",ar.shape)
  if autoContrast:
    ar=npContrast(ar)
  im=Image.fromarray(ar.astype(np.uint8))
  if fname==None:
    return im
  else:
    im.save(fname)

def safelyDeleteAll(path,deleteIt=True):
  """only deletes contents of ./path/SAG/*.* but does NOT delete folders"""
  if os.path.exists(path+"/SAG/"):
    debug("DELETING THINGS FROM "+path+"/SAG/*.*")
    for fname in glob.glob(path+"/SAG/*"):
      if os.path.isdir(fname):
        debug("KEEPING "+os.path.basename(fname))
        continue
      debug("DELETING "+os.path.basename(fname))
      if deleteIt:
        os.remove(fname)

def swapDelta(msg):
  msg=msg.replace("delta",r"$\Delta$")
  return msg

def npContrast(a,minimum=0,maximum=255):
  """return the array stretched between min/max. contrast adjustment."""
  #debug("auto-contrasting the Numpy way.")
  #14.01.02-21.11: implimented numpy contrast rather than ImageChops for LS preview.
  r=maximum-minimum #range
  a=a-np.min(a) # start at zero
  a=a/np.max(a) # now span 0-1
  a=a*r #now span correct range
  a=a+minimum #now go from minimum to maximum
  return a

def imLinescanPrep(im):
  """contrast enhancement for grayscale images."""
  #14.01.02-21.11: created function to maximize contrast of linescan previews
  #debug("auto-contrasting the PIL way.")
  im=ImageOps.autocontrast(im)
  return im

def colorfix(color):
  """fixes some errors associated with qPixmaps and PIL Image data."""
  #14.01.03-16.39: added function to convert RGBA<->BGRA
  color2=(color[2],color[1],color[0],color[3])
  return color2

class LineScan:
  """primary class to handle linescan folders. Just give it a linescan path.

  What to call and when to call it:

    * gauss() - if you change X,T gaussian settings
    * project() - if you changed the sweep selection
    * intensity() - if you changed structure locations
    * saveEverything() - will write tons of garb to the disk

    If you're just flipping through linescan folders in a GUI and maybe
    making some small changes to the structures, just pull the projection.

    If you're just dorking with structures, just load intensity()

    Lower-level functions probably only need to be run once, as their output
    is saved into numpy-formatted binary files.

  """

  def __init__(self,path,version=0):
    """the path MUST have a single valid lienscan .xml file inside it."""
    if path==None: return #dummy
    debug("STARTING LS CLASS: "+os.path.basename(path))
    self.path=path
    self.version=version #this should be set by the editor that uses this class
    self.config={}
    if not os.path.exists(path):
      debug("ERROR: PATH DOES NOT EXIST.",0)
      return
    if not os.path.exists(path+"/SAG/"):
      try:
        os.mkdir(path+"/SAG/")
      except:
        debug("can't make /SAG/ folder - no access?")
    if os.path.exists(path+"/SAG/imgconf.ini"):
      # LOAD ONE, MAYBE OLDER VERSION?
      self.config=dictUpdate(self.config,dictLoad(self.path+"/SAG/imgconf.ini"))
    else:
      # CREATE A NEW ONE, ASSIGN VERSION
      if not glob.glob(self.path+"/*.xml"):
        debug("NO XML FILE FOUND")
        return
      self.config=dictUpdate(self.config,XML_L(glob.glob(self.path+"/*.xml")[0]))
      self.config["version"]=self.version #we know the version is accurate

    if not 'version' in self.config.keys():
      self.config["version"]=0

    # might as well figure out your X ticks.
    # TODO: I really don't want to do this here, but I can't
    # seem to come up with a better place!!!
    self.Xs=np.arange(self.config["imgX"])*self.config["msPerPx"]


    #self.gauss() #this will call self.loadImageData() if needed
    #CALL GAUSS IF YOU NEED SOMETHING

  ### RAW IMAGE DATA ###

  def loadImageData(self,forceFromImages=False):
    """Intelligently build a 4D matrix from a linescan folder.
    RAW IMAGE DATA (float) will be saved in /path/imgdata.npy
    if /path/imgdata.npy exists, data will just be loaded from this.

    In reality, this only needs to be loaded when adjusting gaussian.

    if forceFromImages==True, imgdata.npy will be ignored and overwritten

    Here's some demonstration timed data from my crappy laptop:

    * LOAD FROM IMAGES: 470ms (3.4MB) (actually 12-bit data)
    * SAVE TO NPY: 19ms (3.5MB) (saved as 16-bit integer data)
    * LOAD FROM NPY: 14ms
    * LOAD FROM NPY MMAP:1ms (not huge change)

    """
    timeThis()

    if os.path.exists(self.path+"/SAG/imgdata.npy") and forceFromImages==False:
      ### LOAD FROM NUMPY FILE
      #TODO: determine if memory mapping is truly faster
      self.images=np.load(self.path+"/SAG/imgdata.npy")
      timeTook("loading imgdata.npy")


    else:
      ### EXTRACT DATA FROM RAW IMAGE FILES
      L=2       #L: probably always going to be 2 channels

      print("KEYS:",self.config.keys())

      Z=self.config["imgZ"]   #Z: depth (number of sweeps or cycles)
      Y=self.config["imgY"]   #Y: space (pixels)
      X=self.config["imgX"]   #X: time (pixels)
      self.images=np.empty((L,Z,Y,X),dtype=np.int16) #THE 4D ARRAY
      debug("processing %d images (%dch, %dsw, %dx%dpx) ..."%(Z*L,L,Z,Y,X),2)

      CH1list=sorted(glob.glob(self.path+"/*CurrentSettings_Ch1*"))
      CH2list=sorted(glob.glob(self.path+"/*CurrentSettings_Ch2*"))
      for z in range(Z):
        ch1=np.rot90(pylab.imread(CH1list[z]))
        ch2=np.rot90(pylab.imread(CH2list[z]))
        if ch1.shape==ch2.shape==self.images[0,z,:,:].shape:
          #debug("loaded slice %d"%z)
          pass
        else:
          debug("FAILED slice %d"%z,2)
          ch1=ch2=np.zeros((self.images[0,z,:,:].shape))
        self.images[0,z,:,:]=ch1
        self.images[1,z,:,:]=ch2

      try:
        np.save(self.path+"/SAG/imgdata.npy",self.images)
      except:
        debug("cannot write imgdata.npy")
      timeTook("processing %d images"%(Z*L))

    # REGARDLESS IF THE IMGDATA IS NEW OR LOADED, RE-CHECK VALIDITY
    self.config["guiValidSweeps"]=[]
    for i in range(len(self.images[0])):
      if np.any(self.images[0,i]):
        self.config["guiValidSweeps"].append(i)

    if self.config["guiSelectedSweeps"]==None: #NOT YET CONFIGURED
          self.config["guiSelectedSweeps"]=self.config["guiValidSweeps"]

  ### IMAGE MANIPULATION ###

  def gauss(self,force=False):
    """apply gaussian blur to each slice of raw image.
    AUTOMATICALLY calls projection after.
    * takes 174ms
    """
    timeThis()

    ### Does a gaussian saved file already exist?
    if not 'imGauss' in self.__dict__:
      if force==False and os.path.exists(self.path+"/SAG/imggauss.npy"):
        self.imGauss=np.load(self.path+"/SAG/imggauss.npy")
        timeTook("loaded imgauss.npy")
        self.project()
        return

    ### NO GAUSSIAN SAVE EXISTS - MAKE ONE!
    # since gaussian requires math on original images, load them
    if not 'images' in vars(): self.loadImageData()
    # now perform gaussian math
    #print("XY:",self.config["guiGaussSpace"],self.config["guiGaussTime"])

    #TODO: use this
    #self.imGauss=gaussian_filter(self.images,(0,0,self.config["guiGaussSpace"],self.config["guiGaussTime"]))
    self.imGauss=np.empty(self.images.shape)
    for ch in [0,1]:
      for lyr in self.config["guiValidSweeps"]:
        self.imGauss[ch,lyr]=gaussian_filter(self.images[ch,lyr],(int(self.config["guiGaussSpace"]),int(self.config["guiGaussTime"])))

    timeTook("generated gaussian images")
    self.project(True) # PROCEED HERE AUTOMATICALLY

  def project(self,force=False):
    """create a projection image of gauss.
    MOVE ALL SLICE SELECTION TO BEFORE GAUSSIAN.
    PROJECTION IS SIMPLY PROJECTING ALL NON-NONE GAUSSIAN."""

    timeThis()

    ### Does a projection saved file already exist?
    if not 'imProj' in self.__dict__:
      if force==False and os.path.exists(self.path+"/SAG/imgproj.npy"):
        self.imProj=np.load(self.path+"/SAG/imgproj.npy")
        timeTook("loaded improj.npy")
        return

    if not 'imGauss' in self.__dict__:
      self.gauss(True)

    ### GUESS NOT, LETS MAKE ONE
    self.imProj=[np.average(self.imGauss[0,self.config["guiSelectedSweeps"]],axis=0),
                 np.average(self.imGauss[1,self.config["guiSelectedSweeps"]],axis=0)]
    self.imProj=np.array(self.imProj)

    #14.01.02-21.11: implimented 2D delta(G)/R image creation every time imProj is calculated.
    blR,blG=np.average(self.imProj[:,self.config["guiBaseline"][0]:self.config["guiBaseline"][1]],axis=(1,2))
    self.imProjDG=self.imProj[1]-blG
    self.imProjDGR=self.imProjDG/self.imProj[0]

    timeTook("projection")
    self.intensity() #AUTOMATIC
    #timeTook("projection (%d of %d)"%(len(self.config["guiSelectedSweeps"]),len(self.config["guiValidSweeps"])))

  def saveEverything(self):
    """this is done when SAVE is pressed. Saves ini, npy, and images."""
    timeThis()

    #14.01.04-18.59: fixed bug which inserted incorrection version into LS .ini files
    self.config["version"]=self.version

    self.config["modified"]=time.time()

    #14.01.05-23.57: when saving linescan configuration data, structures are organized by reverse X1 value so they are re-loaded in order vertically next time.
    #self.config["structures"]=sorted(self.config["structures"],key=itemgetter(2)) #sort by name
    self.config["structures"]=sorted(self.config["structures"],key=itemgetter(2))[::-1] #sort by X1

    debug("saving imgconf.ini")
    dictSave(self.config,self.path+"/SAG/imgconf.ini")

    debug("saving imgauss.npy")
    np.save(self.path+"/SAG/imggauss.npy",self.imGauss)

    debug("saving imgproj.npy")
    np.save(self.path+"/SAG/improj.npy",self.imProj)

    debug("saving imprev 1 and 2 .png")
    imFromLSArray(self.imProj[0],self.path+"/SAG/imprev1.png")
    imFromLSArray(self.imProj[1],self.path+"/SAG/imprev2.png")

    debug("saving scans.pkl")
    pickle.dump([self.config,self.structures],open(self.path+"/SAG/scans.pkl","wb"))

    debug("making CSV ...")
    def csvAddCol(out,header,data):
      if "\n" in out:
        out=out.split("\n")
      else:
        out=[out]
      while len(out)<len(data)+1:
        out.append("")
      out[0]+=header+","

      for i in range(len(out)-1):
        if i<len(data):
          out[i+1]+=str(data[i])+','
        else:
          out[i+1]+=(',')

      out="\n".join(out)
      return out

    for structure in self.structures:
      outpath = self.path+"/SAG/scans_"+structure+".csv"
      stuff = self.structures[structure]
      stuff.update(self.config)
      out=""
      for metric in ['G','R','dG','dGR']:
        out=csvAddCol(out,metric,stuff[metric][0])
      for metric in ['absoluteTime', 'dwellTime', 'framePeriod',
      'laserPower_0', 'linesPerFrame', 'micronsPerPixel_XAxis', 'modified',
      'msPerPx', 'opticalZoom', 'pixelsPerLine', 'pmtGain_0', 'pmtGain_1',
      'scanlinePeriod', 'timeFirst', 'timeSpan',  'umPerPx', 'version']:
        out=csvAddCol(out,metric,[stuff[metric]])
      f=open(outpath,'w')
      f.write(out)
      f.close()

    timeTook("saving everything")



  def flag(self):
    """flags this folder by creating /SAG/flagged. (an empty text file)"""
    #14.01.02-21.11: created LS.flag() function
    debug("flagging")
    f=open(self.path+"/SAG/flagged",'w')
    f.close()

  def unflag(self):
    """unflags this folder deleting ./SAG/flagged."""
    #14.01.02-21.11: created LS.unflag() function
    debug("unflagging")
    os.remove(self.path+"/SAG/flagged")

  def hide(self):
    """hide this folder by creating /SAG/hidden. (an empty text file)"""
    #14.01.13-15.39: created LS.hide() function
    debug("hiding")
    f=open(self.path+"/SAG/hidden",'w')
    f.close()

  def unhide(self):
    """unhides this folder deleting ./SAG/hidden."""
    #14.01.13-15.39: created LS.unhude() function
    debug("unhiding")
    os.remove(self.path+"/SAG/hidden")


  ### LINESCAN STRUCTURE EXTRACTION ###
  def intensity(self,force=False):
    """pull structure linescan averages out to generate self.structures{}"""

    if not "structures" in self.__dict__:
      if os.path.exists(self.path+"/SAG/scans.pkl") and force==False:
        timeThis()
        savedCFG,self.structures=pickle.load(open(self.path+"/SAG/scans.pkl","rb"))
        timeTook("loading scans.pkl")
        return

    if self.config["guiSelectedSweeps"]==[]:
      debug("NO SWEEPS SELECTED.")
      return

    if not "imGauss" in self.__dict__.keys():
      debug("intensity called without imGauss")
      self.gauss()
      return

    timeThis()
    if not type(self.config["guiBaseline"])==list or not len(self.config["guiBaseline"])==2:
      self.config["guiBaseline"]=[0,10]
      debug("INVENTING BASELINE")

  #14.01.13-15.39: updated config["guiBaseline"] code to properly range based on ms (not pixels).
    b1,b2=self.config["guiBaseline"] #IN PIXELS
    b1=b1*self.config["imgX"]/(self.config["framePeriod"]*1000.0)
    b2=b2*self.config["imgX"]/(self.config["framePeriod"]*1000.0)
    # NOW IN MS

    self.structures={}
    for s in range(len(self.config["structures"])):
      x1,x2,sName=self.config["structures"][s]
      chunk=self.imGauss[:,self.config["guiSelectedSweeps"],x1:x2,:]
      scan={} # single linescan dictionary
      scan["R"] =np.average(chunk[0],axis=1)
      scan["G"] =np.average(chunk[1],axis=1)
      scan["Rb"]=np.average(scan["R"][:,b1:b2],axis=1) #baseline average
      scan["Gb"]=np.average(scan["G"][:,b1:b2],axis=1) #baseline average
      scan["dR"]=np.empty(scan["R"].shape) # delta(Red)
      scan["dG"]=np.empty(scan["R"].shape) # delta(Green)
      scan["dGR"]=np.empty(scan["R"].shape)   # delta(Green) / (Red)
      for i in range(len(scan["dR"])):
        scan["dR"][i]=scan["R"][i]-scan["Rb"][i] # delta(Red)
        scan["dG"][i]=scan["G"][i]-scan["Gb"][i] # delta(Green)
        scan["dGR"][i]=scan["dG"][i]/scan["R"][i]   # delta(Green) / (Red)

      #14.01.05-23.57: implimented the measurement range now.
      # Is this soemthing to pickle later?
      # AVG is per per sweep, per structure.
      try:
        #average (just find the average of all the data in the region)
        #14.01.13-15.39: updated config["guiMeasure"] code to properly range Avg/Pk pixel bounds.
        a1,a2=self.config["guiMeasure"] #IN PIXELS
        a1=a1*self.config["imgX"]/(self.config["framePeriod"]*1000.0)
        a2=a2*self.config["imgX"]/(self.config["framePeriod"]*1000.0)
        #NOW IN MS
        scan["dGRavA"]=np.average(scan["dGR"][:,a1:a2])
        scan["dGRavS"]=np.std(scan["dGR"][:,a1:a2])
        #peak (first find the peak value of each sweep, then do math on the average peak)
        peaks=np.max(scan["dGR"][:,a1:a2],axis=1)
        scan["dGRpkA"]=np.average(peaks)
        scan["dGRpkS"]=np.std(peaks)
      except:
        scan["dGRav"]=123
        scan["dGRpk"]=321
      #print("AV:",scan["dGRav"])

      self.structures[sName]=scan

  ### EXTERNAL INTERACTION ###

  def configSet(self,key,val):
    """config[key]=val"""
    if not key in self.config.keys():
      debug("creating config[%s]=%s"%(key,str(val)),4)
    else:
      debug("setting config[%s]=%s"%(key,str(val)),4)
    self.config[key]=val

  ### PLOT WITH MATPLOTLIB ###

  def prettyFormat(self,title=None,grid=False,zero=True,baseline=True,
                   events=True,maxmin=True,rawPMT=False,logY=False,
                   xlabel="time (ms)", ylabel=r"($\Delta$G)/R",
                    legendSize=None,legendLoc=1,tight=True,measure=True):
    """apply things to matplotlib plot."""
    if title:
      pylab.title(title)
    if grid:
      pylab.grid()
    if zero:
      pylab.axhline(0,ls="--",alpha=.5,color="k")
    if baseline:
      try:
        b1,b2=self.config["guiBaseline"]
        pylab.axvspan(b1,b2,alpha=.1,lw=0,color='k')
      except:
        pass #bad format baseline range
    if events:
      for event in self.config["guiEvents"]:
        pylab.axvline(event,ls=":",color="r")
    if measure:
      try:
        b1,b2=self.config["guiMeasure"]
        pylab.axvspan(b1,b2,alpha=.1,lw=0,color='g')
      except:
        pass #bad format measurement range
    if maxmin:
      if rawPMT==False:
        pylab.axis([None,None,-0.5,1.5])
      else:
        pylab.axis([None,None,0,2**12])
        ylabel=r"12-bit PMT output"
    if xlabel:
      pylab.xlabel(xlabel)
    if ylabel:
      pylab.ylabel(ylabel)
    if logY:
      pylab.gca().set_yscale('log')
    if legendSize:
      pylab.legend(loc=legendLoc,prop={'size':legendSize})
    if tight:
      pylab.tight_layout()

  def prettySummary(self,save=False):
    """Generate a summary report for a linescan folder."""
    #TODO: current not utilized
    pylab.figure(figsize=(12,8))

    pylab.subplot(231)
    pylab.subplot(232)
    pylab.subplot(233)
    pylab.subplot(234)
    pylab.subplot(235)
    pylab.subplot(236)

    if save==False:
      pylab.show()
    else:
      pylab.savefig(self.path+"/SAG/pretty_summary.png")

  def prettyDGR(self):
    """dG/R data for each structure"""
    # TODO: ADD METHOD TO SHOW SOLID STDEV RANGE
    if not "structures" in self.__dict__.keys():
      self.intensity()
    timeThis()
    for structure in self.structures.keys():
      debug("processing structure "+structure)
      pylab.figure(figsize=(8,6))
      for sweep in self.structures[structure]['dGR']:
        pylab.plot(self.Xs,sweep,'b-',alpha=.2)
      pylab.plot(self.Xs,np.average(self.structures[structure]['dGR'],axis=0),'k')
      self.prettyFormat(swapDelta("(deltaG)/R - "+structure))
      pylab.savefig(self.path+"/SAG/pretty_DGR_%s.png"%structure)
      pylab.close()

    debug("processing composite")
    pylab.figure(figsize=(8,6))
    for structure in self.structures.keys():
      pylab.plot(self.Xs,np.average(self.structures[structure]['dGR'],axis=0),label=structure)
    self.prettyFormat(swapDelta("(deltaG)/R - all structures"),maxmin=False)
    pylab.legend(prop={'size':6})
    pylab.savefig(self.path+"/SAG/pretty_DGR.png")
    pylab.close()
    timeTook("pretty-DGR series")

  def prettyRAW(self):
    """raw PMT data, red and green - for each structure"""
    # TODO: ADD METHOD TO SHOW SOLID STDEV RANGE
    if not "structures" in self.__dict__.keys():
      self.intensity()
    timeThis()
    for structure in self.structures.keys():
      debug("plotting structure "+structure)
      pylab.figure(figsize=(8,6))

      for sweep in self.structures[structure]['G']:
        pylab.plot(self.Xs,sweep,'g-',alpha=.2)
      for sweep in self.structures[structure]['R']:
        pylab.plot(self.Xs,sweep,'r-',alpha=.2)
      pylab.plot(self.Xs,np.average(self.structures[structure]['G'],axis=0),'g')
      pylab.plot(self.Xs,np.average(self.structures[structure]['R'],axis=0),'r')

      self.prettyFormat(swapDelta("PMT Intensity - "+structure),rawPMT=True)
      pylab.savefig(self.path+"/SAG/pretty_RAW_%s.png"%structure)
      pylab.close()

  ### PLOT WITH SCOTTPLOT ###

  def peaksGraph(self,selectedStructure="nothing",channel=1):
    """make a plot of peaks and structures.
    intentionally no input options. dims= 100 by 200"""

    #14.01.09-18.09: if peaksGraph called, ensure projection images are available.
    if not "imProj" in self.__dict__:
      self.project()

    #14.01.03-16.39: selected structure 'background' on peak plot is now different color
    SP=ScottPlot()
    #SP.plot(np.average(LS.imProj[0],axis=1),lc='b')
    #SP.plot(np.average(LS.imProj[1],axis=1),lc='g')
    #h=LS.imProj[1].shape[1]
    spans=[]
    BL=False
    if not 'guiBaseline' in self.config.keys():
      BL=False
    if not type(self.config["guiBaseline"])==list:
      BL=False
    elif not len(self.config["guiBaseline"])==2:
      BL=False
    else:
      BL=True
      h=self.config["guiBaseline"][1] #PIXEL END OF BASELINE

    for structure in self.config["structures"]:
      color=(0,227,255,255) # default structure color
      if selectedStructure==structure[2]:
        color=(152,255,189,255) # selected structure color
      color=colorfix(color)
      spans.append([self.config["imgY"]-structure[0],
                   self.config["imgY"]-structure[1],
                   structure[2],color])
    if not BL:
      debug("no baseline defined. Inventing one of 10ms.")
      h=int(self.imProj[1].shape[1]/5)

    SP.plot(np.average(self.imProj[channel,:,:h],axis=1)[::-1],lc='d')
    SP.plot(np.average(self.imProj[channel,:,-h:],axis=1)[::-1],lc='k')
    SP.hspans=spans
    SP.renderAll(200,100,0,0,0,drawFrame=False)
    SP.imF=SP.imF.rotate(90)
    #SP.save("./test/test.png")
    return SP.imF

  def SpDGR(self):
    """plot (dG)/R for each structure and a summary."""
    SP=ScottPlot()
    SP.hspans=[self.config["guiBaseline"]]
    SP.hlines=[0]
    SP.vlines=self.config["guiEvents"]

    for structure in self.structures.keys():
      SP.dataClear()
      for sweep in self.structures[structure]['dGR']:
        SP.plot(sweep,xs=self.Xs,lc=(200,200,255))
      SP.plot(np.average(self.structures[structure]['dGR'],axis=0),xs=self.Xs,lc='b')
      SP.renderAll(800,600,title="(dG)/R - %s"%structure,xlabel="EXPERIMENT TIME (MS)")
      SP.save(self.path+"/SAG/sp_DGR_%s.png"%structure)
    SP.dataClear()
    for structure in self.structures.keys():
      SP.plot(np.average(self.structures[structure]['dGR'],axis=0),xs=self.Xs,lc='b')
    SP.renderAll(800,600,title="(dG)/R - all structures",xlabel="EXPERIMENT TIME (MS)")
    SP.save(self.path+"/SAG/sp_DGR.png")

  def SpRAW(self):
    """plot raw PMT intensity for each structure."""
    SP=ScottPlot()
    SP.hspans=[self.config["guiBaseline"]]
    for structure in self.structures.keys():
      SP.dataClear()
      for sweep in self.structures[structure]['G']:
        SP.plot(sweep,xs=self.Xs,lc=(200,255,200))
      for sweep in self.structures[structure]['R']:
        SP.plot(sweep,xs=self.Xs,lc=(255,200,200))
      SP.plot(np.average(self.structures[structure]['G'],axis=0),xs=self.Xs,lc='g')
      SP.plot(np.average(self.structures[structure]['R'],axis=0),xs=self.Xs,lc='r')
      SP.renderAll(800,600,title="PMT INTENSITY - %s"%structure,xlabel="EXPERIMENT TIME (MS)")
      SP.save(self.path+"/SAG/sp_RAW_%s.png"%structure)


  ### MISC TESTING FUNCTIONS ###

  def launch(self):
    """open explorer window in LS folder."""
    cmd='explorer.exe "'+self.path+'"'
    threading.Thread(target=execute,args=(cmd,)).start()

  def whatExists(self):
    """show all loaded variables.
    ensure stuff isn't loaded that doesn't have to be."""
    stuff=self.__dict__
    for k in stuff.keys():
      print(k,type(stuff[k]))


class ScottPlot():
  """simple high-speed plotting class by Scott Harden."""
  def __init__(self):
    """start a new ScottPlot"""
    self.dataClear()

  def getTicks(self,x1,x2,xPx,tN=5):
    """standalone function to generate a ticked axis.

    * x1 and x2 - data range
    * xPx - desired pixel width
    * tN - tick number (minimum, may more)

    """
    tS=10
    rng=float(abs(x2-x1))
    xMult=xPx/rng
    while (rng/tS)>tN: tS*=10
    while (rng/tS)<tN: tS/=10
    if (rng/tS)>tN*2: tS*=5 # NOW ITS A MULTIPLE OF 5
    ticks=[]
    x=0
    while x>min([x1,x2]): x-=tN #COMPENSATE FOR NEGATIVE
    while x<x1: x+=tS
    while x<=x2:
      px=int((x-x1)*xMult)
      #print("X:",x)
      if rng<1: s=str("%.02f"%x)
      elif rng<10: s=str("%.01f"%x)
      else: s=str("%d"%x)
      if x==0: s="0"
      ticks.append([s,px])
      x+=tS
    return ticks


  def renderGraph(self,sizePx=(600,400),fill=None):
    """each self.line is a dictionary of info on how to plot it."""
    #print("RENDERING GRAPH")

    if fill==None:
      fill=(255,255,255,255)
    else:
      fill=(255,255,255,0)


    # axis=[x1,x2,y1,y2] but leave it None for unchanged.
    #print ("DATA RANGE:",self.dataRange)
    for i in range(4):
      if not self.axis[i]==None:
        #14.01.02-21.43: fixed bug that ignored y-minimum when it is set to 0
        self.dataRange[i]=self.axis[i]

    xMult=sizePx[0]/float(self.dataRange[1]-self.dataRange[0])
    yMult=sizePx[1]/float(self.dataRange[3]-self.dataRange[2])

    xOffs=-self.dataRange[0]*yMult
    yOffs=-self.dataRange[2]*yMult

    #print("yOFFS:",yOffs)

    ### MAKE NEW CANVAS ###
    self.imGraph=Image.new("RGBA",sizePx,fill)
    self.drGraph=ImageDraw.Draw(self.imGraph)

    hlinecolor=(150,150,150,255)
    hlinecolor=(0,0,0,255)

    vlinecolor=(150,150,150,255)
    hspancolor=(255,222,222,255)
    vspancolor=(255,200,200,255)

    for vspan in self.vspans:
      y1=sizePx[1]-(vspan[0]*yMult+yOffs)
      y2=sizePx[1]-(vspan[1]*yMult+yOffs)
      self.drGraph.rectangle((0,y1,sizePx[0],y2),fill=vspancolor)

    for hspan in self.hspans:
      #print("HSPAN:",hspan)
      x1=(hspan[0]*xMult+xOffs)
      x2=(hspan[1]*xMult+xOffs)
      if len(hspan)>3:
        fill=hspan[3]
      else:
        fill=hspancolor
      self.drGraph.rectangle((x1,0,x2,sizePx[1]),fill=fill)
      if len(hspan)>2 and type(hspan[2])==str:
        #TEXT TOO!
        sX,sY=self.drGraph.textsize(hspan[2])
        x3=int((x1+x2)/2)-int(sX/2)+1
        y3=sizePx[1]-sY
        self.drGraph.text((x3,y3),hspan[2],fill=(0,0,0,255))

    for hline in self.hlines:
      hline=sizePx[1]-(hline*yMult+yOffs)
      self.drGraph.line((0,hline,sizePx[0],hline),fill=hlinecolor)

    for vline in self.vlines:
      if type(vline)==list:
        vline,vlinecolor=vline
      vline=(vline*xMult+xOffs)
      self.drGraph.line((vline,0,vline,sizePx[1]),fill=vlinecolor)

    ### PLOT EACH LINE ###
    for l in self.data:
      l['x']=l['x']*xMult+xOffs
      l['y']=l['y']*yMult+yOffs
      for i in range(len(l['y'])-1):
        x1=l['x'][i]
        x2=l['x'][i+1]
        y1=sizePx[1]-l['y'][i]
        y2=sizePx[1]-l['y'][i+1]
        self.drGraph.line((x1,y1,x2,y2),fill=l['lc'],width=l['lw'])

    ### CREATE AXIS ####

    ### SAVE, DISPLAY, or RETURN ###
    #self.imGraph.save("./test/test.png")
    return self.imGraph


  def renderAll(self,sizeX=500,sizeY=400,padLeft=45,padTop=15,
                padBot=30,title=None,xlabel=None,trans=True,
                axisX=True,axisY=True,drawFrame=True):
    """frame an image to fit the given size"""
    #print("RENDERING ALL",self.data)

    ### RENDER GRAPH
    imG=self.renderGraph((sizeX-padLeft,sizeY-padBot-padTop))
    yTicks=self.getTicks(self.dataRange[2],self.dataRange[3],sizeY-padBot-padTop)
    xTicks=self.getTicks(self.dataRange[0],self.dataRange[1],sizeX-padLeft)
    if trans:
      bgcolor=(255,255,255,0)
    else:
      bgcolor=(255,255,255,255)
    imF=Image.new("RGBA",(sizeX,sizeY),bgcolor)
    imD=ImageDraw.Draw(imF)
    imF.paste(imG,(padLeft,padTop))

    ### FRAME IT
    t,b,l,r=[padTop,sizeY-padBot,padLeft,sizeX-1]
    if drawFrame:
      imD.line((l,t,l,b),fill=(0,0,0,255))
      imD.line((r,t,r,b),fill=(0,0,0,255))
      imD.line((l,t,r,t),fill=(0,0,0,255))
      imD.line((l,b,r,b),fill=(0,0,0,255))

    ### DRAW TICKS
    if axisX:
      for tick in xTicks:
        imD.line((tick[1]+l,sizeY-padBot,tick[1]+l,sizeY-padBot+5),fill=(0,0,0,255))
        sX,sY=imD.textsize(tick[0])
        imD.text(((tick[1]+l)-int(sX/2)+1,sizeY-padBot+5),tick[0],fill=(0,0,0,255))

    if axisY:
      for tick in yTicks:
        ypos=sizeY-padBot-tick[1]-1
        imD.line((l-5,ypos,l,ypos),fill=(0,0,0,255))
        sX,sY=imD.textsize(tick[0])
        ypos=ypos-int(sY/2)
        imD.text((l-5-sX,ypos),tick[0],fill=(0,0,0,255))

    ### TITLE AND AXIS LABELS
    if title:
      sX,sY=imD.textsize(title)
      x=padLeft+int((sizeX-padLeft)/2)-sX/2
      imD.text((x,1),title,fill=(0,0,0,255))

    if xlabel:
      sX,sY=imD.textsize(xlabel)
      x=padLeft+int((sizeX-padLeft)/2)-sX/2
      imD.text((x,sizeY-sY-1),xlabel,fill=(0,0,0,255))

    self.imF=imF

  def save(self,fname,launch=False):
    if not "imF" in self.__dict__:
      self.renderAll()
    self.imF.save(fname)
    if launch:
      print(fname)
      os.system('explorer.exe "'+os.path.abspath(fname)+'"')

  def plot(self,data,label=None,xs=None,ls="-",lw=1,lc='k',alpha=None):
    """Add data to the que for plotting. input MUST be 1d or 2d numpy array."""

    data=np.atleast_2d(data) # [data] -> [[data]]

    # start filling-out plotting detail variables into a dictionary
    if label==None:
      label=len(data)
    if xs==None:
      xs=np.arange(len(data[0]))
    if not len(xs)==len(data[0]):
      print("PROBLEM! length of X is different than Y.")
      return

    if self.dataRange[0]==None or np.min(xs)<self.dataRange[0]:
      self.dataRange[0]=np.min(xs)
    if self.dataRange[1]==None or np.max(xs)>self.dataRange[1]:
      self.dataRange[1]=np.max(xs)

    if not ls in '-o.':
      print("unknown linestyle. defaulting to solid")
      ls='-'

    if lc==None:  lc=(0,0,0)
    elif lc=='k': lc=(0,0,0)
    elif lc=='b': lc=(255,0,0)
    elif lc=='lg': lc=(150,255,150)
    elif lc=='g': lc=(50,150,50)
    elif lc=='r': lc=(0,0,255)
    elif lc=='lr': lc=(150,150,255)
    elif lc=='l': lc=(220,220,220,250) #light
    elif lc=='d': lc=(150,150,150,250) #medium
    elif lc=='ll': lc=(150,255,255) #light yellow

    if alpha==None:
      alpha=255
    else:
      # assume float, where .75 is 75% opacity
      alpha=int(alpha*255)

    lc=(lc[0],lc[1],lc[2],alpha)

    for ydata in data:
      d={}
      d["y"]=ydata
      d["x"]=xs
      d["ls"]=ls
      d["lw"]=lw
      d["lc"]=lc
      self.data.append(d)

      if self.dataRange[2]==None or np.min(ydata)<self.dataRange[2]:
        self.dataRange[2]=np.min(ydata)
      if self.dataRange[3]==None or np.max(ydata)>self.dataRange[3]:
        self.dataRange[3]=np.max(ydata)


  def dataClear(self):
    """clears/initializes all data variables. Clears axis limits too.
    DOES NOT CLEAR SPANS OR LINES."""
    self.data=[]
    self.axis=[None,None,None,None]
    self.dataRange=[None,None,None,None] #Xmin,Xmax,Ymin,Ymax

    if not 'vspans' in self.__dict__.keys():
      self.vspans=[]#[[-.05,0],[.4,.5]]
    if not 'hspans' in self.__dict__.keys():
      self.hspans=[]#[[10,30],[150,200]]
    if not 'hlines' in self.__dict__.keys():
      self.hlines=[]
    if not 'vlines' in self.__dict__.keys():
      self.vlines=[]#[50,60,70]




class LineScanCompare():
  #14.01.13-22.52: added LineScaneCompare class to linescan.py
  #todo: add grouping (3 here, 3 there) and do stats
  #todo: bar graphs for avrage and area differences

  def __init__(self):
    # each scan is 4 strings: [path,structure,label,color]
    self.scans=[]

  def addScan(self,path,structure,label=None,color=None):
    if not label:
      #label=os.path.basename(path).split("-",1)[-1]
      label=None
    scan=[path,structure,label,color]
    self.scans.append(scan)

  def scanUpdate(self,path,structure,label=None,color=None):
    return

  def delScanByIndex(self,i):
    self.scans.pop(i)

  def delScan(self,path,structure=None):
    goodscans=[]
    for scan in self.scans:
      if path in scan:
        if structure in scan or structure==None:
          continue
      goodscans.append(scan)
    self.scans=goodscans

  def scan2txt(self,saveAs=False):
    txt=""
    for scan in self.scans:
      txt+="PTH=%s\nSTR=%s\nLBL=%s\nCOL=%s\n\n"%(scan[0],scan[1],scan[2],scan[3])
    txt=txt.replace("\\","/")
    if saveAs:
      f=open(saveAs,'w')
      f.write(txt)
      f.close()
    return txt

  def inthere(self,path,structure=None):
    """Determine if a path (+structure?) is already in the experiment list."""
    for scan in self.scans:
      if path in scan:
        if structure in scan or structure==None:
          return True
    return False

  def txt2scan(self,s):
    self.scans=[]
    s=s.replace("\\","/")
    for chunk in s.split("\n\n"):
      if len(chunk)<10:
        continue
      parts=chunk.split("\n") #LINESCAN
      scan=[]
      for part in parts:
        if "=" in part:
          print("PART:",part)
          ahha=part.split("=")[1]
          if ahha=="": ahha=None
          if ahha=="None": ahha=None
          if ahha=="False": ahha=False
          scan.append(ahha)
      self.scans.append(scan)
    return self.scans





if __name__ == "__main__":
  t1=time.time()
  debug("EXECUTING TEST SEUQNCE",1)
  #testPath=r"X:\Data\2P01\2013\12-2013\2013-12-12\cell1\LineScan-12122013-1314-576"
  #testPath="../demoData/LineScan-12122013-1314-578/"
  #testPath=r"C:\scott\jason\demoData\LineScan-12052013-1601-443"
  #testPath=r"\\192.168.1.152\2P-Data\2014-01-10 SH rat HPC stability\LineScan-01102014-1455-636"
  #LS=LineScan(testPath)
  #LS.project(True)

  import reports

  scans="""X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1223
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1224
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1225
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1226
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1227
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1228
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1229
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1231
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1233
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1230
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1232
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1234""".split("\n")

  LSC=LineScanCompare()
  for s in scans:
    LSC.addScan(s,'a')
  reports.reportCompareLS(LSC.scans)

  debug("COMPLETED IN %.02fs"%(time.time()-t1),1)