import threading
import json
import time
import smtplib

from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class DaMaiThread(threading.Thread):
    def __init__(self, opts, username, url, qq_num, cookies, start_time, mail_host, mail_user, mail_pass, buy_num,
                 city=None, date=None, price=None):
        threading.Thread.__init__(self)
        self.options = opts
        self.username = username
        self.city = city
        self.date = date
        self.url = url
        self.price = price
        self.qq_num = qq_num
        self.cookies = cookies
        self.start_time = start_time
        self.mail_host = mail_host
        self.mail_user = mail_user
        self.mail_pass = mail_pass
        self.buy_num = buy_num

    def run(self):
        driver = webdriver.Chrome(options=self.options)
        try:
            driver.get(self.url)

            if self.start_time > datetime.now():
                while (self.start_time - datetime.now()).seconds != 0:
                    time.sleep(1)

            # 判断cookie信息
            if "damai.cn_user" not in driver.get_cookies():
                # 赋值cookie信息
                for c in self.cookies:
                    if "expiry" in c:
                        del c["expiry"]
                    driver.add_cookie(c)
                driver.refresh()

            wait_user_load(driver, self.username)

            if self.city is not None:
                # 等待城市信息加载出来
                wait_for_loading((By.CLASS_NAME, "citylist"), driver)
                cityList = driver.find_element_by_class_name("citylist").find_elements_by_css_selector("div")
                for city in cityList:
                    if self.city in city.text:
                        if city.get_attribute("class") != "cityitem active":
                            city.click()
                        break
                wait_user_load(driver, self.username)
                # 等待城市切换成功
                wait_for_loading((By.XPATH, "//div[@class='addr'][contains(.,'{}')]"
                                  .format("场馆：{}".format(self.city))), driver)

            if self.date is not None:
                xPath = "//div[@class='perform__order__select perform__order__select__performs']" \
                        "/div[@class='select_right']/div[@class='select_right_list']"
                # 等待场次信息加载
                wait_for_loading((By.XPATH, xPath), driver)
                dateList = driver.find_elements_by_xpath(xPath + "/div")
                for date in dateList:
                    if self.date in date.text:
                        if date.get_attribute("class") != "select_right_list_item active":
                            date.click()
                        break
                wait_user_load(driver, self.username)
                # 等待场次切换
                wait_for_loading((By.XPATH, xPath + "//div[@class='select_right_list_item active'][contains(.,'{}')]"
                                  .format(self.date)), driver)

            if self.price is not None:
                xPath = "//div[@class='perform__order__select']/div[@class='select_right']" \
                        "/div[@class='select_right_list']"
                # 等待票价加载
                wait_for_loading((By.XPATH, xPath), driver)
                priceList = driver.find_elements_by_xpath(xPath + "/div")
                sub_price = 0
                for price in priceList:
                    can_click = False
                    for p in self.price:
                        if str(p) in price.find_element_by_class_name("skuname").text:
                            can_click = True
                            sub_price = p
                            break

                    if can_click:
                        if price.get_attribute("class") != "select_right_list_item sku_item active":
                            price.click()
                        break
                wait_for_loading((By.XPATH,
                                  xPath + "//div[@class='select_right_list_item sku_item active'][contains(.,'{}')]"
                                  .format(sub_price)), driver)

            # 修改为两张票
            num_input = driver.find_element_by_xpath("//input[@class='cafe-c-input-number-input']")
            num_input.send_keys(Keys.BACKSPACE)
            num_input.send_keys(self.buy_num)

            # 判断是否能买票
            buyBtn = driver.find_element_by_class_name("buybtn")
            if buyBtn.text == "立即购买" or buyBtn.text == "立即预订":
                buyBtn.click()
                # 继续确认订单的流程
                wait_for_loading((By.XPATH, "//div[@class='next-col buyer-list-item']/label//span"), driver)
                driver.find_elements_by_xpath("//div[@class='next-col buyer-list-item']/label")[0].click()
                driver.find_element_by_xpath("//div[@class='submit-wrapper']/button").click()
                wait_for_loading((By.CLASS_NAME, "alipay-logo"), driver)
                print("订单已确认")
                self.send_email()
            else:
                print("哦吼！票卖完了")

        finally:
            driver.quit()

    def send_email(self):
        # 如果发件人信息不全就取消
        if self.mail_host is None or self.mail_user is None or self.mail_pass is None:
            return

        sender = self.mail_user
        receivers = ["{}@qq.com".format(self.qq_num)]

        message = MIMEText("快点去大麦app付款！", "plain", "utf-8")
        message["From"] = Header("那个大麦抢票的程序发的", "utf-8")
        message["To"] = Header("{}@qq.com".format(self.qq_num), "utf-8")
        message["Subject"] = Header("大麦网抢好票了！！！\n时间{}".format(datetime.now()), "utf-8")

        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(self.mail_host, 25)
            smtpObj.login(self.mail_user, self.mail_pass)
            smtpObj.sendmail(sender, receivers, message.as_string())
            smtpObj.quit()
            print("邮件发送成功！")
        except smtplib.SMTPException as e:
            print(e)


# 等待用户信息加载
def wait_user_load(driver, username):
    wait_for_loading((By.XPATH, "//div[@class='box-header user-header']//*[text()='{}']".format(username)), driver)


# 登录获取cookie
def load_cookies(opts, qq_num, qq_pass, username, cookies):
    driver = webdriver.Chrome(options=opts)
    try:
        driver.get("https://www.damai.cn")
        # 判断cookie信息
        if "damai.cn_user" not in driver.get_cookies():
            if len(cookies) == 0:
                # 进行登录
                loginBtn = driver.find_element_by_class_name("span-box-header.span-user")
                loginBtn.click()
                wait_for_loading((By.ID, "alibaba-login-box"), driver)
                driver.switch_to.frame("alibaba-login-box")
                driver.find_element_by_class_name("thirdpart-login-icon.icon-qq").click()
                driver.switch_to.window(driver.window_handles[1])
                driver.switch_to.frame("ptlogin_iframe")
                driver.find_element_by_id("switcher_plogin").click()
                driver.find_element_by_id("u").send_keys(qq_num)
                passIpt = driver.find_element_by_id("p")
                passIpt.send_keys(qq_pass)
                passIpt.send_keys(Keys.ENTER)
                # 获取登录后的cookie
                driver.switch_to.window(driver.window_handles[0])
                wait_user_load(driver, username)
                cookies.extend(driver.get_cookies())

    finally:
        driver.quit()


def wait_for_loading(located, driver, retry_times=3):
    if retry_times < 1:
        raise Exception("等待超时，失败！")

    try:
        WebDriverWait(driver, 5).until(ec.presence_of_all_elements_located(located))
    except TimeoutException:
        driver.refresh()
        wait_for_loading(located, driver, retry_times - 1)


options = webdriver.ChromeOptions()
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
options.add_experimental_option("excludeSwitches", ["enable-automation"])
threads = []

file = open("damai_config.json")
configs = json.loads(file.read())
print(configs)
buy_time = datetime.strptime(configs["buy_time"], "%Y-%m-%d %H:%M")
now_time = datetime.now()
# 睡眠至预定时间
print(buy_time)
print(now_time)
print(buy_time > now_time)

if buy_time > now_time:
    seconds = (buy_time - now_time).seconds
    if seconds > 60:
        time.sleep(seconds - 60)

for cfg in configs["users"]:
    cfg_cookies = []
    load_cookies(options, cfg["qq_num"], cfg["qq_pass"], cfg["username"], cfg_cookies)
    for i in range(2):
        thread = DaMaiThread(options, cfg["username"], cfg["url"], cfg["qq_num"], cfg_cookies, buy_time,
                             configs["mail_host"], configs["mail_user"], configs["mail_pass"], configs["buy_num"],
                             cfg["city"], cfg["date"], cfg["price_list"])
        thread.start()

for t in threads:
    t.join()
