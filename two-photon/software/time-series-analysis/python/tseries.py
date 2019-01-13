"""
When pointed to a Prarie T-Series folder, load all the images
and show the data and sharts needed to calculat dF/F.
Has support for square ROIs at the moment.
"""
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import time

def dGoR(G,R,ROIbox,drugStart=None,label="noLabel",saveDemoPic=True):
    """
    Give me the FULL original image (G then R) and an ROI box.
    This is intended to be called with small ROIs of data.
    """
    X,Y,W,H=ROIbox
    
    if saveDemoPic:
        demoPic=np.average(R,axis=0)
        demoPic[Y]=4096
        demoPic[Y+H]=4096
        demoPic[:,X]=4096
        demoPic[:,X+W]=4096
        plt.imsave(label+".png",demoPic,cmap=plt.cm.Greys_r)   
    
    G=G[:,Y:Y+H,X:X+W]
    R=R[:,Y:Y+H,X:X+W]  
    GoR=G/R
        
    
    plt.figure(figsize=(12,8))
    
    plt.subplot(221)
    plt.title('raw R and G values for "%s"'%label)
    plt.grid()
    Rav=np.array([np.average(x) for x in R]) # make 1D, no ROI
    Gav=np.array([np.average(x) for x in G]) # make 1D, no ROI
    GoRav=np.array([np.average(x) for x in GoR]) # make 1D, no ROI
    plt.plot(Rav,color='r',lw=2,alpha=.8,label="R")
    plt.plot(Gav,color='g',lw=2,alpha=.8,label="G")  
    plt.ylabel("PMT value")  
    plt.margins(0,.1)    
    
    print("\nG:",", ".join(["%.02f"%x for x in Gav]))
    print("\nR:",", ".join(["%.02f"%x for x in Rav]))
    
    if drugStart:
        plt.axvspan(0,drugStart,alpha=.1,color='k')
        
        Gb=np.average(G[:drugStart],axis=0) # G baseline        
        dG=G-Gb # delta G
        dGav=np.array([np.average(x) for x in dG]) # make 1D, no ROI    
        
        plt.subplot(222)
        plt.title("dG")
        plt.grid()
        plt.plot(dGav,color='g',lw=2,alpha=.8,label="R")
        plt.axhline(1,color='0',alpha=.5,lw=2,ls='--')
        plt.axvspan(0,drugStart,alpha=.1,color='k')
        plt.ylabel("PMT value")
        plt.margins(0,.1)
        
        plt.subplot(223)
        plt.title("G/R")
        plt.grid()
        plt.plot(GoRav,color='m',lw=2,alpha=.8,label="R")
        plt.axhline(1,color='r',alpha=.5,lw=2,ls='--')
        plt.axvspan(0,drugStart,alpha=.1,color='k')
        plt.ylabel("ratio")
        plt.margins(0,.1)
        
        plt.subplot(224)
        dGoRav=dGav/Rav*100 # in percent
        plt.title("dG/R (dF/F)")
        plt.grid()
        plt.plot(dGoRav,color='b',lw=2,alpha=.8,label="R")
        plt.axhline(1,color='r',alpha=.5,lw=2,ls='--')
        plt.axvspan(0,drugStart,alpha=.1,color='k')
        plt.ylabel("percent")
        plt.margins(0,.1)
        if max(dGoRav)<100:
            plt.axis([None,None,None,100])
        
        print("\ndG:",", ".join(["%.02f"%x for x in dGav]))
        print("\ndG/R:",", ".join(["%.02f"%x for x in dGoRav]))

        

def tSeries(path,drugStart=None,ROIbox=None,label="noLabel"):
    """Calculate dG/R from time series data.
        
    Args:
        path (str): path of a prarie view TSeries folder
        drugStart (int, optional): number of the first image beyond baseline.
            if drugStart is None, just G/R (no delta) will be reported.
        ROIbox (listm optional): if 4 int values are given, make this a
            square ROI. Units are [X,Y,W,H] like ImageJ.
            
    Returns:
        stuff
        
    """
    if drugStart:
        assert type(drugStart)==int
    assert os.path.exists(path)
    FRs=glob.glob(path+"/*Ch1*.tif")[1:] # skip the first
    FGs=glob.glob(path+"/*Ch2*.tif")[1:] # skip the first
    assert len(FRs)==len(FGs) and len(FRs)
    sizeZ=len(FRs)
    demoImg=plt.imread(FRs[0]) # demo image for referencing 
    sizeY,sizeX = demoImg.shape # determine our boundaries
    print("Found %d scans. First is size %dx%d and max/min of %d/%d"%(sizeZ,sizeX,sizeY,np.max(demoImg),np.min(demoImg)))
    
    # make empty arrays to hold data
    R=np.zeros((len(FRs),sizeY,sizeX))
    G=np.zeros((len(FRs),sizeY,sizeX))
    t1=time.clock()
    for i in range(sizeZ):
        R[i]=plt.imread(FRs[i])
        G[i]=plt.imread(FGs[i])
    print("reading data from %d TIFs took %.02f ms"%(sizeZ*2,(time.clock()-t1)*1000))
    if not ROIbox:    
        ROIbox=[0,0,sizeX,sizeY]
    dGoR(G,R,ROIbox,drugStart,label)
    plt.savefig(label+".jpg",dpi=150)
    

if __name__=="__main__":
    # the format here is Tseries path, image at first drug, box of ROI [X,Y,width,height], and label
    tSeries(r'C:\Users\scott\Documents\important\demodata\TSeries-12022016-1322-1166',20,[75,175,19,30],label="astrocyte")
    tSeries(r'C:\Users\scott\Documents\important\demodata\TSeries-12022016-1322-1166',20,[56,133,29,29],label="neuron")
    print("DONE")
    