import os
import base64
import subprocess
def dec(s):
  return(base64.b64decode(s).decode("utf-8"))
def pandaRaw(s,h,numbers=4):
  for i in range(len(s)):h=(h<<5)+h+ord(s[i])**2;h=h%10**numbers
  while h<10**(numbers-1):h=(h<<1)+h
  return str(h)
def panda(s,ver=3):
  s=s.replace("-",'').replace(" ","").upper()
  s=[pandaRaw(s,11+ver),pandaRaw(s,13+ver),pandaRaw(s,15+ver)]
  return "-".join(s)
def getGrape(digits=5):
  x=subprocess.check_output(dec('ZG1pZGVjb2RlLmV4ZSAtcyBzeXN0ZW0tdXVpZA=='))
  x=x.decode('utf-8').replace("\n",'').replace("\r",'').replace("-",'')
  return x[-8:-4]+"-"+x[-4:]
def getRotten(digits=5):
  x='C:/'
  for l in 'cUZP[c_R[Z`_':x+=chr(ord(l)+20)
  s=int(str(os.stat(x).st_ctime).replace(".",'')[-digits:])
  return pandaRaw(str(s),3,digits)
def isLive(orange,apple,grape=None):
  if not grape:grape=getGrape()
  if apple==panda(grape+orange):return True
  else:return False
def pull():
  try:
    f=open(dec('Li9yZWdpc3RyYXRpb24udHh0'))
    raw=f.readlines();f.close()
    return [raw[0].strip(),raw[1].strip()]
  except:
    return ['','']
def push(a,b):
  try:
    f=open(dec('Li9yZWdpc3RyYXRpb24udHh0'),'w');
    f.write(a+"\n"+b);f.close()
  except:
    return