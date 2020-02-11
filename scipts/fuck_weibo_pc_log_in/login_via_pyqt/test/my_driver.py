# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/1/30 16:12
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------



import os
import time
import sys
import pickle

from redis import Redis

from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from PIL import Image
import matplotlib.pyplot as plt

WEIBO_LOGIN_PC_URL = "https://weibo.com"
WEIBO_LOGOUT_PC_URL = "https://weibo.com/logout.php"
accounts_path = r"F:\MyProjects\PycharmProjects\FightForWuhan\login\accounts\accounts.txt"
CHROME_DRIVER_PATH = r"C:\Users\mark\AppData\Local\Programs\Python\Python37\Scripts\chromedriver.exe"

QR_IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")

ac_name = "18450027581"
ac_pswd = "mas475586"


def yield_account(redis, accounts_path):
    with open(accounts_path, "r") as f:
        ac_list_str = f.read()
        ac_list = [i.split("----") for i in ac_list_str.splitlines()]

    for ac_name, ac_pswd in ac_list:
        if not redis.hexists(redis.db_key, ac_name):
            yield ac_name, ac_pswd


class MyRedis(Redis):

    def __init__(self, *args, db=7, **kwargs):
        super().__init__(*args, **kwargs, db=db)
        self.db_key = "weibo_pc_accounts"

    def save_account(self, account_dict):
        ac_name = account_dict["ac_name"]
        self.hset(self.db_key, ac_name, pickle.dumps(account_dict))

    def get_account(self, ac_name):
        return pickle.loads(self.hget(self.db_key, ac_name))


class MyDriver(Chrome):

    def __init__(self, *args, executable_path=CHROME_DRIVER_PATH, **kwargs):
        chrome_options = ChromeOptions()
        prefs = {
            'profile.default_content_setting_values':
                {
                    'notifications': 2,  # 屏蔽浏览器通知，微博登录之后会有通知
                }
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        super().__init__(*args, **kwargs,
                         options=chrome_options, executable_path=executable_path)
        self.wait = WebDriverWait(self, timeout=10)
        self.id = None  # 为了后续打印driver的信息标识
        self.qr_img_path = None

        
    def show_msg(self, msg):
        print(msg)

    def __del__(self):
        try:
            self.quit()
        except:
            pass

    def _re_input_ele(self, element, value):
        element.clear()
        # assert "\n" not in value
        # os.system("echo {}|clip".format(value))
        # element.send_keys(Keys.CONTROL, "v")
        element.send_keys(value)
        self.show_msg("Sent keys {}".format(value))

    def wait_qr_value(self, qr_img: Image) -> str:
        if __file__.endswith(".ipynb"):
            plt.axis("off")
            plt.imshow(qr_img)
            plt.show()
        else:
            SCALE = 4
            qr_img.resize((qr_img.width * SCALE, qr_img.width * SCALE), Image.ANTIALIAS)
            qr_img.show()
        return input("Verify Code: ")

    def save_qr_img(self):
        self.qr_ele = self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".layer_login_register_v2 .code img")))
        self.qr_src = self.qr_ele.get_attribute("src")
        assert isinstance(self.qr_ele, WebElement)
        self.qr_img_path = os.path.join(QR_IMG_DIR, "{}.png".format(time.time()))
        self.qr_ele.screenshot(self.qr_img_path)

    def show_driver(self):
        from io import BytesIO
        Image.open(BytesIO(self.get_screenshot_as_png())).show()

    def submit_qr_code(self, qr_value: str, MAX_WAIT_VERIFY=10) -> int:
        """
        核心提交登录的判断逻辑，通过状态码进行交互
        如果是-1，建议后续退出浏览器，因为可能是线程开太多了
        :param qr_value:
        :param MAX_WAIT_VERIFY:
        :return:
        """
        print("Sending qr value {}...".format(qr_value))
        self._login_popup.find_element_by_name("verifycode").send_keys(qr_value)
        self._login_popup.find_element_by_link_text("登录").click()

        s_time = time.time()
        while True:
            time.sleep(1)
            if "home" in self.current_url:
                self.show_msg("success, cost: {} s\n".format(time.time() - s_time))
                return 1

            elif self.qr_ele.get_attribute("src") != self.qr_src:
                self.show_msg("failed, cost: {} s".format(time.time() - s_time))
                return 0

            elif time.time() - s_time > MAX_WAIT_VERIFY:
                return -1

    def input_account(self, ac_name, ac_pswd):
        if self.current_url != WEIBO_LOGIN_PC_URL:
            self.show_msg("Visiting weibo home page...")
            self.get(WEIBO_LOGIN_PC_URL)

        self.show_msg("Pop up the login frame...")
        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "登录"))).click()
        self._login_popup = self.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "layer_login_register_v2")))

        self.show_msg("Inputting username and password...")
        self._re_input_ele(self._login_popup.find_element_by_name("username"), ac_name)
        self._re_input_ele(self._login_popup.find_element_by_name("password"), ac_pswd)

    def save_and_log_out(self, redis_to_save_cookies=None):
        self.get(WEIBO_LOGOUT_PC_URL)
        if redis_to_save_cookies:
            account_dict = {"ac_name": ac_name, "ac_pswd": ac_pswd, "ac_cookie_jar": self.get_cookies()}
            redis_to_save_cookies.save_account(account_dict)
            self.show_msg("Added one account {} to redis_to_save_cookies!".format(ac_name))

    def yield_account(self, redis):
        with open(accounts_path, "r") as f:
            ac_list_str = f.read()
            ac_list = [i.split("----") for i in ac_list_str.splitlines()]

        for ac_name, ac_pswd in ac_list:
            if redis.hexists(redis.db_key, ac_name):
                self.show_msg("Redis already has this account {}".format(ac_name))
            else:
                yield ac_name, ac_pswd
