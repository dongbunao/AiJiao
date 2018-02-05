# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from fake_useragent import UserAgent
import requests
import os

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


def main():
    baseUrl = 'http://zyk.ajiao.com'
    startUrl = 'http://zyk.ajiao.com/zsd'
    html = get_index(startUrl)
    nianjis = parse_index(html)
    for nianji in nianjis:
        print(nianji)
        path1 = os.path.join('e:\\spAiJiao\\', nianji['nname'])
        isExists = os.path.exists(path1)
        if not isExists:
            os.makedirs(path1)

        #  已经建立年级文件夹，下面根据年级遍历学科
        subUrl = baseUrl + nianji['link']
        html = get_subject(subUrl)
        subjects = parse_subject(html)
        for subject in subjects:
            print(subject)
            path2 = os.path.join(path1, subject['subname'])
            isExists = os.path.exists(path2)
            if not isExists:
                os.makedirs(path2)




if __name__ == '__main__':
    main()