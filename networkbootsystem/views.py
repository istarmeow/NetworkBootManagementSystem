# -*- coding:utf-8 -*-

from django.shortcuts import render
from .models import BootSelect, SambaServerList, BootFromClonezilla, HttpServerList, BootFromClonezillaLog
from .models import DefaultImageSelect, RestoreDiskNum, ImageFilesList, BootFromISO, BootFromISOLog, User
from .models import SystemInstallStatus, UpdateLog
from . import ext_netspeedout, ext_webconnection
import datetime
import django.utils.timezone as timezone
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse


# Create your viewss here.


# def homepage(request):
#     return render(request, 'homepage.html')


# 后台主页
def back_manage(request):
    return render(request, 'back_manage.html')


def index(request):
    # print(type(request.session))
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    return render(request, 'index.html')


def mac_upper(request):
    for log_mac in BootFromClonezillaLog.objects.all():
        old_mac = log_mac.mac
        BootFromClonezillaLog.objects.filter(mac=old_mac).update(mac=old_mac.upper())

    for auto_mac in BootFromClonezilla.objects.all():
        old_mac = auto_mac.mac
        BootFromClonezilla.objects.filter(mac=old_mac).update(mac=old_mac.upper())
    for status_mac in SystemInstallStatus.objects.all():
        old_mac = status_mac.mac
        SystemInstallStatus.objects.filter(mac=old_mac).update(mac=old_mac.upper())

    return HttpResponse('MAC都已转换成大写！')


# PXE启动选择，根据选择启动控制页面的-选择启动方式参数进行。2017.10.27修改为按照用户选择启动，不先查找数据库
def boot_select(request):
    mac = request.GET.get('mac')
    serial = request.GET.get('serial')
    if serial is None:
        serial = ''
    if mac is not None:
        # mac = mac.lower()
        mac = mac.upper()
    ip = request.GET.get('ip')
    if ip is None:
        ip = ''

    print('\n\nMAC:', mac, '\nIP:', ip, '\n\n')
    get_tag = False
    # 获取是否成功的标记，默认False，如果获取成功则为Ture

    # 增加用户标记
    username = request.GET.get('username')
    if username is not None and User.objects.filter(username=username).count() == 1:
        print('按照该用户表进行启动。。。')
        boot_name = User.objects.filter(username=username)[0].boot_select
        boot_clonezilla_id = User.objects.filter(username=username)[0].boot_clonezilla_id
        boot_iso_id = User.objects.filter(username=username)[0].boot_iso_id
        if (boot_name != '' and boot_clonezilla_id != 0) or (boot_name != '' and boot_iso_id != 0):
            user_choose = True
        else:
            user_choose = False
    else:
        print('用户表无正确值，按照数据库中默认项选择。。。')
        user_choose = False

    # 根据用户选择进行启动默认选择
    if user_choose is True:
        boot = boot_name
        default_image = DefaultImageSelect.objects.filter(id=User.objects.filter(username=username)[0].boot_clonezilla_id)
        print(default_image)
        select_iso = BootFromISO.objects.filter(id=User.objects.filter(username=username)[0].boot_iso_id)
        get_tag = True
    else:
        boot = BootSelect.objects.filter(available=True)[0].boot_name
        default_image = DefaultImageSelect.objects.filter(available=True)
        select_iso = BootFromISO.objects.filter(available=True)

    # ==============================Clonezilla自动恢复模式==============================
    if boot == 'Clonezilla_Auto':
        print('——————————选择clonezilla全自动恢复——————————')
        # 获取此时出口占用最低的samba服务器，如果没获取到值，则返回一个False，假如返回的是False，则在“Samba服务器管理”中选择默认项的IP地址
        select_samba_ip = ext_netspeedout.get_use_samba()
        if select_samba_ip is False:
            # select_samba_ip = '192.168.96.99'
            default_samba = SambaServerList.objects.filter(default=True)
            if default_samba.count() == 1:
                select_samba_ip = default_samba[0].samba_ip
            else:
                select_samba_ip = '0.0.0.0'
            print('\n将使用默认Samba：', select_samba_ip)
        else:
            print('\n将使用自动选择的Samba：', select_samba_ip)

        # 从Samba列表中获取对应的用户名密码信息，get方式，必须保证数据库有值
        search_samba = SambaServerList.objects.get(samba_ip=select_samba_ip, available=True)
        image_server_path = '//' + search_samba.samba_ip + search_samba.samba_folder  # 构造samba目录： //192.168.96.99/images
        user_name = search_samba.samba_user
        user_password = search_samba.samba_password

        print('\n默认恢复，根据用户选择恢复！')
        # default_image = DefaultImageSelect.objects.filter(available=True)  # 前面根据用户选择进行
        if default_image.count() == 1:
            # 无端口号
            if default_image[0].http_server.http_port == '':
                if default_image[0].http_server.http_folder == '':
                    http_svr = 'http://' + default_image[0].http_server.http_ip  # http://192.168.96.96
                else:
                    http_svr = 'http://' + default_image[0].http_server.http_ip + default_image[0].http_server.http_folder  # http://192.168.96.96/XX
            # 有端口号
            else:
                if default_image[0].http_server.http_folder == '':
                    http_svr = 'http://' + default_image[0].http_server.http_ip + ':' + default_image[0].http_server.http_port  # http://192.168.96.96:8898
                else:
                    http_svr = 'http://' + default_image[0].http_server.http_ip + ':' + default_image[0].http_server.http_port + default_image[0].http_server.http_folder  # http://192.168.96.96:8898/VV

            image_name = default_image[0].image_file.image_name
            disk_num = default_image[0].restore_disk.disk_num
            image_path = default_image[0].image_path

            # 判断数据库中记录的clonezilla文件http是否能访问，如果不能访问，就是用http数据库中设置为默认的那项
            if ext_webconnection.judge_web_connection(http_svr) is not True:
                print('\n数据库已存在的clonezilla的http服务器不通，将使用默认的http服务器！\n')
                http_svr_find = HttpServerList.objects.filter(default=True)
                if http_svr_find[0].http_port == '':
                    if http_svr_find[0].http_folder == '':
                        http_svr = 'http://' + http_svr_find[0].http_ip  # http://192.168.96.96
                    else:
                        http_svr = 'http://' + http_svr_find[0].http_ip + http_svr_find[0].http_folder  # http://192.168.96.96/XX
                # 有端口号
                else:
                    if http_svr_find[0].http_folder == '':
                        http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[0].http_port  # http://192.168.96.96:8898
                    else:
                        http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[0].http_port + http_svr_find[0].http_folder  # http://192.168.96.96:8898/VV
                DefaultImageSelect.objects.filter(available=True).update(http_server=http_svr_find[0])
                print('自动修改默认启动镜像中http服务器地址为默认值：', http_svr)
                # 写入日志
                BootFromClonezillaLog.objects.create(
                    mac=mac,
                    ip=ip,
                    serial=serial,
                    image=image_name,
                    disk_num=disk_num,
                    http_path=http_svr,
                    samba_path=image_server_path,
                    get_tag=get_tag,
                    get_way='手动默认' + username,
                )
            else:
                # 写入日志
                BootFromClonezillaLog.objects.create(
                    mac=mac,
                    ip=ip,
                    serial=serial,
                    image=image_name,
                    disk_num=disk_num,
                    http_path=http_svr,
                    samba_path=image_server_path,
                    get_tag=get_tag,
                    get_way='系统记录By_' + username,
                )
            # 写入状态记录日志
            SystemInstallStatus.objects.create(
                mac=mac,
            )
            # http_server = HttpServerList.objects.filter(http_ip=default_image[0].http_server.http_ip)[0]

            # 如果启动数据库中不存在，则写入数据库，如果已存在，则根据mac地址修改数据库为新的信息
            if BootFromClonezilla.objects.filter(mac=mac).count() == 0:
                print('\n执行创建，添加新数据。')
                BootFromClonezilla.objects.create(
                    name=image_name + '-' + mac,
                    mac=mac,
                    http_server=HttpServerList.objects.filter(default=True)[0],
                    samba_server=SambaServerList.objects.filter(samba_ip=search_samba.samba_ip)[0],
                    image_path=image_path,
                    image_file=ImageFilesList.objects.filter(image_name=image_name)[0],
                    restore_disk=RestoreDiskNum.objects.filter(disk_num=disk_num)[0],
                    available=True,
                    explain='根据上次选择自动添加：' + str(datetime.datetime.now()) + '\n' + '创建人：' + username,
                )
            else:
                print('\n数据库已存在，更新数据。')
                # 更新说明记录
                explain = BootFromClonezilla.objects.filter(mac=mac)[0].explain
                BootFromClonezilla.objects.filter(mac=mac).update(
                    name=image_name + '-' + mac,
                    http_server=HttpServerList.objects.filter(default=True)[0],
                    samba_server=SambaServerList.objects.filter(samba_ip=search_samba.samba_ip)[0],
                    image_path=image_path,
                    image_file=ImageFilesList.objects.filter(image_name=image_name)[0],
                    restore_disk=RestoreDiskNum.objects.filter(disk_num=disk_num)[0],
                    available=True,
                    updated=timezone.now(),
                    explain=explain + '\n自动更新添加：' + str(datetime.datetime.now()) + '\n' + '更新人：' + username,
                )

            return render(request, 'script/boot_from_clonezilla.html',
                          {
                              'http_svr': http_svr,
                              'user_name': user_name,
                              'user_password': user_password,
                              'image_server_path': image_server_path,
                              'image_path': image_path,
                              'image_name': image_name,
                              'disk_num': disk_num,
                          })
        else:
            print('默认必须选择一项！')
            return render(request, 'error_page.html')

    # ==============================Clonezilla默认文件==============================
    elif boot == 'Clonezilla_Default':
        print('-----------选择clonezilla默认文件-----------')
        default_image = DefaultImageSelect.objects.filter(available=True)
        if default_image.count() == 1:
            get_tag = True

            http_svr_find = HttpServerList.objects.filter(default=True)
            if http_svr_find[0].http_port == '':
                if http_svr_find[0].http_folder == '':
                    http_svr = 'http://' + http_svr_find[0].http_ip  # http://192.168.96.96
                else:
                    http_svr = 'http://' + http_svr_find[0].http_ip + http_svr_find[
                        0].http_folder  # http://192.168.96.96/XX
            # 有端口号
            else:
                if http_svr_find[0].http_folder == '':
                    http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[
                        0].http_port  # http://192.168.96.96:8898
                else:
                    http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[0].http_port + \
                               http_svr_find[0].http_folder  # http://192.168.96.96:8898/VV

            BootFromClonezillaLog.objects.create(
                mac=mac,
                ip=ip,
                serial=serial,
                image=default_image[0].image_file,
                disk_num='',
                http_path=http_svr,
                samba_path='',
                get_tag=get_tag,
                get_way='默认镜像' + username,
            )
            return render(request, 'script/boot_from_clonezilla_default_image.html',
                          {
                              'http_svr': http_svr,
                          })
        else:
            # 写入日志
            BootFromClonezillaLog.objects.create(
                mac=mac,
                ip=ip,
                serial=serial,
                image='',
                disk_num='',
                http_path='',
                samba_path='',
                get_tag=get_tag,
            )
            return render(request, 'error_page.html')

    # ==============================启动ISO文件==============================
    elif boot == 'ISO':
        print('-----------选择ISO启动-----------')
        # select_iso = BootFromISO.objects.filter(available=True)  # 已在前面根据用户选择
        print(select_iso)
        if select_iso.count() == 1:
            get_tag = True
            # 无端口号
            if select_iso[0].http_server.http_port == '':
                if select_iso[0].http_server.http_folder == '':
                    http_svr = 'http://' + select_iso[0].http_server.http_ip
                else:
                    http_svr = 'http://' + select_iso[0].http_server.http_ip + select_iso[0].http_server.http_folder
            # 有端口号
            else:
                if select_iso[0].http_server.http_folder == '':
                    http_svr = 'http://' + select_iso[0].http_server.http_ip + ':' + select_iso[0].http_server.http_folder
                else:
                    http_svr = 'http://' + select_iso[0].http_server.http_ip + ':' + select_iso[0].http_server.http_port + select_iso[0].http_server.http_folder
            iso_file = select_iso[0].iso_file

            # 写入日志
            BootFromISOLog.objects.create(
                mac=mac,
                ip=ip,
                serial=serial,
                http_path=http_svr,
                iso_name=iso_file,
                get_tag=get_tag,
            )

            return render(request, 'script/boot_from_iso.html',
                          {
                              'http_svr': http_svr,
                              'iso_file': iso_file,
                          })
        else:
            # 写入日志
            BootFromISOLog.objects.create(
                mac=mac,
                ip=ip,
                serial=serial,
                http_path='',
                iso_name='',
                get_tag=get_tag,
            )
            return render(request, 'error_page.html')

    # ==============================Clonezilla自动选择硬盘恢复模式==============================
    elif boot == 'Clonezilla_Auto_SelectDisk':
        print('——————————选择clonezilla全自动选择硬盘恢复——————————')

        # 获取此时出口占用最低的samba服务器
        select_samba_ip = ext_netspeedout.get_use_samba()
        if select_samba_ip is False:
            # select_samba_ip = '192.168.96.99'
            default_samba = SambaServerList.objects.filter(default=True)
            if default_samba.count() == 1:
                select_samba_ip = default_samba[0].samba_ip
            else:
                select_samba_ip = '0.0.0.0'

            print('\n将使用默认Samba：', select_samba_ip)
        else:
            print('\n将使用自动选择的Samba：', select_samba_ip)

        # 从Samba列表中获取对应的用户名密码信息，get方式，必须保证数据库有值
        search_samba = SambaServerList.objects.get(samba_ip=select_samba_ip, available=True)
        image_server_path = '//' + search_samba.samba_ip + search_samba.samba_folder  # 构造samba目录： //192.168.96.99/images
        user_name = search_samba.samba_user
        user_password = search_samba.samba_password

        print('\n自动选择硬盘恢复，根据用户选择恢复！')
        # default_image = DefaultImageSelect.objects.filter(available=True)  # 已在前面说明
        if default_image.count() == 1:
            # 无端口号
            if default_image[0].http_server.http_port == '':
                if default_image[0].http_server.http_folder == '':
                    http_svr = 'http://' + default_image[0].http_server.http_ip  # http://192.168.96.96
                else:
                    http_svr = 'http://' + default_image[0].http_server.http_ip + default_image[
                        0].http_server.http_folder  # http://192.168.96.96/XX
            # 有端口号
            else:
                if default_image[0].http_server.http_folder == '':
                    http_svr = 'http://' + default_image[0].http_server.http_ip + ':' + default_image[
                        0].http_server.http_port  # http://192.168.96.96:8898
                else:
                    http_svr = 'http://' + default_image[0].http_server.http_ip + ':' + default_image[
                        0].http_server.http_port + default_image[
                                   0].http_server.http_folder  # http://192.168.96.96:8898/VV

                image_name = default_image[0].image_file.image_name
                disk_num = default_image[0].restore_disk.disk_num
                image_path = default_image[0].image_path

            # 判断数据库中记录的clonezilla文件http是否能访问，如果不能访问，就是用http数据库中设置为默认的那项
            if ext_webconnection.judge_web_connection(http_svr) is not True:
                print('\n数据库已存在的clonezilla的http服务器不通，将使用默认的http服务器！\n')
                http_svr_find = HttpServerList.objects.filter(default=True)
                if http_svr_find[0].http_port == '':
                    if http_svr_find[0].http_folder == '':
                        http_svr = 'http://' + http_svr_find[0].http_ip  # http://192.168.96.96
                    else:
                        http_svr = 'http://' + http_svr_find[0].http_ip + http_svr_find[
                            0].http_folder  # http://192.168.96.96/XX
                # 有端口号
                else:
                    if http_svr_find[0].http_folder == '':
                        http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[
                            0].http_port  # http://192.168.96.96:8898
                    else:
                        http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[0].http_port + \
                                   http_svr_find[0].http_folder  # http://192.168.96.96:8898/VV
                DefaultImageSelect.objects.filter(available=True).update(http_server=http_svr_find[0])
                print('自动修改默认启动镜像中http服务器地址为默认值：', http_svr)
                # 写入日志
                BootFromClonezillaLog.objects.create(
                    mac=mac,
                    ip=ip,
                    serial=serial,
                    image=image_name,
                    disk_num=disk_num,
                    http_path=http_svr,
                    samba_path=image_server_path,
                    get_tag=get_tag,
                    get_way='手动默认' + username,
                )
            else:
                # 写入日志
                BootFromClonezillaLog.objects.create(
                    mac=mac,
                    ip=ip,
                    serial=serial,
                    image=image_name,
                    disk_num=disk_num,
                    http_path=http_svr,
                    samba_path=image_server_path,
                    get_tag=get_tag,
                    get_way='系统记录By_' + username,
                )
            # 写入状态记录日志
            SystemInstallStatus.objects.create(
                mac=mac,
            )

            # http_server = HttpServerList.objects.filter(http_ip=default_image[0].http_server.http_ip)[0]

            # 如果启动数据库中不存在，则写入数据库，如果已存在，则根据mac地址修改数据库为新的信息
            if BootFromClonezilla.objects.filter(mac=mac).count() == 0:
                print('\n执行创建，添加新数据。')
                BootFromClonezilla.objects.create(
                    name=image_name + '-' + mac,
                    mac=mac,
                    http_server=HttpServerList.objects.filter(default=True)[0],
                    samba_server=SambaServerList.objects.filter(samba_ip=search_samba.samba_ip)[0],
                    image_path=image_path,
                    image_file=ImageFilesList.objects.filter(image_name=image_name)[0],
                    restore_disk=RestoreDiskNum.objects.filter(disk_num=disk_num)[0],
                    available=True,
                    explain='根据上次选择自动添加' + str(datetime.datetime.now()) + '\n' + '创建人：' + username,
                )
            else:
                print('\n数据库已存在该mac，更新数据。')
                explain = BootFromClonezilla.objects.filter(mac=mac)[0].explain
                BootFromClonezilla.objects.filter(mac=mac).update(
                    name=image_name + '-' + mac,
                    http_server=HttpServerList.objects.filter(default=True)[0],
                    samba_server=SambaServerList.objects.filter(samba_ip=search_samba.samba_ip)[0],
                    image_path=image_path,
                    image_file=ImageFilesList.objects.filter(image_name=image_name)[0],
                    restore_disk=RestoreDiskNum.objects.filter(disk_num=disk_num)[0],
                    available=True,
                    updated=timezone.now(),
                    explain=explain + '\n自动更新添加' + str(datetime.datetime.now()) + '\n' + '更新人：' + username,
                )

            return render(request, 'script/boot_from_clonezilla_auto_select_disk.html',
                          {
                              'http_svr': http_svr,
                              'user_name': user_name,
                              'user_password': user_password,
                              'image_server_path': image_server_path,
                              'image_path': image_path,
                              'image_name': image_name,
                              'disk_num': disk_num,
                          })
        else:
            print('默认必须选择一项！')
            return render(request, 'error_page.html')


def boot_select_old_notUse(request):
    mac = request.GET.get('mac')
    serial = request.GET.get('serial')
    if serial is None:
        serial = ''
    if mac is not None:
        # mac = mac.lower()
        mac = mac.upper()
    ip = request.GET.get('ip')
    if ip is None:
        ip = ''

    print('\n\nMAC:', mac, '\nIP:', ip, '\n\n')
    get_tag = False
    # 获取是否成功的标记，默认False，如果获取成功则为Ture

    # 增加用户标记
    username = request.GET.get('username')
    if username is not None and User.objects.filter(username=username).count() == 1:
        print('按照该用户表进行启动。。。')
        boot_name = User.objects.filter(username=username)[0].boot_select
        boot_clonezilla_id = User.objects.filter(username=username)[0].boot_clonezilla_id
        boot_iso_id = User.objects.filter(username=username)[0].boot_iso_id
        if (boot_name != '' and boot_clonezilla_id != 0) or (boot_name != '' and boot_iso_id != 0):
            user_choose = True
        else:
            user_choose = False
    else:
        print('用户表无正确值，按照数据库中默认项选择。。。')
        user_choose = False

    # 根据用户选择进行启动默认选择
    if user_choose is True:
        boot = boot_name
        default_image = DefaultImageSelect.objects.filter(id=User.objects.filter(username=username)[0].boot_clonezilla_id)
        select_iso = BootFromISO.objects.filter(id=User.objects.filter(username=username)[0].boot_iso_id)
    else:
        boot = BootSelect.objects.filter(available=True)[0].boot_name
        default_image = DefaultImageSelect.objects.filter(available=True)
        select_iso = BootFromISO.objects.filter(available=True)

    # ==============================Clonezilla自动恢复模式==============================
    if boot == 'Clonezilla_Auto':
        print('——————————选择clonezilla全自动恢复——————————')
        # 获取此时出口占用最低的samba服务器，如果没获取到值，则返回一个False，假如返回的是False，则在“Samba服务器管理”中选择默认项的IP地址
        select_samba_ip = ext_netspeedout.get_use_samba()
        if select_samba_ip is False:
            # select_samba_ip = '192.168.96.99'
            default_samba = SambaServerList.objects.filter(default=True)
            if default_samba.count() == 1:
                select_samba_ip = default_samba[0].samba_ip
            else:
                select_samba_ip = '0.0.0.0'
            print('\n将使用默认Samba：', select_samba_ip)
        else:
            print('\n将使用自动选择的Samba：', select_samba_ip)

        # 从Samba列表中获取对应的用户名密码信息，get方式，必须保证数据库有值
        search_samba = SambaServerList.objects.get(samba_ip=select_samba_ip, available=True)
        image_server_path = '//' + search_samba.samba_ip + search_samba.samba_folder  # 构造samba目录： //192.168.96.99/images
        user_name = search_samba.samba_user
        user_password = search_samba.samba_password

        # 从Clonezilla恢复列表查数据
        find_mac = BootFromClonezilla.objects.filter(mac=mac)

        # 如果BootFromClonezilla数据库中“自动启动管理”查到有启动mac的值，则直接从该项中获取
        if find_mac.count() == 1:
            print('\nBootFromClonezilla数据库中有条目，直接从数据库中获取该数据！')
            # 无端口号
            if find_mac[0].http_server.http_port == '':
                if find_mac[0].http_server.http_folder == '':
                    http_svr = 'http://' + find_mac[0].http_server.http_ip  # http://192.168.96.96
                else:
                    http_svr = 'http://' + find_mac[0].http_server.http_ip + find_mac[0].http_server.http_folder  # http://192.168.96.96/XX
            # 有端口号
            else:
                if find_mac[0].http_server.http_folder == '':
                    http_svr = 'http://' + find_mac[0].http_server.http_ip + ':' + find_mac[0].http_server.http_port  # http://192.168.96.96:8898
                else:
                    http_svr = 'http://' + find_mac[0].http_server.http_ip + ':' + find_mac[0].http_server.http_port + find_mac[0].http_server.http_folder  # http://192.168.96.96:8898/VV
            # print('判断网络通断\n\n',ext_webconnection.judge_web_connection(http_svr),find_mac[0].http_server.available)
            # 判断数据库中记录的clonezilla文件http是否能访问，如果不能访问，就使用http数据库中设置为默认的那项
            if ext_webconnection.judge_web_connection(http_svr) is not True or find_mac[0].http_server.available is False:
                print('\n数据库已存在的clonezilla的http服务器不通，或该Http服务器未启用，将使用默认的http服务器！\n')
                http_svr_find = HttpServerList.objects.filter(available=True, default=True)
                if http_svr_find[0].http_port == '':
                    if http_svr_find[0].http_folder == '':
                        http_svr = 'http://' + http_svr_find[0].http_ip  # http://192.168.96.96
                    else:
                        http_svr = 'http://' + http_svr_find[0].http_ip + http_svr_find[0].http_folder  # http://192.168.96.96/XX
                # 有端口号
                else:
                    if http_svr_find[0].http_folder == '':
                        http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[0].http_port  # http://192.168.96.96:8898
                    else:
                        http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[0].http_port + http_svr_find[0].http_folder  # http://192.168.96.96:8898/VV
                BootFromClonezilla.objects.filter(mac=mac).update(http_server=http_svr_find[0])
                print('自动修改自动启动中http服务器地址为默认值：', http_svr)

            # 镜像名称
            image_name = find_mac[0].image_file.image_name
            # 镜像加载路径
            image_path = find_mac[0].image_path
            # 恢复硬盘编号
            disk_num = find_mac[0].restore_disk.disk_num

            get_tag = True

            # 写入日志
            BootFromClonezillaLog.objects.create(
                mac=mac,
                ip=ip,
                serial=serial,
                image=image_name,
                disk_num=disk_num,
                http_path=http_svr,
                samba_path=image_server_path,
                get_tag=get_tag,
                get_way='全自动',
            )
            # 写入状态记录日志
            SystemInstallStatus.objects.create(
                mac=mac,
            )
            return render(request, 'script/boot_from_clonezilla.html',
                          {
                              'http_svr': http_svr,
                              'user_name': user_name,
                              'user_password': user_password,
                              'image_server_path': image_server_path,
                              'image_path': image_path,
                              'image_name': image_name,
                              'disk_num': disk_num,
                          })

        # 如果BootFromClonezilla数据库中没有值，则在DefaultImageSelect默认镜像选择中查找
        else:
            print('\nBootFromClonezilla数据库中未找到，使用默认选择执行！')
            # default_image = DefaultImageSelect.objects.filter(available=True)  # 前面根据用户选择进行
            if default_image.count() == 1:
                # 无端口号
                if default_image[0].http_server.http_port == '':
                    if default_image[0].http_server.http_folder == '':
                        http_svr = 'http://' + default_image[0].http_server.http_ip  # http://192.168.96.96
                    else:
                        http_svr = 'http://' + default_image[0].http_server.http_ip + default_image[0].http_server.http_folder  # http://192.168.96.96/XX
                # 有端口号
                else:
                    if default_image[0].http_server.http_folder == '':
                        http_svr = 'http://' + default_image[0].http_server.http_ip + ':' + default_image[0].http_server.http_port  # http://192.168.96.96:8898
                    else:
                        http_svr = 'http://' + default_image[0].http_server.http_ip + ':' + default_image[0].http_server.http_port + default_image[0].http_server.http_folder  # http://192.168.96.96:8898/VV

                # 判断数据库中记录的clonezilla文件http是否能访问，如果不能访问，就是用http数据库中设置为默认的那项
                if ext_webconnection.judge_web_connection(http_svr) != True:
                    print('\n数据库已存在的clonezilla的http服务器不通，将使用默认的http服务器！\n')
                    http_svr_find = HttpServerList.objects.filter(default=True)
                    if http_svr_find[0].http_port == '':
                        if http_svr_find[0].http_folder == '':
                            http_svr = 'http://' + http_svr_find[0].http_ip  # http://192.168.96.96
                        else:
                            http_svr = 'http://' + http_svr_find[0].http_ip + http_svr_find[0].http_folder  # http://192.168.96.96/XX
                    # 有端口号
                    else:
                        if http_svr_find[0].http_folder == '':
                            http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[0].http_port  # http://192.168.96.96:8898
                        else:
                            http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[0].http_port + http_svr_find[0].http_folder  # http://192.168.96.96:8898/VV
                    DefaultImageSelect.objects.filter(available=True).update(http_server=http_svr_find[0])
                    print('自动修改默认启动镜像中http服务器地址为默认值：', http_svr)

                image_name = default_image[0].image_file.image_name
                disk_num = default_image[0].restore_disk.disk_num
                image_path = default_image[0].image_path

                # 写入日志
                BootFromClonezillaLog.objects.create(
                    mac=mac,
                    ip=ip,
                    serial=serial,
                    image=image_name,
                    disk_num=disk_num,
                    http_path=http_svr,
                    samba_path=image_server_path,
                    get_tag=get_tag,
                    get_way='手动',
                )
                # 写入状态记录日志
                SystemInstallStatus.objects.create(
                    mac=mac,
                )
                # http_server = HttpServerList.objects.filter(http_ip=default_image[0].http_server.http_ip)[0]

                # 如果启动数据库中不存在，则写入数据库，如果已存在，则根据mac地址修改数据库为新的信息
                if BootFromClonezilla.objects.filter(mac=mac).count() == 0:
                    print('\n执行创建，添加新数据。')
                    BootFromClonezilla.objects.create(
                        name=image_name + '-' + mac,
                        mac=mac,
                        http_server=HttpServerList.objects.filter(default=True)[0],
                        samba_server=SambaServerList.objects.filter(samba_ip=search_samba.samba_ip)[0],
                        image_path=image_path,
                        image_file=ImageFilesList.objects.filter(image_name=image_name)[0],
                        restore_disk=RestoreDiskNum.objects.filter(disk_num=disk_num)[0],
                        available=True,
                        explain='根据上次选择自动添加' + str(datetime.datetime.now()),
                    )

                return render(request, 'script/boot_from_clonezilla.html',
                              {
                                  'http_svr': http_svr,
                                  'user_name': user_name,
                                  'user_password': user_password,
                                  'image_server_path': image_server_path,
                                  'image_path': image_path,
                                  'image_name': image_name,
                                  'disk_num': disk_num,
                              })
            else:
                print('默认必须选择一项！')
                return render(request, 'error_page.html')

    # ==============================Clonezilla默认文件==============================
    elif boot == 'Clonezilla_Default':
        print('-----------选择clonezilla默认文件-----------')
        default_image = DefaultImageSelect.objects.filter(available=True)
        if default_image.count() == 1:
            get_tag = True

            http_svr_find = HttpServerList.objects.filter(default=True)
            if http_svr_find[0].http_port == '':
                if http_svr_find[0].http_folder == '':
                    http_svr = 'http://' + http_svr_find[0].http_ip  # http://192.168.96.96
                else:
                    http_svr = 'http://' + http_svr_find[0].http_ip + http_svr_find[
                        0].http_folder  # http://192.168.96.96/XX
            # 有端口号
            else:
                if http_svr_find[0].http_folder == '':
                    http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[
                        0].http_port  # http://192.168.96.96:8898
                else:
                    http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[0].http_port + \
                               http_svr_find[0].http_folder  # http://192.168.96.96:8898/VV

            BootFromClonezillaLog.objects.create(
                mac=mac,
                ip=ip,
                serial=serial,
                image=default_image[0].image_file,
                disk_num='',
                http_path=http_svr,
                samba_path='',
                get_tag=get_tag,
                get_way='默认',
            )
            return render(request, 'script/boot_from_clonezilla_default_image.html',
                          {
                              'http_svr': http_svr,
                          })
        else:
            # 写入日志
            BootFromClonezillaLog.objects.create(
                mac=mac,
                ip=ip,
                serial=serial,
                image='',
                disk_num='',
                http_path='',
                samba_path='',
                get_tag=get_tag,
            )
            return render(request, 'error_page.html')

    # ==============================启动ISO文件==============================
    elif boot == 'ISO':
        print('-----------选择ISO启动-----------')
        # select_iso = BootFromISO.objects.filter(available=True)  # 已在前面根据用户选择
        print(select_iso)
        if select_iso.count() == 1:
            get_tag = True
            # 无端口号
            if select_iso[0].http_server.http_port == '':
                if select_iso[0].http_server.http_folder == '':
                    http_svr = 'http://' + select_iso[0].http_server.http_ip
                else:
                    http_svr = 'http://' + select_iso[0].http_server.http_ip + select_iso[0].http_server.http_folder
            # 有端口号
            else:
                if select_iso[0].http_server.http_folder == '':
                    http_svr = 'http://' + select_iso[0].http_server.http_ip + ':' + select_iso[0].http_server.http_folder
                else:
                    http_svr = 'http://' + select_iso[0].http_server.http_ip + ':' + select_iso[0].http_server.http_port + select_iso[0].http_server.http_folder
            iso_file = select_iso[0].iso_file

            # 写入日志
            BootFromISOLog.objects.create(
                mac=mac,
                ip=ip,
                serial=serial,
                http_path=http_svr,
                iso_name=iso_file,
                get_tag=get_tag,
            )

            return render(request, 'script/boot_from_iso.html',
                          {
                              'http_svr': http_svr,
                              'iso_file': iso_file,
                          })
        else:
            # 写入日志
            BootFromISOLog.objects.create(
                mac=mac,
                ip=ip,
                serial=serial,
                http_path='',
                iso_name='',
                get_tag=get_tag,
            )
            return render(request, 'error_page.html')

    # ==============================Clonezilla自动选择硬盘恢复模式==============================
    elif boot == 'Clonezilla_Auto_SelectDisk':
        print('——————————选择clonezilla全自动选择硬盘恢复——————————')

        # 获取此时出口占用最低的samba服务器
        select_samba_ip = ext_netspeedout.get_use_samba()
        if select_samba_ip is False:
            # select_samba_ip = '192.168.96.99'
            default_samba = SambaServerList.objects.filter(default=True)
            if default_samba.count() == 1:
                select_samba_ip = default_samba[0].samba_ip
            else:
                select_samba_ip = '0.0.0.0'

            print('\n将使用默认Samba：', select_samba_ip)
        else:
            print('\n将使用自动选择的Samba：', select_samba_ip)

        # 从Samba列表中获取对应的用户名密码信息，get方式，必须保证数据库有值
        search_samba = SambaServerList.objects.get(samba_ip=select_samba_ip, available=True)
        image_server_path = '//' + search_samba.samba_ip + search_samba.samba_folder  # 构造samba目录： //192.168.96.99/images
        user_name = search_samba.samba_user
        user_password = search_samba.samba_password

        # 从Clonezilla恢复列表查数据
        find_mac = BootFromClonezilla.objects.filter(mac=mac)

        # 如果BootFromClonezilla数据库中查到有这个值
        if find_mac.count() == 1:
            print('\nBootFromClonezilla数据库中有条目，直接从数据库中获取该数据！')
            # 无端口号
            if find_mac[0].http_server.http_port == '':
                if find_mac[0].http_server.http_folder == '':
                    http_svr = 'http://' + find_mac[0].http_server.http_ip  # http://192.168.96.96
                else:
                    http_svr = 'http://' + find_mac[0].http_server.http_ip + find_mac[
                        0].http_server.http_folder  # http://192.168.96.96/XX
            # 有端口号
            else:
                if find_mac[0].http_server.http_folder == '':
                    http_svr = 'http://' + find_mac[0].http_server.http_ip + ':' + find_mac[
                        0].http_server.http_port  # http://192.168.96.96:8898
                else:
                    http_svr = 'http://' + find_mac[0].http_server.http_ip + ':' + find_mac[
                        0].http_server.http_port + find_mac[
                                   0].http_server.http_folder  # http://192.168.96.96:8898/VV

            # 判断数据库中记录的clonezilla文件http是否能访问，如果不能访问，就是用http数据库中设置为默认的那项
            if ext_webconnection.judge_web_connection(http_svr) is not True or find_mac[0].http_server.available is False:
                print('\n数据库已存在的clonezilla的http服务器不通，或者HTTP处于关闭状态，将使用默认的http服务器！\n')
                http_svr_find = HttpServerList.objects.filter(available=True, default=True)
                if http_svr_find[0].http_port == '':
                    if http_svr_find[0].http_folder == '':
                        http_svr = 'http://' + http_svr_find[0].http_ip  # http://192.168.96.96
                    else:
                        http_svr = 'http://' + http_svr_find[0].http_ip + http_svr_find[
                            0].http_folder  # http://192.168.96.96/XX
                # 有端口号
                else:
                    if http_svr_find[0].http_folder == '':
                        http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[
                            0].http_port  # http://192.168.96.96:8898
                    else:
                        http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[0].http_port + \
                                   http_svr_find[0].http_folder  # http://192.168.96.96:8898/VV
                BootFromClonezilla.objects.filter(mac=mac).update(http_server=http_svr_find[0])
                print('自动修改自动启动中http服务器地址为默认值：', http_svr)

            # 镜像名称
            image_name = find_mac[0].image_file.image_name
            # 镜像加载路径
            image_path = find_mac[0].image_path
            # 恢复硬盘编号
            disk_num = find_mac[0].restore_disk.disk_num

            get_tag = True

            # 写入日志
            BootFromClonezillaLog.objects.create(
                mac=mac,
                ip=ip,
                serial=serial,
                image=image_name,
                disk_num=disk_num,
                http_path=http_svr,
                samba_path=image_server_path,
                get_tag=get_tag,
                get_way='全自动',
            )
            # 写入状态记录日志
            SystemInstallStatus.objects.create(
                mac=mac,
            )
            return render(request, 'script/boot_from_clonezilla_auto_select_disk.html',
                          {
                              'http_svr': http_svr,
                              'user_name': user_name,
                              'user_password': user_password,
                              'image_server_path': image_server_path,
                              'image_path': image_path,
                              'image_name': image_name,
                              'disk_num': disk_num,
                          })

        # 如果BootFromClonezilla数据库中没有值，则在DefaultImageSelect默认镜像选择中查找
        else:
            print('\nBootFromClonezilla数据库中未找到，使用默认选择执行！')
            # default_image = DefaultImageSelect.objects.filter(available=True)  # 已在前面说明
            if default_image.count() == 1:
                # 无端口号
                if default_image[0].http_server.http_port == '':
                    if default_image[0].http_server.http_folder == '':
                        http_svr = 'http://' + default_image[0].http_server.http_ip  # http://192.168.96.96
                    else:
                        http_svr = 'http://' + default_image[0].http_server.http_ip + default_image[
                            0].http_server.http_folder  # http://192.168.96.96/XX
                # 有端口号
                else:
                    if default_image[0].http_server.http_folder == '':
                        http_svr = 'http://' + default_image[0].http_server.http_ip + ':' + default_image[
                            0].http_server.http_port  # http://192.168.96.96:8898
                    else:
                        http_svr = 'http://' + default_image[0].http_server.http_ip + ':' + default_image[
                            0].http_server.http_port + default_image[
                                       0].http_server.http_folder  # http://192.168.96.96:8898/VV

                # 判断数据库中记录的clonezilla文件http是否能访问，如果不能访问，就是用http数据库中设置为默认的那项
                if ext_webconnection.judge_web_connection(http_svr) != True:
                    print('\n数据库已存在的clonezilla的http服务器不通，将使用默认的http服务器！\n')
                    http_svr_find = HttpServerList.objects.filter(default=True)
                    if http_svr_find[0].http_port == '':
                        if http_svr_find[0].http_folder == '':
                            http_svr = 'http://' + http_svr_find[0].http_ip  # http://192.168.96.96
                        else:
                            http_svr = 'http://' + http_svr_find[0].http_ip + http_svr_find[
                                0].http_folder  # http://192.168.96.96/XX
                    # 有端口号
                    else:
                        if http_svr_find[0].http_folder == '':
                            http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[
                                0].http_port  # http://192.168.96.96:8898
                        else:
                            http_svr = 'http://' + http_svr_find[0].http_ip + ':' + http_svr_find[0].http_port + \
                                       http_svr_find[0].http_folder  # http://192.168.96.96:8898/VV
                    DefaultImageSelect.objects.filter(available=True).update(http_server=http_svr_find[0])
                    print('自动修改默认启动镜像中http服务器地址为默认值：', http_svr)

                image_name = default_image[0].image_file.image_name
                disk_num = default_image[0].restore_disk.disk_num
                image_path = default_image[0].image_path

                # 写入日志
                BootFromClonezillaLog.objects.create(
                    mac=mac,
                    ip=ip,
                    serial=serial,
                    image=image_name,
                    disk_num=disk_num,
                    http_path=http_svr,
                    samba_path=image_server_path,
                    get_tag=get_tag,
                    get_way='手动',
                )
                # 写入状态记录日志
                SystemInstallStatus.objects.create(
                    mac=mac,
                )

                # http_server = HttpServerList.objects.filter(http_ip=default_image[0].http_server.http_ip)[0]

                # 如果启动数据库中不存在，则写入数据库，如果已存在，则根据mac地址修改数据库为新的信息
                if BootFromClonezilla.objects.filter(mac=mac).count() == 0:
                    print('\n执行创建，添加新数据。')
                    BootFromClonezilla.objects.create(
                        name=image_name + '-' + mac,
                        mac=mac,
                        http_server=HttpServerList.objects.filter(default=True)[0],
                        samba_server=SambaServerList.objects.filter(samba_ip=search_samba.samba_ip)[0],
                        image_path=image_path,
                        image_file=ImageFilesList.objects.filter(image_name=image_name)[0],
                        restore_disk=RestoreDiskNum.objects.filter(disk_num=disk_num)[0],
                        available=True,
                        explain='根据上次选择自动添加' + str(datetime.datetime.now()),
                    )

                return render(request, 'script/boot_from_clonezilla_auto_select_disk.html',
                              {
                                  'http_svr': http_svr,
                                  'user_name': user_name,
                                  'user_password': user_password,
                                  'image_server_path': image_server_path,
                                  'image_path': image_path,
                                  'image_name': image_name,
                                  'disk_num': disk_num,
                              })
            else:
                print('默认必须选择一项！')
                return render(request, 'error_page.html')


# 网页选择启动控制 ->ISO文件、Clonezilla无参数版、Clonezilla全自动版
def select_boot_control(request):
    username = request.session['session_name']
    if User.objects.filter(username=username).count() == 1:
        print('用户 %s 已有权限访问！' % username)
        if request.method == 'POST':
            print('\n选择启动控制：POST')
            boot_select_list = BootSelect.objects.all()
            get_select = request.POST.get('get_select')
            print(get_select)

            # 将切换的启动项记录到用户表中2017.10.22
            if User.objects.filter(username=username).count() == 1:
                User.objects.filter(username=username).update(boot_select=get_select)
                print('记录选择启动控制 %s 到用户 %s 数据库' % (get_select, username))

            for boot in boot_select_list:
                # 循环获取启动选择，如果启动选择的名称和前端传过来的值相同，则将启动设置为True
                if get_select == boot.boot_name:
                    print(boot.name + '的状态：' + str(boot.available))
                    # 所选择的设置为True，其他的设置为False
                    BootSelect.objects.filter(boot_name=get_select).update(available=True)
                    BootSelect.objects.exclude(boot_name=get_select).update(available=False)

            backup_name = ''
            for http in HttpServerList.objects.all():
                if '默认备份' in http.http_name:
                    backup_name = http.http_name
                if '默认恢复' in http.http_name:
                    recovery_name = http.http_name
                if '自动硬盘选择' in http.http_name:
                    auto_select_disk = http.http_name

            # 默认ISO启动的选项
            boot_iso = ''
            for iso in BootFromISO.objects.all():
                if 'WePE' in iso.name:
                    boot_iso = iso.name

            # 如果get_select==Clonezilla_Default，则启用默认项，选择Http服务器中（http服务器名称）字段中有备份的字符
            if get_select == 'Clonezilla_Default':
                HttpServerList.objects.filter(http_name=backup_name).update(default=True, available=True)
                HttpServerList.objects.exclude(http_name=backup_name).update(default=False)
                info = '选择【默认Clonezilla】，自动切换Http服务器选项：' + backup_name

            # 如果get_select==Clonezilla_Auto，则启用默认项，选择Http服务器中（http服务器名称）字段中有备恢复的字符
            elif get_select == 'Clonezilla_Auto':
                HttpServerList.objects.filter(http_name=recovery_name).update(default=True, available=True)
                HttpServerList.objects.exclude(http_name=recovery_name).update(default=False)
                info = '选择【自动恢复Clonezilla】，自动切换Http服务器选项：' + recovery_name
            elif get_select == 'ISO':
                BootFromISO.objects.filter(name=boot_iso).update(available=True)
                BootFromISO.objects.exclude(name=boot_iso).update(available=False)
                info = '选择ISO启动项，自动切换【WePE.iso】，如需修改其他，前往【ISO默认启动控制】处修改。'

                # 将选择启动的id加入到用户表中2017.10.22
                if BootFromISO.objects.filter(available=True).count() == 1:
                    boot_iso_id = BootFromISO.objects.filter(available=True)[0].id
                    User.objects.filter(username=username).update(boot_iso_id=boot_iso_id)
                    print('更新用户表ISO的id为 %s' % boot_iso_id)

            elif get_select == "Clonezilla_Auto_SelectDisk":
                HttpServerList.objects.filter(http_name=auto_select_disk).update(default=True, available=True)
                HttpServerList.objects.exclude(http_name=auto_select_disk).update(default=False)
                info = '选择【自动选择硬盘恢复Clonezilla】，自动切换Http服务器选项：' + auto_select_disk
            else:
                info = '选择了其它项！'

            boot_select_list = BootSelect.objects.all().order_by("name")
            return render(request, 'manager/select_boot_control.html',
                          {
                              'boot_select_list': boot_select_list,
                              'info': info
                          })

        else:
            boot_select_list = BootSelect.objects.all().order_by("name")
            print('\n选择启动控制：GET')
            # 启动的方式名称
            return render(request, 'manager/select_boot_control.html',
                          {
                              'boot_select_list': boot_select_list,
                          })
    else:
        print('未登录！请登陆后操作。')
        # return render(request, 'user/login.html')
        return HttpResponseRedirect('/user/login?next=%s' % request.path)


# 显示当前选择的启动
def show_current_select_boot(request):
    # 修改为显示每个用户启动选择2017.10.22
    try:
        username = request.session['session_name']
        print('当前用户：', username)
    except KeyError:
        username = request.session['session_name'] = '匿名'
    # 如果当前用户为匿名，或用户表选择记录为空时，则使用选择控制的默认选择，如果当前用户已有选择，则使用该用户自己的选择2017.10.22
    if username == '匿名':
        current_select = BootSelect.objects.get(available=True)
        select1 = current_select.name
        if 'Clonezilla' in current_select.boot_name:
            # select2 = DefaultImageSelect.objects.get(available=True).select_name
            if DefaultImageSelect.objects.filter(available=True).count() == 1:
                select2 = DefaultImageSelect.objects.get(available=True).select_name
            else:
                select2 = '启动Clonezilla选择错误！'
            # print(select2)
        elif 'ISO' in current_select.boot_name:
            # select2 = BootFromISO.objects.get(available=True).name
            if BootFromISO.objects.filter(available=True).count() == 1:
                select2 = BootFromISO.objects.get(available=True).name
            else:
                select2 = '启动ISO选择错误！'
        else:
            select2 = '启动文件未选择！'
    else:
        boot_name = User.objects.filter(username=username)[0].boot_select
        boot_clonezilla_id = User.objects.filter(username=username)[0].boot_clonezilla_id
        boot_iso_id = User.objects.filter(username=username)[0].boot_iso_id

        if (boot_name != '' and boot_clonezilla_id != 0) or (boot_name != '' and boot_iso_id != 0):
            current_select = BootSelect.objects.get(boot_name=boot_name)
            select1 = current_select.name
            if 'Clonezilla' in current_select.boot_name:
                if DefaultImageSelect.objects.filter(id=boot_clonezilla_id).count() == 1:
                    select2 = DefaultImageSelect.objects.get(id=boot_clonezilla_id).select_name
                else:
                    select2 = '启动Clonezilla选择错误！'
                # print(select2)
            elif 'ISO' in current_select.boot_name:
                if BootFromISO.objects.filter(id=boot_iso_id).count() == 1:
                    select2 = BootFromISO.objects.get(id=boot_iso_id).name
                else:
                    select2 = '启动ISO选择错误！'
            else:
                select2 = '启动方式未选择'
        else:
            current_select = BootSelect.objects.get(available=True)
            select1 = current_select.name
            if 'Clonezilla' in current_select.boot_name:
                if DefaultImageSelect.objects.filter(available=True).count() == 1:
                    select2 = DefaultImageSelect.objects.get(available=True).select_name
                    print('!!!!!!!!!!!!!!')
                else:
                    select2 = '启动Clonezilla选择错误！'
                # print(select2)
            elif 'ISO' in current_select.boot_name:
                if BootFromISO.objects.filter(available=True).count() == 1:
                    select2 = BootFromISO.objects.get(available=True).name
                else:
                    select2 = '启动ISO选择错误！'
            else:
                select2 = '启动文件未选择！'

    return HttpResponse('<b>当前选择：</b><br>' + select1 + '<br> >>> <br>' + select2)


# 文档说明
def document(request):
    return render(request, 'document/common_command.html')


# 安装系统前请求
def start_request(request):
    mac = request.GET.get('mac')
    mac = mac.upper()
    ip = request.GET.get('ip')
    print('\n\n系统开始安装------->')
    if ip is not None and mac is not None:
        print(mac + '   ' + ip + '\n\n')
    start_time = timezone.now()  # 统一使用UTC时间
    print(start_time)
    SystemInstallStatus.objects.filter(mac=mac, status='-1').update(start_time=start_time, status='0')

    return HttpResponse('start')


# 完成系统安装后请求
def complete_request(request):
    mac = request.GET.get('mac')
    mac = mac.upper()
    ip = request.GET.get('ip')
    print('\n\n<-------系统安装完成')
    if ip is not None and mac is not None:
        print(mac + '   ' + ip + '\n\n')
    # complete_time = datetime.datetime.now()
    complete_time = timezone.now()  # 统一使用UTC时间
    # print(complete_time)
    if SystemInstallStatus.objects.filter(mac=mac, status='0').count() != 0:
        start_time = SystemInstallStatus.objects.filter(mac=mac, status='0')[0].complete_time
        # print(start_time)
        time_difference = complete_time - start_time
        # print(str(time_difference).split('.')[0])
        print(time_difference.total_seconds(), type(time_difference))
        m, s = divmod(float(time_difference.total_seconds()), 60)
        # 秒转换成分钟+秒形式

        # print('使用 ' + str(time_difference.total_seconds() / 60).split('.')[0] + '分钟！')
        # process_time = str(time_difference.total_seconds() / 60).split('.')[0]

        process_time = str(int(m)) + "分" + str(int(s)) + '秒'
        print(process_time)

        SystemInstallStatus.objects.filter(mac=mac, status='0').update(
            complete_time=complete_time,
            status='1',
            process_time=process_time
        )
    # return render(request, 'complete_request.html')
    return HttpResponse('complete')


# 显示这个系统的更新日志
def update_logs(request):
    logs = UpdateLog.objects.all().order_by('-created')
    return render(request, 'logs/updatelogs.html',
                  {
                      'logs': logs,
                  })


# 获取最新的版本号
def get_new_version(request):
    update_logs_list = UpdateLog.objects.all().order_by('-created')
    if update_logs_list.count() != 0:
        version = update_logs_list[0]
    else:
        version = 'Beta 0.0.0'
    return HttpResponse(version)
