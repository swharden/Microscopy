# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 14:37:32 2014

@author: Scott W Harden

This script contains all the code necessary to register/keygen/keycheck.
These functions are intentionally messy to keep people from modifying them.

ENCODING:
  [PCID] = 9 digit unique computer number
  [NAME] = a 9 digit number generated from the values of letters in the name
  [ENCODER] = unique distribution ID created by combining [PCID] and [NAME]
  [DATE] = a 10 digit integer (epoch time) determines the expiration date
  [ENCODED] = combining the [DATE] with the [ENCODER]. This is the key core.
  [CHECKSUM] = a creative checksum generated from [ENCODED] and [NAME].
               the algorythm can be easily modified for version control.
  [KEY] = a combination of the [ENCODED] date code and [CHECKSUM]
          tampering with the key to try to extend time violates the [CHECKSUM]
        
DECODING:
  
  1.) split your [KEY] into the [CHECKSUM] and [ENCODED] date value
  2.) make sure [CHECKSUM] rules are appropriately followed
  3.) determine your [ENCODER] from your [PCID] and [NAME]
       


"""



import os
import time

# Scott's home PC-ID: 5559-7465

secInDay=60*60*24
  
def regGetPCID(digits=9):
  x='C:/'
  for l in 'cUZP[c_R[Z`_': x+=chr(ord(l)+20)
  s=int(str(os.stat(x).st_ctime).replace(".",'')[-digits:])
  n=0
  s=str(s)
  s2=''
  for i in range(len(s)): 
    n+=ord(s[i])
  for i in range(len(s)):
    s2+=str(n+int(s[i]))[-1]
    n=(n+3)*3
  return int(s2)

def regGenCode(name,pcid=None):
  if not pcid:
    pcid=regGetPCID()
  pcid=int(pcid)
  name=name.upper().replace(" ",'')
  s=0
  for letter in name:s=s+(ord(letter)-64)**2
  c=str((s*pcid)**2)
  code=''
  for i in range(len(c)):
      code+=c[i]
      if len(code.replace("-",''))%4==0:
        code+="-"
  while not len(code.replace('-',''))%4==0:
    code+="0"
  return code

def lookUpReg():
  try:
    f=open("./registration.txt")
    raw=f.readlines()
    f.close()
    name=raw[0].strip()
    code=raw[1].strip()
  except:
    name,code=os.environ['COMPUTERNAME'],""
  return [name,code]

def regValid():
  """check if registration.txt exists and try loading it."""
  try:
    pcid=regGetPCID()
    name,code=lookUpReg()
    key=regGenCode(name,pcid)
    if key==code:return True
    else:return False
  except:return False
  
def regExpIn(x):
  """show time-formatted countdown."""
  if x==None or x==False:
    return "INVALID KEY"
  secInDay=60*60*24
  x=x-time.time()
  if x<=0:
    return "EXPIRED"
  d=int(x/(60*60*24));  x-=(60*60*24)*d
  h=int(x/(60*60));     x-=(60*60)*h
  m=int(x/60);          x-=(60)*m
  s=x
  return "%d days, %02d hours, %02d minutes, %02d seconds"%(d,h,m,s)

def regCycleBy(num,by=3,forceLength=1):
  num=str(num)
  while len(num)<forceLength:
    num="0"+num
  newnum=''
  for i in range(len(num)):
    newnum+=str((int(num[i])+by)%10)
  return newnum

def regDashify(num,every=5,sym='-'):
  out=''
  num=str(num)
  for i in range(len(num)):
    out+=num[i]
    if i%every==every-1: 
      if i<len(num)-1:
        out+=sym
  return out

def regName2Val(name,digits=5):
  nameval=0
  digits=10**digits
  for i in range(len(name)):  
    nameval+=((i+3)*3+ord(name[i])**(i+3))+i
    if nameval>digits: 
      nameval=nameval%digits
  int(str(nameval)[::-1])  
  return nameval

def regGenCode2(name,pcid=None,maxdate=None):  
  if not maxdate:
    maxdate=time.time()+10*secInDay+99
  if not pcid:
    pcid=regGetPCID()
  pcid=int(pcid)
  maxdate=int(maxdate/100)
  nameval=regName2Val(name)
  encoder=(nameval*pcid)%100000
  encoded=maxdate*encoder
  encoded=regCycleBy(encoded,3,15)
  encoded=regDashify(encoded)
  checksum=str(int(maxdate*encoder))
  checksum=checksum[:2]+checksum[-3:]
  key=encoded+"-"+checksum    
  
  print("%s (%s) = %s"%(name,pcid,key))
  
def regCheckValid2(name,key,pcid=None):
  if not pcid:
    pcid=regGetPCID()
  parts=key.split("-")
  checksum=parts[-1]  
  encoded=''
  for i in range(len(parts)-1):
    encoded+=parts[i]
  encoded=int(regCycleBy(encoded,-3))
  encoder=int(regName2Val(name)*int(pcid))%100000
  maxdate=encoded/encoder
  predictedChk=str(int(maxdate*encoder))
  predictedChk=predictedChk[:2]+predictedChk[-3:]  
  if checksum == predictedChk:
    print(time.ctime(maxdate*100))
  else:
    print("INVALID KEY")
  
def regChkSum(s,digits=5,version=3):
  s=str(s)
  checksum=0
  for i in range(len(s)):
    checksum+=i**(int(s[i])+1)+i+version
  checksum=checksum%(10**digits)
  return checksum

def regKeyGen(name,pcid=None,maxdate=None):
  encoderDigits=9
  if not pcid:
    pcid=regGetPCID(encoderDigits)
  name=regName2Val(name,encoderDigits)
  encoder=(pcid*name)%10**encoderDigits
  if not maxdate:
    maxdate=maxdate=time.time()+10*secInDay
  maxdate=int(maxdate)
  encoded=str(maxdate+encoder)
  key="%s-%05d-%s"%(encoded[:5],regChkSum(int(encoded)+name),encoded[5:])
  print(key)
  
def regKeyDecode(name,key,pcid=None):
  encoderDigits=9
  name=regName2Val(name,encoderDigits)
  keys=key.split("-")
  encodedProvided=keys[0]+keys[2]
  checksumProvided=int(keys[1])
  if not regChkSum(int(encodedProvided)+name) == checksumProvided:
    return False
  if not pcid:
    pcid=regGetPCID(encoderDigits)    
  if not regChkSum(int(encodedProvided)+name)==checksumProvided:
    return False
  encoder=(pcid*name)%10**encoderDigits
  dateval=int(encodedProvided)-encoder
  return dateval



if __name__=="__main__":
  print("PC-ID:",regDashify(regGetPCID(),4))
  name="Scott W Harden"
  print("name code:",regName2Val(name))
  #regKeyGen("Scott W Harden")
  #print(regExpIn(regKeyDecode("Scott W Harden","17941-97600-18497")))
  #print(regExpIn(regKeyDecode("Scott W Harden","17941-97600-18498")))
  #print(regExpIn(regKeyDecode("Scott W Hardeo","17941-97600-18498")))
#  print(regKeyDecode("Scott W Harden","17940-75476-18113"))
#  print(regKeyDecode("Scott W Harden","17941-75476-18112"))
#  print(regKeyDecode("Scott W Hardem","17941-75476-18113"))
#  print(regKeyDecode("Scott W Hardeo","17941-75476-18113"))
