import serial
import time 
import os
import pyautogui
import winsound
import glob
import numpy as np
from PIL import Image

def epochToHash(n=None):
  hashchars='0123456789abcdefghijklmnopqrstuvwxyz'
  if n==None:
    n=time.time()
  hash=''
  while n>0:
    hash = hashchars[int(n % len(hashchars))] + hash
    n = int(n / len(hashchars))
  return hash

def takePic(saveToo=True,fname=None):
  #beep(1)
  #print "HANDS OFF! Taking picture..."
  if fname==None:
    fname="frame_"+str(time.time()).replace(".","")+".tif"

  time.sleep(.5) #give it a little time to stabalize
  pyautogui.click(159,51) #camera button
  time.sleep(2) #seconds to allow for photo acquisition before moving again
  
  pyautogui.keyDown('alt')
  pyautogui.press('w')
  pyautogui.keyUp('alt')
  pyautogui.press('2')
  time.sleep(0.1)

  pyautogui.keyDown('alt')
  pyautogui.press('f')
  pyautogui.keyUp('alt')
  pyautogui.press('s')
  time.sleep(0.5)
  
  pyautogui.typewrite(fname)
  time.sleep(0.1)
  
  pyautogui.press('enter')
  time.sleep(0.1)
  
  pyautogui.keyDown('alt')
  pyautogui.press('f')
  pyautogui.keyUp('alt')
  pyautogui.press('c')
  print "picture saved as",fname
  

def takePic2(tag,lens,x,y,z):
  """higher level takePic() that saves filename as actual coordinates.
  DISREGARD LENS.
  """
  fname="%s_%05d_%05d_%05d.TIF"%(tag,12345+x,12345+y,12345+z)
  #fname = "%s_%s_%.02f_%.02f_%.02f"%(tag,lens,x,y,z)
  takePic(True,fname)
    
def hex2str(h):
  """given a hex byte string (can have spaces), return the ASCII equivalent."""
  return h.replace(" ","").strip().decode('hex')

def str2hex(s,spaces=True):
  """given an ASCII string return HEX bytes, optionally with spacers."""
  s=s.encode('hex')
  if spaces:
    s=" ".join(s[i:i+2] for i in range(0, len(s), 2))
  return s.upper()
    

class SWHstage:
  def __init__(self,lens="10x",debug=False):
    """class to take over control of the stage and track position."""
    #print "\nSWHstage is connecting to stage controller..."
    if lens=="10x":
      self.setLens10x()
    elif lens=="20x":
      self.setLens20x()
    else:
      raw_input("ERROR! LENS NOT RECOGNIZED")
    self.debug=debug   
    
  def stage_open(self):
    #print "opening COM3..."
    self.stage=serial.Serial("COM3",baudrate=115200)
    #print " -- DEVICE:",self.stage.port
    #print " -- BAUD:",self.stage.baudrate
    #print " -- DATA BITS:",self.stage.bytesize
    #print " -- STOP BITS:",self.stage.stopbits
    #print " -- PARITY:",self.stage.parity
    #print ""
    self.sendSequence(r'X:\Users_Public\Scott\Software\2p stage control\test 1\CONTROL_STARTUP.txt')
    self.updatePosition()

  def stage_close(self):
    print "SHUTTING DOWN SERIAL DEVICE"
    self.sendSequence(r'X:\Users_Public\Scott\Software\2p stage control\test 1\CONTROL_SHUTDOWN.txt')
    self.stage.close()
    
  def sendSequence(self,hexFile):
      """take a text file of hex and run it with the given serial device."""
      print "sending HEX sequence:", os.path.split(hexFile)[1]
      f=open(hexFile)
      raw=f.readlines()
      f.close()
      for line in raw:
          if len(line)<3:
              continue
          self.sendHexString(line)
      return

  def sendHexString(self,h):
      h = h.replace(" ","").strip()
      a=h.decode('hex')
      self.runCommand(a)
    
  def setLens10x(self):
    """default settings for air objective 10x lens"""
    self.lens="10x"
    self.resX=1392 #camera pixels
    self.resY=1040 #camera pixels
    self.sizeX=916 #microns visible
    self.sizeY=717 #microns visible
    self.overX=100 #overlap in microns
    self.overY=100 #overlap in microns
    self.scootX=self.sizeX-self.overX #number of microns to slide over
    self.scootY=self.sizeY-self.overY #number of microns to slide over

  def setLens20x(self):
    """default settings for air objective 20x lens"""
    self.lens="20x"
    self.resX=1392 #camera pixels
    self.resY=1040 #camera pixels
    self.sizeX=455 #microns visible
    self.sizeY=352 #microns visible
    self.overX=50 #overlap in microns
    self.overY=50 #overlap in microns
    self.scootX=self.sizeX-self.overX #number of microns to slide over
    self.scootY=self.sizeY-self.overY #number of microns to slide over

  def updatePosition(self,showIt=False):
    self.posX=float(self.runCommand("Rn 0"))
    self.posY=float(self.runCommand("Rn 1"))
    self.posZ=float(self.runCommand("Rn 2"))
    if showIt:
      print "current position: (%.02f, %.02f, %.02f)"%(self.posX,self.posY,self.posZ)

  def setToZero(self):
    """defines current stage position as (0,0,0).
    YOU SHOULD PROBABLT NEVER DO THIS"""
    self.updatePosition(True)
    print "\nsetting stage to (0,0,0)"
    print "!!!YOU SHOULD PROBABLT NEVER DO THIS!!!"
    self.runCommand("Is 0")
    self.runCommand("Is 1")
    self.runCommand("Is 2")
    self.updatePosition(True)

  def runCommand(self,cmd):
    """send a serial command (ASCII) and return the output.
    Automatically appends line break (0D) and carriage return (0A)."""
    cmd+="\r\n"
    if self.debug:
      print "-> [%s] %s"%(cmd.strip(),str2hex(cmd))
    self.stage.write(cmd)
    time.sleep(.1) # this is REALLY inelegant. use a buffer with end of line detection!
    s=self.stage.read(self.stage.inWaiting())
    s = s.replace("\n","").replace("\r","").replace("\x00","").strip()
    if self.debug:
      print "<- [%s] %s"%(s,str2hex(s))
    return s

  def moveTo1Axis(self,axis=0,position=0,respectHome=True):
    """this does the moving and waits until it's there."""
    #print "-- moving axis %d to %.02f"%(axis,position)
    position=int(position)
    self.runCommand("Ra %d %.02f"%(axis,position))
    if respectHome and axis==0: position=position
    if respectHome and axis==1: position=position
    if respectHome and axis==2: position=position
    while not int(float(self.runCommand("Rn %d"%axis)))==position:
      pass
    #print " -- ARRIVED!\n"

  def moveTo(self,goToX=None,goToY=None,goToZ=None):
    """given an (x,y,z) coordinate pair in MICRONS, move to that point.
    Don't return from this function until you're there!."""
    if goToX==None: goToX=self.posX
    if goToY==None: goToY=self.posY
    if goToZ==None: goToZ=self.posZ
    self.moveTo1Axis(0,goToX)
    self.moveTo1Axis(1,goToY)
    self.moveTo1Axis(2,goToZ)
    self.updatePosition()

def determineBounds():
  SS = SWHstage()
  SS.stage_open()
  try:
    SS.updatePosition()
    X1=SS.posX
    X2=SS.posX
    Y1=SS.posY
    Y2=SS.posY
    Z1=SS.posZ
    Z2=SS.posZ
    while True:
      SS.updatePosition()
      X1=min(X1,SS.posX)
      X2=max(X2,SS.posX)
      Y1=min(Y1,SS.posY)
      Y2=max(Y2,SS.posY)
      Z1=min(Z1,SS.posZ)
      Z2=max(Z2,SS.posZ)
      nCols = int((X2-X1)/SS.scootX)+1
      nRows = int((Y2-Y1)/SS.scootY)+1
      nZ = int(abs(Z2-Z1))+1
      print
      print "X = %.02f [%.02f,%.02f] (%d columns)"%(SS.posX,X1,X2,nCols)
      print "Y = %.02f [%.02f,%.02f] (%d rows)"%(SS.posY,Y1,Y2,nRows)
      print "Z = %.02f [%.02f,%.02f] (%d levels)"%(SS.posZ,Z1,Z2,nZ)
      print "%d total images (%d x %d x %d)" % (nCols*nRows*nZ,(SS.resX-SS.scootX)*nCols,(SS.resY-SS.scootY)*nRows,nZ)
  except:
    print "BREAKING"
  SS.stage_close()
  print "\nBOUNDS:",[X1,X2,Y1,Y2,Z1,Z2]
  return [X1,X2,Y1,Y2,Z1,Z2]

def captureZstack(bounds,lens,stepMicrons=1.0,label="Z"):
  """does not move the stage in any direction except Z."""
  X1,X2,Y1,Y2,Z1,Z2=bounds
  stamp=label#+"_"+str(time.time()).replace(".",'')[-5:]
  SS = SWHstage(lens)
  SS.stage_open()
  for zpos in np.arange(Z1,Z2+stepMicrons,stepMicrons):
    #beep(2)
    #print "MOVING TO:",SS.posX,SS.posY,zpos
    SS.moveTo(SS.posX,SS.posY,zpos)
    takePic2(stamp,SS.lens,SS.posX,SS.posY,SS.posZ)
  SS.stage_close()
  
def captureBounds(bounds,lens,label,Zs=None):
  X1,X2,Y1,Y2,Z1,Z2=bounds
  if Zs is None or Z1==Z2:
      Zs=[Z1]
  stamp=label #+""+str(time.time()).replace(".",'')
  SS = SWHstage(lens)
  SS.stage_open()
  nCols = int((X2-X1)/SS.scootX)+1
  nRows = int((Y2-Y1)/SS.scootY)+1
  picsTaken=0
  rows=range(nRows+1)
  cols=range(nCols+1)
  for row in rows[::-1]:
    for col in cols[::-1]:
      X=col*SS.scootX+X1
      Y=row*SS.scootY+Y1
      for Z in Zs:
          print "going to [row %d, col %d, Z %d] (%.02f um, %.02f um) ..."%(row,col,X,Y,Z)
          SS.moveTo(X,Y,Z)
          print "SNAP!"
          takePic2(stamp,SS.lens,SS.posX,SS.posY,SS.posZ)
      picsTaken+=1
      print "taking picture %d of %d (%.02f%% complete)"%(picsTaken,(nRows+1)*(nCols+1),picsTaken*100.0/((nRows+1)*(nCols+1)))
  print "FINISHED SCANNING!"
  SS.stage_close()
  beep()
  
def createPreMosaic(path):
  im=Image.open(glob.glob(path+"/*.tif")[0])
  imX,imY=im.size
  #SHIFTS
  #there are two shifts, one is the offset in (X,Y) for each image from left to right (X offset).
  #The other is how to start the next row (Y offset)
  offsetXX=-16 #for uneven scanning, shifting positive scoots images to the left
  offsetXY=-15 #for uneven scanning, shifting negative maxes the image tilt up from left to right
  offsetYX=10
  offsetYY=0
  overX=100/2
  overY=100/2 
  out=""
  for fname in glob.glob(path+"/*.tif"):
    tag,x,y=os.path.split(fname)[1].split(".")[0].split("_")
    x=int(x)
    y=int(y)
    xPx=x*(imX-overX)+x*offsetXX+y*offsetYX
    yPx=y*(imY-overY)+x*offsetXY+y*offsetYY
    out+="1.0	0.0	0.3333333333333333	0.3333333333333333	0.3333333333333333	%d	%d	1	unfrozen	%s\n"%(-xPx,-yPx,fname)
  f=open(path+"/PreMosaic automatic %d.txt"%(time.time()),'w')
  f.write(out)
  f.close()
  print "wrote pre-mosaic to disk."

def beep(times=5):
  #for i in range(times):
    winsound.Beep(2000,1000)
    #time.sleep(.05)

def getZ(lbl,dualChannel=False):
  print lbl
  #bounds=[-1207.75, -1207.75, -1383.75, -1383.75, -163.15, -136.5]
  bounds=determineBounds()
  beep()
  captureZstack(bounds,lblLens,stepMicrons=5,label=lbl+'_Z_R')
  beep()
  if dualChannel:
    raw_input("\nSWITCH TO OTHER CHANNEL!\npress ENTER...")
    captureZstack(bounds,lblLens,stepMicrons=5,label=lbl+'_Z_G')
    beep()  

if __name__=="__main__":
  lblDate='16.09.16'
  lblID='.050'
  lblLens='10x'
  lbl=lblDate+'.'+lblID+'_'+epochToHash()+'_'+lblLens
#  
#  #get2channelZ(lbl)16.09.09..073_odg701_10x_14619_15092_12043.TIF
  
  #bounds=determineBounds()
  bounds=[-321.5, 4475.75, -661.75, 5542.75, -481.15, -481.15]

  #bounds=[-4765.0, 4490.0, -3500.25, 1964.0, -41.37, -41.37]
  #Zs = np.arange(int(bounds[4]),int(bounds[5]),10)
  #captureBounds(bounds,lblLens,lbl,Zs)  
  captureBounds(bounds,lblLens,lbl)  
  
  
  #captureZstack(bounds,lblLens,stepMicrons=3.0,label="Z") 
  #createPreMosaic(r'E:\Data\2015\2015-10-15 imaging\TGOT\stitch')  
  print "\n\n\nDONE!" 