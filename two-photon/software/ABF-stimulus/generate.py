import numpy as np
import pylab
import time

def genSine(MAXFREQ=20,DUR=20,RATE=10000):
  print("generating sine wave ...")
  MULT=MAXFREQ/DUR/2
  xs=np.arange(0,DUR,1/RATE)                         # time points for x axis
  zi=np.sqrt(np.arange(0,(xs[-1]**2)*MULT,1)/MULT)   # zero intercept times
  ys=np.sin(2*np.pi*(xs**2)*MULT)                    # sin(2*pi*x^2*MULT)
  return [xs,ys,zi]

def genATF(xs,ys,fname='stimulus.atf'):
  print("saving ATF ...")
  out="""ATF	1.0
8	2
"AcquisitionMode=Episodic Stimulation"
"Comment="
"YTop=100"
"YBottom=-100"
"SyncTimeUnits=20"
"SweepStartTimesMS=0.000"
"SignalsExported=IN 0"
"Signals="	"IN 0"
"Time (s)"	"SCOTT STIMULUS"
"""
  for i in range(len(ys)):
    out+="%.04f\t%.04f\n"%(xs[i],ys[i])
  f=open(fname,'w')
  f.write(out)
  f.close()
  print("saved")

def graphData(xs,ys,zi,title="",fname=False):
  print("plotting data ...")
  pylab.figure(figsize=(12,5))        # create a figure of defined size
  pylab.plot(xs,ys,'b-',alpha=.5)     # plot the sine wave
  pylab.plot(zi,[ys[0]]*len(zi),'kx')     # plot the zero intercept points
  pylab.savefig("sine.png")           # save the figure
  pylab.title(title)
  pylab.tight_layout()                # minimize gray space
  if fname: pylab.savefig(fname)
  else: pylab.show()


def genChirpIC(Ih=-100,Rm=100,amp=5):
  """Create a current-clamp sine protocol.
  Ih - holding current (pA)
  Rm - membrane resistance (Mohm)
  amp - amplitude of sine (deviation from Ih potential, in mV)
  """
  pA_per_mV=1000/Rm
  print("%.02f pA requried to shift 1mV"%pA_per_mV)
  xs,ys,zi=genSine()
  ys=ys*pA_per_mV*amp+Ih
  genATF(xs,ys,'stimulus-IC.atf')
  graphData(xs,ys,zi,"Current Clamp Stimulus",'stimulus-IC.png')


def genChirpVC(Vclamp=-70,Rm=100,amp=10,graphToo=False):
  """Create a voltage-clamp sine protocol.
  Vclamp - center of clamped voltage (mV)
  Rm - membrane resistance (Mohm)
  amp - amplitude of sine (deviation Vclamp, in mV)
  """
  xs,ys,zi=genSine()
  ys=ys*amp+Vclamp
  genATF(xs,ys,'stimulus-VC.atf')
  graphData(xs,ys,zi,"Voltage Clamp Stimulus",'stimulus-VC.png')

if __name__=="__main__":
  print("\n\n### STIM-U-GATOR ### ")
  #V,Ih,Rm=-70,20,100
  V=float(input("Vclamp (mV) = "))
  Ih=float(input("Ih (pA) = "))
  Rm=float(input("Rm (Mohm) = "))
  print("\n\n### GENERATING STIMULUS ### ")
  genChirpIC(Ih,Rm)
  genChirpVC(V,Rm)
  print("\nCOMPLETE!")
  time.sleep(1)