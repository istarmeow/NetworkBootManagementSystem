from threading import Thread
import urllib.request
import json
import sys

def get_samba_netspeed(samba_ip, samba_url):
    x = samba_ip + samba_url
    return x
    # print('进入函数')
    # samba_speed = dict()
    # try:
    #     # url = 'http://192.168.66.99:8898/netspeed'  # 测试用，实际需要删除
    #     # req = urllib.request.urlopen(url)
    #     with urllib.request.urlopen(samba_url, timeout=3) as req:
    #         if req.getcode() == 200:
    #             date = req.read().decode('utf-8')
    #             json_date = json.loads(date)
    #             net_out = json_date['net_io']['net_out']
    #             net_in = json_date['net_io']['net_in']
    #             # print(net_out)
    #             # 根据网速，改变单位
    #             if net_out < 1000:
    #                 net_out_str = str(net_out) + 'KB/s'
    #             elif net_out < 1000000:
    #                 net_out_str = str(round(net_out / 1000, 2)) + 'MB/s'
    #             else:
    #                 net_out_str = str(round(net_out / 1000000, 2)) + 'GB/s'
    #             # print(net_out)
    #             samba_speed[samba_ip] = {'net_out': net_out, 'net_in': net_in}
    #             return samba_speed
    #         # else:
    #         #     print('无法连接')
    #         #     return None
    #
    # except urllib.error.URLError:
    #     pass


class ShowSambaNetspeed(Thread):
    def __init__(self, samba_ip, samba_url):
        Thread.__init__(self)
        self.samba_ip = samba_ip
        self.samba_url = samba_url
        # self.netspeed = {}

    def run(self):  # 必须要使用run()，不能变化
        print(self.samba_ip)
        self.result = get_samba_netspeed(self.samba_ip, self.samba_url)

    def get_result1(self):
        return self.result


# a = ShowSambaNetspeed('172.16.66.66:8899', 'http://192.168.66.99/netspeed')
# # a.samba_netspeed()
# a.start()
# a.join()
# print(a.get_result())

l = []
for i in range(3):
    td = ShowSambaNetspeed('172.16.66.66:8899', 'http://192.168.66.99/netspeed')
    l.append(td)
print(l)
for i in l:
    i.start()
for i in l:
    i.join()
for i in l:
    print(i.get_result1())