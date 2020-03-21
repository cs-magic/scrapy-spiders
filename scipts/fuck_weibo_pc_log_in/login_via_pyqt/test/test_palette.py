# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/2/1 18:56
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------


from PyQt5 import QtGui, QtWidgets, QtCore

import sys
import os


app = QtWidgets.QApplication(sys.argv)

window = QtWidgets.QMainWindow()

widget = QtWidgets.QWidget(window)
widget.setAutoFillBackground(True)
palette = QtGui.QPalette()
qr_img_path = redis'F:\MyProjects\PycharmProjects\FightForWuhan\scrapy_weibo\login\login_via_pyqt\temp\1580506793.6206954.png'
palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(QtGui.QPixmap(qr_img_path).scaled(400, 160)))
widget.setPalette(palette)

window.show()

sys.exit(app.exec_())