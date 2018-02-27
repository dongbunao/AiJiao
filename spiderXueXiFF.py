# -*- coding: utf-8 -*-
import time
import re
import requests
from pyquery import PyQuery as pq
import os
from requests.adapters import HTTPAdapter


s = requests.session()
# s.config['keep_alive'] = False
s.keep_alive = False
requests.adapters.DEFAULT_RETRIES = 5


def get_index(url):
    try:
        response = requests.get(url)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            return response.text
        else:
            print('请求首页出错了', response.status_code)
            return None
    except Exception as e:
        print('请求首页出现异常', e.args)
        return None

def parse_index(html):
    doc = pq(html)
    items = doc('#weater-right a').items()
    for item in items:
        yield {
            'nianji': item.text(),
            'link': item.attr('href')
        }

def get_NJSub(url):
    try:
        response = requests.get(url)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            return response.text
        else:
            print('请求年级首页出错了', response.status_code)
            return None
    except Exception as e:
        print('请求年级首页出现异常', e.args)
        return None

def parse_NJSub(html):
    doc = pq(html)
    items = doc('#weater-right a').items()
    for item in items:
        yield {
            'subject': item.text(),
            'link': item.attr('href')
        }

def get_subList(url):
    try:
        response = requests.get(url)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            return response.text
        else:
            print('请求学科资源列表页出错了', response.status_code)
            return None
    except Exception as e:
        print('请求学科资源列表页出现异常', e.args)
        return None

def parse_subList(html):
    doc = pq(html)
    items = doc('body > div.main.cbody.margintop > div.pleft > div.newslist > dl').items()
    for item in items:
        yield {
            'title': item.find('dt a').text(),
            'link': item.find('dt a').attr('href')
        }

def get_totalPage(html):
    doc = pq(html)
    totalPage = doc('.dede_pages > .pagelist .pageinfo strong:nth-child(1)').text()
    print(totalPage)
    nextPageSuf = ''
    if int(totalPage) > 1:
        nextPageSuf = doc('.dede_pages ul > li:nth-child(3) > a').attr('href')
        return int(totalPage), nextPageSuf
    else:
        return int(totalPage), nextPageSuf

def get_zsdDetail(url):
    try:
        response = requests.get(url)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            return response.text
        else:
            print('请求知识点详情页出错了', response.status_code)
            return None
    except Exception as e:
        print('请求知识点详情页出现异常', e.args)
        return None

def parse_zsdDetail(html, path, title):
    doc = pq(html)
    doc = doc('body > div.main.cbody.margintop > div.pleft > div.newsview.viewbox > div.content')
    doc = doc.remove('.ggad')
    doc = doc.remove('table')
    doc = doc.remove(':first-child')

    content = doc.text()
    table = str.maketrans("|\\?*<\":>+[]/'", '_' * 13)
    title = title.translate(table)
    file_name = os.path.join(path, title + '.txt')

    isExists = os.path.exists(file_name)
    if not isExists:  # 文件不存在才下载
        # os.makedirs(file_name)
        # u = urllib.request.urlopen(baseurl + downLink)
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(content)
            print("Sucessful to download" + " " + file_name)
    else:
        print(file_name + '文件已经存在，不再重复下载。')

def main():
    baseUrl = 'http://www.xuexifangfa.com'
    startUrl = 'http://www.xuexifangfa.com/xiaoxue'
    html = get_index(startUrl)
    nianjis = parse_index(html)
    for nianji in nianjis:
        if nianji['nianji'] == '小学语文' or nianji['nianji'] == '小学数学' or nianji['nianji'] == '小学英语' or nianji['nianji'] == '作文':
            print(nianji['nianji'] + ' 结构特殊，单独解析')
        else:
            print(nianji)
            path1 = os.path.join('e:\\学习方法网\\', nianji['nianji'])
            isExists = os.path.exists(path1)
            if not isExists:
                os.makedirs(path1)

            nianjiUrl = baseUrl + nianji['link']
            nianjiHtml = get_NJSub(nianjiUrl)
            subjects = parse_NJSub(nianjiHtml)
            for subject in subjects:
                pattern = re.compile('.*年级(.*)')
                sub = re.findall(pattern, subject['subject'])[0]
                print(sub, '5555555555555555555555555555555555555555555555555')
                if sub == '作文':
                    print(subject['subject'] + '结构特殊，单独解析')
                else:
                    print(subject)
                    path2 = os.path.join(path1, subject['subject'])
                    isExists = os.path.exists(path2)
                    if not isExists:
                        os.makedirs(path2)

                    # 创建了年级和学科的文件目录
                    subUrl = baseUrl + subject['link']
                    subHtml = get_subList(subUrl)
                    zsds = parse_subList(subHtml)
                    totalPage, nextPage = get_totalPage(subHtml)
                    print(totalPage)
                    print(nextPage)

                    # 对 nextPage 进行处理，提取公共部分
                    pattern = re.compile('(.*)_.*.html')
                    nextPage = re.findall(pattern, nextPage)[0]
                    print(nextPage)

                    for zsd in zsds:
                        print(zsd)
                        zsdUrl = baseUrl + zsd['link']
                        zsdDetailHtml = get_zsdDetail(zsdUrl)
                        parse_zsdDetail(zsdDetailHtml, path2, zsd['title'])

                    if totalPage > 1:
                        count = 0

                        nextPageUrl = baseUrl + subject['link'] + '{nextPage}_{number}.html'

                        for x in range(2, totalPage + 1):
                            print('第 ' + str(x) + ' 页。。。。。。。。。')
                            nextPageHtml = get_subList(nextPageUrl.format(nextPage=nextPage, number=x))
                            print(nextPageUrl.format(nextPage=nextPage, number=x))
                            items = parse_subList(nextPageHtml)
                            if items:
                                for item in items:
                                    if count % 50 == 0:
                                        print(str(count) + '条  有点累了，休息五秒···')
                                        time.sleep(5)
                                    print(item)
                                    zsdUrl = baseUrl + item['link']
                                    zsdDetailHtml = get_zsdDetail(zsdUrl)
                                    parse_zsdDetail(zsdDetailHtml, path2, item['title'])
                                    count = count + 1







if __name__ == '__main__':
    main()