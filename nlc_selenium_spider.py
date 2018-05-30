#encoding: utf-8
import os

from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from pyquery import PyQuery as pq
import requests
import time
import re
import json
import math

header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
    }

class NlcSpider(object):
    # chromedriver的绝对路径
    driver_path = r'D:\chromedriver\chromedriver.exe'
    def __init__(self):
        # 初始化一个driver，并且指定chromedriver的路径
        self.driver = webdriver.Chrome(executable_path=self.driver_path)
        self.driver.set_page_load_timeout(30)
        self.driver.set_script_timeout(30)  # 这两种设置都进行才有效

    def run(self):
        url = 'http://202.106.125.14:8000/Usp/nlc/?pid=dlib.index&cult=CN'
        # 初次建立连接，随后方可修改cookie
        self.driver.get(url)
        # 删除第一次建立连接时的cookie
        self.driver.delete_all_cookies()
        # 读取登录时存储到本地的cookie
        with open('cookies.json', 'r', encoding='utf-8') as f:
            listCookies = json.loads(f.read())
        for cookie in listCookies:
            self.driver.add_cookie({
                'domain': cookie['domain'],  # 此处xxx.com前，需要带点
                'name': cookie['name'],
                'value': cookie['value'],
                'path': cookie['path'],
                'secure': cookie['secure'],
                'httpOnly': cookie['httpOnly'],
                'expires': None
            })
        # 再次访问页面，便可实现免登陆访问
        try:
            self.driver.get(url)
        except:
            self.driver.execute_script('window.stop()')
        xiaolei_url = r'http://202.106.125.14:8000/Usp/nlc/?pid=usp.catsearch&db=dlib&dt=EBook&cult=CN&of=PublishDate&om=desc&ct=CAT_ZTF&cl=2&cc=002002&il=0'
        # 打开一个新的页面
        try:
            self.driver.execute_script("window.open('" + xiaolei_url + "')")
        except:
            self.driver.execute_script('window.stop()')
        # 切换到这个新的页面中
        self.driver.switch_to.window(self.driver.window_handles[1])

        # 获取总的数量  (总数量/10) + 1 = 总页数
        count = self.driver.find_element_by_css_selector('#right2 > div:nth-child(1) > ul > li > span').text
        print('本类的书本数量：', count)
        total_page = math.ceil(int(count)/10)  # math.ceil()向上取整
        print('总页数：', total_page)
        # 遍历每一页的图书，然后对每一本图书进行点击下载
        for num in range(47, total_page+1):
            print('当前页码：', num)
            next_page_url = r'http://202.106.125.14:8000/Usp/nlc/?pid=usp.catsearch&db=dlib&dt=EBook&cult=CN&of=PublishDate&om=desc&ct=CAT_ZTF&cl=2&cc=002002&il=0&pg={num}'
            next_page_url = next_page_url.format(num=num)
            try:
                self.driver.get(next_page_url)
            except:
                self.driver.execute_script('window.stop()')
            resource = self.driver.page_source

            self.parse_book_list_page(resource)
            time.sleep(3)


    def parse_book_list_page(self, resource):
        links = self.driver.find_elements_by_class_name('nav')
        for link in links:
            print(link)
            time.sleep(2)
            # 点击进入图书详情页
            try:
                link.click()
                self.driver.switch_to.window(self.driver.window_handles[2])
                handle2 = self.driver.current_window_handle
                time.sleep(10)
                # 获取图书名称、总页数、和图片的下载链接
                book_name = self.driver.find_element_by_id('bookName').get_attribute('value')
                print(book_name)
                total_count = self.driver.find_element_by_id('TotalCount').text
                print(total_count)
                img_link = self.driver.find_element_by_id('img1').get_attribute('src')
                print(img_link)

                table = str.maketrans("|\\?*<\":>+[]/'.、", '0' * 15)
                book_name = book_name.translate(table)
                path = os.path.join('F:\\图书\\哲学&宗教\\哲学理论\\', book_name)
                isExists = os.path.exists(path)
                if not isExists:
                    os.makedirs(path)
                    # 下载图书图片
                    self.download_book(path, total_count, img_link, 1)
                    time.sleep(4)
                else:
                    print('图书已经下载过了：', book_name)
                    time.sleep(2)

                if self.driver.current_window_handle == handle2:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    time.sleep(5)
            except Exception as e:
                print('进入图书详情页出现异常：', e.args)
                if self.driver.current_window_handle == handle2:
                    self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[1])
                time.sleep(5)


    def download_book(self, path, total_count, img_link, start_num, num_retries=30):
        img_link = str(img_link).replace('pageid=1', 'pageid={pagenum}')
        print( img_link)
        session = requests.Session()
        session.mount('http://', HTTPAdapter(max_retries=3))
        session.mount('https://', HTTPAdapter(max_retries=3))

        for pagenum in range(start_num, int(total_count)+1):
            quickUrl = img_link
            # pagenum = "%03d" % pagenum
            quickUrl = quickUrl.format(pagenum=pagenum)
            print('具体图片链接：', quickUrl)
            pagenum2 = "%03d" % pagenum
            file_name = os.path.join(path, str(pagenum2) + '.jpg')
            isExists = os.path.exists(file_name)
            if not isExists:  # 文件不存在才下载
                try:
                    response = session.get(quickUrl, headers=header, timeout=20)
                    print(response.status_code)
                    if response.status_code == 200:
                        with open(file_name, 'wb') as f:
                            f.write(response.content)
                        print("Sucessful to download-------" + " " + file_name)
                    else:
                        print('下载出现出错', response.status_code)
                        if num_retries > 0:
                            time.sleep(5)
                            print('重试-----------------------------------------------------------------   ' + str(
                                num_retries))
                            return self.download_book(path, total_count, img_link, pagenum, num_retries - 1)
                except Exception as e:
                    print('下载出现异常', e.args)
                    # 重试
                    if num_retries > 0:
                        time.sleep(5)
                        print('重试-----------------------------------------------------------------   ' + str(num_retries))
                        return self.download_book(path, total_count, img_link, pagenum, num_retries-1)
            else:
                print('图片已经存在，不重复下载-------', file_name)



def main():
    spider = NlcSpider()
    spider.run()

if __name__ == '__main__':
    main()