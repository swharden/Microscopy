import sys
import time
import os
from PyQt4.QtGui import QPixmap, QApplication
tag=str(time.time()).replace(".",'')
os.mkdir(tag)
app = QApplication(sys.argv)
for i in range(100000):
  fname=tag+'/%05d.bmp'%i
  QPixmap.grabWindow(QApplication.desktop().winId()).save(fname, 'bmp')
  time.sleep(2)
  print(i,fname)