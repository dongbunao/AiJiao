# -*- coding：utf-8 -*-
import selenium
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import requests

# browser = webdriver.Chrome()
# wait = WebDriverWait(browser, 10)

def get_index():
    try:
        response = requests.get('http://zyk.ajiao.com/')
        if response.status_code == 200:
            html = response.text
            return html
        else:
            print('出现错误：', response.status_code)
            return None
    except Exception:
        print('资源库首页超时-----------------------------------------------------------------------------------------')
        return get_index()

def parse_index(html):
    doc = pq(html)
    items = doc('body > div.bj > div.header > div.nav a').items()
    for item in items:
        yield item.attr('href')


def main():
    html = get_index()
    if html:
        print(html)
        articals = parse_index(html)
        for artical in articals:
            print(artical)
            # 解析导航栏所指向的页面（页面格式不统一可以为每个页面写一个方法在此调用？）



if __name__ == '__main__':
    main()
