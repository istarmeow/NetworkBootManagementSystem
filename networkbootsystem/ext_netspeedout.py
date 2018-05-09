# -*- coding:utf-8 -*-

import urllib.request
import urllib.error
from .models import SambaServerList
import json
import threading
import time
import socket


def get_samba_netspeed(samba_ip, samba_url):
    # print('%s 进入获取Samba网速的函数' % samba_ip)
    samba_speed = dict()
    try:
        # url = 'http://192.168.66.99:8898/netspeed'  # 测试用，实际需要删除
        # req = urllib.request.urlopen(url)
        with urllib.request.urlopen(samba_url, timeout=5) as req:
            if req.getcode() == 200:
                date = req.read().decode('utf-8')
                json_date = json.loads(date)
                net_out = json_date['net_io']['net_out']
                net_in = json_date['net_io']['net_in']
                samba_speed[samba_ip] = net_out
                # print('--------------,', samba_speed)
                return samba_speed
            else:
                print('无法连接')
                return None
    except (socket.timeout, urllib.error.URLError):
        return None


# python从子线程中获得返回值
class ShowSambaNetspeed(threading.Thread):
    def __init__(self, samba_ip, samba_url):
        threading.Thread.__init__(self)
        self.samba_ip = samba_ip
        self.samba_url = samba_url

    def run(self):
        # print('\n正在处理IP： ', self.samba_ip)
        self.netspeed = get_samba_netspeed(self.samba_ip, self.samba_url)

    def get_result(self):
        return self.netspeed


def get_use_samba():
    '''
    获取出口流量最小的一个Samba服务器
    :return:
    '''
    samba_speed = dict()
    samba_server_list = SambaServerList.objects.filter(available=True)
    if samba_server_list.count() == 0:
        return False
    else:
        start_time = time.clock()
        task_threads = []  # 存储线程
        print('\n----------多线程获取网速最小值开始')
        samba_speed_all = {}
        for samba_server in samba_server_list:
            if samba_server.netspeed_port is None:
                if samba_server.netspeed_path is None:
                    url = 'http://' + samba_server.samba_ip  # http://192.168.96.96
                else:
                    url = 'http://' + samba_server.samba_ip + samba_server.netspeed_path  # http://192.168.96.96/netspeedout
            else:
                if samba_server.netspeed_path is None:
                    url = 'http://' + samba_server.samba_ip + ':' + samba_server.netspeed_port  # http://192.168.96.96:8898
                else:
                    url = 'http://' + samba_server.samba_ip + ':' + samba_server.netspeed_port + samba_server.netspeed_path  # http://192.168.96.96:8898/netspeedout

            td = ShowSambaNetspeed(samba_server.samba_ip, url)
            task_threads.append(td)
        # print(task_threads)
        for task in task_threads:
            task.start()
        for task in task_threads:
            task.join()  # 等待所有线程结束
        for task in task_threads:
            samba_speed = task.get_result()
            # print('正在处理', samba_speed)
            if samba_speed is not None:
                samba_speed_all = dict(samba_speed_all, **samba_speed)
        end_time = time.clock()
        print('\n----------多线程获取网速最小值结束，耗时%fs\n' % (end_time - start_time))

    print('Smaba列表：', samba_speed_all)

    if len(samba_speed_all) == 0:
        print('-----------------测速结果为空，从数据库中选择默认samba')
        return False
    else:
        print('出口占用最小：', min(samba_speed_all.values()))
        min_speed = min(samba_speed_all.values())
        for samba_ip in samba_speed_all.keys():
            if samba_speed_all[samba_ip] == min_speed:
                return samba_ip


if __name__ == '__main__':
    get_use_samba()
