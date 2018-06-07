import os
import sys
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from PIL import Image
import time
'''
遍历当前目录下所有的jpg文件,并按照文件夹名称合并成pdf文档
python 3.4.4
图片文件用数字按顺序命名
'''

def conpdf(path, file_name):
    # 遍历当前目录
    for root, dirs, files in os.walk(path):
        c = canvas.Canvas(file_name, pagesize=(540, 800))
        # 用于存放jpg文件
        jpg_list = []
        # 从文件列表中取出jpg文件放入到list中
        for p in files:
            # 将jpg文件名存入列表
            if p[-4:] == '.jpg':
                # jpg_list.append(root + "\\" +p)
                jpg_list.append(p)

        # 对文件名称排序
        jpg_list.sort(key=lambda x: int(x[:-4]))

        for f in jpg_list:
            # 按顺序把图片画到画布上
            c.drawImage(root + "\\" + f, 0, 0, 540, 800)
            # 结束当前页并新建页
            c.showPage()
        c.save()
    print(file_name + "转换成功")


def main():
    xiaolei_path = 'E:\图书\哲学'
    # 1,遍历给定路径下的所有文件件
    # dirs = [x for x in os.listdir(xiaolei_path) if os.path.isdir(x)]
    dirs = os.listdir(xiaolei_path)

    # 2,对每个文件夹的图片进行转换
    for dir in dirs:
        if os.path.isdir(os.path.join(xiaolei_path, dir)):
            book_path = os.path.join(xiaolei_path, dir)
            print('图书路径：  ' + book_path)
            file_name = os.path.join(xiaolei_path, dir + '.pdf')
            print('要生成的文件名称：  ' + file_name)
            isExists = os.path.exists(file_name)
            print('文件是否已经存在：  ' + str(isExists))

            if not isExists:
                start = time.clock()
                conpdf(book_path, file_name)
                end = time.clock()
                print('转换耗时：', end-start)
                print('*' * 80)
            else:
                print(file_name + '： 已经转换过了，不再重复转换')
                print('*'*80)





if __name__ == '__main__':
    main()