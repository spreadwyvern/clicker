# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'clicker_simple.ui'
#
# Created by: PyQt5 UI code generator 5.13.1


from PyQt5 import QtCore, QtGui, QtWidgets
# import custom image button
from custom_button import PicButton
# import resource_path to get the source path of file for pyinstaller to compile
from utils import resource_path


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 826)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(20, 390, 761, 391))
        self.textBrowser.setObjectName("textBrowser")
        self.recordIndicator = QtWidgets.QLabel(self.centralwidget)
        self.recordIndicator.setGeometry(QtCore.QRect(300, 330, 201, 41))
        font = QtGui.QFont()
        font.setFamily("Open Sans")
        font.setPointSize(18)
        self.recordIndicator.setFont(font)
        self.recordIndicator.setObjectName("recordIndicator")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 761, 311))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_2 = QtWidgets.QFrame(self.layoutWidget)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setFamily("Open Sans")
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.patientID = QtWidgets.QLineEdit(self.frame_2)
        self.patientID.setObjectName("patientID")
        self.horizontalLayout_2.addWidget(self.patientID)
        self.verticalLayout.addWidget(self.frame_2)
        self.frame_3 = QtWidgets.QFrame(self.layoutWidget)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setAlignment(QtCore.Qt.AlignJustify)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.startTest = PicButton(resource_path('start.png'), resource_path('start_hover.png'), resource_path('start_click.png'), self.frame_3)
        self.startTest.setObjectName("startTest")
        self.horizontalLayout_3.addWidget(self.startTest)
        self.endTest = PicButton(resource_path('stop.png'), resource_path('stop_hover.png'), resource_path('stop_click.png'), self.frame_3)
        font = QtGui.QFont()
        font.setFamily("Open Sans")
        font.setPointSize(16)
        self.endTest.setFont(font)
        self.endTest.setObjectName("endTest")
        self.horizontalLayout_3.addWidget(self.endTest)
        self.verticalLayout.addWidget(self.frame_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.recordIndicator.setText(_translate("MainWindow", "Not Recording"))
        self.label.setText(_translate("MainWindow", "Patient ID"))
        self.startTest.setText(_translate("MainWindow", "Start Test"))
        self.endTest.setText(_translate("MainWindow", "End Test"))
