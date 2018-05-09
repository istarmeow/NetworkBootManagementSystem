# -*- coding:utf-8 -*-

'''
通过对镜像名称以及文件夹大小来判断，镜像文件是否已完成同步。
'''

import urllib.request
import urllib.error
import json
import time
import socket
from .models import SambaServerList
import threading
import re


def get_files_info(ip):
    url = 'http://%s:8898/images' % ip
    try:
        req = urllib.request.urlopen(url, timeout=10)
        if req.getcode() == 200:
            date = req.read().decode('utf-8')
            # print(date)
            json_date = json.loads(date)
            # print(json_date)
            dir_list = []
            dir_date = {}
            dir_size = {}
            for dir_name, dir_info in json_date.items():
                # print(dir_name)
                dir_list.append(dir_name)
                # print('修改时间：', json_date[dir_name]['date'], '文件夹大小：', json_date[dir_name]['size'])
                time_array = time.strptime(json_date[dir_name]['date'], "%Y-%m-%d %H:%M:%S")
                time_stamp = int(time.mktime(time_array))
                dir_date[dir_name] = time_stamp
                dir_size[dir_name] = json_date[dir_name]['size']
            # 获取最新创建的文件夹
            recent_image_name = ''
            t = max(dir_date.values())
            for k, v in dir_date.items():
                if v == t:
                    recent_image_name = k
            # 获取文件夹名列表
            dir_list = sorted(dir_list)
            # print(dir_size)
            return dir_list, recent_image_name, dir_date, dir_size
        else:
            print('无法连接')
            return None

    except (socket.timeout, urllib.error.URLError):
        print('%s访问不到' % url)
        return None


class GetSambaSvrInfo(threading.Thread):
    def __init__(self, samba_url):
        threading.Thread.__init__(self)
        self.samba_url = samba_url
        self.speed = ''

    def get_imageslist(self):
        try:
            req = urllib.request.urlopen(self.samba_url, timeout=3)
            if req.getcode() == 200:
                data = req.read().decode('utf-8')
                # print(data)
                json_data = json.loads(data)
                dir_list = []
                dir_date = {}
                dir_size = {}
                recent_image_name = ''
                if len(json_data) != 0:
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


def samba_sync():
    """
    多线程获取镜像列表，返回所有镜像的名称：大小字典列表
    :return:
    """
    samba_server = SambaServerList.objects.filter(available=True)
    start_time = time.clock()
    task_threads = []  # 存储线程
    print('\n\n>>>>>>>>>>多线程开始获取Samba镜像同步')
    samba_images_all = []
    for samba in samba_server:
        td = GetSambaSvrInfo('http://%s:8898/images' % samba.samba_ip)
        task_threads.append(td)
    # print(task_threads)
    for task in task_threads:
        task.start()
    for task in task_threads:
        task.join()  # 等待所有线程结束
    for task in task_threads:
        samba_images = task.get_imageslist()
        # print(samba_images)
        if samba_images:
            samba_images_all.append(samba_images[3])

    end_time = time.clock()
    print('>>>>>>>>>>线程结束，耗时%fs\n' % (end_time - start_time))

    if len(samba_images_all) == 0:
        return None
    else:
        # print('Smaba列表：', len(samba_images_all), samba_images_all, type(samba_images_all), '\n')
        return samba_images_all


if __name__ == '__main__':
    samba1 = '192.168.96.99'
    samba2 = '192.168.96.66'
    samba3 = '192.168.96.166'
    print(get_files_info(samba1))
    # print(get_files_info(samba1)[3] == get_files_info(samba2)[3], get_files_info(samba1)[3] == get_files_info(samba3)[3])
    # if get_files_info(samba1)[3] == get_files_info(samba2)[3] == get_files_info(samba3)[3]:
    #     print('镜像文件已完全同步！')
    # else:
    #     print('镜像文件未完成同步！')




