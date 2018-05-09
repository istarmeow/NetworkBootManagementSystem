# -*- coding:utf-8 -*-

from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .models import BootFromISO, User, HttpServerList
from django.db import models
import datetime
import time
import re
import os
from django.conf import settings
from django.db.models import Q
import urllib


# 选择启动哪个服务器的哪个ISO文件
def select_boot_iso_control(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    username = request.session['session_name']
    if request.method == 'POST':
        print('\n选择ISO启动控制：POST')
        boot_select_list = BootFromISO.objects.all()
        get_select = request.POST.get('get_select')
        for boot in boot_select_list:
            # 循环获取启动选择，如果启动选择的名称和前端传过来的值相同，则将启动设置为True
            if get_select == boot.name:
                print(boot.name + '的状态：' + str(boot.available))
                # 所选择的设置为True，其他的设置为False
                BootFromISO.objects.filter(name=get_select).update(available=True)
                BootFromISO.objects.exclude(name=get_select).update(available=False)
                # 将选择启动的id加入到用户表中2017.10.22
                if BootFromISO.objects.filter(available=True).count() == 1:
                    boot_iso_id = BootFromISO.objects.filter(available=True)[0].id
                    User.objects.filter(username=username).update(boot_iso_id=boot_iso_id)
                    print('更新用户表ISO的id为 %s' % boot_iso_id)

        boot_select_list = BootFromISO.objects.all().order_by('name', 'http_server')
        return render(request, 'manager/boot_from_iso/select_boot_iso_control.html',
                      {
                          'boot_select_list': boot_select_list,
                      })
    if request.method == 'GET':
        print('\n选择ISO启动控制：GET')
        boot_select_list = BootFromISO.objects.all().order_by('name', 'http_server')
        return render(request, 'manager/boot_from_iso/select_boot_iso_control.html',
                      {
                              'boot_select_list': boot_select_list,
                      })


# 获取iso文件列表保存到数据库
def sync_iso_file(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'

    if User.objects.filter(username=request.session['session_name'], auth_add=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        ip = request.GET.get('ip')
        port = request.GET.get('port')
        folder = request.GET.get('folder')
        print(folder)
        url = 'http://%s:8898/get_iso_list' % ip
        print(url)
        try:
            with urllib.request.urlopen(url, timeout=5) as req:
                if req.getcode() == 200:
                    date = req.read().decode('utf-8')
                    if '|' in date:
                        iso_list = date.split('|')
                        print(iso_list)
                    else:
                        iso_list = list(date)

                    http_server = HttpServerList.objects.filter(http_ip=ip, http_port=port, http_folder=folder)
                    if http_server.count() < 1:
                        pass
                    else:
                        for iso_name in iso_list:
                            if BootFromISO.objects.filter(http_server=http_server, iso_file=iso_name).count() == 0:
                                print('执行同步更新！')
                                BootFromISO.objects.create(
                                    name='启动'+iso_name.replace('.iso', ''),
                                    http_server=http_server[0],
                                    iso_file=iso_name,
                                    available=False,
                                    explain='自动同步增加'

                                )
                            else:
                                print('数据库已存在，执行信息更新！')
                                BootFromISO.objects.filter(http_server=http_server, iso_file=iso_name).update(
                                    name='启动' + iso_name.replace('.iso', ''),
                                    http_server=http_server[0],
                                    iso_file=iso_name,
                                    available=False,
                                    explain='自动同步增加'
                                )
                        # 删除对应http服务器iso文件不在获取的iso列表中的
                        for iso in BootFromISO.objects.filter(http_server=http_server).all():
                            if iso.iso_file not in iso_list:
                                BootFromISO.objects.filter(http_server=http_server, iso_file=iso.iso_file).delete()
                                print('删除镜像文件列表：', iso.iso_file)
                else:
                    print('无法连接！')
        except urllib.error.URLError:
            print('连接错误！')
        return HttpResponseRedirect('/manage/select_boot_iso_control.html')

    else:
        print('用户不存在！返回登录页面', request.path)
        if User.objects.filter(username=request.session['session_name']).count() == 1:
            print('用户 %s 无权限！' % request.session['session_name'])
            return render(request, 'user/unauth_access.html')
        else:
            print('未登录！请登陆后操作。')
            # return render(request, 'user/login.html')
            return HttpResponseRedirect('/user/login?next=%s' % request.path)


# 删除iso文件
def del_iso_select(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'

    if User.objects.filter(username=request.session['session_name'], auth_del=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        del_id = request.GET.get('del_id')
        print('删除ISO', del_id)
        BootFromISO.objects.filter(id=del_id).delete()
        return HttpResponseRedirect('/manage/select_boot_iso_control.html')

    else:
        print('用户不存在！返回登录页面', request.path)
        if User.objects.filter(username=request.session['session_name']).count() == 1:
            print('用户 %s 无权限！' % request.session['session_name'])
            return render(request, 'user/unauth_access.html')
        else:
            print('未登录！请登陆后操作。')
            # return render(request, 'user/login.html')
            return HttpResponseRedirect('/user/login?next=%s' % request.path)






# ############################################################################################
# PXE启动获取，通过get获取url的参数，然后查找数据库，如果数据库没有则，记录日志
def boot_from_iso(request):
    mac = request.GET.get('mac')
    serial = request.GET.get('serial')
    if serial is None:
        serial = ''
    if mac is not None:
        mac = mac.lower()
    ip = request.GET.get('ip')
    if ip is None:
        ip = ''
    print('\n\nMAC:', mac, '\nIP:', ip, '\n\n')
    get_tag = False
    # 获取是否成功的标记，默认False，如果获取成功则为Ture
    try:
        find_mac = BootFromISO.objects.get(mac='%s' % mac, available=True)
        # 在数据库中查找mac地址为该值，且已启用的数据
        http_url = find_mac.iso_svr
        iso_file = find_mac.iso_name
        get_tag = True

    except models.ObjectDoesNotExist:
        http_url = None
        iso_file = None
    finally:
        print(datetime.datetime.now())
        BootFromISOLog.objects.create(mac=mac, ip=ip, get_tag=get_tag, serial=serial)
        return render(request, 'script/boot_from_iso.html',
                      {
                          'http_url': http_url,
                          'iso_file': iso_file,
                      })


# # 简单的查询，只有模糊查询名称get方法
def query_boot_from_iso_info_get(request):
    name = request.GET.get('name')
    # print(name)
    # 判断传入的字符串是否是空值SearchGetBootImages.html?name=，或者SearchGetBootImages.html?name= 传入空值
    if name is None or len(name) == 0:
        boot_iso_list = BootFromISO.objects.all()
        name = ''
    else:
        # 固定搜索
        # boot_iso_list = BootFromImage.objects.filter(name=name)
        # 模糊搜索
        boot_iso_list = BootFromISO.objects.filter(name__icontains=name)
        name = '查询关键词：' + name

    # boot_iso_list = BootFromImage.objects.all()
    # print(boot_iso_list)
    # 查询得到一个QuerySet
    return render(request, 'manager/boot_from_iso/query_boot_from_iso_info_get.html', {'boot_iso_list': boot_iso_list, 'searchName': name})


# 使用post有选择性的综合查询
def query_boot_from_iso_info_post(request):
    select = request.POST.get('select')
    keyword = request.POST.get('keyword')
    # 去掉空格方式
    # "   xyz   ".strip()  # returns "xyz"
    # "   xyz   ".lstrip()  # returns "xyz   "
    # "   xyz   ".rstrip()  # returns "   xyz"
    # "  x y z  ".replace(' ', '')  # returns "xyz"
    print(select, keyword)
    # 判断传入的字符串是否是空值SearchGetBootImages.html?name=，或者SearchGetBootImages.html?name= 传入空值
    if keyword is None or len(keyword) == 0:
        boot_iso_list = BootFromISO.objects.all()
        keyword = '显示所有记录'
        searchResult = '查询结果统计：' + str(boot_iso_list.count()) + '条'
        # print(boot_iso_list)
        # 查询得到一个QuerySet
    else:
        keyword = keyword.strip()  # 输入框可能会出现前后空格，需要踢出
        if select == 'name':
            boot_iso_list = BootFromISO.objects.filter(name__icontains=keyword)
            keyword = '查询关键词：' + keyword
            searchResult = '查询结果统计：' + str(boot_iso_list.count()) + '条'
        elif select == 'mac':
            boot_iso_list = BootFromISO.objects.filter(mac__icontains=keyword)
            keyword = '查询关键词：' + keyword
            searchResult = '查询结果统计：' + str(boot_iso_list.count()) + '条'
        elif select == 'iso_name':
            boot_iso_list = BootFromISO.objects.filter(iso_name__icontains=keyword)
            keyword = '查询关键词：' + keyword
            searchResult = '查询结果统计：' + str(boot_iso_list.count()) + '条'
        elif select == 'explain':
            boot_iso_list = BootFromISO.objects.filter(explain__icontains=keyword)
            keyword = '查询关键词：' + keyword
            searchResult = '查询结果统计：' + str(boot_iso_list.count()) + '条'
        else:
            boot_iso_list = BootFromISO.objects.filter(
                Q(name__icontains=keyword) |
                Q(mac__icontains=keyword) |
                Q(iso_svr__icontains=keyword) |
                Q(iso_name__icontains=keyword) |
                Q(available__icontains=keyword) |
                Q(created__icontains=keyword) |
                Q(updated__icontains=keyword) |
                Q(explain__icontains=keyword))
            keyword = '查询关键词：' + keyword
            searchResult = '查询结果统计：' + str(boot_iso_list.count()) + '条'
            # print('结果数量', boot_iso_list.count())

    return render(request, 'manager/boot_from_iso/query_boot_from_iso_info_post.html', {'boot_iso_list': boot_iso_list, 'searchName': keyword, 'searchResult': searchResult})


# 普通添加功能，后端进行正则判断
def add_boot_iso_info(request):
    if request.method == 'POST':
        # 两种方式获取前端提交的数据
        # name = request.POST['name']
        name = request.POST.get('name')
        mac = request.POST['mac']
        iso_svr = request.POST['iso_svr']

        # iso_upload = request.FILES['iso_upload']
        iso_upload = request.FILES.get('iso_upload')
        # print(iso_upload, type(iso_upload))
        # 未上传：None <class 'NoneType'>
        # 上传后：name.iso <class 'django.core.files.uploadedfile.TemporaryUploadedFile'>，等于说iso_upload就是文件名
        # iso_upload.name也是取上传的文件名字

        iso_name = request.POST['iso_name']

        # print(request.POST['available'])
        # 前端输入方式
        # if request.POST['available'] is None:
        #     available = request.POST['available']
        # elif request.POST['available'].lower() == 'y' or request.POST['available'] is True:
        #     available = True
        # else:
        #     available = False
        # print(available)

        # 前端选择方式
        if request.POST['available'] == 'y':
            available = True
        else:
            available = False

        explain = request.POST['explain']

        now_time = time.time()
        now_time_array = time.localtime(now_time)  # 转换成时间数组
        created = updated = time.strftime("%Y-%m-%d %H:%M", now_time_array)

        if '-' in mac:
            mac = mac.replace('-', ':')
            # print(mac)
        if '_' in mac:
            mac = mac.replace('_', ':')
            # print(mac)

        # 判断是否已存在数据库
        mac_exist_flag = 1
        try:
            BootFromISO.objects.get(mac='%s' % mac)
        except models.ObjectDoesNotExist:
            mac_exist_flag = 0
        # print('flag=', flag)
        if len(name) == 0:
            return render(request, 'manager/boot_from_iso/add_boot_iso_info.html',
                          {
                              'nameCheck': '启动名称不能为空！'
                           })
        if re.match(r"^\s*([0-9a-fA-F]{2,2}:){5,5}[0-9a-fA-F]{2,2}\s*$", mac) is None:
            return render(request, 'manager/boot_from_iso/add_boot_iso_info.html',
                          {
                              'macCheck': 'MAC地址输入有误：%s，需修改为类似：11:22:33:aa:bb:cc' % mac
                          })
        if mac_exist_flag == 1:
            return render(request, 'manager/boot_from_iso/add_boot_iso_info.html',
                          {
                              'macCheck': 'MAC地址已存在！'
                          })
        if re.match(r"[a-zA-z]+://[^\s]*", iso_svr) is None:
            return render(request, 'manager/boot_from_iso/add_boot_iso_info.html',
                          {
                              'iso_svrCheck': 'ISO地址输入有误！'
                          })
        # 后端iso名字取上传的文件名字，这段就舍弃判断
        # elif re.match(r"(.+).([iI][sS][oO])$", iso_name) is None:
        #     return render(request, 'manager/boot_from_iso/add_boot_iso_info.html', {'iso_nameCheck': 'ISO名称不正确！'})
        if len(explain) == 0:
            return render(request, 'manager/boot_from_iso/add_boot_iso_info.html',
                          {
                              'explainCheck': '说明不能为空！'
                          })
        if iso_upload is None:
            return render(request, 'manager/boot_from_iso/add_boot_iso_info.html',
                          {'iso_uploadCheck': '没有上传文件！'})
        if iso_upload is not None:
            if re.match(r"(.+).([iI][sS][oO])$", iso_upload.name) is None:
                return render(request, 'manager/boot_from_iso/add_boot_iso_info.html', {'iso_uploadCheck': 'ISO上传文件不正确，需iso文件！'})
            else:
                iso_open = open(os.path.join(settings.MEDIA_ROOT + '/isofiles/', iso_upload.name), 'wb')
                for chunk in iso_upload.chunks(chunk_size=1024):
                    iso_open.write(chunk)
                iso_open.close()
                iso_name = iso_upload.name
                BootFromISO.objects.create(name=name, mac=mac, iso_svr=iso_svr, iso_upload='/isofiles/' + iso_upload.name, iso_name=iso_name, available=available, explain=explain)
                return render(request, 'manager/boot_from_iso/add_boot_iso_info.html', {'success': '成功添加数据库！'})
        else:
            BootFromISO.objects.create(name=name, mac=mac, iso_svr=iso_svr, iso_upload='isofiles/' + iso_upload.name, iso_name=iso_name, available=available, explain=explain)
            return render(request, 'manager/boot_from_iso/add_boot_iso_info.html', {'success': '成功添加数据库！'})
    else:
        return render(request, 'manager/boot_from_iso/add_boot_iso_info.html')


def boot_from_iso_info_query_operation(request):
    search_flag = 'N'  # 搜索状态初始为无，当有搜索值时，赋值为Y
    keyword = request.GET.get('keyword')
    # print(keyword)
    # 判断传入的字符串是否是空值SearchGetBootImages.html?name=，或者SearchGetBootImages.html?name= 传入空值
    if keyword is None or len(keyword) == 0:
        boot_iso_list = BootFromISO.objects.all()
        # 查询得到一个QuerySet
        keyword = ''
        search_result = boot_iso_list.count()
        if search_result != 0:
            search_flag = 'Y'
        return render(request, 'manager/boot_from_iso/boot_from_iso_info_query_operation.html',
                      {
                          'search_flag': search_flag,
                          'boot_iso_list': boot_iso_list,
                          'searchWord': keyword,
                          'search_result': '查询结果共%s条！' % search_result
                       })
    else:
        # 固定搜索
        # boot_iso_list = BootFromISO.objects.filter(name=name)
        # 模糊搜索
        boot_iso_list = BootFromISO.objects.filter(
            Q(name__icontains=keyword) |
            Q(mac__icontains=keyword) |
            Q(iso_svr__icontains=keyword) |
            Q(iso_name__icontains=keyword) |
            Q(available__icontains=keyword) |  # 似乎这个查询不到
            Q(created__icontains=keyword) |
            Q(updated__icontains=keyword) |
            Q(explain__icontains=keyword)
        )
        keyword = '查询关键词：' + keyword
        search_result = boot_iso_list.count()
        if search_result != 0:
            search_flag = 'Y'
        return render(request, 'manager/boot_from_iso/boot_from_iso_info_query_operation.html',
                      {
                          'search_flag': search_flag,
                          'boot_iso_list': boot_iso_list,
                          'search_word': keyword,
                          'search_result': '查询结果共%s条！' % search_result
                       })


# 显示结果详情
def boot_iso_info_query_details(request):
    mac = request.GET.get('mac')
    image_info = BootFromISO.objects.get(mac=mac)
    print(image_info.iso_upload)
    return render(request, 'manager/boot_from_iso/boot_iso_info_query_details.html',
                  {
                      'image_info': image_info
                  })


# 执行删除
def boot_iso_info_execute_delete(request):
    search_flag = 'N'  # 搜索值有无得状态初始为无，当有搜索值时，赋值为Y
    if request.method == 'GET':
        print('GET')
        delete_mac = request.GET.get('delete_mac')
        print('需要删除的值：', delete_mac)
        if delete_mac is not None:
            BootFromISO.objects.filter(mac=delete_mac).delete()
            return render(request, 'manager/boot_from_iso/boot_from_iso_info_query_operation.html',
                          {
                              'search_flag': search_flag,
                              'statue': '删除%s对应的信息完成！' % delete_mac
                          })
        else:
            return render(request, 'manager/boot_from_iso/boot_from_iso_info_query_operation.html',
                          {
                              'statue': '不删除！'
                           })


# 执行更新
def boot_iso_info_execute_update(request):
    flag = 'update'
    if request.method == 'GET':
        print('GET')
        update_mac = request.GET.get('update_mac')
        print('需要更新的mac对应信息：', update_mac)
        old_info = BootFromISO.objects.filter(mac=update_mac)[0]
        print(old_info)
        return render(request, 'manager/boot_from_iso/boot_iso_info_execute_update.html',
                      {
                          'flag': flag,
                          'old_info': old_info,
                      })
    if request.method == 'POST':
        print('POST')
        state = '未更新数据！'
        choose_id = request.POST.get('id')
        name = request.POST.get('name')
        mac = request.POST.get('mac')
        iso_svr = request.POST.get('iso_svr')
        iso_upload = request.FILES.get('iso_upload')
        # print(iso_upload)  # 不上传时为None
        if iso_upload is None:
            iso_name = request.POST.get('iso_name')
        else:
            iso_name = iso_upload.name  # 根据上传的文件提取文件名
        # 前端选择方式
        if request.POST['available'] == 'y':
            available = True
        else:
            available = False
        explain = request.POST.get('explain')
        print(choose_id)
        update_info = BootFromISO.objects.filter(id=choose_id)
        print('旧的mac', update_info[0].mac)
        print('新的mac', mac)
        if update_info[0].mac != mac:
            update_info.update(mac=mac)
            state = '已完成更新提交！'
        if update_info[0].name != name:
            update_info.update(name=name)
            state = '已完成更新提交！'
        if update_info[0].iso_svr != iso_svr:
            update_info.update(iso_svr=iso_svr)
            state = '已完成更新提交！'
        if iso_upload is not None:
            if update_info[0].iso_upload != iso_upload:
                print(iso_upload)
                update_info.update(iso_upload=iso_upload)
                iso_open = open(os.path.join(settings.MEDIA_ROOT + '/isofiles/', iso_upload.name), 'wb')
                for chunk in iso_upload.chunks(chunk_size=1024):
                    iso_open.write(chunk)
                iso_open.close()
                state = '已完成更新提交！'
        if update_info[0].iso_name != iso_name:
            update_info.update(iso_name=iso_name)
            state = '已完成更新提交！'
        if update_info[0].available != available:
            update_info.update(available=available)
            state = '已完成更新提交！'
        if update_info[0].explain != explain:
            update_info.update(explain=explain)
            state = '已完成更新提交！'

        return render(request, 'manager/boot_from_iso/boot_iso_info_execute_update.html',
                      {
                          'state': state
                      })