# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/2/9 2:32
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------
from scipts.fuck_weibo_pc_log_in.login_via_pyqt.core import *


if __name__ == '__main__':

	app = QApplication(sys.argv)

	main_window = MyMainWindow()
	main_window.show()

	sys.exit(app.exec_())