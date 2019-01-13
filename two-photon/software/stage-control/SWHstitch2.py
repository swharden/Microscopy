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

def imLoad16(fname):
  """load a 16-bit TIF image cleanly. Return 8-bit grayscale image."""
  im = Image.open(fname)
  im = im.convert('I')
  im = ImageMath.eval('a/16',a=im)
  im = im.convert('L')
  return im

def shrink_snaps(path,divideSizeBy=10,match=".TIF",newtype=".png"):
  """given a folder of huge TIFs, compress them into memory-light smaller files."""
  #delAllPng(path,"png")
  #delAllPng(path,"jpg")  
  for fname in glob.glob(path+"/*.TIF"):
    if not match in fname:
      continue
    if not os.path.exists(fname+newtype+"_large.jpg"):   
      print "processing",os.path.split(fname)[1],"..."
      im=imLoad16(fname)
      im.save(fname+newtype+"_large.jpg")
      im=im.resize((im.size[0]/divideSizeBy,im.size[1]/divideSizeBy))
      im.save(fname+newtype)

def fname2XYZ(fname):
  fname=fname.upper()
  fname=fname.replace(".TIF","")
  fname=fname.replace(".PNG","")
  fname=fname.split("_")
  z=int(float(fname[-1]))
  y=int(float(fname[-2]))
  x=int(float(fname[-3]))
  return [-x,-y,z]
  
def determineImageSize(fname):
  im=Image.open(fname)
  x,y=im.size
  im.close()
  print "-- images appear to be [%dpx X %dpx]"%(x,y)
  return x,y
  
def determinePixelPositions(pngFolder,extension=".png"):
  images=[]
  minX=9999999999999
  minY=9999999999999
  for fname in glob.glob(pngFolder+"/*"+extension):
    x,y,z=fname2XYZ(fname)
    minX=min(minX,x)
    minY=min(minY,y)
  #print "MINIMUM: (%d, %d)"%(minX,minY)
  imgSizeX,imgSizeY=determineImageSize(fname)
  if "_10x" in fname:micronsX = CALIB_10x_sizeX
  elif "_20x" in fname:micronsX = CALIB_20x_sizeX
  else:raw_input("PROBLEM! DUNNO WHAT LENS TO USE")
  pixelsPerMicron = imgSizeX/micronsX
  for fname in glob.glob(pngFolder+"/*"+extension):
    x,y,z=fname2XYZ(fname)
    images.append([int((y-minY)*pixelsPerMicron),int((x-minX)*pixelsPerMicron),fname,imgSizeX,imgSizeY])
  images = sorted(images)
#  for i in images: #note they're in [y,x,fname,w,h]
#    print i[:-1]
  print "-- analzyed [x,y,z] for %d images"%(len(images))
  return images
  
def images2html(path):
  html='<html>'
  html+="""<head>
<style>
img {-webkit-filter: brightness(500%); }
</style>  
</head>"""
  html+='<body>\n\n'
  images=determinePixelPositions(path)
  for image in images:
    y,x,f,w,h=image
    #html+='<IMG STYLE="position:absolute; TOP:%dpx; LEFT:%dpx;" SRC="%s">\n'%(y,x,f)
    html+='<a href="%s_large.jpg">\a'%f
    html+='<IMG STYLE="position:absolute; TOP:%dpx; LEFT:%dpx; WIDTH:%dpx; HEIGHT:%dpx" SRC="%s"></a>\n\n'%(y,x,w,h,f)
  html+="\n\n</body></html>"
  f=open(path+"/map.html",'w')
  f.write(html)
  f.close()
  
def images2premosaic(path,large=False):
  #if large is a number, thats the multiple
  images=determinePixelPositions(path)
  out=""
  #for image in images:
  for i in range(len(images)):
    y,x,f,w,h=images[i]
    if large:
      f+="_large.jpg"
      x=x*large
      y=y*large
    out+="1.0\t0.0\t0.3333333333333333\t0.3333333333333333\t0.3333333333333333\t"
    out+="%d\t%d\t%d\tunfrozen\t%s"%(x,y,1,f) #the 1 is the stack slice number
    out+="\n"
    #out+=r" \n "
  #out=out.replace("\r",'')
  f=open(path+"/premosaic.txt",'wb')
  f.write(out)
  f.close()



  
  
if __name__=="__main__":
  path=r"X:\Data\2P01\2015\2015-10-28 PV imaging\CCK"
  
  #delAllPng(path,"png")
  #delAllPng(path,"jpg")    
  
  shrink_snaps(path,1)
  images2premosaic(path,1)
  #images2html(path)
  print "\n\n\nDONE!"