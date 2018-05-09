# -*- coding:utf-8 -*-

from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from .models import BootFromClonezilla, HttpServerList, SambaServerList, DefaultImageSelect
from .models import ImageFilesList, RestoreDiskNum, User, HttpServerList
import datetime
import os
from django.conf import settings
from django.db.models import Q
from .ext_getsambafiles import get_images_list, get_del_images_list
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .ext_renameimage import rename_image, rename_logs
from .ext_sambasyncstate import get_files_info, samba_sync
from .ext_delrstimage import del_image, restore_image
import json


# #################################################################
# 默认Clonezilla启动管理


# 从 DefaultImageSelect中修改默认值，启动,查询权限
def select_default_image_control(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    username = request.session['session_name']
    if User.objects.filter(username=username, auth_search=1).count() == 1:
        print('用户 %s 已有权限访问！' % username)

        if request.method == 'POST':
            print('\n选择Clonezilla镜像启动控制：POST')

            get_select = request.POST.get('get_select')
            switch_status = ''

            boot_select_list = DefaultImageSelect.objects.all().order_by('select_name')

            for boot in boot_select_list:
                # 循环获取启动选择，如果启动选择的名称和前端传过来的值相同，则将启动设置为True
                if get_select == boot.select_name:
                    print(boot.select_name + '的原状态：' + str(boot.available))
                    # 所选择的设置为True，其他的设置为False
                    DefaultImageSelect.objects.filter(select_name=get_select).update(available=True)
                    DefaultImageSelect.objects.exclude(select_name=get_select).update(available=False)
                    switch_status = '切换完成！'
                    # 将选择启动的id加入到用户表中2017.10.22
                    if DefaultImageSelect.objects.filter(available=True).count() == 1:
                        boot_clonezilla_id = DefaultImageSelect.objects.filter(available=True)[0].id
                        User.objects.filter(username=username).update(boot_clonezilla_id=boot_clonezilla_id)
                        print('更新用户表Clonezilla的id为 %s' % boot_clonezilla_id)

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
                boot_select_list = DefaultImageSelect.objects.all().order_by('select_name')
            else:
                boot_select_list = DefaultImageSelect.objects.filter(
                    Q(select_name__icontains=keyword) |
                    Q(created__icontains=keyword) |
                    Q(updated__icontains=keyword) |
                    Q(explain__icontains=keyword)
                ).order_by('select_name')
            find_num = boot_select_list.count()
            if find_num == 0:
                can_find = False
            else:
                can_find = True
            print('是否可以查到：', can_find)
            print('查询到的数量：', find_num)

            image_files_list = ImageFilesList.objects.all()
            http_server_list = HttpServerList.objects.all()
            samba_server_list = SambaServerList.objects.all()
            disk_num_list = RestoreDiskNum.objects.all()
            return render(request, 'manager/boot_from_clonezilla/select_default_image_control.html',
                          {
                              'boot_select_list': boot_select_list,
                              'can_find': can_find,
                              'find_num': find_num,
                              'switch_status': switch_status,
                              'image_files_list': image_files_list,
                              'http_server_list': http_server_list,
                              'samba_server_list': samba_server_list,
                              'disk_num_list': disk_num_list,
                          })
        else:
            boot_select_list = DefaultImageSelect.objects.all().order_by('select_name')
            can_find = True
            find_num = boot_select_list.count()
            print('\n选择Clonezilla镜像启动控制：GET')
            image_files_list = ImageFilesList.objects.all()
            http_server_list = HttpServerList.objects.all()
            samba_server_list = SambaServerList.objects.all()
            disk_num_list = RestoreDiskNum.objects.all()
            return render(request, 'manager/boot_from_clonezilla/select_default_image_control.html',
                          {
                              'boot_select_list': boot_select_list,
                              'can_find': can_find,
                              'find_num': find_num,
                              'image_files_list': image_files_list,
                              'http_server_list': http_server_list,
                              'samba_server_list': samba_server_list,
                              'disk_num_list': disk_num_list,
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


# 使用GET方法选中，测试使用
def select_default_image_control_choose(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_search=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])
        if request.method == 'GET':
            get_select = request.GET.get('select_name')
            boot_select_list = DefaultImageSelect.objects.all()
            for boot in boot_select_list:
                # 循环获取启动选择，如果启动选择的名称和前端传过来的值相同，则将启动设置为True
                if get_select == boot.select_name:
                    print(boot.select_name + '的状态：' + str(boot.available))
                    # 所选择的设置为True，其他的设置为False
                    DefaultImageSelect.objects.filter(select_name=get_select).update(available=True)
                    DefaultImageSelect.objects.exclude(select_name=get_select).update(available=False)
                    switch_status = '切换完成！刷新本页显示结果。'
            image_files_list = ImageFilesList.objects.all()
            http_server_list = HttpServerList.objects.all()
            samba_server_list = SambaServerList.objects.all()
            disk_num_list = RestoreDiskNum.objects.all()
            boot_select_list = DefaultImageSelect.objects.all().order_by('select_name')
            find_num = boot_select_list.count()
            if find_num == 0:
                can_find = False
            else:
                can_find = True
            return render(request, 'manager/boot_from_clonezilla/select_default_image_control.html',
                          {
                              'boot_select_list': boot_select_list,
                              'can_find': can_find,
                              'find_num': find_num,
                              'switch_status': switch_status,
                              'image_files_list': image_files_list,
                              'http_server_list': http_server_list,
                              'samba_server_list': samba_server_list,
                              'disk_num_list': disk_num_list,
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


# 增加一个默认选择对象，add权限
def select_default_image_control_add(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_add=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == 'GET':
            image_files_list = ImageFilesList.objects.all().order_by('name')
            http_server_list = HttpServerList.objects.all()
            samba_server_list = SambaServerList.objects.all()
            disk_num_list = RestoreDiskNum.objects.all()
            # 前端选择默认镜像出现的列表，select设置一个默认值
            default_recent_image_name = ImageFilesList.objects.all().order_by('-created')[0].name
            return render(request, 'manager/boot_from_clonezilla/select_default_image_control_add.html',
                          {
                              'image_files_list': image_files_list,
                              'http_server_list': http_server_list,
                              'samba_server_list': samba_server_list,
                              'disk_num_list': disk_num_list,
                              'default_recent_image_name': default_recent_image_name,
                          })

        else:
            name = request.POST.get('name')

            image_file = request.POST.get('image_file')
            image_file_select = ImageFilesList.objects.get(name=image_file)

            http_server = request.POST.get('http_server')
            http_server_select = HttpServerList.objects.get(http_name=http_server)

            samba_server = request.POST.get('samba_server')
            samba_server_select = SambaServerList.objects.get(samba_name=samba_server)

            disk_num = request.POST.get('disk_num')
            disk_num_select = RestoreDiskNum.objects.get(disk_name=disk_num)

            image_path = request.POST.get('image_path')

            available = request.POST.get('available')
            if available == 'y':
                available = True
            else:
                available = False
            explain = request.POST.get('explain')

            if DefaultImageSelect.objects.filter(select_name=name).count() == 0:
                DefaultImageSelect.objects.create(
                    select_name=name,
                    image_file=image_file_select,
                    http_server=http_server_select,
                    samba_server=samba_server_select,
                    restore_disk=disk_num_select,
                    image_path=image_path,
                    available=available,
                    explain=explain,
                )
                add_status = '添加成功！'
            else:
                add_status = '添加失败！'

            image_files_list = ImageFilesList.objects.all()
            http_server_list = HttpServerList.objects.all()
            samba_server_list = SambaServerList.objects.all()
            disk_num_list = RestoreDiskNum.objects.all()
            return render(request, 'manager/boot_from_clonezilla/select_default_image_control_add.html',
                          {
                              'image_files_list': image_files_list,
                              'http_server_list': http_server_list,
                              'samba_server_list': samba_server_list,
                              'disk_num_list': disk_num_list,
                              'add_status': add_status,
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


# bootstrap模态框添加默认启动数据
def select_default_image_control_add_bootstrap(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_add=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        name = request.POST.get('name')
        print('使用模态框添加数据%s' % name)
        image_file = request.POST.get('image_file')
        image_file_select = ImageFilesList.objects.get(name=image_file)

        http_server = request.POST.get('http_server')
        http_server_select = HttpServerList.objects.get(http_name=http_server)

        samba_server = request.POST.get('samba_server')
        samba_server_select = SambaServerList.objects.get(samba_name=samba_server)

        disk_num = request.POST.get('disk_num')
        disk_num_select = RestoreDiskNum.objects.get(disk_name=disk_num)

        image_path = request.POST.get('image_path')

        available = request.POST.get('available')
        if available == 'y':
            available = True
        else:
            available = False
        explain = request.POST.get('explain')
        if DefaultImageSelect.objects.filter(select_name=name).count() == 0:
            DefaultImageSelect.objects.create(
                select_name=name,
                image_file=image_file_select,
                http_server=http_server_select,
                samba_server=samba_server_select,
                restore_disk=disk_num_select,
                image_path=image_path,
                available=available,
                explain=explain,
            )
            add_status = '添加完成！'
        else:
            add_status = '添加失败，已有数据！'
        boot_select_list = DefaultImageSelect.objects.all().order_by('select_name')
        can_find = True
        find_num = boot_select_list.count()
        image_files_list = ImageFilesList.objects.all().order_by('name')
        http_server_list = HttpServerList.objects.all()
        samba_server_list = SambaServerList.objects.all()
        disk_num_list = RestoreDiskNum.objects.all()
        return render(request, 'manager/boot_from_clonezilla/select_default_image_control.html',
                      {
                          'boot_select_list': boot_select_list,
                          'can_find': can_find,
                          'find_num': find_num,
                          'image_files_list': image_files_list,
                          'http_server_list': http_server_list,
                          'samba_server_list': samba_server_list,
                          'disk_num_list': disk_num_list,
                          'add_status': add_status,
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


# 删除一个默认选择对象
def select_default_image_control_delete(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_del=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == 'GET':
            delete_id = request.GET.get('delete_id')
            print('需要删除的对象id值：', delete_id)
            DefaultImageSelect.objects.filter(id=delete_id).delete()

            boot_select_list = DefaultImageSelect.objects.all().order_by('select_name')
            find_num = boot_select_list.count()
            if find_num == 0:
                can_find = False
            else:
                can_find = True
            # 删除后就查询不到了，后续显示全部
            if DefaultImageSelect.objects.filter(id=delete_id).count() == 0:

                delete_status = '删除完成！'
            else:
                delete_status = '删除失败！'
            image_files_list = ImageFilesList.objects.all()
            http_server_list = HttpServerList.objects.all()
            samba_server_list = SambaServerList.objects.all()
            disk_num_list = RestoreDiskNum.objects.all()
            return render(request, 'manager/boot_from_clonezilla/select_default_image_control.html',
                          {
                              'delete_status': delete_status,
                              'boot_select_list': boot_select_list,
                              'can_find': can_find,
                              'find_num': find_num,
                              'image_files_list': image_files_list,
                              'http_server_list': http_server_list,
                              'samba_server_list': samba_server_list,
                              'disk_num_list': disk_num_list,
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


# 更新一个默认选择对象
def select_default_image_control_update(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_update=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == 'GET':
            # select_name = request.GET.get('update_select_name')
            # print('需要更新的对象：', select_name)
            update_id = request.GET.get('update_id')
            print('需要更新的对象id值：', update_id)
            update_select_name = DefaultImageSelect.objects.get(id=update_id)
            image_files_list = ImageFilesList.objects.all().order_by('name')
            http_server_list = HttpServerList.objects.all()
            samba_server_list = SambaServerList.objects.all()
            disk_num_list = RestoreDiskNum.objects.all()
            print(type(update_select_name.samba_server), '----', type(update_select_name.samba_server.samba_name))
            # 注意前面的是个对象，要获得字符串才能在html进行比较
            print(update_select_name.samba_server.samba_name)
            return render(request, 'manager/boot_from_clonezilla/select_default_image_control_update.html',
                          {
                              'update_select_name': update_select_name,
                              'image_files_list': image_files_list,
                              'http_server_list': http_server_list,
                              'samba_server_list': samba_server_list,
                              'disk_num_list': disk_num_list,
                          })
        else:
            update_id = request.POST.get('id')
            # 如果用name来确认，假如name发生变化，后面的 DefaultImageSelect.objects.get(select_name=name)将查不到
            print('使用Django自动创建的唯一的id作为查询修改：', update_id)
            name = request.POST.get('name')

            image_file = request.POST.get('image_file')
            image_file_select = ImageFilesList.objects.get(name=image_file)

            http_server = request.POST.get('http_server')
            http_server_select = HttpServerList.objects.get(http_name=http_server)

            samba_server = request.POST.get('samba_server')
            samba_server_select = SambaServerList.objects.get(samba_name=samba_server)

            disk_num = request.POST.get('disk_num')
            disk_num_select = RestoreDiskNum.objects.get(disk_name=disk_num)

            image_path = request.POST.get('image_path')

            available = request.POST.get('available')
            if available == 'y':
                available = True
            else:
                available = False
            explain = request.POST.get('explain')

            # 执行所有更新
            if DefaultImageSelect.objects.filter(id=update_id, select_name=name).count() == 1 or DefaultImageSelect.objects.filter(select_name=name).count() == 0:
                DefaultImageSelect.objects.filter(id=update_id).update(
                    select_name=name,
                    image_file=image_file_select,
                    http_server=http_server_select,
                    samba_server=samba_server_select,
                    restore_disk=disk_num_select,
                    image_path=image_path,
                    available=available,
                    explain=explain,
                )

                update_status = '更新完成！上面显示更新后的结果。'
            else:
                update_status = '数据库已存在该名称数据，将不再更新！'

            update_select_name = DefaultImageSelect.objects.get(id=update_id)
            image_files_list = ImageFilesList.objects.all()
            http_server_list = HttpServerList.objects.all()
            samba_server_list = SambaServerList.objects.all()
            disk_num_list = RestoreDiskNum.objects.all()
            # print(type(update_select_name.samba_server), '----', type(update_select_name.samba_server.samba_name))
            # 注意前面的是个对象，要获得字符串才能在html进行比较
            # print(update_select_name.samba_server.samba_name)
            return render(request, 'manager/boot_from_clonezilla/select_default_image_control_update.html',
                          {
                              'update_select_name': update_select_name,
                              'image_files_list': image_files_list,
                              'http_server_list': http_server_list,
                              'samba_server_list': samba_server_list,
                              'disk_num_list': disk_num_list,
                              'update_status': update_status
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


# #################################################################


# Clonezilla镜像文件管理
def image_file_query_operation(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_search=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        get_images = get_images_list()
        if get_images is None:
            images_list = []
            default_recent_image_name = ''
        else:
            # 通过外部调用ext_getsambafiles.py获取文件夹的列表
            images_list = get_images[0]
            # 通过外部调用ext_getsambafiles.py获取创建的最新的文件夹名字
            default_recent_image_name = get_images[1]

        if request.method == 'GET':
            image_files_list = ImageFilesList.objects.all().order_by('name')
            can_find = True
            find_num = image_files_list.count()
            return render(request, 'manager/boot_from_clonezilla/image_file_query_operation.html',
                          {
                              'image_files_list': image_files_list,
                              'images_list': images_list,
                              'can_find': can_find,
                              'find_num': find_num,
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
                image_files_list = ImageFilesList.objects.all().order_by('name')
                find_num = image_files_list.count()
                if find_num == 0:
                    can_find = False
                else:
                    can_find = True
            else:
                image_files_list = ImageFilesList.objects.filter(
                    Q(name__icontains=keyword) |
                    Q(image_name__icontains=keyword) |
                    Q(disk_type__icontains=keyword) |
                    Q(disk_size__icontains=keyword) |
                    Q(available_model__icontains=keyword) |
                    Q(created__icontains=keyword) |
                    Q(updated__icontains=keyword) |
                    Q(explain__icontains=keyword)
                ).order_by('name')
                find_num = image_files_list.count()
                if find_num == 0:
                    can_find = False
                else:
                    can_find = True
                print('是否可以查到：', can_find)
            print('查询到的数量：', find_num)
            return render(request, 'manager/boot_from_clonezilla/image_file_query_operation.html',
                          {
                              'image_files_list': image_files_list,
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


# Clonezilla镜像文件信息增加
def image_file_add(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_add=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == 'GET':
            get_images = get_images_list()
            if get_images is None:
                images_list = []
                default_recent_image_name = ''
            else:
                # 通过外部调用ext_getsambafiles.py获取文件夹的列表
                images_list = get_images[0]
                # 通过外部调用ext_getsambafiles.py获取创建的最新的文件夹名字
                default_recent_image_name = get_images[1]

            if images_list is None or len(images_list) == 0:
                can_choose = False
            else:

                can_choose = True
            return render(request, 'manager/boot_from_clonezilla/image_file_add.html',
                          {
                              'images_list': images_list,
                              'can_choose': can_choose,
                              'default_recent_image_name': default_recent_image_name,
                          })
        else:
            name = request.POST.get('name')
            image_name = request.POST.get('image_name')
            disk_type = request.POST.get('disk_type')
            disk_size = request.POST.get('disk_size')
            available_model = request.POST.get('available_model')
            available = request.POST.get('available')
            if available == 'y':
                available = True
            else:
                available = False
            explain = request.POST.get('explain')

            images_list = get_images_list()[0]
            if images_list is None or len(images_list) == 0:
                can_choose = False
            else:
                can_choose = True

            # 判断数据库中是否已存在
            if ImageFilesList.objects.filter(image_name=image_name).count() == 0:
                ImageFilesList.objects.create(
                    name=name,
                    image_name=image_name,
                    disk_type=disk_type,
                    disk_size=disk_size,
                    available_model=available_model,
                    available=available,
                    explain=explain,
                )
                add_status = '添加完成！'

                print('增加镜像文件信息提交：', name)
                return render(request, 'manager/boot_from_clonezilla/image_file_add.html',
                              {
                                  'add_status': add_status,
                                  'images_list': images_list,
                                  'can_choose': can_choose,
                              })
            else:
                add_status = '添加失败，数据库中已存在 %s 的信息!' % image_name
                return render(request, 'manager/boot_from_clonezilla/image_file_add.html',
                              {
                                  'add_status': add_status,
                                  'images_list': images_list,
                                  'can_choose': can_choose,
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


# Clonezilla镜像文件信息删除
def image_file_delete(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_del=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == 'GET':
            # name = request.GET.get('delete_name')
            delete_id = request.GET.get('delete_id')
            print('需要删除的对象id值：', delete_id)
            ImageFilesList.objects.filter(id=delete_id).delete()

            # 删除后就查询不到了，后续显示全部
            if ImageFilesList.objects.filter(id=delete_id).count() == 0:
                image_files_list = ImageFilesList.objects.all()
                find_num = image_files_list.count()
                if find_num == 0:
                    can_find = False
                else:
                    can_find = True
            delete_status = '删除完成！'
            return render(request, 'manager/boot_from_clonezilla/image_file_query_operation.html',
                          {
                              'image_files_list': image_files_list,
                              'can_find': can_find,
                              'find_num': find_num,
                              'delete_status': delete_status,
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


# Clonezilla镜像文件更新
def image_file_update(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_update=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == 'GET':
            # name = request.GET.get('update_name')
            update_id = request.GET.get('update_id')
            print('需要更新的对象id值：', update_id)
            update_name = ImageFilesList.objects.get(id=update_id)
            # 获取镜像文件列表信息
            get_images = get_images_list()
            if get_images is None:
                images_list = []
                default_recent_image_name = ''
            else:
                # 通过外部调用ext_getsambafiles.py获取文件夹的列表
                images_list = get_images[0]
                # 通过外部调用ext_getsambafiles.py获取创建的最新的文件夹名字
                default_recent_image_name = get_images[1]

            if images_list is None or len(images_list) == 0:
                can_choose = False
            else:
                can_choose = True
            return render(request, 'manager/boot_from_clonezilla/image_file_update.html',
                          {
                              'update_name': update_name,
                              'can_choose': can_choose,
                              'images_list': images_list,
                          })
        else:
            update_id = request.POST.get('id')
            name = request.POST.get('name')
            image_name = request.POST.get('image_name')
            disk_type = request.POST.get('disk_type')
            disk_size = request.POST.get('disk_size')
            available_model = request.POST.get('available_model')
            available = request.POST.get('available')
            if available == 'y':
                available = True
            else:
                available = False
            explain = request.POST.get('explain')

            images_list = get_images_list()[0]
            # print(images_list)
            if images_list is None or len(images_list) == 0:
                can_choose = False
            else:
                can_choose = True

            if ImageFilesList.objects.filter(id=update_id)[0].image_name == image_name or ImageFilesList.objects.filter(image_name=image_name).count() == 0:
                ImageFilesList.objects.filter(id=update_id).update(
                    name=name,
                    image_name=image_name,
                    disk_type=disk_type,
                    disk_size=disk_size,
                    available_model=available_model,
                    available=available,
                    explain=explain,
                )
                update_name = ImageFilesList.objects.get(id=update_id)
                update_status = '更新完成！上面显示更新后的结果。'
                return render(request, 'manager/boot_from_clonezilla/image_file_update.html',
                              {
                                  'update_name': update_name,
                                  'update_status': update_status,
                                  'can_choose': can_choose,
                                  'images_list': images_list,
                              })
            else:
                update_name = ImageFilesList.objects.get(id=update_id)
                update_status = '更新失败，数据库中已存在 %s 的信息!' % image_name
                return render(request, 'manager/boot_from_clonezilla/image_file_update.html',
                              {
                                  'update_name': update_name,
                                  'update_status': update_status,
                                  'images_list': images_list,
                                  'can_choose': can_choose,
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


# 默认Samba服务器选择
def select_default_samba(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_search=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])
        if request.method == 'POST':
            print('\n选择启动控制：POST')

            get_select = request.POST.get('get_select')
            switch_status = ''

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
                samba_select_list = SambaServerList.objects.all()
                find_num = samba_select_list.count()
                if find_num == 0:
                    can_find = False
                else:
                    can_find = True
            else:
                samba_select_list = SambaServerList.objects.filter(
                    Q(samba_name__icontains=keyword) |
                    Q(samba_ip__icontains=keyword) |
                    Q(samba_user__icontains=keyword) |
                    Q(explain__icontains=keyword)
                )
                find_num = samba_select_list.count()
                if find_num == 0:
                    can_find = False
                else:
                    can_find = True
                print('是否可以查到：', can_find)
            print('查询到的数量：', find_num)

            for samba_select in samba_select_list:
                # 循环获取启动选择，如果启动选择的名称和前端传过来的值相同，则将启动设置为True
                if get_select == samba_select.samba_name:
                    print(samba_select.samba_name + ' 是否默认：' + str(samba_select.default))
                    # 所选择的设置为True，其他的设置为False
                    SambaServerList.objects.filter(samba_name=get_select).update(default=True)
                    SambaServerList.objects.exclude(samba_name=get_select).update(default=False)
                    switch_status = '切换完成！刷新本页显示结果。'
                    samba_select_list = SambaServerList.objects.all()
            return render(request, 'manager/boot_from_clonezilla/select_default_samba.html',
                          {
                              'samba_select_list': samba_select_list,
                              'can_find': can_find,
                              'find_num': find_num,
                              'switch_status': switch_status,
                          })
        else:
            samba_select_list = SambaServerList.objects.all()
            print('\n选择默认Samba：GET')
            can_find = True
            find_num = samba_select_list.count()
            return render(request, 'manager/boot_from_clonezilla/select_default_samba.html',
                          {
                              'samba_select_list': samba_select_list,
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


# 增加Samba服务器
def select_default_samba_add(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_add=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])
        if request.method == 'GET':
            return render(request, 'manager/boot_from_clonezilla/select_default_samba_add.html')
        else:
            samba_name = request.POST.get('samba_name')
            samba_ip = request.POST.get('samba_ip')
            samba_folder = request.POST.get('samba_folder')
            samba_user = request.POST.get('samba_user')
            samba_password = request.POST.get('samba_password')
            netspeed_port = request.POST.get('netspeed_port')
            netspeed_path = request.POST.get('netspeed_path')

            available = request.POST.get('available')
            if available == 'y':
                available = True
            else:
                available = False

            default = request.POST.get('default')
            if default == 'y':
                default = True
            else:
                default = False

            # 如果新增的把默认设置为True，则先筛选其他默认为True的更新成False
            if default is True:
                SambaServerList.objects.filter(default=default).update(default=False)

            explain = request.POST.get('explain')
            SambaServerList.objects.create(
                samba_name=samba_name,
                samba_ip=samba_ip,
                samba_folder=samba_folder,
                samba_user=samba_user,
                samba_password=samba_password,
                netspeed_port=netspeed_port,
                netspeed_path=netspeed_path,
                available=available,
                default=default,
                explain=explain,
            )
            add_status = True
            print('新Samba信息提交', samba_name)
            return render(request, 'manager/boot_from_clonezilla/select_default_samba_add.html',
                          {
                              'add_status': add_status,
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


# 删除Samba服务器
def select_default_samba_delete(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_del=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])
        if request.method == 'GET':
            samba_name = request.GET.get('delete_samba_name')
            print('需要删除的对象：', samba_name)
            SambaServerList.objects.filter(samba_name=samba_name).delete()

            # 删除后就查询不到了，后续显示全部
            if SambaServerList.objects.filter(samba_name=samba_name).count() == 0:
                samba_select_list = SambaServerList.objects.all()
                find_num = samba_select_list.count()
                if find_num == 0:
                    can_find = False
                else:
                    can_find = True
            delete_status = '删除完成！'
            return render(request, 'manager/boot_from_clonezilla/select_default_samba.html',
                          {
                              'samba_select_list': samba_select_list,
                              'find_num': find_num,
                              'can_find': can_find,
                              'delete_status': delete_status,
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


# 更新Samba服务器
def select_default_samba_update(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_update=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == 'GET':
            samba_name = request.GET.get('update_samba_name')
            print('需要更新的对象：', samba_name)
            update_samba_name = SambaServerList.objects.get(samba_name=samba_name)

            return render(request, 'manager/boot_from_clonezilla/select_default_samba_update.html',
                          {
                              'update_samba_name': update_samba_name,
                          })
        else:
            id = request.POST.get('id')
            samba_name = request.POST.get('samba_name')
            samba_ip = request.POST.get('samba_ip')
            samba_folder = request.POST.get('samba_folder')
            samba_user = request.POST.get('samba_user')
            samba_password = request.POST.get('samba_password')
            netspeed_port = request.POST.get('netspeed_port')
            netspeed_path = request.POST.get('netspeed_path')

            available = request.POST.get('available')
            if available == 'y':
                available = True
            else:
                available = False

            default = request.POST.get('default')
            if default == 'y':
                default = True
            else:
                default = False

            # 如果新增的把默认设置为True，则先筛选其他默认为True的更新成False
            if default is True:
                SambaServerList.objects.filter(default=default).update(default=False)

            explain = request.POST.get('explain')
            SambaServerList.objects.filter(id=id).update(
                samba_name=samba_name,
                samba_ip=samba_ip,
                samba_folder=samba_folder,
                samba_user=samba_user,
                samba_password=samba_password,
                netspeed_port=netspeed_port,
                netspeed_path=netspeed_path,
                available=available,
                default=default,
                explain=explain,
            )
            update_samba_name = SambaServerList.objects.get(id=id)
            update_status = '更新完成！上面显示更新后的结果。'
            return render(request, 'manager/boot_from_clonezilla/select_default_samba_update.html',
                          {
                              'update_samba_name': update_samba_name,
                              'update_status': update_status,
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


# 自动启动信息查询
def boot_from_clonezilla_auto(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_search=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])
        if request.method == 'GET':
            boot_from_clonezilla_list = BootFromClonezilla.objects.all().order_by('name')
            if boot_from_clonezilla_list.count() != 0:
                can_find = True
                find_num = boot_from_clonezilla_list.count()
            else:
                can_find = False
                find_num = 0

            paginator = Paginator(boot_from_clonezilla_list, 16, 2)
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
            return render(request, 'manager/boot_from_clonezilla/boot_from_clonezilla_auto.html',
                          {
                              'boot_from_clonezilla_list': customer,
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
                boot_from_clonezilla_list = BootFromClonezilla.objects.all().order_by('name')
                find_num = boot_from_clonezilla_list.count()
                if find_num == 0:
                    can_find = False
                else:
                    can_find = True
            else:
                boot_from_clonezilla_list = BootFromClonezilla.objects.filter(
                    Q(name__icontains=keyword) |
                    Q(mac__icontains=keyword) |
                    Q(updated__icontains=keyword) |
                    Q(explain__icontains=keyword)
                ).order_by('name')
                find_num = boot_from_clonezilla_list.count()
                if find_num == 0:
                    can_find = False
                else:
                    can_find = True
                print('是否可以查到：', can_find)
            print('查询到的数量：', find_num)

            return render(request, 'manager/boot_from_clonezilla/boot_from_clonezilla_auto.html',
                          {
                              'boot_from_clonezilla_list': boot_from_clonezilla_list,
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


# 自动启动信息删除
def boot_from_clonezilla_auto_delete(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_del=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == 'GET':
            # delete_name = request.GET.get('delete_name')
            # BootFromClonezilla.objects.filter(name=delete_name).delete()
            delete_id = request.GET.get('delete_id')
            BootFromClonezilla.objects.filter(id=delete_id).delete()
            delete_status = '删除完成！'
            print('删除自动启动信息，Django的id值是：', delete_id)
            boot_from_clonezilla_list = BootFromClonezilla.objects.all()
            if boot_from_clonezilla_list.count() != 0:
                can_find = True
                find_num = boot_from_clonezilla_list.count()
            else:
                can_find = False
                find_num = 0
            return render(request, 'manager/boot_from_clonezilla/boot_from_clonezilla_auto.html',
                          {
                              'delete_status': delete_status,
                              'boot_from_clonezilla_list': boot_from_clonezilla_list,
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


# 自动启动信息更新
def boot_from_clonezilla_auto_update(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_update=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])
        print('进入更新自动启动信息')
        if request.method == 'GET':
            http_server_list = HttpServerList.objects.all()
            samba_server_list = SambaServerList.objects.all()
            image_file_list = ImageFilesList.objects.all().order_by('name')
            restore_disk_list = RestoreDiskNum.objects.all()

            update_id = request.GET.get('update_id')
            update_name = BootFromClonezilla.objects.get(id=update_id)
            print('需要更新的对象的id值：', update_id, '对象是：', update_name.name)
            return render(request, 'manager/boot_from_clonezilla/boot_from_clonezilla_auto_update.html',
                          {
                              'http_server_list': http_server_list,
                              'samba_server_list': samba_server_list,
                              'image_file_list': image_file_list,
                              'restore_disk_list': restore_disk_list,
                              'update_name': update_name,
                          })
        else:
            id = request.POST.get('id')
            # 如果用name来确认，假如name发生变化，后面的 DefaultImageSelect.objects.get(select_name=name)将查不到
            print('使用Django自动创建的唯一的id作为查询修改：', id)
            name = request.POST.get('name')

            mac = request.POST.get('mac')

            http_server = request.POST.get('http_server')
            http_server_select = HttpServerList.objects.get(http_name=http_server)

            samba_server = request.POST.get('samba_server')
            samba_server_select = SambaServerList.objects.get(samba_name=samba_server)

            image_file = request.POST.get('image_file')
            image_file_select = ImageFilesList.objects.get(name=image_file)

            image_path = request.POST.get('image_path')

            restore_disk = request.POST.get('restore_disk')
            restore_disk_select = RestoreDiskNum.objects.get(disk_name=restore_disk)

            available = request.POST.get('available')
            if available == 'y':
                available = True
            else:
                available = False
            explain = request.POST.get('explain')

            # 执行所有更新
            BootFromClonezilla.objects.filter(id=id).update(
                name=name,
                mac=mac,
                http_server=http_server_select,
                samba_server=samba_server_select,
                image_file=image_file_select,
                image_path=image_path,
                restore_disk=restore_disk_select,
                available=available,
                explain=explain,
            )

            update_status = '更新完成！上面显示更新后的结果。'

            http_server_list = HttpServerList.objects.all()
            samba_server_list = SambaServerList.objects.all()
            image_file_list = ImageFilesList.objects.all()
            restore_disk_list = RestoreDiskNum.objects.all()
            update_name = BootFromClonezilla.objects.get(name=name)
            print(update_name.name)
            return render(request, 'manager/boot_from_clonezilla/boot_from_clonezilla_auto_update.html',
                          {
                              'http_server_list': http_server_list,
                              'samba_server_list': samba_server_list,
                              'image_file_list': image_file_list,
                              'restore_disk_list': restore_disk_list,
                              'update_name': update_name,
                              'update_status': update_status,
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


# HTTP服务器管理，默认项确定
def select_default_http(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_search=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        choose_http = request.GET.get('choose')
        update_http = request.GET.get('update')
        delete_http = request.GET.get('delete')
        add_http = request.GET.get('add')
        switch_status = ''
        # 设置默认的Http服务器
        if choose_http is not None:
            if HttpServerList.objects.filter(http_name=choose_http)[0].available is True:
                HttpServerList.objects.filter(http_name=choose_http).update(default=True)
                HttpServerList.objects.exclude(http_name=choose_http).update(default=False)
                print('\n将 %s 设置为默认HTTP服务器\n' % choose_http)
                switch_status = '\n将【 %s 】设置为默认HTTP服务器\n' % choose_http
            else:
                switch_status = '【 %s 】未启用，需启用后在进行切换！' % choose_http

        # 删除Http服务器
        if delete_http is not None:
            if User.objects.filter(username=request.session['session_name'], auth_del=1).count() == 1:
                print('用户 %s 已有权限访问！' % request.session['session_name'])
                HttpServerList.objects.filter(http_name=delete_http).delete()
                print('\n将 %s HTTP服务器删除\n' % choose_http)
            else:
                if User.objects.filter(username=request.session['session_name']).count() == 1:
                    print('用户 %s 无删除权限！' % request.session['session_name'])
                    return render(request, 'user/unauth_access.html')
                else:
                    print('未登录！请登陆后操作。')
                    # return render(request, 'user/login.html')
                    return HttpResponseRedirect('/user/login?next=%s' % request.path)

        # 更新
        if update_http is not None:
            if User.objects.filter(username=request.session['session_name'], auth_update=1).count() == 1:
                print('用户 %s 已有权限访问！' % request.session['session_name'])
                update_http_server = HttpServerList.objects.get(http_name=update_http)
                return render(request, 'manager/boot_from_clonezilla/select_default_http_update.html',
                              {
                                  'update_http_server': update_http_server,
                              })
            else:
                if User.objects.filter(username=request.session['session_name']).count() == 1:
                    print('用户 %s 无权限！' % request.session['session_name'])
                    return render(request, 'user/unauth_access.html')
                else:
                    print('未登录！请登陆后操作。')
                    # return render(request, 'user/login.html')
                    return HttpResponseRedirect('/user/login?next=%s' % request.path)

        # 增加
        if add_http is not None:
            if User.objects.filter(username=request.session['session_name'], auth_add=1).count() == 1:
                print('用户 %s 已有权限访问！' % request.session['session_name'])
                return render(request, 'manager/boot_from_clonezilla/select_default_http_add.html')
            else:
                if User.objects.filter(username=request.session['session_name']).count() == 1:
                    print('用户 %s 无权限！' % request.session['session_name'])
                    return render(request, 'user/unauth_access.html')
                else:
                    print('未登录！请登陆后操作。')
                    # return render(request, 'user/login.html')
                    return HttpResponseRedirect('/user/login?next=%s' % request.path)

        http_select_list = HttpServerList.objects.all().order_by('http_name')
        find_num = http_select_list.count()
        if find_num != 0:
            can_find = True
        return render(request, 'manager/boot_from_clonezilla/select_default_http.html',
                      {
                          'http_select_list': http_select_list,
                          'can_find': can_find,
                          'find_num': find_num,
                          'switch_status': switch_status,
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


def select_default_http_update(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_update=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == 'GET':
            http_name = request.GET.get('http_name')
            print('需要更新的Http对象：', http_name)
            update_http_server = HttpServerList.objects.get(id=id)
            return render(request, 'manager/boot_from_clonezilla/select_default_http_update.html',
                          {
                              'update_http_server': update_http_server,

                          })

        else:
            id = request.POST.get('id')
            http_name = request.POST.get('http_name')
            http_ip = request.POST.get('http_ip')
            http_port = request.POST.get('http_port')
            http_folder = request.POST.get('http_folder')
            available = request.POST.get('available')
            if available == 'y':
                available = True
            else:
                available = False

            default = request.POST.get('default')
            if default == 'y':
                default = True
            else:
                default = False

            # 如果新增的把默认设置为True，则先筛选其他默认为True的更新成False
            if default is True:
                HttpServerList.objects.filter(default=default).update(default=False)

            explain = request.POST.get('explain')
            HttpServerList.objects.filter(id=id).update(
                http_name=http_name,
                http_ip=http_ip,
                http_port=http_port,
                http_folder=http_folder,
                available=available,
                default=default,
                explain=explain,
            )
            update_http_server = HttpServerList.objects.get(id=id)
            update_status = '更新完成！上面显示更新后的结果。'
            print('\n更新 %s 的信息完成。\n' % http_name)
            return render(request, 'manager/boot_from_clonezilla/select_default_http_update.html',
                          {
                              'update_http_server': update_http_server,
                              'update_status': update_status,
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


def select_default_http_add(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_add=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        id = request.POST.get('id')
        http_name = request.POST.get('http_name')
        http_ip = request.POST.get('http_ip')
        http_port = request.POST.get('http_port')
        http_folder = request.POST.get('http_folder')
        available = request.POST.get('available')
        if available == 'y':
            available = True
        else:
            available = False

        default = request.POST.get('default')
        if default == 'y':
            default = True
        else:
            default = False

        # 如果新增的把默认设置为True，则先筛选其他默认为True的更新成False
        if default is True:
            HttpServerList.objects.filter(default=default).update(default=False)

        explain = request.POST.get('explain')
        HttpServerList.objects.create(
            http_name=http_name,
            http_ip=http_ip,
            http_port=http_port,
            http_folder=http_folder,
            available=available,
            default=default,
            explain=explain,
        )
        add_http_server = HttpServerList.objects.get(http_name=http_name)
        add_status = '增加完成！上面显示更新后的结果。'
        print('\n增加 %s 的信息完成。\n' % http_name)
        return render(request, 'manager/boot_from_clonezilla/select_default_http_add.html',
                      {
                          'add_http_server': add_http_server,
                          'add_status': add_status,
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


# 更新默认启动控制的HTTP服务器未HTTP服务器管理表中默认的项
def update_select_default_image_http(request):
    http_server = HttpServerList.objects.filter(default=True)
    if http_server.count() == 1:
        DefaultImageSelect.objects.all().update(http_server=http_server[0])
    return HttpResponseRedirect('/manage/select_default_image_control.html')


# Clonezilla镜像文件名称远程管理
def image_name_remote_manage(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_add=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == 'GET':
            get_images = get_images_list()
            if get_images is None:
                images_list = []
                default_recent_image_name = ''
            else:
                # 通过外部调用ext_getsambafiles.py获取文件夹的列表
                images_list = get_images[0]
                # 通过外部调用ext_getsambafiles.py获取创建的最新的文件夹名字
                default_recent_image_name = get_images[1]

            if images_list is None or len(images_list) == 0:
                can_choose = False
            else:

                can_choose = True
            return render(request, 'manager/boot_from_clonezilla/image_name_remote_manage.html',
                          {
                              'images_list': images_list,
                              'can_choose': can_choose,
                              'default_recent_image_name': default_recent_image_name,
                          })
        else:
            image_name = request.POST.get('image_name')
            new_name = request.POST.get('new_name')

            status = ''
            if rename_image(image_name, new_name) is True:
                status += '远程镜像重命名成功，'
                if ImageFilesList.objects.filter(image_name=image_name).count() != 0:
                    ImageFilesList.objects.filter(image_name=image_name).update(image_name=new_name)
                    status += '更新本地数据库。'
                else:
                    status += '未更新本地数据库。'
            else:
                status += '远程镜像重命名失败。'

            get_images = get_images_list()
            if get_images is None:
                images_list = []
                default_recent_image_name = ''
            else:
                # 通过外部调用ext_getsambafiles.py获取文件夹的列表
                images_list = get_images[0]
                # 通过外部调用ext_getsambafiles.py获取创建的最新的文件夹名字
                default_recent_image_name = get_images[1]

            if images_list is None or len(images_list) == 0:
                can_choose = False
            else:
                can_choose = True

            return render(request, 'manager/boot_from_clonezilla/image_name_remote_manage.html',
                          {
                              'status': status,
                              'images_list': images_list,
                              'can_choose': can_choose,
                              'default_recent_image_name': default_recent_image_name,
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


# Clonezilla远程重命名日志
def image_rename_logs(request):
    rename_log = rename_logs().split('|')
    # print(rename_log)
    # logs = []
    # for log in rename_log:
    #     tmp = log.split()
    #     logs.append(tmp)
    # print(logs)
    logs = [log.split() for log in rename_log]  # 列表生成式
    # print(logs)

    return render(request, 'manager/boot_from_clonezilla/image_rename_logs.html',
                  {
                      'logs': logs,
                  })


# 镜像是否在所有服务器上完成同步
def samba_sync_state(request):
    get_files_list = []
    # samba_server = SambaServerList.objects.filter(available=True)
    # for samba in samba_server:
    #     file_return = get_files_info(samba.samba_ip)
    #     print('\n', samba.samba_ip, '\n', file_return)
    #     if file_return is not None:
    #         # print('有返回值！')
    #         if file_return[3] not in get_files_list:
    #             get_files_list.append(file_return[3])
    # print(len(get_files_list), '++++++++++')
    for images in samba_sync():
        if images not in get_files_list:
            get_files_list.append(images)
    if len(get_files_list) == 1:
        return HttpResponse('''
                <a href="#">
                    <i class="fa fa-circle-o text-aqua"></i> <span>镜像文件已完成同步！</span>
                    <span class="pull-right-container">
                        <small class="label pull-right bg-green">:)</small>
                    </span>
                </a>
        ''')
    else:
        # print('未同步')
        return HttpResponse('''
                <a href="#">
                    <i class="fa fa-circle-o text-red"></i> <span>镜像%s台未完成同步！</span>
                    <span class="pull-right-container">
                        <small class="label pull-right bg-red">:(</small>
                    </span>
                </a>
        ''' % str(len(get_files_list)-1))


# Clonezilla镜像文件名称远程删除-调用接口是移动到另一个文件夹
def image_remote_del(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_del=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == 'GET':
            get_images = get_images_list()
            if get_images is None:
                images_list = []
                default_recent_image_name = ''
            else:
                # 通过外部调用ext_getsambafiles.py获取文件夹的列表
                images_list = get_images[0]
                # 通过外部调用ext_getsambafiles.py获取创建的最新的文件夹名字
                default_recent_image_name = get_images[1]

            if images_list is None or len(images_list) == 0:
                can_choose = False
            else:

                can_choose = True
            return render(request, 'manager/boot_from_clonezilla/image_remote_del.html',
                          {
                              'images_list': images_list,
                              'can_choose': can_choose,
                              'default_recent_image_name': default_recent_image_name,
                          })
        else:
            image_name = request.POST.get('image_name')

            status = ''
            if del_image(image_name) is True:
                status += '远程删除镜像成功，'
            else:
                status += '远程删除镜像失败。'

            get_images = get_images_list()
            if get_images is None:
                images_list = []
                default_recent_image_name = ''
            else:
                # 通过外部调用ext_getsambafiles.py获取文件夹的列表
                images_list = get_images[0]
                # 通过外部调用ext_getsambafiles.py获取创建的最新的文件夹名字
                default_recent_image_name = get_images[1]

            if images_list is None or len(images_list) == 0:
                can_choose = False
            else:
                can_choose = True

            return render(request, 'manager/boot_from_clonezilla/image_remote_del.html',
                          {
                              'status': status,
                              'images_list': images_list,
                              'can_choose': can_choose,
                              'default_recent_image_name': default_recent_image_name,
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


# Clonezilla镜像还原
def image_remote_restore(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_add=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == 'GET':
            get_images = get_del_images_list()
            if get_images is None:
                images_list = []
                default_recent_image_name = ''
            else:
                # 通过外部调用ext_getsambafiles.py获取文件夹的列表
                images_list = get_images[0]
                # 通过外部调用ext_getsambafiles.py获取创建的最新的文件夹名字
                default_recent_image_name = get_images[1]

            if images_list is None or len(images_list) == 0:
                can_choose = False
            else:

                can_choose = True
            return render(request, 'manager/boot_from_clonezilla/image_remote_restore.html',
                          {
                              'images_list': images_list,
                              'can_choose': can_choose,
                              'default_recent_image_name': default_recent_image_name,
                          })
        else:
            image_name = request.POST.get('image_name')
            new_name = request.POST.get('new_name')

            if new_name.strip() == '':
                new_name = image_name

            status = ''
            if restore_image(image_name, new_name) is True:
                status += '远程还原镜像成功，'
            else:
                status += '远程还原镜像失败。'

            get_images = get_del_images_list()
            if get_images is None:
                images_list = []
                default_recent_image_name = ''
            else:
                # 通过外部调用ext_getsambafiles.py获取文件夹的列表
                images_list = get_images[0]
                # 通过外部调用ext_getsambafiles.py获取创建的最新的文件夹名字
                default_recent_image_name = get_images[1]

            if images_list is None or len(images_list) == 0:
                can_choose = False
            else:
                can_choose = True

            return render(request, 'manager/boot_from_clonezilla/image_remote_restore.html',
                          {
                              'status': status,
                              'images_list': images_list,
                              'can_choose': can_choose,
                              'default_recent_image_name': default_recent_image_name,
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


def show_image_info(request):
    image_name = request.POST.get('image_name')
    flag = request.POST.get('flag')
    # print(flag)
    print('需要获取信息的镜像名：', image_name)
    if flag == 'del_list':
        print('获取已删除镜像')
        get_images_info = get_del_images_list()
    else:
        get_images_info = get_images_list()
    print(get_images_info)
    image_date = get_images_info[2][image_name]
    image_date = datetime.datetime.utcfromtimestamp(image_date).strftime("%Y-%m-%d %H:%M:%S")
    # print(image_date)
    image_size = get_images_info[3][image_name]
    image_size = round(image_size / 1024, 1)
    # print(image_size)
    image_info = dict()
    image_info['date'] = image_date
    image_info['size'] = image_size
    print('信息：', image_info)
    return HttpResponse(json.dumps(image_info))