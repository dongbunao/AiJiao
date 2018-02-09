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
            print('请求首页正常：')
            return response.text
        else:
            print('请求首页出错：', response.status_code)
            return None
    except Exception as e:
        print('请求首页出现异常：', e.args)
        return None

def parse_index(html):
    doc = pq(html)
    print('doc 执行结束')
    items = doc('body .clearfix.czsx .widbox454.widbox908').items()
    for item in items:
        yield {
            'subName': item.find('h2 em a').text(),
            'link': item.find('h2 em a').attr('href')
        }

def get_subject(url):
    try:
        response = requests.get(url)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            print('请求学科页正常：')
            return response.text
        else:
            print('请求学科页出错：', response.status_code)
            return None
    except Exception as e:
        print('请求学科页出现异常：', e.args)
        return None

def parse_subject(html):
    doc = pq(html)
    items = doc('body .wrapper >.grid680.left.rp20 >h2 ').items()
    for item in items:
        yield {
            'subItem': item.find('em').text(),
            'link': item.find('span a').attr('href')
        }

def get_zsdList(url):
    try:
        response = requests.get(url)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            print('请求知识点列表页正常：')
            return response.text
        else:
            print('请求知识点列表页出错：', response.status_code)
            return None
    except Exception as e:
        print('请求知识点列表页出现异常：', e.args)
        return None

def parse_zsdList_totalPage(html):
    doc = pq(html)
    totalPage = doc('body >.wrapper >.bk-listcon.right >.pages a:last').prev().text()
    print(totalPage)
    return int(totalPage)

def parse_zsdList(html):
    doc = pq(html)
    items = doc('body >.wrapper >.bk-listcon.right >.bk-item').items()
    for item in items:
        yield {
            'title': item.find('dd h3 a').text(),
            'link': item.find('dd h3 a').attr('href'),
            'tag': item.find('dd .c-b9 span a').text()
        }

def get_zsdDetail(url):
    try:
        response = requests.get(url)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            print('请求知识点详情页正常：')
            return response.text
        else:
            print('请求知识点详情页出错：', response.status_code)
            return None
    except Exception as e:
        print('请求知识点详情页出现异常：', e.args)
        return None

def parse_zsdDetail(html, path, title):
    doc = pq(html)
    # content = doc('body .wrapper .ku-container.left.ku-content .content.ft14 p:first-of-type').text()
    doc = doc('body .wrapper .ku-container.left.ku-content .content.ft14').remove('.pages')
    doc = doc.remove('style')
    doc = doc.remove('script')
    doc = doc.remove(':last-child')
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
    baseUrl = 'http://www.zhongkao.com/zsdk'
    indexHtml = get_index(baseUrl)
    if indexHtml:
        subjects = parse_index(indexHtml)
        if subjects:
            for subject in subjects:
                print(subject)

                time.sleep(10)
                print(subject['link'])
                pattern = re.compile(r'http://www.zhongkao.com/zsdk/(.*?)/')
                subCode = re.findall(pattern, subject['link'])[0]
                print(subCode)

                path1 = os.path.join('e:\\中考网2\\', subject['subName'])
                isExists = os.path.exists(path1)
                if not isExists:
                    os.makedirs(path1)

                subUrl = subject['link']
                subHtml = get_subject(subUrl)
                zsds = parse_subject(subHtml)
                if zsds:
                    for zsd in zsds:
                        print(zsd)

                        time.sleep(10)

                        print(zsd['link'])
                        pattern = re.compile(r'http://www.zhongkao.com/zsdk/.*?/(.*?)/')
                        itemCode = re.findall(pattern, zsd['link'])[0]
                        print(itemCode)

                        # if zsd['subItem'] == '文言文' or zsd['subItem'] == '标点符号' or zsd['subItem'] == '病句' or zsd['subItem'] == '仿句联句' or zsd['subItem'] == '文学常识' or zsd['subItem'] == '现代文阅读' or zsd['subItem'] == '修词手法' or zsd['subItem'] == '字音字形':
                        #     print(zsd['subItem'] + '  已经抓取过了·····················')
                        # else:
                        path2 = os.path.join(path1, zsd['subItem'])
                        isExists = os.path.exists(path2)
                        if not isExists:
                            os.makedirs(path2)

                        zsdUrl = zsd['link']
                        # 第一页的内容
                        zsdListHtml = get_zsdList(zsdUrl)
                        totalPage = parse_zsdList_totalPage(zsdListHtml)    # totalPage知识点列表的总的页数
                        items = parse_zsdList(zsdListHtml)
                        if items:
                            for item in items:
                                print(item)
                                zsdDetailHtml = get_zsdDetail(item['link'])
                                parse_zsdDetail(zsdDetailHtml, path2, item['title'])

                        # 如果内容有多页（大于1页）
                        if totalPage > 1:
                            count = 0

                            nextPageUrl = 'http://www.zhongkao.com/zsdk/{subCode}/{itemCode}/index_{number}.shtml'

                            for x in range(2, totalPage+1):
                                print('第 ' + str(x) + ' 页。。。。。。。。。')
                                nextPageHtml = get_zsdList(nextPageUrl.format(subCode=subCode, itemCode=itemCode, number=x))
                                print(nextPageUrl.format(subCode=subCode, itemCode=itemCode, number=x))
                                items = parse_zsdList(nextPageHtml)
                                if items:
                                    for item in items:
                                        if count % 50 == 0:
                                            print(str(count) + '有点累了，休息五秒···')
                                            time.sleep(5)
                                        print(item)
                                        zsdDetailHtml = get_zsdDetail(item['link'])
                                        parse_zsdDetail(zsdDetailHtml, path2, item['title'])
                                        count = count + 1












if __name__ == '__main__':
    main()