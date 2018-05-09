# -*- coding:utf-8 -*-

from django.shortcuts import render, HttpResponse
from . import ext_batfilegenerate


def generate_bat_file(request):
    adminpasswd = 'duoyi'
    if request.method == 'GET':
        show_download = False
        # 删除文件夹下所有内容
        ext_batfilegenerate.del_files()
        print('文件夹下所有内容删除。')
        return render(request, 'batfolder/generate_bat_file.html',
                      {
                          'show_download': show_download,
                          'adminpasswd': adminpasswd,
                      })
    else:
        show_download = True
        seat = request.POST.get('seat')
        seat_disk = request.POST.get('seat_disk')
        software = request.POST.get('software')
        software_disk = request.POST.get('software_disk')
        bookcd = request.POST.get('bookcd')
        bookcd_disk = request.POST.get('bookcd_disk')

        password = request.POST.get('password')
        username = request.POST.get('username')
        print(seat, software)

        if seat is None and software is None and bookcd is None:
            show_download = False
            filename = None
        else:
            cmd = r'net use %s: %s %s %s /persistent:no'
            cmd_list = list()
            if seat is not None:
                if len(seat_disk) == 1:
                    seat_cmd = cmd % (seat_disk, r'\\192.168.96.25\座位名单', 'guest', '/user:guest')
                else:
                    seat_cmd = cmd % ('S', r'\\192.168.96.25\座位名单', 'guset', '/user:guest')
                print(seat_cmd)
                cmd_list.append(seat_cmd)

            if software is not None and password == adminpasswd:
                if len(software_disk) == 1:
                    software_cmd = cmd % (software_disk, r'\\192.168.96.96\工具软件', '', '')
                else:
                    software_cmd = cmd % ('W', r'\\192.168.96.96\工具软件', '', '')
                print(software_cmd)
                cmd_list.append(software_cmd)

            if bookcd is not None:
                if len(bookcd_disk) == 1:
                    bookcd_cmd = cmd % (bookcd_disk, r'\\192.168.96.66\书籍光盘', 'guest', '/user:guest')
                else:
                    bookcd_cmd = cmd % ('K', r'\\192.168.96.66\书籍光盘', 'guest', '/user:guest')
                print(bookcd_cmd)
                cmd_list.append(bookcd_cmd)

            if seat is None and software is None and bookcd is None:
                show_download = False

            filename = ext_batfilegenerate.create_bat(username, cmd_list)
            print('下载的文件名：', filename, '是否显示：', show_download)

        return render(request, 'batfolder/generate_bat_file.html',
                      {
                          'filename': filename,
                          'show_download': show_download,
                          'adminpasswd': adminpasswd,
                      })
