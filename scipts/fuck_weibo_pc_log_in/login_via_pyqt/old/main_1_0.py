# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/1/31 20:45
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------

from scipts.fuck_weibo_pc_log_in.login_via_pyqt.mainwindow import Ui_MainWindow

import os
import sys
import time
import pickle
import threading
from queue import Queue
from redis import Redis

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget


from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement



WEIBO_LOGIN_PC_URL = "https://weibo.com"
WEIBO_LOGOUT_PC_URL = "https://weibo.com/logout.php"
ACCOUNTS_PATH = r"F:\MyProjects\PycharmProjects\FightForWuhan\login\accounts\accounts.txt"
CHROME_DRIVER_PATH = r"C:\Users\mark\AppData\Local\Programs\Python\Python37\Scripts\chromedriver.exe"
LOADING_GIF_PATH = r"F:\MyProjects\PycharmProjects\FightForWuhan\scrapy_weibo\login\login_via_pyqt\resources\loading2.gif"
LOGO_ICON_PATH = r"F:\MyProjects\PycharmProjects\FightForWuhan\scrapy_weibo\login\login_via_pyqt\resources\nc_logo_3.ico"

QR_IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")

# ac_name = "18450027581"
# ac_pswd = "mas475586"


def yield_account(redis, accounts_path):
    with open(accounts_path, "r") as f:
        ac_list_str = f.read()
        ac_list = [i.split("----") for i in ac_list_str.splitlines()]

    for ac_name, ac_pswd in ac_list:
        if not redis.hexists(redis.db_key, ac_name):
            yield ac_name, ac_pswd


class MyRedis(Redis):

    REDIS_DB = 7

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, db=self.REDIS_DB)
        self.db_key = "weibo_pc_accounts"

    def save_account(self, account_dict) -> None:
        ac_name = account_dict["ac_name"]
        save_result = self.hset(self.db_key, ac_name, pickle.dumps(account_dict))
        if save_result == 1:
            print("Redis saved a new account {}".format(ac_name))
        else:
            print("Redis saved an old account {}".format(ac_name))

    def get_account(self, ac_name) -> dict:
        return pickle.loads(self.hget(self.db_key, ac_name))

def check_error(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print("Failed in the func {}".format(func.__name__))
            return False
        else:
            return True
    return wrapper


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
        # chrome_options.add_argument("--disable-gpu")  # 如果把这个关了，就看不到图片了
        chrome_options.add_argument("--no-sandbox")

        super().__init__(*args, **kwargs,
                         options=chrome_options, executable_path=executable_path)
        self.wait = WebDriverWait(self, timeout=10)

        self.id = None  # 为了后续打印driver的信息标识
        self.ac_name = None
        self.ac_pswd = None
        self.ac_cookie_jar = None
        self.qr_img_path = None
        self.succeeded_cnt = 0
        self.continual_failed_cnt = 0
        self.failed_cnt = 0

    def _re_input_ele(self, element, value):
        element.clear()
        element.send_keys(value)

    @check_error
    def input_account(self, ac_name, ac_pswd):
        self.ac_name = ac_name
        self.ac_pswd = ac_pswd

        if self.current_url != WEIBO_LOGIN_PC_URL:
            self.get(WEIBO_LOGIN_PC_URL)

        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "登录"))).click()
        self._login_popup = self.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "layer_login_register_v2")))
        self._re_input_ele(self._login_popup.find_element_by_name("username"), ac_name)
        self._re_input_ele(self._login_popup.find_element_by_name("password"), ac_pswd)

    @check_error
    def save_qr_img(self):
        self.qr_ele = self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".layer_login_register_v2 .code img")))
        self._qr_src = self.qr_ele.get_attribute("src")

        self.qr_img_path = os.path.join(QR_IMG_DIR, "{}.png".format(time.time()))
        self.qr_ele.screenshot(self.qr_img_path)

    def show_driver(self):
        from io import BytesIO
        from PIL import Image
        Image.open(BytesIO(self.get_screenshot_as_png())).show()


    def submit_qr_code(self, qr_value: str, MAX_WAIT_VERIFY=10) -> int:
        """
        核心提交登录的判断逻辑，通过状态码进行交互
        如果是-1，建议后续退出浏览器，因为可能是线程开太多了
        :param qr_value:
        :param MAX_WAIT_VERIFY:
        :return:
        """
        # TODO 这里的逻辑问题很大，为什么总是会有driver.account_name为空的情况出现！
        print("Driver {} with ac_name {} is verifying using {}...".format(self.id, self.ac_name, qr_value))
        self._login_popup.find_element_by_name("verifycode").send_keys(qr_value)
        self._login_popup.find_element_by_link_text("登录").click()

        s_time = time.time()
        while True:
            time.sleep(1)
            if "home" in self.current_url:
                print("Success, cost: {} s\n".format(time.time() - s_time))
                self.succeeded_cnt += 1
                self.continual_failed_cnt = 0
                return 1

            elif self.qr_ele.get_attribute("src") != self._qr_src:
                print("Failed, cost: {} s".format(time.time() - s_time))
                self.continual_failed_cnt += 1
                self.failed_cnt += 1
                return 0

            elif time.time() - s_time > MAX_WAIT_VERIFY:
                return -1

    def log_out_and_save(self, redis_to_save_cookies=None):
        self.get(WEIBO_LOGOUT_PC_URL)
        if redis_to_save_cookies:
            account_dict = {"ac_name": self.ac_name, "ac_pswd": self.ac_pswd, "ac_cookie_jar": self.get_cookies()}
            redis_to_save_cookies.save_account(account_dict)
            print("Added one account {} to redis_to_save_cookies!".format(self.ac_name))


class PrintfMainWindow(Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super(Ui_MainWindow).__init__(*args, **kwargs)

    def printf(self, msg):
        # Console中插入一句msg，自动换行的
        self.console.append(msg)
        # 始终显示到最后一行
        self.console.moveCursor(self.console.textCursor().End)



class DriverThread(QtCore.QThread):

    def __init__(self, drivers_queue: Queue, accounts_queue: Queue, redis: MyRedis, root: PrintfMainWindow):
        super().__init__()
        self.drivers_queue = drivers_queue
        self.drivers_sum = self.drivers_queue.maxsize
        self.accounts_queue = accounts_queue
        self.redis = redis
        self.root = root
        self.drivers = []

    def run(self) -> None:
        """
        本函数是一个单线程，如果要优化，这里也是可以优化的
        这里并不推荐使用while循环，去判断队列是否满，这可能会使实际运行的drivers驱动数目大于给定值，违背了初衷
        因此简单的使用for循环即可，次数是由队列的初设置的队列最大长度决定的
        :return:
        """
        for ac_name, ac_pswd in yield_account(self.redis, ACCOUNTS_PATH):
            self.accounts_queue.put((ac_name, ac_pswd))
        self.root.printf("Accounts Max To {}".format(self.accounts_queue._qsize()))

        for driver_id in range(self.drivers_queue.maxsize):
            driver = MyDriver()
            self.drivers.append(driver)
            driver.id = driver_id
            self.init_account(driver)

    def del_driver(self, driver: MyDriver, reason=None):
        # TODO 在退出driver时也要判断是否正常退出，不是的话就要回收账号信息
        driver.quit()
        self.drivers.remove(driver)
        self.drivers_sum -= 1
        self.root.printf("Delete driver {}, Reason: {}".format(driver.id, reason))
        self.root.printf("Now the surplus is {} and can max to {}".format(self.drivers.__len__(), self.drivers_sum))
        if self.drivers_sum == 0:
            print("Programme ended since no driver_using is stil alive.")


    def enqueue(self, driver: MyDriver):
        if driver.save_qr_img():    # driver_using.driver_using
            self.drivers_queue.put(driver)
            self.root.printf("Driver {} put into the queue, with ac_name {}".format(driver.id, driver.ac_name))
            return True

    def init_account_old(self, driver: MyDriver):
        if not self.accounts_queue.empty():
            account_info = self.accounts_queue.get()
            if driver.input_account(*account_info):
                if self.enqueue(driver):
                    return True
                else:
                    self.del_driver(driver, reason="Troubled when saving image...")
            else:
                self.del_driver(driver, reason="Troubled when inputting account info...")
        else:
            self.del_driver(driver, reason="No more account need to be verified !")

    def init_account(self, driver: MyDriver):
        if self.accounts_queue.empty():
            self.del_driver(driver, reason="No more account need to be verified !")
        elif not driver.input_account(*self.accounts_queue.get()):
            self.del_driver(driver, reason="Troubled when inputting account info...")
        elif not self.enqueue(driver):
            self.del_driver(driver, reason="Trouble when saving image...")
        else:
            return True

    def verify_account(self, driver: MyDriver, qr_value: str):
        driver_login_status = driver.submit_qr_code(qr_value)
        # 状态码为1或者0的时候，都可以使driver重新回到队列
        if driver_login_status == 1:
            self.root.printf("Driver {} successfully logged in! Next account now...".format(driver.id))
            driver.log_out_and_save(self.redis)
            self.init_account(driver)

        elif driver_login_status == 0:
            self.root.printf("Driver {} failed to pass the verification! Refresh now...".format(driver.id))
            self.enqueue(driver)

        # 这种情况下driver会退出队列
        elif driver_login_status == -1:
            self.del_driver(driver, reason="Login Failed...")

    def __del__(self):
        self.terminate()        # 终止进程
        self.wait()             # 回收线程资源


class MyUi(QMainWindow, PrintfMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        # 初始化提交按钮不可提交
        self.submit_btn.setEnabled(False)
        self.submit_btn.clicked.connect(self.slot_submit)
        # 按Enter键的slot函数需要首先对输入框的内容做一个判断
        self.qr_code.returnPressed.connect(self.slot_submit)

        self.start_btn.clicked.connect(self.start_drivers)

        self.drivers_thread = None
        self.driver_using = None

        self.setWindowIcon(QtGui.QIcon(LOGO_ICON_PATH))

    def start_drivers(self):
        assert self.input_threads_cnt.text().isdecimal()
        self.threads_cnt = int(self.input_threads_cnt.text())
        assert self.threads_cnt > 0 and self.threads_cnt < 10
        assert os.path.exists(self.input_driver_path.text())
        assert os.path.exists(self.input_accounts_path.text())
        self.accounts_path = self.input_accounts_path.text()

        self.start_btn.setEnabled(False)
        self.start_btn.setStyleSheet("back_run-color: rgb(150, 150, 150)")
        self.printf("Drivers  Max To {}".format(self.threads_cnt))

        # 重置主显示窗，变成一个label，以显示图片
        self.verticalLayout.removeWidget(self.qr_widget)
        self.qr_widget.setParent(None)

        self.qr_img_label = QtWidgets.QLabel()
        self.qr_img_label.setMinimumSize(400, 160)
        self.qr_img_label.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.insertWidget(0, self.qr_img_label)
        self.clear_qr_img()

        # 后台启动浏览器队列程序
        accounts_redis = MyRedis()
        accounts_queue = Queue()
        drivers_queue = Queue(maxsize=self.threads_cnt)
        self.drivers_thread = DriverThread(drivers_queue, accounts_queue, redis=accounts_redis, root=self)
        self.drivers_thread.start()

        # 后台刷新验证码程序
        t_refresh_qr_img = threading.Thread(target=self.func_refresh_qr_img, )
        t_refresh_qr_img.setDaemon(True)
        t_refresh_qr_img.start()

    def show_driver_img(self):
        qr_img_pixmap = QtGui.QPixmap(self.driver_using.qr_img_path).scaled(400, 160)
        self.qr_img_label.setPixmap(qr_img_pixmap)
        self.printf("Driver {} is using, with ac_name {}".format(self.driver_using.id, self.driver_using.ac_name))
        self.submit_btn.setEnabled(True)
        self.statusbar.showMessage("Driver id: {}, succeeded: {}, failed: {}".format(
            self.driver_using.id, self.driver_using.succeeded_cnt, self.driver_using.failed_cnt))

    def clear_qr_img(self):
        """
        当清除图片之后，也应该立马将按钮禁用
        :return:
        """
        self.qr_img_label.clear()
        # 如果目前没有其他验证码可以展示的话，就显示加载圈
        if not self.drivers_thread or self.drivers_thread.drivers_queue.empty():
            loading_gif = QtGui.QMovie(LOADING_GIF_PATH)
            self.qr_img_label.setMovie(loading_gif)
            loading_gif.start()

    def func_refresh_qr_img(self):
        """
        后台刷新验证码的逻辑部分
        + 控制Submit按钮的打开
        :return:
        """
        while True:
            if self.driver_using:
               time.sleep(0.5)
            elif not self.drivers_thread:
                # 如果多线程还没启动的话，那就等待
                time.sleep(3)
            elif self.drivers_thread.drivers_queue.empty():
                # 如果因为验证码输入过快，导致线程队列中浏览器暂为空，则等待
                time.sleep(2)
            else:
                # 立即上锁
                self.driver_using = self.drivers_thread.drivers_queue.get() 
                self.printf("Driver {} got from the queue, with ac_name {}".format(self.driver_using.id, self.driver_using.ac_name))
                # 显示图片后，立即拥有self.qr_img_showing函数；
                # 并且立即可被slot监测到，然后就要调用self.driver进行验证，
                self.show_driver_img()

    def slot_submit(self):
        if self.driver_using:
            driver = self.driver_using
            self.driver_using = None            # 迅速清空driver，以腾出下一张driver信息
            qr_value = self.qr_code.text()
            self.submit_btn.setEnabled(False)   # 迅速设置禁止按钮
            self.qr_code.clear()                # 迅速清空输入框
            # 由于图片的展示形式可能有多种方式，所以与验证码输入的清空独立开来
            self.clear_qr_img()                 # 迅速清除图片，或加载一张动图
            t_qr_verify = threading.Thread(target=self.drivers_thread.verify_account, args=(driver, qr_value,))
            t_qr_verify.setDaemon(True)
            t_qr_verify.start()                 # 最后后台验证登录
        else:
            self.statusbar.showMessage("请等待验证码显示后再输入！", 2000)



if __name__ == '__main__':
	app = QApplication(sys.argv)
	my_window = MyUi()
	my_window.show()
	sys.exit(app.exec_())