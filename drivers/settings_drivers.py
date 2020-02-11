# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/2/9 1:29
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------

import logging
logger_driver = logging.getLogger("DRIVER")
logger_driver.setLevel(logging.DEBUG)


BACKGROUND_RUN_ENABLED      = False         # 测试环境下开着界面方便调试
GPU_ENABLED                 = True          # 图片渲染还是要打开的
IMPLICIT_WAIT_TIME          = 10
PAGE_LODE_TIME              = 10
WEBDRIVER_WAIT_TIME         = 20