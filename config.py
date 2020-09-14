from util import Object


class LoginConfig(Object):
    def __init__(self):
        # 重试次数
        self.max_retry_count = 3
        # 重试间隔时间（秒）
        self.retry_wait_time = 1
        # 打开网页后等待时长
        self.open_url_wait_time = 3
        # 加载页面的超时时间，以登录按钮出现为完成标志
        self.load_page_timeout = 60
        # 点击登录按钮后的超时时间，加载登录iframe，以其显示出来为完成标志
        self.load_login_iframe_timeout = 5
        # 登录的超时时间，从登录界面显示为开始，以用户完成登录为结束标志
        self.login_timeout = 600
        # 等待登录完成的超时时间，以活动结束的按钮弹出来标志
        self.login_finished_timeout = 60


class RetryConfig(Object):
    def __init__(self):
        # 每次兑换请求之间的间隔时间（秒），避免请求过快而报错，目前测试1s正好不会报错~
        self.request_wait_time = 1
        # 当提示【"msg": "系统繁忙，请稍候再试。", "ret": "-9905"】时的最大重试次数
        self.max_retry_count = 3
        # 上述情况下的重试间隔时间（秒）
        self.retry_wait_time = 1


class Config(Object):
    def __init__(self):
        # 是否强制使用打包附带的便携版chrome
        self.force_use_portable_chrome = False
        # http(s)请求超时时间(秒)
        self.http_timeout = 10
        # 是否展示chrome的debug日志，如DevTools listening，Bluetooth等
        self._debug_show_chrome_logs = False
        # 自动登录模式是否不显示浏览器界面
        self.run_in_headless_mode = False
        # 登录各个阶段的最大等待时间，单位秒（仅二维码登录和自动登录需要配置，数值越大容错性越好）
        self.login = LoginConfig()
        # 各种操作的通用重试配置
        self.retry = RetryConfig()
        # 自动登录需要设置的信息
        self.account = "123456789"
        self.password = "使用账号密码自动登录有风险_请审慎决定"
