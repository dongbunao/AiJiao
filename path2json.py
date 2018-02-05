# -*- coding: utf-8 -*-

import os
import json

# 把文件的目录结构转换成json格式
def read_directory(path, result):
    paths = os.listdir(path)
    for i, item in enumerate(paths):
        sub_path = os.path.join(path, item)
        if os.path.isdir(sub_path):
            result[item] = {}
            read_directory(sub_path, result[item])
        else:
            result[item] = item

if __name__ == '__main__':
    fpath = 'e:/spider1'   # 这里的路径需要时要转换的目录的顶层目录
    filename = 'e:/spider1/json_res.json'   # 转换后的结果文件名称和存放路径
    result = {}
    read_directory(fpath, result)
    json_res = json.dumps(result, ensure_ascii=False, indent=2)   # ensure_ascii=False 用来解决中文乱码
    print(json_res)
    with open(filename, 'w') as fp:
        fp.write(json_res)