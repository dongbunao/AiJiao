# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from fake_useragent import UserAgent
import requests
import os
import re
import time

ua = UserAgent()

def get_index(url):
    try:
        headers = {"User-Agent": ua.random}
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print('请求资源库首页出现错误：', response.status_code)
            return None
    except Exception as e:
        print('请求资源库首页出现异常：', e.args)
        return None

def parse_index(html):
    doc = pq(html)
    items = doc('body > div.bj > div.hroup.w > div.module > div.fl > div.list_screen > div:nth-child(2) > dl > dd a').items()
    for item in items:
        yield {
            'nname': item.text(),
            'link': item.attr('href')
        }

def get_subject(url):
    try:
        headers = {"User-Agent": ua.random}
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print('请求年级的学科页面出现错误：', response.status_code)
            return None
    except Exception as e:
        print('请求年级的学科页面出现异常：', e.args)
        return None

def parse_subject(html):
    doc = pq(html)
    items = doc('body > div.bj > div.hroup.w > div.module > div.fl > div.list_screen > div:nth-child(3) > dl > dd a').items()
    for item in items:
        yield {
            'subname': item.text(),
            'link': item.attr('href')
        }

# 返回资源列表总的页数 pageNum
def get_pageNum(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            doc = pq(response.text)
            total = doc('body > div.bj > div.hroup.w > div.module > div.fl > div.mokao_list > div.refresh > div.page > span:nth-child(1) > b').text()
            print('资源总数： ' + total)
            if total == '0':
                return 0

            pageNum = doc('body > div.bj > div.hroup.w > div.module > div.fl > div.mokao_list > div.pageBar > span > b')  # 页数
            print(pageNum.text())  # <b>第8/265页</b>
            pattern = re.compile(r'.*?/(.*?)页')
            pageNum = int(re.findall(pattern, str(pageNum))[0])
            print(pageNum)
            return pageNum
        else:
            print('请求资源总数和页数出错', response.status_code)
            return 0
    except Exception as e:
        print('请求资源总数和页数出现异常', e.args)
        return 0

def get_zsd_list(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print('请求资源列表页出错', response.status_code)
            time.sleep(10)
            return get_zsd_list(url)
    except Exception as e:
        print('请求资源列表页出现异常', e.args)
        return None

def parse_zsd_list(html):
    doc = pq(html)
    items = doc('body > div.bj > div.hroup.w > div.module > div.fl > div.mokao_list > div.mokao_zsdk > ul li').items()
    for item in items:
        yield {
            'title': item.find('.book_comm h3 a').text(),
            'link': item.find('.book_comm h3 a').attr('href'),
            'content': item.find('.book_comm .doc_info').text(),
            'tag': item.find('.book_comm .tag .orange').text(),
            'heat': item.find('.book_comm .tag .blue').text()
        }

def main():
    baseUrl = 'http://zyk.ajiao.com'
    startUrl = 'http://zyk.ajiao.com/zsd'
    html = get_index(startUrl)
    nianjis = parse_index(html)
    for nianji in nianjis:
        print(nianji)
        if nianji['nname'] == '一年级' or nianji['nname'] == '二年级' or nianji['nname'] == '三年级' or nianji['nname'] == '四年级' or nianji['nname'] == '五年级' or nianji['nname'] == '六年级':
            pass
        else:
            path1 = os.path.join('e:\\spAiJiao\\', nianji['nname'])
            isExists = os.path.exists(path1)
            if not isExists:
                os.makedirs(path1)
            #  已经建立年级文件夹，下面根据年级遍历学科
            nianjiUrl = baseUrl + nianji['link']
            html = get_subject(nianjiUrl)
            subjects = parse_subject(html)
            for subject in subjects:
                print(subject)
                path2 = os.path.join(path1, subject['subname'])
                isExists = os.path.exists(path2)
                if not isExists:
                    os.makedirs(path2)
                # 已经在班级文件夹下建立学科文件夹，遍历选定班级学科的知识点列表（分页）
                subUrl = baseUrl + subject['link']

                pageNum = get_pageNum(subUrl)
                for x in range(1, pageNum + 1):
                    nextUrl = subUrl + str(x)

                    print('nextUrl: ' + nextUrl)

                    html = get_zsd_list(nextUrl)
                    zsds = parse_zsd_list(html)
                    for zsd in zsds:
                        print(zsd['title'])
                        # 如果在知识点列表页提取内容，这里就不再请求和解析详情页
                        table = str.maketrans("|\\?*<\":>+[]/'", '_' * 13)
                        zsd['title'] = zsd['title'].translate(table)
                        file_name = os.path.join(path2, zsd['title'] + '.txt')
                        isExists = os.path.exists(file_name)

                        if not isExists:  # 文件不存在才下载
                            # os.makedirs(file_name)
                            # u = urllib.request.urlopen(baseurl + downLink)
                            with open(file_name, 'w', encoding='utf-8') as f:
                                f.write(zsd['content'])
                                print("Sucessful to download" + " " + file_name)
                        else:
                            print(file_name + '文件已经存在，不再重复下载。')



if __name__ == '__main__':
    main()