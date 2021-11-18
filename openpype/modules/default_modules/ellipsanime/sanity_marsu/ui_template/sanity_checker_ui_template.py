# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\selami.boudjerda\git\smurfs\j_smurfs\python\j_smurfs\sanity\ui_template\sanity_checker_ui_template.ui'
#
# Created: Fri Jan 15 18:01:20 2021
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_sanity_checker_ui(object):
    def setupUi(self, sanity_checker_ui):
        sanity_checker_ui.setObjectName("sanity_checker_ui")
        sanity_checker_ui.resize(601, 590)
        self.verticalLayout = QtWidgets.QVBoxLayout(sanity_checker_ui)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_list = QtWidgets.QVBoxLayout()
        self.verticalLayout_list.setObjectName("verticalLayout_list")
        self.widget_label = QtWidgets.QLabel(sanity_checker_ui)
        self.widget_label.setText("")
        self.widget_label.setObjectName("widget_label")
        self.verticalLayout_list.addWidget(self.widget_label)
        self.verticalLayout.addLayout(self.verticalLayout_list)
        self.ok_pushButton = QtWidgets.QPushButton(sanity_checker_ui)
        self.ok_pushButton.setObjectName("ok_pushButton")
        self.verticalLayout.addWidget(self.ok_pushButton)

        self.retranslateUi(sanity_checker_ui)
        QtCore.QMetaObject.connectSlotsByName(sanity_checker_ui)

    def retranslateUi(self, sanity_checker_ui):
        sanity_checker_ui.setWindowTitle(QtWidgets.QApplication.translate("sanity_checker_ui", "Dialog", None, -1))
        self.ok_pushButton.setText(QtWidgets.QApplication.translate("sanity_checker_ui", "OK", None, -1))

