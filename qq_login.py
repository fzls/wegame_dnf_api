# Generated by Selenium IDE
import os
import subprocess
import threading
import time

import win32api
import win32con
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config import Config
from util import Object


class LoginResult(Object):
    def __init__(self, uin="", skey="", openid=""):
        super().__init__()
        # 使用炎炎夏日活动界面得到
        self.uin = uin
        self.skey = skey
        # 使用心悦活动界面得到
        self.openid = openid


class QQLogin():
    bandizip_executable_path = os.path.realpath("./bandizip_portable/bz.exe")
    chrome_driver_executable_path = os.path.realpath("./chromedriver_85.0.4183.87.exe")
    chrome_binary_7z = os.path.realpath("./chrome_portable_85.0.4183.59.7z")
    chrome_binary_directory = os.path.realpath("./chrome_portable_85.0.4183.59")
    chrome_binary_location = os.path.realpath("./chrome_portable_85.0.4183.59/chrome.exe")

    def __init__(self, common_config):
        print("正在初始化chrome driver，用以进行登录相关操作")

        self.cfg = common_config  # type: Config

        caps = DesiredCapabilities().CHROME
        # caps["pageLoadStrategy"] = "normal"  #  Waits for full page load
        caps["pageLoadStrategy"] = "none"  # Do not wait for full page load

        options = Options()
        if not self.cfg._debug_show_chrome_logs:
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
        if self.cfg.run_in_headless_mode:
            print("已配置使用headless模式运行chrome")
            options.headless = True

        inited = False

        try:
            if not self.cfg.force_use_portable_chrome:
                # 如果未强制使用便携版chrome，则首先尝试使用系统安装的chrome85
                self.driver = webdriver.Chrome(executable_path="./chromedriver_85.0.4183.87.exe", desired_capabilities=caps, options=options)
                print("使用自带chrome")
                inited = True
        except:
            pass

        if not inited:
            # 如果找不到，则尝试使用打包的便携版chrome85
            # 先判定是否是下载的无附带浏览器的小包
            if not os.path.isfile(self.chrome_binary_7z):
                msg = (
                    "当前电脑未发现合适版本chrome85版本，且当前目录无便携版chrome的压缩包，因此猜测你下载的是未附带浏览器的小包\n"
                    "请采取下列措施之一\n"
                    "\t1. 去蓝奏云网盘下载chrome85离线安装包.exe，并安装，从而系统有合适版本的chrome浏览器\n"
                    "\t2. 去蓝奏云网盘下载完整版的本工具压缩包，也就是大概是95MB的最新的压缩包\n"
                    "\n"
                    "请进行上述操作后再尝试~\n"
                )
                win32api.MessageBox(0, msg, "出错啦", win32con.MB_ICONERROR)
                exit(-1)

            # 先判断便携版chrome是否已解压
            if not os.path.isdir(self.chrome_binary_directory):
                print("自动解压便携版chrome到当前目录")
                subprocess.call('{} x -target:auto {}'.format(self.bandizip_executable_path, self.chrome_binary_7z))

            # 然后使用本地的chrome来初始化driver对象
            options.binary_location = self.chrome_binary_location
            # you may need some other options
            options.add_argument('--no-sandbox')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--no-first-run')
            self.driver = webdriver.Chrome(executable_path=self.chrome_driver_executable_path, desired_capabilities=caps, options=options)
            print("使用便携版chrome")

        self.cookies = self.driver.get_cookies()

    def login(self, account, password, is_xinyue=False):
        """
        自动登录指定账号，并返回登陆后的cookie中包含的uin、skey数据
        :param account: 账号
        :param password: 密码
        :rtype: LoginResult
        """
        print("即将开始自动登录，无需任何手动操作，等待其完成即可")
        print("如果出现报错，可以尝试调高相关超时时间然后重新执行脚本")

        def login_with_account_and_password():
            # 选择密码登录
            self.driver.find_element(By.ID, "switcher_plogin").click()
            # 输入账号
            self.driver.find_element(By.ID, "u").send_keys(account)
            # 输入密码
            self.driver.find_element(By.ID, "p").send_keys(password)
            # 发送登录请求
            self.driver.find_element(By.ID, "login_button").click()

        return self._login("账密自动登录", login_action_fn=login_with_account_and_password, need_human_operate=False, is_xinyue=is_xinyue)

    def qr_login(self, is_xinyue=False):
        """
        二维码登录，并返回登陆后的cookie中包含的uin、skey数据
        :rtype: LoginResult
        """
        print("即将开始扫码登录，请在弹出的网页中扫码登录~")
        return self._login("扫码登录", is_xinyue=is_xinyue)

    def _login(self, login_type, login_action_fn=None, need_human_operate=True, is_xinyue=False):
        for idx in range(self.cfg.login.max_retry_count):
            idx += 1
            try:
                login_fn = self._login_real
                if is_xinyue:
                    login_fn = self._login_xinyue_real

                return login_fn(login_type, login_action_fn=login_action_fn, need_human_operate=need_human_operate)
            except Exception as e:
                print("第{}/{}次尝试登录出错，等待{}秒后重试\n{}".format(idx, self.cfg.login.max_retry_count, self.cfg.login.retry_wait_time, e))
                time.sleep(self.cfg.login.retry_wait_time)

    def _login_real(self, login_type, login_action_fn=None, need_human_operate=True):
        """
        通用登录逻辑，并返回登陆后的cookie中包含的uin、skey数据
        :rtype: LoginResult
        """

        def switch_to_login_frame_fn():
            print("打开活动界面")
            self.driver.get("https://dnf.qq.com/lbact/a20200716wgmhz/index.html")

            print("浏览器设为1936x1056")
            self.driver.set_window_size(1936, 1056)

            print("等待登录按钮#dologin出来，确保加载完成")
            WebDriverWait(self.driver, self.cfg.login.load_page_timeout).until(expected_conditions.visibility_of_element_located((By.ID, "dologin")))

            print("点击登录按钮")
            self.driver.find_element(By.ID, "dologin").click()

            print("等待#loginIframe显示出来并切换")
            WebDriverWait(self.driver, self.cfg.login.load_login_iframe_timeout).until(expected_conditions.visibility_of_element_located((By.ID, "loginIframe")))
            loginIframe = self.driver.find_element_by_id("loginIframe")
            self.driver.switch_to.frame(loginIframe)

        def assert_login_finished_fn():
            print("请等待#logined的div可见，则说明已经登录完成了...")
            WebDriverWait(self.driver, self.cfg.login.login_finished_timeout).until(expected_conditions.visibility_of_element_located((By.ID, "logined")))

        self._login_common(login_type, switch_to_login_frame_fn, assert_login_finished_fn, login_action_fn, need_human_operate)

        # 从cookie中获取uin和skey
        return LoginResult(uin=self.get_cookie("uin"), skey=self.get_cookie("skey"))

    def _login_xinyue_real(self, login_type, login_action_fn=None, need_human_operate=True):
        """
        通用登录逻辑，并返回登陆后的cookie中包含的uin、skey数据
        :rtype: LoginResult
        """

        def switch_to_login_frame_fn():
            print("打开活动界面")
            self.driver.get("https://xinyue.qq.com/act/a20181101rights/index.html")

            print("浏览器设为1936x1056")
            self.driver.set_window_size(1936, 1056)

            print("等待#loginframe加载完毕并切换")
            WebDriverWait(self.driver, self.cfg.login.load_login_iframe_timeout).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, "loginframe")))
            login_frame = self.driver.find_element_by_class_name("loginframe")
            self.driver.switch_to.frame(login_frame)

            print("等待#loginframe#ptlogin_iframe加载完毕并切换")
            WebDriverWait(self.driver, self.cfg.login.load_login_iframe_timeout).until(expected_conditions.visibility_of_element_located((By.ID, "ptlogin_iframe")))
            ptlogin_iframe = self.driver.find_element_by_id("ptlogin_iframe")
            self.driver.switch_to.frame(ptlogin_iframe)

        def assert_login_finished_fn():
            print("请等待#btn_wxqclogin可见，则说明已经登录完成了...")
            WebDriverWait(self.driver, self.cfg.login.login_finished_timeout).until(expected_conditions.invisibility_of_element_located((By.ID, "btn_wxqclogin")))

            print("等待1s，确认获取openid的请求完成")
            time.sleep(1)

            # 确保openid已设置
            for t in range(3):
                t += 1
                if self.driver.get_cookie('openid') is None:
                    print("第{}/3未在心悦的cookie中找到openid，等一秒再试".format(t))
                    time.sleep(1)
                    continue
                break

        self._login_common(login_type, switch_to_login_frame_fn, assert_login_finished_fn, login_action_fn, need_human_operate)

        # 从cookie中获取openid
        return LoginResult(openid=self.get_cookie("openid"))

    def _login_common(self, login_type, switch_to_login_frame_fn, assert_login_finished_fn, login_action_fn=None, need_human_operate=True):
        """
        通用登录逻辑，并返回登陆后的cookie中包含的uin、skey数据
        :rtype: LoginResult
        """
        switch_to_login_frame_fn()

        print("等待#loginframe#ptlogin_iframe#switcher_plogin加载完毕")
        WebDriverWait(self.driver, self.cfg.login.load_login_iframe_timeout).until(expected_conditions.visibility_of_element_located((By.ID, 'switcher_plogin')))

        if need_human_operate:
            print("请在{}s内完成{}操作".format(self.cfg.login.login_timeout, login_type))

        # 实际登录的逻辑，不同方式的处理不同，这里调用外部传入的函数
        print("开始{}流程".format(login_type))
        if login_action_fn is not None:
            login_action_fn()

        print("等待登录完成（也就是#loginIframe#login登录框消失）")
        WebDriverWait(self.driver, self.cfg.login.login_timeout).until(expected_conditions.invisibility_of_element_located((By.ID, "login")))

        print("回到主iframe")
        self.driver.switch_to.default_content()

        assert_login_finished_fn()

        print("登录完成")

        self.cookies = self.driver.get_cookies()

        # 最小化网页
        self.driver.minimize_window()
        threading.Thread(target=self.driver.quit, daemon=True).start()

        return

    def get_cookie(self, name):
        for cookie in self.cookies:
            if cookie['name'] == name:
                return cookie['value']
        return ''


if __name__ == '__main__':
    # 读取配置信息
    cfg = Config()
    # 自行填入实际账号密码，并调整其他配置
    # cfg.account = "111"
    # cfg.password = "222"
    ql = QQLogin(cfg)
    is_xinyue = False
    # lr = ql.login(cfg.account, cfg.password, is_xinyue)
    lr = ql.qr_login()
    print(lr)