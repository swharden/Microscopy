import ui_st
import ui_activate

import sys

from PyQt4 import QtCore, QtGui

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    ### SET-UP WINDOWS
    
    # WINDOW activate
    win_activate = ui_activate.QtGui.QMainWindow()
    uiactivate = ui_activate.Ui_win_activate()
    uiactivate.setupUi(win_activate)

    # WINDOW st
    win_st = ui_st.QtGui.QMainWindow()
    uist = ui_st.Ui_win_st()
    uist.setupUi(win_st)

    ### DISPLAY WINDOWS
    win_activate.show()
    win_st.show()

    #WAIT UNTIL QT RETURNS EXIT CODE
    sys.exit(app.exec_())