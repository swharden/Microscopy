import ui_plot
import sys
import numpy
from PyQt4 import QtCore, QtGui, Qt
import PyQt4.Qwt5 as Qwt
import glob
import pylab
from PIL import Image
from PIL import ImageDraw
import numpy as np



p=r"C:\Users\scott\dev\data\two photon\12-2013\2013-12-16\cell02\LineScan-12162013-1854-613"
p+=r"/*Current*Ch2*"
fname=glob.glob(p)[0]
ar=pylab.imread(fname)
ar=numpy.rot90(ar)

arAvg=np.average(ar,1)

numPoints=1000
xs=numpy.arange(len(arAvg))
ys=arAvg/numpy.max(arAvg)*90

features=[]
features.append([11,16,"d1"])
features.append([30,35,"s1"])
features.append([42,47,"s2"])
features.append([65,70,"s3"])
features.append([85,90,"d2"])
selected=0

baseline=[50,100]
events=[120,140,160]

sX=200.0/ar.shape[1]
sY=200.0/ar.shape[0]

def updateOL():

    features[0][1]=uiplot.vs1.value()

    imOvr=Image.new("RGBA",(200,200),color=(0,0,0,0))
    drOvr = ImageDraw.Draw(imOvr)
    alpha=255
    trans=200
    
    #draw horizontal lines in space domain
    for feature in features: 
        drOvr.line((0,200-feature[0]*sY,200,200-feature[0]*sY), fill=(0,alpha,0,trans))
        drOvr.line((0,200-feature[1]*sY,200,200-feature[1]*sY), fill=(0,alpha,0,trans))
    
    #draw vertical lines in time domain
    drOvr.line((baseline[0]*sX,0,baseline[0]*sX,200), fill=(0,0,alpha,trans))
    drOvr.line((baseline[1]*sX,0,baseline[1]*sX,200), fill=(0,0,alpha,trans))

    for event in events:
        drOvr.line((event*sX,0,event*sX,200), fill=(alpha,0,0,trans))
    #imOvr.save("test.png", "PNG")
    
    image = QtGui.QImage(imOvr.tostring(), 200, 200, QtGui.QImage.Format_ARGB32)
    pix = QtGui.QPixmap.fromImage(image)
    uiplot.lblOL.setPixmap(pix)
    
    
    
    ### GRAPH ###
    imGraph=Image.new("RGBA",(100,200),color=(0,0,0,0))
    drGraph=ImageDraw.Draw(imGraph)    
    lasty=0

    for i in range(len(features)): 
        feature=features[i]
        c=[0,0,0]
        if i==selected: c=[255,0,0]
        drGraph.line((0,200-feature[0]*sY,100,200-feature[0]*sY), fill=(c[0],c[1],c[2],50))
        drGraph.line((0,200-feature[1]*sY,100,200-feature[1]*sY), fill=(c[0],c[1],c[2],50))
        drGraph.text((70,200-feature[1]*sY),feature[2],fill=(c[0],c[1],c[2],150))
    
    for y in range(len(ys)-1):
        drGraph.line((100-ys[y],lasty+2,100-ys[y+1],y*sY+2), fill=(c[0],c[1],c[2],255))
        lasty=y*sY
        
        
    
    image2 = QtGui.QImage(imGraph.tostring(), 100, 200, QtGui.QImage.Format_ARGB32)
    pix2 = QtGui.QPixmap.fromImage(image2)
    uiplot.lblPK.setPixmap(pix2)
    
      
def updateLS():
    
    uiplot.vs1.setMaximum(np.shape(ar)[0])
    uiplot.vs2.setMaximum(np.shape(ar)[0])
    uiplot.vs3.setMaximum(np.shape(ar)[0])
    
    #im=Image.new("L",(500,500),100)
    im=Image.fromarray((ar/16).astype(numpy.uint8))
    im=im.convert("RGBA")

    data = im.tostring()
    #image = QtGui.QImage(data, im.size[0], im.size[1], QtGui.QImage.Format_Indexed8)
    image = QtGui.QImage(data, im.size[0], im.size[1], QtGui.QImage.Format_ARGB32)
    pix = QtGui.QPixmap.fromImage(image)
    uiplot.lblLS.setPixmap(pix)

def getPos(event):
    print(dir(event))
    print(event.pos().x(),event.pos().y())

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    ### SET-UP WINDOWS
    
    # WINDOW plot
    win_plot = ui_plot.QtGui.QMainWindow()
    uiplot = ui_plot.Ui_win_plot()
    uiplot.setupUi(win_plot)
    
    #c=Qwt.QwtPlotCurve()
    #c.setData(xs, y
    #c.attach(uiplot.qwtPlot)

    #mYA,mYB,mYC = Qwt.QwtPlotMarker(),Qwt.QwtPlotMarker(),Qwt.QwtPlotMarker()
    #mX.setLabel(Qwt.QwtText('x = 2 pi'))
    #mY1A.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)

    #mY1A=Qwt.QwtPlotMarker()
    #mY1A.setLineStyle(Qwt.QwtPlotMarker.HLine)
    #mY1A.setYValue(200)
    #mY1A.attach(uiplot.qwtPlot)
    
    #uiplot.timer = QtCore.QTimer()
    #uiplot.timer.start(100.0)
    
    #win_plot.connect(uiplot.timer, QtCore.SIGNAL('timeout()'), plotSomething) 
    
    updateLS()
    uiplot.lblLS.setScaledContents(True)
    uiplot.lblPK.setScaledContents(True)
    
    uiplot.lblOL.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    uiplot.lblPK.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    
    uiplot.lblOL.mousePressEvent = getPos
    
    uiplot.vs1.valueChanged.connect(updateOL)
    uiplot.vs2.valueChanged.connect(updateOL)
    uiplot.vs3.valueChanged.connect(updateOL)



    ### DISPLAY WINDOWS
    win_plot.show()

    #WAIT UNTIL QT RETURNS EXIT CODE
    sys.exit(app.exec_())