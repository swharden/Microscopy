"""
01 - this script creates an output folder intended to be loaded into
imageJ and manually scrolled around. The commented-out code will also
make a movie if that's desired.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.animation as animation
import glob
import os

def xml_value_from_key(xml,match,matchNumber=1):
    """
    Given a huge string of XML, find the first match
    of a given a string, then go to the next value="THIS"
    and return the THIS as a string.

    if the match ends in ~2~, return the second value.
    """
    for i in range(1,10):
        if match.endswith("~%d~"%i):
            match=match.replace("~%d~"%i,'')
            matchNumber=i
    if not match in xml:
        return False
    else:
        val=xml.split(match)[1].split("value=",3)[matchNumber]
        val=val.split('"')[1]
    try:
        val=float(val)
    except:
        val=str(val)
    return val

def xml_parse_prarie(xmlFileName):
    """
    given the path to a TSeries XML file from Prarie,
    parse it and return a dictionary with the useful info.
    """
    xmlFileName=os.path.abspath(xmlFileName)
    print("parsing",xmlFileName)
    assert os.path.exists(xmlFileName)

    with open(xmlFileName) as f:
        xml=f.read()
        xml=xml.split(">")
        for i,line in enumerate(xml):
            xml[i]=line.strip()
        xml="".join(xml)
    conf={}
    for key in ['opticalZoom','objectiveLens', # physical lens
                'pixelsPerLine','linesPerFrame', # dimensions
                'dwellTime','framePeriod','scanLinePeriod' # laser pixel timing
                'laserPower', # laser settings
                'pmtGain~1~','pmtGain~2~', # PMT settings
                ]:
        conf[key.replace("~",'')]=xml_value_from_key(xml,key)
    for key in sorted(conf.keys()):
        print("XML parsing produced: [%s]=%s"%(key,conf[key]))

    times=[float(x.split('"')[1]) for x in xml.split("absoluteTime=")[1:]]
    conf["times"]=np.array(times)
    print("XML parsing produced: %d time points"%len(times))
    return conf

def inspect_Tseries_folder(folder):
    """
    Given a 2P folder right off the 2P scope, load all the image data
    and it (as two numpy arrays) plus a dictionary of XML settings (i.e.,
    magnification, scan rate, laser settings, etc.)
    """

    assert os.path.exists(folder)
    matches=glob.glob(folder+"/*.xml")
    fnamesCH1=sorted(glob.glob(folder+"/*_Ch1_*.tif"))
    fnamesCH2=sorted(glob.glob(folder+"/*_Ch2_*.tif"))
    print(matches)
    assert len(matches)==1
    conf=xml_parse_prarie(matches[0])

    sizeX=conf['pixelsPerLine']
    sizeY=conf['linesPerFrame']
    times=conf['times']
    nFrames=len(times)

    if os.path.exists(folder+"/data_G.npy"):
        print("loading data from disk...")
        G,R=np.load(folder+"/data_G.npy"),np.load(folder+"/data_R.npy")
    else:
        R,G=np.empty((nFrames,sizeY,sizeX)),np.empty((nFrames,sizeY,sizeX))
        for i,timePoint in enumerate(times):
            print("loading frame %d of %d (%.02f%%)"%(i+1,len(times),(i+1)*100.0/len(times)))
            R[i]=mpimg.imread(fnamesCH1[i])
            G[i]=mpimg.imread(fnamesCH2[i])
        print("saving data to disk...")
        np.save(folder+"/data_G.npy",G)
        np.save(folder+"/data_R.npy",R)
    print("time series data is in memory and ready to process!")

    G=G/2**12 # put on a 0-1 scale
    R=R/2**12 # put on a 0-1 scale

    G=G/R
    G=G-np.average(G,axis=0)


    print(R[0])
    fig=plt.figure(figsize=(5,5))
    im=plt.imshow(R[0],clim=(-2, 2), cmap="seismic")
    #fig=plt.gcf()
    plt.title('asdf')
    plt.ylabel('asdf')
    plt.xlabel('(G-Gavg)/R')
    plt.tight_layout()

    def update(i):
        print("encoding frame %d of %d (%.02f%%)"%(i+1,len(times),(i+1)*100.0/len(times)))
        msg='baseline'
        if times[i]>60*7+20:
            msg='GABA'
        if times[i]>60*12+20:
            msg='washoff'
        if times[i]>60*25+00:
            msg='TGOT'
        if times[i]>60*29+00:
            msg='washoff'
        im.set_data(G[i])
        plt.title("%.02f m"%(times[i]/60.0))
        plt.ylabel(msg)
        plt.savefig(r'C:\Users\swharden\Documents\temp\test\%09d.tif'%i,dpi=100)
        return im

#    debug=True
##    debug=False
#    for i in range(len(times)):
#        update(i)
#        if i>10 and debug:
#            return

    ani = animation.FuncAnimation(fig,update,len(times),interval=30)
    writer = animation.writers['ffmpeg'](fps=30)
    ani.save(r'C:\Users\swharden\Documents\temp\demo.mp4',writer=writer,dpi=300)



if __name__=="__main__":
    fldr=r'C:\Users\swharden\Documents\temp\TSeries-01112017-1536-1177'
    inspect_Tseries_folder(fldr)
    print("DONE")