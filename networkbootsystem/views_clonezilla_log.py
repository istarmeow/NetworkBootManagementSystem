# -*- coding:utf-8 -*-

from django.shortcuts import render
from .models import BootFromClonezillaLog, SystemInstallStatus, BootFromClonezilla, User
from django.core import serializers
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from . import ext_netspeedshow
import json
import django.utils.timezone as timezone
import urllib
from django.db.models import Q


# Clonezilla获取日志查询
def boot_from_clonezilla_get_log(request):
    print('查询Clonezilla获得日志')
    clonezilla_get_log = BootFromClonezillaLog.objects.order_by('-updated')[0:20]
    # print(clonezilla_get_log)
    return render(request, 'logs/boot_from_clonezilla/boot_from_clonezilla_get_log.html',
                  {
                     'clonezilla_get_log': clonezilla_get_log,
                  })


# 装机进度显示列表
def system_install_status(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name']).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])
        return render(request, 'logs/boot_from_clonezilla/system_install_status.html')
    else:
        print('未登录！请登陆后操作。')
        # return render(request, 'user/login.html')
        return HttpResponseRedirect('/user/login?next=%s' % request.path)


# 装机进度显示列表json
def system_install_status_json(request):
    install_list_json = serializers.serialize('json', SystemInstallStatus.objects.all().order_by('-get_time')[0:10])
    # 超时异常判断，只获取20条数据
    # 存在于一个范围内，未获取或进行中
    now_time = timezone.now()
    error_status = SystemInstallStatus.objects.filter(status__in=['0', '-1']).order_by('-get_time')[0:20]
    for error in error_status:
        get_time = error.get_time
        time_difference = (now_time - get_time).total_seconds()  # 时差转换成秒
        m, s = divmod(float(time_difference), 60)
        process_time = str(int(m)) + "分" + str(int(s)) + '秒'
        if int(time_difference) > 1800:
            # 超时30分钟判断失败
            print('失败执行，更新时间和状态')
            SystemInstallStatus.objects.filter(id=error.id, status__in=['0', '-1']).update(process_time=process_time, status='error')

    # 超时处理
    overtime_status = SystemInstallStatus.objects.filter(status='error').order_by('-get_time')[0:20]
    for overtime in overtime_status:
        get_time = overtime.get_time
        time_difference = (now_time - get_time).total_seconds()
        m, s = divmod(float(time_difference), 60)
        process_time = str(int(m)) + "分" + str(int(s)) + '秒'
        if int(time_difference) > 7200:
            # 如果超时时间大于了2小时
            print('执行超过2小时删除')
            SystemInstallStatus.objects.filter(id=overtime.id, status='error').delete()
        else:
            # 如果没超过2小时，就执行更新时长的状态
            SystemInstallStatus.objects.filter(id=overtime.id, status='error').update(process_time=process_time)
    return HttpResponse(install_list_json)


# 通过进度界面点击显示一条日志
def system_install_status_info(request):
    mac = request.GET.get('mac')
    # print(mac)
    recent = BootFromClonezillaLog.objects.filter(mac=mac).order_by('-created')[0]
    install_status_info = serializers.serialize('json', [recent])
    return HttpResponse(install_status_info)


# 调用ext_netspeedshow模块，多线程获取网速信息，转换成json，再展示到前端
def show_netspeed(request):
    # print('\n\n\n\n\n\n-----------------\n\n\n\n')
    samba_netspeed = ext_netspeedshow.show_samba_netspeed()
    if samba_netspeed:
        # 如果测速结果不等于False，那么字典不为空，则返回一个列表
        samba_netspeed = json.dumps(samba_netspeed)
        return HttpResponse(samba_netspeed, content_type="application/json")
        # return HttpResponse(json.dumps({}), content_type="application/json")
    else:
        # Object.keys(samba_netspeed).length > 0
        return HttpResponse(json.dumps({}))


# 装机进度显示数量
def system_install_status_num(request):
    install_num_json = serializers.serialize('json', SystemInstallStatus.objects.filter(~Q(status='1')))
    return HttpResponse(install_num_json)


# 通过获取日志页面点击mac地址显示自动启动的信息，用于修改
def show_boot_auto_from_mac(request):
    mac = request.GET.get('mac')
    # print(mac)
    if BootFromClonezilla.objects.filter(mac=mac).count() != 0:
        info = BootFromClonezilla.objects.filter(mac=mac)[0]
        # boot_auto_info = serializers.serialize('json', [info])

        # 自己构建json的序列，变成serializers.serialize类似的序列
        auto = dict()
        # id用于查询的数据进行更新，删除操作
        auto["op_id"] = info.id
        auto["name"] = info.name
        auto["mac"] = info.mac
        auto["http_server"] = info.http_server.http_name
        auto["samba_server"] = info.samba_server.samba_name
        auto["image_file"] = info.image_file.name
        auto["image_path"] = info.image_path
        auto['restore_disk'] = info.restore_disk.disk_name
        auto["available"] = info.available
        auto["created"] = str(info.created)
        auto['updated'] = str(info.updated)
        auto["explain"] = info.explain

        auto_info = dict()
        auto_info["fields"] = auto

        boot_auto_info_json = json.dumps(auto_info)
        # print(boot_auto_info_json)
        boot_auto_info = "[" + boot_auto_info_json + "]"
        # print(boot_auto_info)

        return HttpResponse(boot_auto_info)
    else:
        return HttpResponse("None")
