import sys
import time
import os
import glob

import sys
import time
import os
import glob

x,y=[190,230]
width=240 #must be a multiple of 2
height=240 #must be a multiple of 2
path1="./139886085877"


### DONT EDIT BELOW THIS LINE ###
path2=path1+"-cropped"
if not os.path.exists(path2):
  os.mkdir(path2)
fnames=sorted(glob.glob(path1+"/*.bmp"))
for i in range(len(fnames)):
  # size of box, then start pixel
  if os.path.exists(fnames[i].replace(path1,path2)+".png" ):
    continue
  cmd="""convert %s -crop %dx%d+%d+%d \
          -stroke "#000C" -strokewidth 2 -annotate +X1+Y1 "STR2" \
          -stroke  none   -fill white    -annotate +X1+Y1 "STR2" \
          -draw "line 10,15 72,15" \
          -stroke "#000C" -strokewidth 2 -annotate +X1+Y2 "STR1" \
          -stroke  none   -fill white    -annotate +X1+Y2 "STR1" \
          -fill white -stroke black  -draw "line 10,15 72,15" \
          %s.jpg""" %(fnames[i],width,height,x,y,fnames[i].replace(path1,path2))
  secs=i*2 #for 1/2 fps
  mins=int(secs/60)
  secs-=mins*+60
  stamp="%02dm:%02ds"%(mins,secs)
  print("processing %d of %d (%.02f%%) timestamp: %s"%(i,len(fnames),100.0*i/len(fnames),stamp))
  cmd=cmd.replace("STR1","    20 uM").replace("STR2","    "+stamp)
  cmd=cmd.replace("X1",str(x)).replace("Y1",(str(y+10))).replace("Y2",str(y+30))
  os.system(cmd)

print("DONE")
