# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/2/9 2:36
# @Author       : Mark Shawn

from scipts.fuck_weibo_pc_log_in.login_via_pyqt.mainwindow import Ui_MainWindow
from drivers.driver_weibo_pc import WeiboDriver

import re
import sys
import time
import json
import vthread
import threading
from queue import Queue
from redis import StrictRedis
from settings_global import REDIS_DB_TO_USE

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QMainWindow,QWidget
from PyQt5.QtCore import pyqtSignal

import logging
fmt = "%(asctime)-15s %(levelname)s %(threadName)s %(funcName)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=fmt)

ACCOUNTS_FILE_PATH = redis'F:\MyProjects\PycharmProjects\ScrapyAnything\scipts\fuck_weibo_pc_log_in\weibo_pc_accounts\accounts4.txt'



class MyMainWindow(QMainWindow, Ui_MainWindow):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setupUi(self)
		self.submit_mutex = QtCore.QMutex()
		self.q_drivers = Queue()
		self.driver = None
		self.redis = StrictRedis(db=REDIS_DB_TO_USE)

		self.start_btn.clicked.connect(self.run)
		self.submit_btn.clicked.connect(self.slot_submit)
		self.qr_code.returnPressed.connect(self.slot_submit)

	def run(self):
		self.drivers_cnt = int(self.input_threads_cnt.text())
		self.start_btn.setEnabled(False)
		self.start_btn.setStyleSheet("background-color: RGB(170, 170, 170);")

		self.verticalLayout.removeWidget(self.qr_widget)
		self.qr_widget.setParent(None)
		self.qr_lable = QtWidgets.QLabel(self)
		self.qr_lable.setMinimumSize(400, 160)
		self.qr_lable.setAlignment(QtCore.Qt.AlignCenter)
		self.verticalLayout.insertWidget(0, self.qr_lable)

		self.loading = QtGui.QMovie('resources/loading.gif')
		self._show_img_of_loading()

		t_refresh_qr_img = threading.Thread(target=self.func_refresh_qr_img)
		t_refresh_qr_img.setDaemon(True)
		t_refresh_qr_img.start()

		@vthread.pool(self.drivers_cnt)
		def verify_account(ac_name, ac_pswd):
			print("Verifying ac_name {}".format(ac_name))
			driver = WeiboDriver(back_run=True, ac_name=ac_name, ac_pswd=ac_pswd)
			driver.input_ac_info()
			self.q_drivers.put(driver)
			logging.info("Put driver {}".format(driver.ac_name))
			while driver.service.process:
				time.sleep(2)

		self.verify_account = verify_account

		t_login = threading.Thread(target=self.func_login)
		t_login.setDaemon(True)
		t_login.start()

	def _show_img_of_loading(self):
		self.qr_lable.setMovie(self.loading)
		self.loading.start()

	def func_login(self):
		with open(ACCOUNTS_FILE_PATH, "redis") as f:
			ac_list = re.findall("(\S+)----(\S+)", f.read())
			for ac_name, ac_pswd in ac_list:
				self.verify_account(ac_name, ac_pswd)

	def func_refresh_qr_img(self):
		while True:
			if self.driver:
				time.sleep(0.5)
			elif self.q_drivers.empty():
				time.sleep(0.5)
			else:
				self.driver = self.q_drivers.get()  # type: WeiboDriver
				logging.info("Got driver {}".format(self.driver.ac_name))
				driver_imp_path = "qr_imgs/{}.png".format(str(time.time()))
				self.driver.qr_img.save(driver_imp_path)
				self.qr_lable.setPixmap(QtGui.QPixmap(driver_imp_path).scaled(400, 160))
				self.console.append("Current driver showing the img is {}".format(self.driver.ac_name))

	def func_test_target_url(self, the_driver):
		the_driver.test_target_url()
		ac_info = the_driver.get_ac_info()
		if ac_info["ac_status"] > 20:
			self.redis.hset("weibo_pc_valid", ac_info["ac_name"], json.dumps(ac_info))
		else:
			self.redis.hset("weibo_pc_invalid", ac_info["ac_name"], json.dumps(ac_info))
		the_driver.quit()


	def func_driver_input_code(self, the_driver, qr_code_value):
		self.console.append("driver {} is inputting {}".format(the_driver.ac_name, qr_code_value))
		if not the_driver.input_qrcode(qr_code_value):
			logging.info("Not input qrcode correctly")
			self.q_drivers.put(the_driver)
			logging.info("Put driver {}".format(the_driver.ac_name))
		else:
			logging.info("Inputted qrcode correctly")
			t = threading.Thread(target=self.func_test_target_url, args=(the_driver, ))
			t.setDaemon(True)
			t.start()


	def slot_submit(self):
		self.submit_mutex.lock()
		if self.driver:
			the_driver = self.driver    # type: WeiboDriver
			self.driver = None
			self.qr_lable.clear()
			qr_code_value = self.qr_code.text()
			self.qr_code.clear()
			self._show_img_of_loading()
			t = threading.Thread(target=self.func_driver_input_code, args=(the_driver, qr_code_value, ))
			t.setDaemon(True)
			t.start()
		self.submit_mutex.unlock()



if __name__ == '__main__':
	app = QApplication(sys.argv)
	my_window = MyMainWindow()
	my_window.show()
	sys.exit(app.exec_())