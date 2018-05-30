#encoding: utf-8

from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import re
import json

class NlcSpider(object):
    # chromedriver的绝对路径
    driver_path = r'D:\chromedriver\chromedriver.exe'
    def __init__(self):
        # 初始化一个driver，并且指定chromedriver的路径
        self.driver = webdriver.Chrome(executable_path=self.driver_path)
        self.driver.set_page_load_timeout(20)
        self.driver.set_script_timeout(20)

    def run(self):
        url = 'http://202.106.125.14:8000/Usp/nlc/?pid=dlib.index&cult=CN'
        # 首次登录
        self.driver.get(url)
        # window_1 = self.driver.current_window_handle
        # windows = self.driver.window_handles
        # for current_window in windows:
        #     if current_window != window_1:
        #         self.driver.switch_to.window(current_window)
        time.sleep(3)
        # 打开一个新的页面
        self.driver.execute_script("window.open('" + url + "')")
        # 切换到这个新的页面中
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.login('15603059107', '15603059107')

        time.sleep(3)

        # 打开一个新的页面
        # self.driver.execute_script("window.open('" + url + "')")
        # 切换到第一个页面中
        self.driver.switch_to_window(self.driver.window_handles[0])
        try:
            self.driver.get(url)
        except:
            self.driver.execute_script('window.stop()')

        # 获取cookie并通过json模块将dict转化成str
        dictCookies = self.driver.get_cookies()
        jsonCookies = json.dumps(dictCookies)
        # 登录完成后，将cookie保存到本地文件
        with open('cookies.json', 'w') as f:
            f.write(jsonCookies)

    def login(self, username, password):
        username_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        password_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        username_input.send_keys(username)
        password_input.send_keys(password)

        if self.driver.find_element_by_class_name('yzimg').is_displayed():
            print('验证码已经显示 ', self.driver.find_element_by_class_name('yzimg').is_displayed())
        val = input('请输入验证码：\n>')
        time.sleep(1)  # 等待用户手工输入验证码
        if val and len(val) > 0:
            print(val)
            self.driver.find_element_by_id('imgCode').send_keys(val)

        submit_buttn = self.driver.find_element_by_class_name('loginbtn')
        submit_buttn.click()
        time.sleep(2)



        # try:
        #     WebDriverWait(self.driver, 3).until(EC.alert_is_present())
        #     alert = self.driver.switch_to_alert.accept()
        #     print("alert accepted")
        #
        # except Exception:
        #     print("no alert")

        # alert = self.driver.switch_to.alert
        # alert.accept()


def main():
    spider = NlcSpider()
    spider.run()

if __name__ == '__main__':
    main()