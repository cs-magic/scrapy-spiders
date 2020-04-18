# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/2/9 1:52
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------

from .driver_base import *
from .settings_drivers import logger_driver
from selenium.common.exceptions import TimeoutException

import time
from PIL import Image
from io import BytesIO


class WeiboDriver(DriverBaseChrome):

	WEIBO_LOGIN_PC_URL = "https://weibo.com"
	TEST_ACCOUNT_URL = 'https://s.weibo.com/weibo?q=%E5%8F%A3%E7%BD%A9&scope=ori&suball=1&timescope=custom:2020-01-01:2020-02-01&Refer=g'

	class ACCOUNT_STATUS:
		UNCHECKED       = 0
		FAIL_TO_LOG_IN  = 10
		PASS_LOG_IN     = 11
		FAIL_TO_TEST    = 20
		PASS_TEST_URL   = 21

	def __init__(self, ac_name, ac_pswd, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ele_login_popup = None
		self.ac_name = ac_name
		self.ac_pswd = ac_pswd
		self.ac_status  = self.ACCOUNT_STATUS.UNCHECKED

	@property
	def qr_img(self) -> Image:
		try:
			ele_qr_img = self.wait.until(EC.element_to_be_clickable(
				(By.CSS_SELECTOR, ".layer_login_register_v2 .code img"))) # type: WebElement
		except TimeoutException as e:
			logger_driver.warning("Timeout and Auto Quit！")
			self.quit()
		else:
			# self._qr_src = self.qr_ele.get_attribute("src")
			return Image.open(BytesIO(ele_qr_img.screenshot_as_png))

	def input_ac_info(self):
		# 当当前页面非微博登录首页时，则访问
		# 主要用于二次登录，实际并无判断的必要
		if not self.current_url == self.WEIBO_LOGIN_PC_URL:
			self.get(self.WEIBO_LOGIN_PC_URL)
			logger_driver.debug("Visited the home page of weibo.")

		# 点击首页的登录按钮，打开其V2的登录框
		self.wait.until(EC.element_to_be_clickable(
			(By.LINK_TEXT, "登录")
		)).click()
		self.ele_login_popup = ele_login_popup = \
			self.wait.until(EC.presence_of_element_located(
			(By.CLASS_NAME, "layer_login_register_v2")
		))  # type: WebElement
		logger_driver.debug("Popped up the login layer, and auto inputting the name and the pswd now.")
		ele_login_name = ele_login_popup.find_element_by_name("username")
		ele_login_pswd = ele_login_popup.find_element_by_name("password")
		time_wait = 0
		logger_driver.info("Inputting the name and pswd...")
		while True:
			time_wait += 1
			time.sleep(time_wait)
			if self.robust_input(ele_login_name, self.ac_name, ensure_value=True) and \
				self.robust_input(ele_login_pswd, self.ac_pswd, ensure_value=True):
				logger_driver.info("Correctly inputted the account info.")
				break
			elif time_wait <= 5:
				logger_driver.warning("Failed to input the account info, retrying the {} time".format(time_wait))
			else:
				raise Exception("Can't correctly input the account info, please check the internet.")

	def input_qrcode(self, qr_value: str, MAX_WAIT=10) -> bool:
		if not qr_value or len(qr_value) != 5:
			return False

		ele_login_popup = self.wait.until(EC.presence_of_element_located(
			(By.CLASS_NAME, "layer_login_register_v2")
		))      # type: WebElement

		qr_src_before = ele_login_popup.find_element_by_css_selector(".code img").get_attribute("src")

		ele_qr_input = ele_login_popup.find_element_by_name("verifycode")
		logger_driver.info("Inputting the qr code...")
		while not self.robust_input(ele_qr_input, qr_value, ensure_value=True):
			logger_driver.warning("Failed to input the qr value, auto retry again...")
			time.sleep(1)

		ele_login_popup.find_element_by_link_text("登录").click()

		s_time = time.time()
		while True:
			time.sleep(1)
			if "home" in self.current_url:
				self.ac_status = self.ACCOUNT_STATUS.PASS_LOG_IN
				logger_driver.info("Success, cost: {} s\n".format(time.time() - s_time))
				return True
			elif ele_login_popup.find_element_by_css_selector(".code img").get_attribute("src") != qr_src_before:
				logger_driver.warning("Failed, cost: {} s".format(time.time() - s_time))
				self.ac_status = self.ACCOUNT_STATUS.FAIL_TO_LOG_IN
				return False
			elif time.time() - s_time > MAX_WAIT:
				self.ac_status = self.ACCOUNT_STATUS.FAIL_TO_LOG_IN
				raise Exception("Exceed the max wait time for verifying the qr result.")

	def test_target_url(self) -> bool:
		logger_driver.info("Testing the target url...")
		self.get(self.TEST_ACCOUNT_URL)
		if "security" in self.current_url:
			self.ac_status = self.ACCOUNT_STATUS.FAIL_TO_TEST
			logger_driver.info("Failed to pass the test!")
			return False
		elif self.TEST_ACCOUNT_URL == self.current_url:
			self.ac_status = self.ACCOUNT_STATUS.PASS_TEST_URL
			logger_driver.info("Successfully passed the test!")
			return True
		else:
			logger_driver.error({
				"The current url": self.current_url,
				"The target  url": self.TEST_ACCOUNT_URL
			})
			self.ac_status = self.ACCOUNT_STATUS.FAIL_TO_TEST
			raise Exception("The current url is not the target url, for more info please check the logs.")

	def get_ac_info(self) -> dict:
		return {
			"ac_name": self.ac_name,
			"ac_pswd": self.ac_pswd,
			"ac_status": self.ac_status,
			"ac_cookie_str": self.get_cookie_str(),
		}
