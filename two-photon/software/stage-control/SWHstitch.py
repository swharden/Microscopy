import serial
import time 
import os
import pyautogui
import winsound
import glob
import numpy as np
from PIL import Image, ImageMath, ImageOps
import matplotlib.pyplot as plt


CALIB_10x_sizeX=916.0 #microns visible
CALIB_20x_sizeX=455.0 #microns visible

def delAllPng(path,ftype="png"):
  for fname in glob.glob(path+"/*."+ftype):
    print "deleting",os.path.split(fname)[1],'...'
    os.remove(fname)

def temporary_addlens():
  """take a folder of TIFs with coordinates but no lens, and rename them appropriately."""
  for fname in glob.glob(r'X:\Data\2P01\2015\2015-04-29 tgot erc imaging\*.TIF'):
    a,b=os.path.split(fname)
    b=b.split("_")
    b[0]=b[0]+"_10x"
    b="_".join(b)
    fname2=os.path.join(a,b)
    os.rename(fname,fname2)

def discover_snaps():
  for fname in glob.glob(path+"/*.TIF"):
    a,b=os.path.split(fname)
    b=b.split("_")

def imLoad16(fname):
  """load a 16-bit TIF image cleanly. Return 8-bit grayscale image."""
  im = Image.open(fname)
  im = im.convert('I')
  im = ImageMath.eval('a/16',a=im)
  im = im.convert('L')
  return im

def shrink_snaps(path,divideSizeBy=10,match=".TIF",newtype=".png"):
  """given a folder of huge TIFs, compress them into memory-light smaller files."""
  delAllPng(path,"png")
  delAllPng(path,"jpg")  
  for fname in glob.glob(path+"/*.TIF"):
    if not match in fname:
      continue
    print "processing",os.path.split(fname)[1],"..."
    im=imLoad16(fname)
    im=im.resize((im.size[0]/divideSizeBy,im.size[1]/divideSizeBy))
    im.save(fname+newtype)

def find_stitches(path,match="_"):
  
  # FIND BOUNDS OF CANVAS
  xs=[]
  ys=[]
  stitches=[]
  for fname in sorted(glob.glob(path+"/*%s*.png"%match)):
    if not match in fname:
      continue
    tag,lens,x,y,z=os.path.split(fname)[1].split(".TIF")[0].split("_")
    x,y,z=float(x),float(y),float(z)
    xs.append(x)
    ys.append(y)
    stitches.append([fname,x,y,z])
  x1,x2,y1,y2=min(xs),max(xs),min(ys),max(ys)
  canvas_width_microns=abs(x2-x1)
  canvas_height_microns=abs(y2-y1)
  im=imLoad16(fname)
  micronsPerPixel=CALIB_10x_sizeX/im.size[0]
  pixelsPerMicron=1.0/micronsPerPixel
  canvas_width=int(pixelsPerMicron*canvas_width_microns)
  canvas_height=int(pixelsPerMicron*canvas_height_microns)
  
  #make the big canvas
  print "making canvas (%d,%d)"%(canvas_width,canvas_height)
  canv=Image.new("I",(canvas_width,canvas_height),0)

  #paste each image onto the canvas
  for i in range(len(stitches)):
    print "processing stitch %d of %d [%s]"%(i+1,len(stitches),os.path.split(fname)[1])
    fname,x,y,z=stitches[i]
    #im=imLoad16(fname)
    im=Image.open(fname)
    im.copy()
    pasteX=canvas_width-(x-x1)*pixelsPerMicron
    pasteY=canvas_height-(y-y1)*pixelsPerMicron
    print "pasting at",pasteX,pasteY
    canv.paste(im,(int(pasteX),int(pasteY)))
    im.close()
  return canv
  #canv.show()
  #print "micronsPerPixel =",micronsPerPixel

if __name__=="__main__":
  path=r'X:\Data\2P01\2015\2015-04-29 tgot erc imaging'
  #shrink_snaps(path,2)
  im=find_stitches(path,'143032072609')
  im = im.convert('L')
  im=ImageOps.autocontrast(im,.2)
  im.show()
  #find_stitches(path,'143032145505')
  
  print "\n\n\nDONE!"