# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_activate.ui'
#
# Created: Mon Jan 20 09:16:14 2014
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_win_activate(object):
    def setupUi(self, win_activate):
        win_activate.setObjectName(_fromUtf8("win_activate"))
        win_activate.resize(331, 146)
        self.lblProgram = QtGui.QLabel(win_activate)
        self.lblProgram.setGeometry(QtCore.QRect(9, 9, 190, 23))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.lblProgram.setFont(font)
        self.lblProgram.setObjectName(_fromUtf8("lblProgram"))
        self.frame_2 = QtGui.QFrame(win_activate)
        self.frame_2.setGeometry(QtCore.QRect(0, 35, 331, 111))
        self.frame_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.frame_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_8 = QtGui.QLabel(self.frame_2)
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_2.addWidget(self.label_8, 2, 0, 1, 1)
        self.label_9 = QtGui.QLabel(self.frame_2)
        self.label_9.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_2.addWidget(self.label_9, 3, 0, 1, 1)
        self.lblStatus = QtGui.QLabel(self.frame_2)
        self.lblStatus.setEnabled(True)
        self.lblStatus.setObjectName(_fromUtf8("lblStatus"))
        self.gridLayout_2.addWidget(self.lblStatus, 3, 1, 1, 1)
        self.leName = QtGui.QLineEdit(self.frame_2)
        self.leName.setStyleSheet(_fromUtf8("font: 8pt \"Courier\";"))
        self.leName.setObjectName(_fromUtf8("leName"))
        self.gridLayout_2.addWidget(self.leName, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.frame_2)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.leKey = QtGui.QLineEdit(self.frame_2)
        self.leKey.setStyleSheet(_fromUtf8("font: 8pt \"Courier\";\n"
"background-color: rgba(255, 0, 0, 100);"))
        self.leKey.setObjectName(_fromUtf8("leKey"))
        self.gridLayout_2.addWidget(self.leKey, 2, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.frame_2)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 1, 0, 1, 1)
        self.lePCID = QtGui.QLineEdit(self.frame_2)
        self.lePCID.setStyleSheet(_fromUtf8("font: 8pt \"Courier\";"))
        self.lePCID.setReadOnly(True)
        self.lePCID.setObjectName(_fromUtf8("lePCID"))
        self.gridLayout_2.addWidget(self.lePCID, 0, 1, 1, 1)

        self.retranslateUi(win_activate)
        QtCore.QMetaObject.connectSlotsByName(win_activate)

    def retranslateUi(self, win_activate):
        win_activate.setWindowTitle(_translate("win_activate", "Software Activation", None))
        self.lblProgram.setText(_translate("win_activate", "Software Activation", None))
        self.label_8.setText(_translate("win_activate", "Key:", None))
        self.label_9.setText(_translate("win_activate", "Status:", None))
        self.lblStatus.setText(_translate("win_activate", "registration key not found", None))
        self.leName.setText(_translate("win_activate", "Scott W Harden", None))
        self.label_3.setText(_translate("win_activate", "This PC-ID:", None))
        self.leKey.setText(_translate("win_activate", "5933-6867-5905-6000", None))
        self.label_5.setText(_translate("win_activate", "Registrant:", None))
        self.lePCID.setText(_translate("win_activate", "1234-7895", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win_activate = QtGui.QDialog()
    ui = Ui_win_activate()
    ui.setupUi(win_activate)
    win_activate.show()
    sys.exit(app.exec_())

