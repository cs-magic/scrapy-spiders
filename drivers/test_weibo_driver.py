# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/2/10 18:24
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------
from drivers.driver_weibo_pc import WeiboDriver

if __name__ == '__main__':
	driver = WeiboDriver('17680288342', 'xh666666')
	driver.input_ac_info()
