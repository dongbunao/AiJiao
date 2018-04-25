# -*- coding: utf-8 -*-

import requests
from requests.exceptions import RequestException
from pyquery import PyQuery as pq
import re
import os
import time

s = requests.session()
s.keep_alive = False

headers = {
    'Host':'zyk.ajiao.com',
    'Referer':'http://zyk.ajiao.com/',
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
}

#
def get_index(url, num_retries=5):
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
        else:
            print('请求首页出错：', response.status_code)
            if num_retries > 0:
                time.sleep(100)
                get_index(url, num_retries - 1)
            return None
        response.close()
        return None
    except RequestException as e:
        print('请求首页出现异常', e.args)
        if num_retries > 0:
            time.sleep(300)
            get_index(url, num_retries-1)
        return None

# 解析学科列表
def parse_sub(html):
    doc = pq(html)
    subs = doc('body > div.bj > div.hroup.w > div.module > div.fl > div.list_screen > div:nth-child(3) > dl > dd a').items()
    for sub in subs:
        yield {
            'sub_name': sub.text(),
            'sub_url': sub.attr('href')
        }

# 获取资源列表页源码
def get_list_page(url, num_retries=5):
    try:
        response = requests.get(url,  headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
        else:
            print('请求列表页出错：', response.status_code)
            if num_retries > 0:
                time.sleep(100)
                get_list_page(url, num_retries - 1)
            return None
        response.close()
        return None
    except RequestException as e:
        print('请求列表页出现异常', e.args)
        if num_retries > 0:
            time.sleep(300)
            get_list_page(url, num_retries-1)
        return None

# 从资源列表页 解析出资源的 总页数和总数
def get_page_nums(html):
    doc = pq(html)
    page_nums = doc('.ui-page-skip b').text()
    print(page_nums)

    totle_nums = doc('.mokao_list .refresh .page span b.C9').text()
    totle_nums = int(totle_nums)

    pattern = re.compile(r'.*/(.*)页')
    page_nums = int(re.findall(pattern, str(page_nums))[0])

    return page_nums, totle_nums

def get_nianji(url, num_retries=5):
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
        else:
            print('出版社、学科选定后请求年级页出错：', response.status_code)
            if num_retries > 0:
                time.sleep(100)
                get_nianji(url, num_retries - 1)
            return None
        response.close()
        return None
    except RequestException as e:
        print('出版社、学科选定后请求年级页出现异常', e.args)
        if num_retries > 0:
            time.sleep(300)
            get_nianji(url, num_retries-1)
        return None

# 出版社、学科选定后，获取所有年级
def parse_nianji(html):
    doc = pq(html)
    nianjis = doc(
        'div.list_screen > div:nth-child(2) > dl > dd a').items()
    for nianji in nianjis:
        yield {
            'nianji_name': nianji.text(),
            'nianji_url': nianji.attr('href')
        }


# 从资源列表页 解析出资源列表
def parse_list_page(html):
    doc = pq(html)
    items = doc('.mokao_list .mokao_blk ul li').items()
    for item in items:
        yield {
            'title': item.find('div.txt > p:nth-child(1) a').attr('title'),
            'link': item.find('div.txt > p:nth-child(1) a').attr('href')
        }

# 请求资源详情页
def get_detail(url, num_retries=5):
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
        else:
            print('请求资源详情页出错：', response.status_code)
            if num_retries > 0:
                time.sleep(100)
                get_detail(url, num_retries - 1)
            return None
        response.close()
        return None
    except RequestException as e:
        print('请求资源详情页出现异常', e.args)
        if num_retries > 0:
            time.sleep(300)
            get_detail(url, num_retries-1)
        return None

# 解析资源详情页获得下载链接
def parse_detail(html):
    doc = pq(html)
    title = doc('.doctopic h1').text()
    pattern = re.compile('<script>.*?downloadcount.*?location.href = "(.*?)";.*?</script>', re.S)
    down_url = str(re.findall(pattern, html)[0])
    print(title + ' : ' + down_url)
    return down_url

# dowm_url：资源的下载地址， path：文件存储的路径 file_name：文件名
def save_file(dowm_url, path, file_name, num_retries=5):
    dowm_url = str(dowm_url)
    path = str(path)
    file_name = str(file_name)

    file_name1 = os.path.join(path, file_name + '.ppt')
    isExists = os.path.exists(file_name1)
    if not isExists:  # 文件不存在才下载
        try:
            response = requests.get(dowm_url)
            print(response.status_code)
            if response.status_code == 200:
                with open(file_name1, 'wb') as f:
                    f.write(response.content)
                print("Sucessful to download" + " " + file_name1)
                response.close()
            else:
                print('下载出错，错误码:', response.status_code)
                if num_retries > 0:
                    time.sleep(100)
                    save_file(dowm_url, path, file_name, num_retries - 1)
                response.close()
                return None
        except Exception as e:
            print('下载出现异常', e.args)
            if num_retries > 0:
                time.sleep(300)
                save_file(dowm_url, path, file_name, num_retries - 1)
            #response.close()
            return None
    else:
        print(file_name + '文件已经存在，不再重复下载。')


def main():
    base_url = 'http://zyk.ajiao.com'
    start_url = 'http://zyk.ajiao.com/kejian/all-all-13/'

    subs = parse_sub(get_index(start_url)) # 出版社选定后，获取所有学科
    for sub in subs:    #遍历学科
        print(sub)
        time.sleep(150)

        path1 = os.path.join('e:\\课件\\人教版\\', sub['sub_name'])
        isExists = os.path.exists(path1)
        if not isExists:
            os.makedirs(path1)

        sub_url = base_url + sub['sub_url']

        # 出版社、学科选定后，获取所有年级
        nianjis = parse_nianji(get_nianji(sub_url))
        for nianji in nianjis:
            print(sub['sub_name'], nianji['nianji_name'])
            time.sleep(60)

            path2 = os.path.join(path1,  nianji['nianji_name'])
            isExists = os.path.exists(path2)
            if not isExists:
                os.makedirs(path2)

            # 从资源列表页 解析出资源的 总页数
            nianji_url = base_url + nianji['nianji_url']
            page_nums, totle_nums = get_page_nums(get_list_page(nianji_url))

            if totle_nums > 0:  # 选定出版社、学科、年级下有资源时进行下载
                for x in range(1, page_nums + 1):
                    time.sleep(15)
                    next_url = nianji_url + str(x)
                    print('下一页url:', next_url)
                    print('\n')
                    print('*********************************************************************************')

                    kejians = parse_list_page(get_list_page(next_url))
                    for kejian in kejians:
                        print(kejian)

                        file_name = os.path.join(path2, kejian['title'] + '.ppt')
                        isExists = os.path.exists(file_name)
                        if not isExists:  # 文件不存在才下载
                            down_url = parse_detail(get_detail(kejian['link']))
                            save_file(down_url, path2, kejian['title'])
                            time.sleep(3)
                        else:
                            print(file_name + '文件已经存在，不再重复下载。')




if __name__ == '__main__':
    main()