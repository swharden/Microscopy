from PIL import Image
import numpy as np
import glob

fldr="140027735927"

x1=10
y1=108
x2=694
y2=618
#width=640
#height=480
#x2=x1+width
#y2=y1+height

def getAvg(fname):
  im=Image.open(fname)
  imW, imHh = im.size
  im=im.crop((x1,y1,x2,y2))
  data=np.asarray(im.convert("L"))
  avg=np.average(data)
  return avg

f=open(fldr+'.csv','a')
fnames=sorted(glob.glob(fldr+"/*.bmp"))
for i in range(len(fnames)):
  print('processing %d of %d'%(i+1,len(fnames)))
  f.write("%d,%f\n"%(i,getAvg(fnames[i])))
f.close()

print("DONE")