
import matplotlib
matplotlib.use('TkAgg') # <-- THIS MAKES IT FAST!
import glob
import Image
import numpy
import pylab
from scipy import misc
from scipy.ndimage import gaussian_filter
import skimage.io

def lookupScanTime(path_scans):
    f=open(glob.glob(path_scans+"/*.xml")[0])
    raw=f.readlines()
    f.close()
    for line in raw:
        if "scanlinePeriod" in line:
            line=line.split("value")[1].split('"')
            return float(line[1])*1000 #ms

def pic2data(impath,limit=None,sigma=1):

    ### PIL METHOD ###    
    im=Image.open(impath)
    data=numpy.array(im.getdata())
    data=numpy.reshape(data,im.size[::-1])
    data=gaussian_filter(data,sigma)    
    
    limit=[14,22]
    #limit=[10,25]
    if limit: 
        data=data[:,limit[0]:limit[1]]    

    return data

def findScans(path_scans):
    ch1=glob.glob(path_scans+"/*CurrentSettings_Ch1*.tif")
    ch2=glob.glob(path_scans+"/*CurrentSettings_Ch2*.tif")
    rep=glob.glob(path_scans+"/References/*Ch1*.tif")[0]
    ch1.sort()
    ch2.sort()
    scanTime=lookupScanTime(path_scans)
    return [ch1,ch2,rep,scanTime]

def scanReport(path_scans):
    ch1,ch2,rep,scanTime=findScans(path_scans)
    scans=None
    for i in range(len(ch1)):
        scanCH1=numpy.average(pic2data(ch1[i]),1)
        scanCH2=numpy.average(pic2data(ch2[i]),1)
        scanDFF=scanCH2/scanCH1
        if scans==None: scans=scanDFF
        else: scans=numpy.vstack((scans,scanDFF))
    times=numpy.arange(len(scans[0]))*scanTime
    pylab.grid(alpha=.3)
    for scan in scans:    
        pylab.plot(times,scan,'k-',alpha=.2)
    pylab.plot(times,numpy.average(scans,0),'b')
    pylab.xlabel("time (ms)")
    pylab.ylabel("relative intensity (G/R)")
    
    startTime=50
    pylab.axvline(startTime,color="g",linewidth=1)
    pylab.axvline(startTime+20,color="g",linewidth=1)
    pylab.axvline(startTime+40,color="g",linewidth=1)
    
    pylab.show()


#path_scans="C:/Users/SHarden/Desktop/LSDEMO2"
path_scans="X:/Data/2P01/2013/01-2013/01-09-2013-HC/LineScan-01092013-1520-004"

scanReport(path_scans)