# -*- coding: utf-8 -*-

import requests
from requests.exceptions import RequestException
from pyquery import PyQuery as pq
import re
import os
import time


headers = {
    'Host':'zyk.ajiao.com',
    'Referer':'http://zyk.ajiao.com/',
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
}


#
def get_index(url):
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
        else:
            print('请求首页出错：', response.status_code)
            return None
        response.close()
        return None
    except RequestException as e:
        print('请求首页出现异常', e.args)
        return None

# 解析学科列表
def parse_subs(html):
    doc = pq(html)
    subs = doc('body > div.bj > div.hroup.w > div.module > div.fl > div.list_screen > div:nth-child(3) > dl > dd a').items()
    for sub in subs:
        yield {
            'sub_name': sub.text(),
            'sub_url': sub.attr('href')
        }

# 获取资源列表页源码
def get_list_page(url):
    try:
        response = requests.get(url,  headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
        else:
            print('请求列表页出错：', response.status_code)
            return None
        response.close()
        return None
    except RequestException as e:
        print('请求列表页出现异常', e.args)
        return None

# 从资源列表页 解析出资源的 总页数
def get_page_nums(html):
    doc = pq(html)
    page_nums = doc('.ui-page-skip b').text()
    print(page_nums)

    pattern = re.compile(r'.*/(.*)页')
    page_nums = int(re.findall(pattern, str(page_nums))[0])

    return page_nums


# 从资源列表也 解析出资源列表
def parse_list_page(html):
    doc = pq(html)
    items = doc('.mokao_list .mokao_blk ul li').items()
    for item in items:
        yield {
            'title': item.find('div.txt > p:nth - child(1) a').text(),
            'link': item.find('div.txt > p:nth - child(1) a').attr('href')
        }




def main():
    base_url = 'http://zyk.ajiao.com'
    start_url = 'http://zyk.ajiao.com/kejian/all-all-13/'

    subs = parse_subs(get_index(start_url))
    for sub in subs:
        print(sub)
        sub_name = sub['sub_name']
        sub_url = base_url + sub['sub_url']

        page_nums = get_page_nums(get_list_page(sub_url))
        for x in range(1, page_nums + 1):
            next_url = sub_url + str(x)
            print('下一页url:', next_url)

            parse_list_page(get_list_page(next_url))


if __name__ == '__main__':
    main()