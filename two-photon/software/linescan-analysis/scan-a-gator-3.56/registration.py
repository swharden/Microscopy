import ui_activate
import default
import sys
from experiment import *
import threading
from PyQt4 import QtCore, QtGui
import webbrowser

#14.01.11-17.31: created standalone activation screen
#14.01.13-15.39: modification of PC-ID, now fully hardware based


def activator_isActivated():
  """call if correct key is entered."""
  uiactivate.leKey.setStyleSheet('background-color: rgb(0, 170, 127);')
  uiactivate.leKey.setReadOnly(True)
  uiactivate.leName.setEnabled(False)
  uiactivate.lblStatus.setText("This software has been successfully activated.")
  print("verified. locked.")

def activator_notActivated(reason="dunno"):
  """call if incorrect key is entered."""
  uiactivate.leKey.setStyleSheet('background-color: rgb(255, 85, 127);')
  uiactivate.lblStatus.setText(reason)
  print("failed.")

def activator_checkKey():
  """call every time key is modified."""
  if uiactivate.leKey.text()=="":
    activator_notActivated("missing registration key")
  elif uiactivate.leName.text()=="":
    activator_notActivated("missing registrant name")
  elif not isLive(uiactivate.leName.text(),uiactivate.leKey.text()):
    activator_notActivated("invalid registration key")
  else:
    activator_isActivated()
    return True
  return False

def activator_update():
  """call this when user changes fields. Will saveKey() if entered right."""
  if activator_checkKey():
    activator_saveKey()

def activator_saveKey():
  """correct key has been entered, save it, and call isActivated()."""
  print("SAVING ACTIVATION CODE")
  f=open("registration.txt",'w')
  f.write(uiactivate.leName.text()+"\n"+uiactivate.leKey.text())
  f.close()
  msg="Please restart this software completely."
  QtGui.QMessageBox.about(None,"SUCCESSFUL REGISTRATION",msg)

def activator_alone():
  global win_activate
  global uiactivate
  win_activate = ui_activate.QtGui.QMainWindow()
  uiactivate = ui_activate.Ui_win_activate()
  uiactivate.setupUi(win_activate)
  try:
    name,code=default.lookUpReg()
    uiactivate.leName.setText(name)
    uiactivate.leKey.setText(code)
  except:
    uiactivate.leName.setText(os.environ['COMPUTERNAME'])
    uiactivate.leKey.setText("")
  activator_checkKey()
  uiactivate.lePCID.setText(getGrape())
  uiactivate.leName.textChanged.connect(activator_update)
  uiactivate.leKey.textChanged.connect(activator_update)
  win_activate.show()

def activator_execute(cmd):
  os.system('"'+cmd+'"')  
  
def activator_website():  
  n=uiactivate.leName.text()
  p=uiactivate.lePCID.text()
  #14.01.13-22.52: registration box now launches registration website
  url="http://www.SWHarden.com/version/reg/index.php?p=%s&n=%s&x=SAG"%(p,n)
  webbrowser.open(url)

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  activator_alone()
  sys.exit(app.exec_())