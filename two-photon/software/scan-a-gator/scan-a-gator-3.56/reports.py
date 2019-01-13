import linescan
from PIL import Image
import numpy as np
import pylab
import os
import glob

#14.01.09-18.09: created report.py to assemble individual folder report functions
#14.01.13-15.39: added raw (where every sweep is shown) average plots for each structure.
#14.01.13-15.39: added colormap to color-code sweep time

def reportCompareLS(scans,CH="dGR",show=True):
  if len(scans)==0: return
  pylab.figure(figsize=(10,8))
  for i in range(len(scans)):
    scan=scans[i]
    path,stName,label,color=scan
    if type(color)==str:
      print("setting color to",color)
    else:
      c=float(i)/(len(scans)+1)
      color=pylab.cm.jet(c)
    LS=linescan.LineScan(path)
    LS.project()
    if not label:
      label=path.split("-")[-1]
      label+=" ("+LS.config["timeFirst"].split(" ",1)[1]+")"
    for structure in LS.structures:
      if not stName==structure:
        continue
      for y in range(len(LS.structures[structure][CH])):
        pylab.plot(LS.Xs,LS.structures[structure][CH][y],color=color,alpha=.2)
      pylab.plot(LS.Xs,np.average(LS.structures[structure][CH],axis=0),label=label,color=color,alpha=1,lw=2)
  if CH=='dGR':
    LS.prettyFormat(r"Average ($\Delta$G)/R",legendSize=12,maxmin=False)
  else:
    LS.prettyFormat(r"Raw PMT Intensity [CH=%s]"%CH,legendSize=12,rawPMT=True,maxmin=False)
  if show:
    pylab.show()

def reportSummaryLS(path):

  out="""<html>
<body>
<div align="center">
<h1>%s</h1><br>
<img src="ref.jpg">
<hr>
  """%(os.path.basename(path))

  outpath=path+"/SAG/html/"
  if not os.path.exists(outpath):
    os.makedirs(outpath)

  LS=linescan.LineScan(path)
  LS.project() #force all projections

  # reference image
  im=Image.open(path+"/References/"+LS.config["ref"])
  im.save(outpath+"ref.jpg")

  # merged image
  data=np.zeros((LS.imProj.shape[1],LS.imProj.shape[2],3))
  data[:,:,0]=linescan.npContrast(LS.imProj[0,:,:]) #RED
  data[:,:,1]=linescan.npContrast(LS.imProj[1,:,:]) #GREEN
  data[:,:,2]=linescan.npContrast(LS.imProj[0,:,:]) #BLUE
  imRG=Image.fromarray(data.astype(np.uint8),mode="RGB")
  linescan.imSave(imRG,outpath+'/all_RG.png',size=(None,200))
  linescan.imSave(linescan.imFromNumpyArray(data[:,:,0]),outpath+'all_R.png',size=(None,200))
  linescan.imSave(linescan.imFromNumpyArray(data[:,:,1]),outpath+'all_G.png',size=(None,200))
  out+='<img src="all_RG.png"><hr>'
  out+='<img src="all_Rp.png">'
  out+='<img src="all_R.png"> '
  out+='<img src="all_Gp.png">'
  out+='<img src="all_G.png"><hr>'

  # indidual channel gray projection
  LS.peaksGraph(channel=0).save(outpath+'all_Rp.png')
  LS.peaksGraph(channel=1).save(outpath+'all_Gp.png')


  #dict_keys(['Gb', 'G', 'dGRavS', 'R', 'dGRpkS', 'dGRavA', 'dR',
              #'dGR', 'dG', 'dGRpkA', 'Rb'])

  # python graph of average line for each structure
  pylab.figure(figsize=(8,6))
  for structure in LS.structures:
    pylab.plot(LS.Xs,np.average(LS.structures[structure]["dGR"],axis=0),label=structure)
  LS.prettyFormat("All Structures",legendSize=10)
  pylab.savefig(outpath+'plot_all.png',dpi=80)
  pylab.close()
  out+='<img src="plot_all.png"><hr>'

  # image for each structure
  for structure in LS.structures:

    out+="""
    <h2>Structure: %STR<br>SWEEPS<br>
    <img src="st_dGRav_%STR.png"> <img src="st_dGRraw_%STR.png"><br>
    <img src="st_Rav_%STR.png"> <img src="st_Gav_%STR.png"><br>
    <img src="st_Rraw_%STR.png"> <img src="st_Graw_%STR.png"><br>
    <hr>
    """.replace("%STR",structure)



    #DGR AV
    pylab.figure(figsize=(8,6))
    for i in range(LS.structures[structure]["dGR"].shape[0]):
      pylab.plot(LS.Xs,LS.structures[structure]["dGR"][i],'b-',alpha=.2)
    pylab.plot(LS.Xs,np.average(LS.structures[structure]["dGR"],axis=0),'b-',lw=2)
    pylab.title(r"Average ($\Delta$G)/R")
    pylab.xlabel("Experiment time (ms)")
    pylab.ylabel(r"($\Delta$G)/R")
    pylab.savefig(outpath+'st_dGRav_'+structure,dpi=60)
    pylab.close()

    #DGR RAW
    #14.01.24-14.51: fixed issue with colorbar having n-1 colors
    #14.01.24-14.51: rather than show time points as seconds, show it sa sweep number
    #timePoints=np.arange(LS.structures[structure]["dGR"].shape[0]+1)/LS.structures[structure]["R"].shape[0]
    timePoints=np.arange(LS.structures[structure]["dGR"].shape[0]+1)
    if "absoluteTime" in LS.config.keys():
      timePoints=timePoints*LS.config["absoluteTime"]
    CLR=pylab.contourf([timePoints],timePoints,cmap=pylab.cm.rainbow)
    pylab.clf() #clear the colorbar plot
    pylab.figure(figsize=(8,6))
    for i in range(LS.structures[structure]["dGR"].shape[0]):
      c=float(i)/LS.structures[structure]["dGR"].shape[0]
      pylab.plot(LS.Xs,LS.structures[structure]["dGR"][i],alpha=.8,color=pylab.cm.rainbow(c))
    pylab.title(r"($\Delta$G)/R by Sweep")
    pylab.xlabel("Experiment time (ms)")
    pylab.ylabel(r"($\Delta$G)/R")
    pylab.colorbar(CLR)
    pylab.savefig(outpath+'st_dGRraw_'+structure,dpi=60)
    pylab.close()


    #RED RAW
    CLR=pylab.contourf([timePoints],timePoints,cmap=pylab.cm.rainbow)
    pylab.clf() #clear the colorbar plot
    pylab.figure(figsize=(8,6))
    for i in range(LS.structures[structure]["R"].shape[0]):
      c=float(i)/LS.structures[structure]["R"].shape[0]
      pylab.plot(LS.Xs,LS.structures[structure]["R"][i],color=pylab.cm.rainbow(c))
    LS.prettyFormat("CH1 (red) PMT Value",rawPMT=True,baseline=False)
    pylab.colorbar(CLR)
    pylab.savefig(outpath+'st_Rraw_'+structure,dpi=60)
    pylab.close()

    #RED AV
    pylab.figure(figsize=(8,6))
    for i in range(LS.structures[structure]["R"].shape[0]):
      pylab.plot(LS.Xs,LS.structures[structure]["R"][i],'r:',alpha=.8)
    pylab.plot(LS.Xs,np.average(LS.structures[structure]["R"],axis=0),'r-')
    LS.prettyFormat("CH1 (red) PMT Value",rawPMT=True,baseline=False)
    pylab.savefig(outpath+'st_Rav_'+structure,dpi=60)
    pylab.close()


    #GREEN RAW
    CLR=pylab.contourf([timePoints],timePoints,cmap=pylab.cm.rainbow)
    pylab.clf() #clear the colorbar plot
    pylab.figure(figsize=(8,6))
    for i in range(LS.structures[structure]["G"].shape[0]):
      c=float(i)/LS.structures[structure]["G"].shape[0]
      pylab.plot(LS.Xs,LS.structures[structure]["G"][i],color=pylab.cm.rainbow(c))
    pylab.plot(LS.Xs,np.average(LS.structures[structure]["G"],axis=0),'g-')
    LS.prettyFormat("CH2 (green) PMT Value",rawPMT=True,baseline=False)
    pylab.colorbar(CLR)
    pylab.savefig(outpath+'st_Graw_'+structure,dpi=60)
    pylab.close()

    #GREEN AV
    pylab.figure(figsize=(8,6))
    for i in range(LS.structures[structure]["G"].shape[0]):
      pylab.plot(LS.Xs,LS.structures[structure]["G"][i],'g:',alpha=.8)
    pylab.plot(LS.Xs,np.average(LS.structures[structure]["G"],axis=0),'g-')
    LS.prettyFormat("CH2 (green) PMT Value",rawPMT=True,baseline=False)
    pylab.savefig(outpath+'st_Gav_'+structure,dpi=60)
    pylab.close()

    #stackable dGR
    #for i in range(LS.structures[structure]["dGR"].shape[0]):
      #data=LS.structures[structure]["dGR"][i],

    for s in LS.config["structures"]:
      if s[2]==structure:
        x1,x2,sName=s
        h=int(x2-x1)

    out2="<table>"
    chunk=LS.imGauss[:,LS.config["guiSelectedSweeps"],x1:x2,:]
    chunk=chunk[1] #GREEN ONLY
    chunk=linescan.npContrast(chunk) #do this only once, before splitting things
    for y in range(chunk.shape[0]):
      fname="st_G_swp_%03d_%s.png"%(y,structure)
      linescan.imFromNumpyArray(chunk[y,:,:],outpath+fname)
      out2+='<tr><td>%d</td><td><img src="%s" height="30" width="400"></td></tr>'%(y,fname)
    out2+="</table>"

    out=out.replace("SWEEPS",out2)


  out+="</div><hr>"
  out+="<br>"*5
  out+="<code>"+linescan.dictSave(LS.config).replace("\n",'<br>')+"</code>"

  out+="</body></html>"

  f=open(outpath+"index.html",'w')
  f.write(out)
  f.close()

  print("DONE")


if __name__=="__main__":
  #testPath=r'X:\Data\2P01\2014\2014-01\2014-01-11 SH rat HPC stability\LineScan-01112014-1240-728'
  #reportSummaryLS(testPath)
  scans="""X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1223
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1224
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1225
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1226
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1227
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1228
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1229
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1231
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1233
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1230
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1232
X:/Data/2P01/2014/2014-01/2014-01-29 rat pup/LineScan-01292014-1431-1234""".split("\n")
  print(scans)
  reportCompareLS(scans)
