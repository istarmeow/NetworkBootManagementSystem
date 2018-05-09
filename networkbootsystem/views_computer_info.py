# -*- coding:utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import DiskSmartInfo, User, WakeOnLan
import django.utils.timezone as timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import django.utils.timezone as timezone
from . import ext_pywakeonlan
import urllib


# 接收vbs传输的数据，并做存储处理
def disk_smart_info(request):
    computer_info = request.POST
    error_smart = ''
    instance_list = []
    if len(computer_info) != 0:
        # print(computer_info)
        print('\n')
        print('MAC:', computer_info.get('mac'))
        mac = computer_info.get('mac')
        print('\n')
        print('IP：', computer_info.get('ip'))
        ip = computer_info.get('ip')
        print('\n')
        # print('IP', computer_info.get('disk2'))
        for key in computer_info.keys():
            # print(disk)
            if 'disk' in key:
                # print(computer_info.get(key).split('|'))
                disk = computer_info.get(key).split('|')
                print('序列号:', disk[0], "硬盘名:", disk[1], '规格:', disk[2], '容量:', disk[3], 'PNPDeviceID:', disk[4])
                if DiskSmartInfo.objects.filter(serial=disk[0]).count() == 0:
                    print('硬盘序列号信息添加。\n')
                    DiskSmartInfo.objects.create(
                        serial=disk[0],
                        caption=disk[1],
                        size=disk[2],
                        capacity=disk[3],
                        pnpdeviceid=disk[4],
                        ip=ip,
                        mac=mac,
                        diskinfo=True
                    )
                else:
                    print('硬盘序列号信息更新。\n')
                    DiskSmartInfo.objects.filter(serial=disk[0]).update(
                        caption=disk[1],
                        size=disk[2],
                        capacity=disk[3],
                        pnpdeviceid=disk[4],
                        ip=ip,
                        mac=mac,
                        diskinfo=True
                    )
        print('\n\n')
        for key in computer_info.keys():
            if 'smart' in key:
                # print(computer_info.get(key).split('|'))
                smart = computer_info.get(key).split('|')
                if smart[0].endswith('_0'):
                    instance = smart[0][:-2].upper()
                else:
                    instance = smart[0].upper()
                if DiskSmartInfo.objects.filter(pnpdeviceid=instance).count() != 0:
                    print('硬盘匹配更新SMART数据。')
                    DiskSmartInfo.objects.filter(pnpdeviceid=instance).update(
                        instancename=smart[0],
                        reallocated=smart[1],
                        poweron=smart[2],
                        powercycle=smart[3],
                        currentpending=smart[4],
                        totalwritten=smart[5],
                        smartinfo=True,
                        smarttime=timezone.now()
                    )
                else:
                    if DiskSmartInfo.objects.filter(instancename=smart[0]).count() == 0:
                        print('不匹配重新添加SMART数据。')
                        DiskSmartInfo.objects.create(
                            instancename=smart[0],
                            reallocated=smart[1],
                            poweron=smart[2],
                            powercycle=smart[3],
                            currentpending=smart[4],
                            totalwritten=smart[5],
                            smartinfo=True,
                            ip=ip,
                            mac=mac,
                            smarttime=timezone.now()
                        )
                instance_list.append(smart[0])
                print('InstanceName:', smart[0], '重定位扇区数:', smart[1], '通电时间:', smart[2], '通电次数:', smart[3], '等待重映射扇区数:', smart[4], '写入总数:', smart[5], '\n')
                # if int(smart[1]) > 0 or int(smart[5]) > 0:
                #     error_smart += '硬盘：' + smart[0] + '\n重定位扇区数：' + smart[1] + '；等待重映射扇区数：' + smart[5] + '\n\n'

        smart_info = DiskSmartInfo.objects.filter(instancename__in=instance_list)
        for info in smart_info:
            if int(info.reallocated) > 0 or int(info.currentpending) > 0:
                error_smart += '硬盘：' + info.caption + '\n重定位扇区数：' + info.reallocated + '；等待重映射扇区数：' + info.currentpending + '\n\n'
        if len(error_smart) == 0:
            return HttpResponse('各硬盘【05、C5】数值无异常！')
        else:
            return HttpResponse(error_smart)
    else:
        return HttpResponse('数据为空！')


# 硬盘SMART信息查询
def query_disk_smart_info(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_search=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])
        if request.method == 'GET':
            disk_smart_info_list = DiskSmartInfo.objects.all().order_by('-smarttime', '-disktime', 'mac', 'serial')
            disk_smart_info_num = disk_smart_info_list.count()
            if disk_smart_info_num != 0:
                can_find = True
                find_num = disk_smart_info_num
            else:
                can_find = False
                find_num = 0

            paginator = Paginator(disk_smart_info_list, 16, 2)
            # 实例化查询结果集，每页显示16条数据，少于2条则合并到上一页
            print(paginator)
            page = request.GET.get('page')
            try:
                customer = paginator.page(page)
            except PageNotAnInteger:
                customer = paginator.page(1)
            except EmptyPage:
                customer = paginator.page(paginator.num_pages)
            print('分页', customer)
            show_pages = True
            return render(request, 'computer_info/query_disk_smart_info.html',
                          {
                              'disk_smart_info_list': customer,
                              'can_find': can_find,
                              'find_num': find_num,
                              'show_pages': show_pages,
                          })
        else:
            keyword = request.POST.get('keyword')
            print('关键字：', keyword)
            if keyword is None:
                show_all = True
            elif keyword.strip().replace(' ', '') == '':
                show_all = True
            else:
                keyword = keyword.strip().replace(' ', '')
                show_all = False
            print('是否显示全部：', show_all)
            if show_all:
                disk_smart_info_list = DiskSmartInfo.objects.all().order_by('-smarttime', '-disktime', 'mac', 'serial')
                find_num = disk_smart_info_list.count()
                if find_num == 0:
                    can_find = False
                else:
                    can_find = True
            else:
                disk_smart_info_list = DiskSmartInfo.objects.filter(
                    Q(serial__icontains=keyword) |
                    Q(caption__icontains=keyword) |
                    Q(ip__icontains=keyword) |
                    Q(mac__icontains=keyword)
                ).order_by('mac', 'serial')
                find_num = disk_smart_info_list.count()
                if find_num == 0:
                    can_find = False
                else:
                    can_find = True
                print('是否可以查到：', can_find)
            print('查询到的数量：', find_num)

            return render(request, 'computer_info/query_disk_smart_info.html',
                          {
                              'disk_smart_info_list': disk_smart_info_list,
                              'can_find': can_find,
                              'find_num': find_num,
                          })

    else:
        print('用户不存在！返回登录页面', request.path)
        if User.objects.filter(username=request.session['session_name']).count() == 1:
            print('用户 %s 无权限！' % request.session['session_name'])
            return render(request, 'user/unauth_access.html')
        else:
            print('未登录！请登陆后操作。')
            # return render(request, 'user/login.html')
            return HttpResponseRedirect('/user/login?next=%s' % request.path)


def wakeonlan(request):
    wakeonlan_all = WakeOnLan.objects.all().order_by("-updated")
    wakeonlan_list = []
    if wakeonlan_all.count() < 1:
        can_find = False
        status = '无历史信息，不显示！'
    elif wakeonlan_all.count() <= 10:
        can_find = True
        wakeonlan_list = wakeonlan_all
        status = '显示所有历史记录！'
    else:
        can_find = True
        wakeonlan_list = wakeonlan_all[0:10]
        status = '只显示最新的10条历史记录！'

    if request.method == "GET":
        mac = request.GET.get("mac")
        if mac is None:
            return render(request, 'computer_info/wakeonlan.html',
                          {
                              "status": status,
                              'can_find': can_find,
                              "wakeonlan_list": wakeonlan_list,
                          })
        else:
            if ext_pywakeonlan.send_magic_packet(mac) is True:
                status = '发送唤醒包完成！'
                if WakeOnLan.objects.filter(mac=mac).count() > 0:
                    WakeOnLan.objects.filter(mac=mac).update(updated=timezone.now())
                else:
                    WakeOnLan.objects.create(
                        mac=mac,
                    )
                return render(request, 'computer_info/wakeonlan.html',
                              {
                                  "status": status,
                                  'can_find': can_find,
                                  "wakeonlan_list": wakeonlan_list,
                              })
            else:
                status = 'MAC格式错误！'
                return render(request, 'computer_info/wakeonlan.html',
                              {
                                  "status": status,
                                  'can_find': can_find,
                                  "wakeonlan_list": wakeonlan_list,
                              })

    else:
        mac = request.POST.get("mac")
        print(mac)
        if ext_pywakeonlan.send_magic_packet(mac) is True:
            status = '发送唤醒包完成！'
            if WakeOnLan.objects.filter(mac=mac).count() > 0:
                WakeOnLan.objects.filter(mac=mac).update(updated=timezone.now())
            else:
                WakeOnLan.objects.create(
                    mac=mac,
                )
            return render(request, 'computer_info/wakeonlan.html',
                          {
                              "status": status,
                              'can_find': can_find,
                              "wakeonlan_list": wakeonlan_list,
                          })
        else:
            status = 'MAC格式错误！'
            return render(request, 'computer_info/wakeonlan.html',
                          {
                              "status": status,
                              'can_find': can_find,
                              "wakeonlan_list": wakeonlan_list,
                          })


# 96.20 dhcp状态操作
def dhcp_operate(request):
    keyword = request.GET.get('keyword').strip()
    print(keyword)
    if keyword == 'status':
        url = 'http://192.168.96.20:8898/get_dhcp_status'
    elif keyword == 'stop':
        url = 'http://192.168.96.20:8898/stop_dhcp'
    elif keyword == 'start':
        url = 'http://192.168.96.20:8898/start_dhcp'
    elif keyword == 'restart':
        url = 'http://192.168.96.20:8898/restart_dhcp'
    elif keyword == 'switch':
        url = 'http://192.168.96.20:8898/switch_net_segment'
    elif keyword == 'use':
        url = 'http://192.168.96.20:8898/get_dhcp_use'
    else:
        url = ''
    print(url)
    try:
        with urllib.request.urlopen(url, timeout=5) as req:
            if req.getcode() == 200:
                date = req.read().decode('utf-8')
                return HttpResponse(date)
            else:
                return HttpResponse('无法连接！')
    except urllib.error.URLError:
        return HttpResponse('连接错误！')


def dhcp_index(request):
    return render(request, 'computer_info/dhcp.html')