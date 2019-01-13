import numpy as np
import pylab

### DEFINE SINE WAVE CRITERIA ###
DUR=5                   # duration of stimulus file (seconds)
MAXFREQ=20              # maximum frequency at end of duration (Hz)
RATE=1000               # sample rate in Hz
MULT=MAXFREQ/DUR/2      # multiplier (for 2*pi*x^2)

### CREATE ARRAYS ###
xs=np.arange(0,DUR,1/RATE)                         # time points for x axis
zi=np.sqrt(np.arange(0,(xs[-1]**2)*MULT,1)/MULT)   # zero intercept times
ys=np.sin(2*np.pi*(xs**2)*MULT)                    # sin(2*pi*x^2*MULT)

### SHOW DATA IN CONSOLE ###
print("Zero-intercept cross time points:\n",zi)    # show the times

### PLOT DATA ###
pylab.figure(figsize=(12,5))        # create a figure of defined size
pylab.plot(xs,ys,'b-',alpha=.5)     # plot the sine wave
pylab.plot(zi,[0]*len(zi),'kx')     # plot the zero intercept points
pylab.axis([-.1,DUR+.1,-1.1,1.1])   # zoom out a touch
pylab.tight_layout()                # minimize gray space
pylab.savefig("sine.png")           # save the figure
pylab.show()                        # present plot to the user