import glob
import time
import os

def howIndent(s):
  """returs indentation depth."""
  s=s.replace("\t"," "*2)
  indent=0
  while len(s) and s[0]==" ":
    indent+=1
    s=s[1:]
  return indent

def destructivelyReplace(fname):
  """Fiven a file, rename the #change lines appropriately.
  Append each change to changes.txt in that folder.
  Format is [fname,stamp,line,func,desc]

  #CHANGE: some description
   ... becomes ...
  #13.12.24-15.43: some description

   REQUIRES that indentation be based on SPACES ONLY

  APPENDS changelog.csv
  OVERWRITES changelog.html

  The big idea is that once a #change is read, it's reformatted so it's not
  seen again. That way it can be later removed from the code, but its
  presence was stored in changelog.csv.

  """
  stamp=time.strftime("%y.%m.%d-%H.%M",time.localtime())
  stamp2=time.strftime("%y-%m-%d",time.localtime())
  #print("PROCESSING:",fname)
  f=open(fname)
  raw=f.read().split("\n")
  f.close()

  out=""

  func="OUTSIDE"
  titles=["??????"]
  lastLevel=0

  for i in range(len(raw)):
    line=raw[i]
    iTitle=None
    if line.lstrip()[:5]=="class":
      iTitle=line.split("class ")[1].split(":")[0]+""
    elif line.lstrip()[:3]=="def":
      iTitle=line.split("def ")[1].split("(")[0]+"()"

    if iTitle:
      level=howIndent(line)
      if level<lastLevel:
        titles.pop(-1)
      elif level>lastLevel:
        titles.append(">")
      titles[-1]=iTitle
      lastLevel=level
      func="/".join(titles)

    if raw[i][:17]=="versionSecondary=":
      print(raw[i])
      vrs=eval(raw[i].split("=")[1].split(" ")[0])+1
      raw[i]="versionSecondary=%d #modified by script only"%vrs
      

    if raw[i][:17]=="versionDate=":
      raw[i]="versionDate=%s #modified by script only"%stamp2

    if "#change:" in line or "#CHANGE:" in line:
      line=line.replace("change","CHANGE",1)
      com=line.split("#CHANGE: ")[1]
      line=line.replace("#CHANGE","#"+stamp)
      raw[i]=line
      out+="%s,%s,%d,%s,%s\n"%(stamp,os.path.basename(fname),i,func,com)

  f=open(fname,'w')
  f.write("\n".join(raw))
  f.close()

  if len(out)>3:
    print(fname,"WRITING OUTPUT")
    f=open("changelog.csv",'a')
    f.write(out)
    f.close()
#  else:
#    print(fname,"NO CHANGES FOUND")

def changelogCSV2HTML(fin='./changelog.csv',fout='./changelog.html'):
  """convert a CSV formatted changelog to pretty HTML format."""
  f=open(fin)
  raw=f.readlines()
  f.close()
  for i in range(len(raw)):
    if "," in raw[i]:
      raw[i]=raw[i].split(",",4)
  out="""<html>

<style>

body {
  font-family:Arial, Helvetica, sans-serif;
  font-size:8px;
  }

#datatable{
  border: 1px solid #000;
  font-size: 12px;
  width: 800px;
}

td{
  //border: 1px solid #000;
  //padding-left:5px;
  //padding-right:5px;
  padding:5px;
}

.nopad{

}

#row0{
  background: #d9f2ff;
}

#row1{
  background: #e7f7ff;
}

#tabhead1{
  background: #255975;
  color: #FFF;
  font-weight: bold;
  //font-size: 16px;
}

#tabhead2{
  background: #255975;
  color: #FFF;
  font-weight: bold;
  //text-decoration: underline;
}

.cmptr{
  font-family: "Lucida Console", Monaco, monospace
}

</style>

<body><div align="center">
<h1>Changelog</h1>"""



  #0: 14.01.02-21.11
  #1: EDITOR.py
  #2: 692
  #3: flagClicked()
  #4: made the FLAG button do something

  lastDate=""
  out+="<table>"
  for item in raw[::-1]:
    if not lastDate==item[0]:
      i=0
      lastDate=item[0]
      out+="</table>"
      #out+="<h3>%s</h3>"%item[0]
      out+='<br><br><table cellspacing="0" id="datatable">'
      out+='<tr id="tabhead1"><td class="nopad" colspan="4"><b>%s</b></td></tr>'%item[0].replace(".","/",2).replace("-"," ").replace(".",":")
      out+='<tr id="tabhead2"><td class="nopad" width="200">File</td><td width="50">line</td><td width="200">function</td><td>description</td></td></tr>'
    i+=1
    out+='<tr id="row%d""><td class="cmptr">%s</td><td class="cmptr">[%s]</td><td class="cmptr">%s</td><td>%s</td></td></tr>'%(i%2,item[1],item[2],item[3],item[4])
  out+="</table>"

  out+="</div></body></html>"
  f=open(fout,'w')
  f.write(out)
  f.close()

def updateCangelog():
  """update the changelog for everything in ../ except this folder."""
  for fname in glob.glob("../*.py"):
  #for fname in ["../linescan.py"]:
    destructivelyReplace(fname)
    changelogCSV2HTML()

if __name__ == "__main__":
  updateCangelog()
  print("COMPLETE")
  input()