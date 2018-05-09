# -*- coding:utf-8 -*-
import urllib.request
import json
import time


def get_images_list():
    url = 'http://192.168.96.99:8898/images'
    try:
        req = urllib.request.urlopen(url, timeout=3)
        if req.getcode() == 200:
            data = req.read().decode('utf-8')
            json_data = json.loads(data)
            dir_list = []
            dir_date = {}
            dir_size = {}
            recent_image_name = ''
            for dir_name, dir_info in json_data.items():
                # print(dir_name)
                dir_list.append(dir_name)
                # print('修改时间：', json_date[dir_name]['date'], '文件夹大小：', json_date[dir_name]['size'])
                time_array = time.strptime(json_data[dir_name]['date'], "%Y-%m-%d %H:%M:%S")
                time_stamp = int(time.mktime(time_array))
                dir_date[dir_name] = time_stamp
                dir_size[dir_name] = json_data[dir_name]['size']
            # 获取最新创建的文件夹

            t = max(dir_date.values())
            for k, v in dir_date.items():
                if v == t:
                    recent_image_name = k
            # 获取文件夹名列表
            dir_list = sorted(dir_list)
            return dir_list, recent_image_name, dir_date, dir_size
        else:
            print('无法连接')
            return None
    except urllib.error.URLError:
        return None


def get_del_images_list():
    url = 'http://192.168.96.99:8898/restore_image'
    try:
        req = urllib.request.urlopen(url, timeout=3)
        if req.getcode() == 200:
            date = req.read().decode('utf-8')
            json_date = json.loads(date)
            dir_list = []
            dir_date = {}
            dir_size = {}
            recent_image_name = ''
            for dir_name, dir_info in json_date.items():
                # print(dir_name)
                dir_list.append(dir_name)
                # print('修改时间：', json_date[dir_name]['date'], '文件夹大小：', json_date[dir_name]['size'])
                time_array = time.strptime(json_date[dir_name]['date'], "%Y-%m-%d %H:%M:%S")
                time_stamp = int(time.mktime(time_array))
                dir_date[dir_name] = time_stamp
                dir_size[dir_name] = json_date[dir_name]['size']
            # 获取最新创建的文件夹
            if len(dir_date) < 1:
                return None
            else:
                t = max(dir_date.values())
                for k, v in dir_date.items():
                    if v == t:
                        recent_image_name = k
                # 获取文件夹名列表
                dir_list = sorted(dir_list)
                return dir_list, recent_image_name, dir_date, dir_size
        else:
            print('无法连接')
            return None
    except urllib.error.URLError:
        return None


if __name__ == '__main__':
    print(get_images_list())



