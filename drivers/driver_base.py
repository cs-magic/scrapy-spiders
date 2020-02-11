# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/2/9 1:23
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from .settings_drivers import *
from common import Cookie

class DriverBaseChrome(webdriver.Chrome):

	def __init__(self, back_run=None, show_img=None, *args, **kwargs):
		options = webdriver.ChromeOptions()
		preferences   = {
			"profile.default_content_setting_values":
				{
					"notifications": 2,                 # 屏蔽浏览器通知
				}
		}
		options.add_experimental_option("prefs", preferences)

		background_run = back_run if back_run is not None else BACKGROUND_RUN_ENABLED
		if background_run:
			options.add_argument("--headless")              # 后台运行
			options.add_argument("--no-sandbox")

		show_img = show_img if show_img is not None else GPU_ENABLED
		if not show_img:
			options.add_argument("--disable-gpu")

		super().__init__(*args, options=options, **kwargs)

		self.implicitly_wait(IMPLICIT_WAIT_TIME)
		self.wait = WebDriverWait(self, WEBDRIVER_WAIT_TIME)

		logger_driver.debug("Initialized driver.")

	def get_cookie_str(self) -> str:
		return Cookie.cookie_dict2str(Cookie.cookie_jar2dict(self.get_cookies()))

	def robust_input(self, ele: WebElement, text: str,
	                 use_paste=False, ensure_value=False) -> bool:
		ele.clear()
		if use_paste:
			import os
			os.system("echo {}|clip".format(text))
			ele.send_keys(Keys.CONTROL, "v")
		else:
			ele.send_keys(text)

		if ensure_value:
			if ele.get_attribute("value") == text:
				return True
			else:
				logger_driver.warning({"target input": text, "inputted": ele.get_attribute("value")})
				return False
		else:
			return True
