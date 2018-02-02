# -*- coding:utf-8 -*-
from pyquery import PyQuery as pq
from fake_useragent import UserAgent
import requests
import os
import time
import urllib

ua = UserAgent()


def get_index(url):
    try:
        headers = {"User-Agent": ua.random}
        response = requests.get(url)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            return response.text
        else:
            print('请求首页出现错误：', response.status_code)
            return None
    except Exception as e:
        print('请求首页出现异常：', e.args)
        return None

def parse_index(html):
    doc = pq(html)
    items = doc('body > div.nav > ul > li a').items()
    for item in items:
        yield {
            'pub': item.text(),
            'link': item.attr('href')
        }

def get_detail(url):
    try:
        headers = {"User-Agent": ua.random}
        response = requests.get(url)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            return response.text
        else:
            print('请求出版社首页出现错误：', response.status_code)
            return None
    except Exception as e:
        print('请求出版社首页出现异常：', e.args)
        return None

def parse_detail(html):
    doc = pq(html)
    items = doc('#J_TreeCate > ul > li .t-tit .t-name').items()
    for item in items:
        yield {
            'name': item.text(),
            'link': item.find('a').attr('href')
        }

def get_tree(url):
    try:
        headers = {"User-Agent": ua.random}
        response = requests.get(url)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            return response.text
        else:
            print('请求年级结构树出现错误：', response.status_code)
            return None
    except Exception as e:
        print('请求年级结构树出现异常：', e.args)
        return None

# def parse_tree(html):
#     doc = pq(html)
#     items = doc('#J_TreeCate >.t-bd >li >.t-bd >.t-end >.t-tit').items()
#     for item in items:
#         yield {
#             'unit': item.find('.t-name').text(),
#             'unitUrl': item.find('.t-name a').attr('href')
#         }

def parse_tree(html):
    doc = pq(html)
    items = doc('#J_TreeCate >.t-bd >li >.t-bd >.t-end >.t-tit').items()
    for item in items:
        yield {
            'unit': item.find('.t-name').text(),
            'unitUrl': item.find('.t-name a').attr('href')
        }

def get_branch(url):
    try:
        headers = {"User-Agent": ua.random}
        response = requests.get(url)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            return response.text
        else:
            print('请求单元构树出现错误：', response.status_code)
            return None
    except Exception as e:
        print('请求单元结构树出现异常：', e.args)
        return None

#
def parse_branch(html):
    doc = pq(html)
    doc = doc('[class~=selected]').parent().parent()  # [class~=selected] 意为选择class属性中包含selected单词的所有元素
    items = doc('ul li').items()
    lessions = []
    for item in items:
        lession = {
            'lession': item.find('.t-name').text(),
            'lessionUrl': item.find('.t-name a').attr('href')
        }
        lessions.append(lession)
    return lessions


# 获取和解析资源列表页面，返回每条资源的名字、类型和链接
def get_parse_source(url):
    try:
        headers = {"User-Agent": ua.random}
        response = requests.get(url)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            doc = pq(response.text)
            items = doc('body > div.indexwidth > div.w.fl > div > div.list-items .pt-item').items()  ###### .pt-item

            for item in items:
                yield {
                    'title': item.find('.item-mc .tit a').text(),
                    'type': item.find('.item-act').text(),
                    'link': item.find('.item-mc .tit a').attr('href')
                }
        else:
            print('请求资源列表页出错，错误码:' + response.status_code)
            return None
    except Exception as e:
        print('请求资源列表页出现异常', e.args)
        return None

# sourceurl 是单个资源的地址， path 是文件存储的路径 url是网站url用来拼接下载地址
def save_to_docx(sourceurl, dwnpath, baseurl):
    try:
        # headers = {"User-Agent": ua.random}
        response = requests.get(baseurl + sourceurl)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            doc = pq(response.text)
            title = doc('#J_ListBd > h1').text()
            content = doc('#J_ListBd > div > div.content').text()  # 备用（页面中的文本信息）
            downLink = doc('#J_ListBd > div > div.content > a').attr('href')

            # file_name = dwnpath + '\\' + title + '.ppt'
            file_name = os.path.join(dwnpath, title + '.ppt')
            isExists = os.path.exists(file_name)

            if not isExists:    # 文件不存在才下载
                # os.makedirs(file_name)
                u = urllib.request.urlopen(baseurl + downLink)
                f = open(file_name, 'wb')

                block_sz = 8192
                while True:
                    buffer = u.read(block_sz)
                    if not buffer:
                        break

                    f.write(buffer)
                f.close()
                print("Sucessful to download" + " " + file_name)
            else:
                print(file_name + '文件已经存在，不再重复下载。')
        else:
            print('请求资源详情页出错，错误码:' + response.status_code)
            return None
    except Exception as e:
        print('请求资源详情页出现异常', e.args)
        return None

def main():
    url = 'http://www.shuxue9.com'
    html = get_index(url)
    if html:
        navs = parse_index(html)
        for nav in navs:
            time.sleep(5)
            if nav['link'] == '/':
                pass    # 如果是当前地址就不解析
            else:
                print(nav)
                path1 = os.path.join('e:\\spider1\\', nav['pub'])
                isExists = os.path.exists(path1)
                if not isExists:
                    os.makedirs(path1)

                # 解析出版社的所有年级的山下册
                detailUrl = url + nav['link']
                detailHtml = get_detail(detailUrl)
                nianjis = parse_detail(detailHtml)
                for nianji in nianjis:
                    time.sleep(2)
                    print(nianji)
                    path2 = os.path.join(path1, nianji['name'])
                    isExists = os.path.exists(path2)
                    if not isExists:
                        os.makedirs(path2)

                    # 解析年级（册）的所有单元
                    treeUrl = url + nianji['link']
                    treeHtlm = get_tree(treeUrl)
                    units = parse_tree(treeHtlm)
                    for unit in units:
                        time.sleep(1)
                        print(unit)
                        table = str.maketrans("|\\?*<\":>+[]/'", '_' * 13)
                        unit['unit'] = unit['unit'].translate(table)
                        path3 = os.path.join(path2, unit['unit'])
                        isExists = os.path.exists(path3)
                        if not isExists:
                            os.makedirs(path3)

                        # 解析单元的所有小节（课）
                        branchUrl = url + unit['unitUrl']
                        branchHtml = get_branch(branchUrl)
                        parse_branch(branchHtml)
                        lessions = parse_branch(branchHtml)

                        print(unit['unit'] + '    包含小节数：', len(lessions))

                        if len(lessions) > 0:    # 说明单元下有小节（课），对资料按小节分类
                            for lession in lessions:
                                time.sleep(1)
                                print(lession)
                                lession['lession'] = lession['lession'].translate(table)
                                path4 = os.path.join(path3, lession['lession'])
                                isExists = os.path.exists(path4)
                                if not isExists:
                                    os.makedirs(path4)
                                sourceUrl = url + lession['lessionUrl']
                                sources = get_parse_source(sourceUrl)
                                for source in sources:
                                    if source['type'] == '阅读':  # 阅读 说明是课件的扫描图片
                                        print('课件图片直接忽略······')
                                    else:
                                        save_to_docx(source['link'], path4, url)
                        else:    # 单元下没有小节（课），如果有单元对应的资料，直接存到单元文件夹下
                            sources = get_parse_source(branchUrl)
                            for source in sources:
                                if source['type'] == '阅读':  # 阅读 说明是课件的扫描图片
                                    pass
                                else:
                                    save_to_docx(source['link'], path3, url)


if __name__ == '__main__':
    main()