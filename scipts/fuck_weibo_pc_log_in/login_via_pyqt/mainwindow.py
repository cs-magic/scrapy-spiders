# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(418, 378)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.qr_widget = QtWidgets.QWidget(self.centralwidget)
        self.qr_widget.setMinimumSize(QtCore.QSize(400, 160))
        self.qr_widget.setObjectName("qr_widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.qr_widget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.qr_widget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.groupBox_2 = QtWidgets.QGroupBox(self.qr_widget)
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName("formLayout")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.input_threads_cnt = QtWidgets.QLineEdit(self.groupBox_2)
        self.input_threads_cnt.setObjectName("input_threads_cnt")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.input_threads_cnt)
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.input_driver_path = QtWidgets.QLineEdit(self.groupBox_2)
        self.input_driver_path.setObjectName("input_driver_path")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.input_driver_path)
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.input_accounts_path = QtWidgets.QLineEdit(self.groupBox_2)
        self.input_accounts_path.setObjectName("input_accounts_path")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.input_accounts_path)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        self.verticalLayout.addWidget(self.qr_widget)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.qr_code = QtWidgets.QLineEdit(self.groupBox)
        self.qr_code.setObjectName("qr_code")
        self.horizontalLayout.addWidget(self.qr_code)
        self.submit_btn = QtWidgets.QPushButton(self.groupBox)
        self.submit_btn.setObjectName("submit_btn")
        self.horizontalLayout.addWidget(self.submit_btn)
        self.start_btn = QtWidgets.QPushButton(self.groupBox)
        self.start_btn.setStyleSheet("background-color: rgb(0, 170, 0);\n"
"color: rgb(255, 255, 255);")
        self.start_btn.setObjectName("start_btn")
        self.horizontalLayout.addWidget(self.start_btn)
        self.verticalLayout.addWidget(self.groupBox)
        self.console = QtWidgets.QTextBrowser(self.centralwidget)
        self.console.setMinimumSize(QtCore.QSize(0, 100))
        self.console.setStyleSheet("background-color: rgb(0, 0, 0);\n"
"color: rgb(255, 255, 255);")
        self.console.setObjectName("console")
        self.verticalLayout.addWidget(self.console)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 418, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "南川多线程极限打码V1.0"))
        self.label_2.setText(_translate("MainWindow", "欢迎使用南川极限打码软件！"))
        self.label_3.setText(_translate("MainWindow", "启动线程数目："))
        self.input_threads_cnt.setText(_translate("MainWindow", "5"))
        self.label_4.setText(_translate("MainWindow", "谷歌驱动路径："))
        self.input_driver_path.setText(_translate("MainWindow", "C:\\Users\\mark\\AppData\\Local\\Programs\\Python\\Python37\\Scripts\\chromedriver.exe"))
        self.label_5.setText(_translate("MainWindow", "账号配置路径："))
        self.input_accounts_path.setText(_translate("MainWindow", "F:\\MyProjects\\PycharmProjects\\FightForWuhan\\login\\accounts\\accounts.txt"))
        self.label.setText(_translate("MainWindow", "请输入验证码："))
        self.submit_btn.setText(_translate("MainWindow", "Submit"))
        self.start_btn.setText(_translate("MainWindow", "START"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

