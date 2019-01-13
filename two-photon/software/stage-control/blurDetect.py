from PIL import Image
import glob
import numpy as np
import shutil

def findSharpest(fnames):
    # given a list of images, return the sharpest
    bestfname,bestsharpness=fnames[0],0
    for fname in sorted(fnames):
        im = Image.open(fname)
        im = im.resize((im.size[0]/4,im.size[1]/4))
        #im.show()
        pix = np.array(im.getdata()).reshape(im.size[0], im.size[1])
		#im.show()
        pix = pix.flatten()
        pix = pix[1:]-pix[:-1]
        sharpness = np.std(pix)
        print fname,sharpness
        if sharpness>bestsharpness:
            bestfname=fname
            bestsharpness=sharpness
    return bestfname
    
if __name__=="__main__":
    folderIn=r"C:\Users\swharden\Desktop\stack" #contains stack images
    folderOut=r"C:\Users\swharden\Desktop\jason" #output folder
    groups=[] # a group is a z stack
    for fname in glob.glob(folderIn+"/*.tif"):
        group=fname.replace(fname.split("_")[-1],"")
        if not group in groups:
            groups.append(group)
    for i in range(len(groups)):
        files = glob.glob(groups[i]+"*.tif")
        sharpest = findSharpest(files)
        shutil.copy(sharpest,folderOut)
    print "DONE"
    
    
    
    
    