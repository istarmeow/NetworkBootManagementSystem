# -*- coding:utf-8 -*-

from django.shortcuts import render, redirect
from .models import User, UserAuthApply, UserVerificationCode
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
import re
from django.core import serializers
from django.db.models import Q
import json
import django.utils.timezone as timezone
import random
from .ext_sendemail import send_mail
import django.utils.timezone as timezone


# 用户注册
def register_old(request):
    if request.method == 'GET':
        return render(request, 'user/register.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        email = request.POST.get('email')
        reg = r"^[\w\d]+[\d\w\_\.]+@([\d\w]+)\.([\d\w]+)(?:\.[\d\w]+)?$"

        if password == repassword:
            # 加密，生成密文
            mp_password = make_password(password)
            if User.objects.filter(username=username).count() != 0:
                seccess_status = '已有用户%s！返回登录选择忘记密码。' % username
            else:
                if not re.match(reg, email):
                    seccess_status = '邮箱 %s 格式错误！' % email
                else:
                    User.objects.create(
                        username=username,
                        password=mp_password,
                        email=email,
                        auth_search=1,
                        available=False
                    )
                    seccess_status = '用户 %s 验证码成功，请输入。' % username
        else:
            seccess_status = '两次输入密码不一致！'

        return render(request, 'user/register.html',
                      {
                          'seccess_status': seccess_status,
                      })


def register_123(request):
        if request.method == 'GET':
            return render(request, 'user/register.html')
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
            repassword = request.POST.get('repassword')
            email = request.POST.get('email')
            verify = request.POST.get('verify')
            if UserVerificationCode.objects.filter(username=username).count() != 0:
                if UserVerificationCode.objects.filter(username=username).order_by('-created')[0].verify == verify:
                    mp_password = make_password(password)
                    User.objects.create(
                        username=username,
                        password=mp_password,
                        email=email,
                        auth_search=1,
                        verify=verify,
                        available=True,
                    )
                    seccess_status = '用户 %s 验证码成功，返回登录。' % username
                    print(seccess_status)

                    now = timezone.now()
                    old = now - timezone.timedelta(minutes=1)
                    UserVerificationCode.objects.filter(created__lt=old, username=username).delete()

                    return render(request, 'user/register.html',
                                  {
                                      'seccess_status': seccess_status,
                                  })
                else:
                    seccess_status = '用户 %s 验证码失败，请重试。' % username
                    print(seccess_status)

                    retrynum = UserVerificationCode.objects.filter(username=username)[0].retrynum
                    UserVerificationCode.objects.filter(username=username).update(retrynum=retrynum + 1)
                    if UserVerificationCode.objects.filter(username=username)[0].retrynum > 3:
                        UserVerificationCode.objects.filter(username=username).delete()
                        seccess_status = '用户 %s 验证次数超过三次，请稍后再试。' % username

                    now = timezone.now()
                    old = now - timezone.timedelta(minutes=3)
                    UserVerificationCode.objects.filter(created__lt=old, username=username).delete()

                    return render(request, 'user/register.html',
                                  {
                                      'seccess_status': seccess_status,
                                  })
            else:
                seccess_status = '用户 %s 验证码异常，请重试。' % username
                return render(request, 'user/register.html',
                              {
                                  'seccess_status': seccess_status,
                      })


# 用户注册
def register(request):
    if request.method == 'GET':
        return render(request, 'user/register.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        email = request.POST.get('email')
        verify = request.POST.get('verify')
        if UserVerificationCode.objects.filter(username=username, inbox=email).count() != 0:
            now = timezone.now()
            # old = now - timezone.timedelta(minutes=10)
            created_time = UserVerificationCode.objects.filter(username=username, inbox=email).order_by('-created')[0].created

            # 使用注册时间作为判断时间
            regist_time = UserVerificationCode.objects.filter(username=username, inbox=email).order_by('-created')[0].updated
            time_difference = (now - regist_time).total_seconds()  # 时差转换成秒
            m, s = divmod(float(time_difference), 60)
            process_time = str(int(m)) + "分" + str(int(s)) + '秒'
            m = int(m)
            print(process_time)

            retrynum = UserVerificationCode.objects.filter(username=username, inbox=email, created=created_time).order_by('-created')[0].retrynum

            # 验证码执行一次后，次数+1，当验证码重试次数超过3次后，则在m分钟内不能再重试
            if retrynum < 3:
                # 如果验证码相同，则将用户信息注册到数据库，否则更新重试次数和更新时间两个字段
                if UserVerificationCode.objects.filter(username=username, inbox=email).order_by('-created')[0].verify == verify:
                    mp_password = make_password(password)
                    User.objects.create(
                        username=username,
                        password=mp_password,
                        email=email,
                        auth_search=1,
                        verify=verify,
                        available=True,
                    )
                    seccess_status = '用户 %s 验证码成功，返回登录。' % username
                else:
                    UserVerificationCode.objects.filter(username=username, inbox=email, created=created_time).update(retrynum=retrynum + 1)
                    retrynum = UserVerificationCode.objects.filter(username=username, inbox=email, created=created_time).order_by('-created')[0].retrynum
                    seccess_status = '用户 %s 验证重试第%s次。' % (username, retrynum)
            else:
                # 时间超出允许范围后才能开始验证注册
                if m >= 10:
                    # 将发送时间和更新时间重置为现在的时间
                    if UserVerificationCode.objects.filter(username=username, inbox=email).order_by('-created')[0].verify == verify:
                        mp_password = make_password(password)
                        User.objects.create(
                            username=username,
                            password=mp_password,
                            email=email,
                            auth_search=1,
                            verify=verify,
                            available=True,
                        )
                        seccess_status = '用户 %s 验证码成功，返回登录。' % username
                    else:
                        seccess_status = '用户 %s 验证重试第1次。' % username
                        UserVerificationCode.objects.filter(username=username, inbox=email, created=created_time).update(retrynum=1, updated=now)
                        print('重试超过3次后，在重试时间后，将注册时间更新为当前时间。')
                else:
                    seccess_status = '用户 %s 验证码失败，重试请在%s分钟后重试。' % (username, str(10-m))

            return render(request, 'user/register.html',
                          {
                              'seccess_status': seccess_status,
                          })

        else:
            seccess_status = '用户 %s 验证码异常，请重新获取。' % username
            return render(request, 'user/register.html',
                          {
                              'seccess_status': seccess_status,
                          })


# 发送验证码存储到数据库
def send_verify(request):
    username = request.POST.get('username')
    inbox = request.POST.get('inbox')
    password = request.POST.get('password')
    repassword = request.POST.get('repassword')
    print(username, inbox)
    reg = r"^[\w\d]+[\d\w\_\.]+@([\d\w]+)\.([\d\w]+)(?:\.[\d\w]+)?$"
    send_status = False
    if password == repassword:
        # 加密，生成密文
        if User.objects.filter(username=username).count() != 0:
            seccess_status = '已有用户%s！返回登录选择忘记密码。' % username
        elif User.objects.filter(email=inbox).count() != 0:
            seccess_status = '已有邮箱%s！需更换邮箱注册。' % inbox

        else:
            if not re.match(reg, inbox):
                if len(inbox) == 0:
                    seccess_status = '邮箱不能为空！'
                else:
                    seccess_status = '邮箱 %s 格式错误！' % inbox
            else:
                seccess_status = '成功发送验证码！'
                send_status = True
    else:
        seccess_status = '两次输入密码不一致！'

    verify = random.randint(1000, 9999)
    if send_status:
        now = timezone.now()
        # 数据库中不存在这个邮箱的记录
        if UserVerificationCode.objects.filter(inbox=inbox).count() < 1:
            UserVerificationCode.objects.create(
                username=username,
                verify=verify,
                outbox='xyliurui@yeah.net',
                inbox=inbox,
            )
            can_send = True
            print('第1次发送验证码。')
        else:
            # 如果已存在，则获取最新创建的那个时间
            created_time = UserVerificationCode.objects.filter(inbox=inbox).order_by('-created')[0].created
            time_difference = (now - created_time).total_seconds()  # 时差转换成秒
            m, s = divmod(float(time_difference), 60)
            m = int(m)

            sendnum = UserVerificationCode.objects.filter(inbox=inbox, created=created_time)[0].sendnum
            print('时间：', m, sendnum)
            # 如果发送次数没超过三次，则可以继续发送，并且把次数+1，如果在这个时间段内次数少于三次才继续发，超出该时间段，不管怎么都重新创建数据库，并发送邮件。
            if sendnum < 3 and m < 10:
                UserVerificationCode.objects.filter(inbox=inbox, created=created_time).update(sendnum=sendnum+1)
                verify = UserVerificationCode.objects.filter(inbox=inbox, created=created_time)[0].verify
                can_send = True
                print('第%s次发送验证码。' % sendnum)
            else:
                if m >= 10:
                    UserVerificationCode.objects.create(
                        username=username,
                        verify=verify,
                        outbox='xyliurui@yeah.net',
                        inbox=inbox,
                    )
                    can_send = True
                    print('时间更新，重新发送验证码。')
                else:
                    can_send = False
        if can_send is True:
            subject = 'PXE控制系统：%s' % str(verify)
            content = '''
            <html>
                <body>
                <h1>***欢迎使用PXE控制系统***</h1>
                <h2>【%s】您的验证码是：%s</h2>
                <p>网站地址：<a href="http://192.168.96.20/manage/select_default_image_control.html">点击跳转</a></p>
                </body>
            </html>''' % (username, str(verify))
            if send_mail(inbox, subject, content) is True:
                seccess_status = '成功发送验证码！'
            else:
                seccess_status = '发送验证码失败！'
        else:
            print('系统判断次数过多，%s 分钟内阻止发送邮件。' % str(10-m))
            seccess_status = '系统判断次数过多，%s 分钟内阻止发送邮件。' % str(10-m)

    return HttpResponse(seccess_status)


# 用户登录
def login(request):
    next_url = request.GET.get('next')
    print('获取跳转的页面：', next_url)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).count() == 0:
            no_user = True

            print('登录用户不存在！跳转到注册页面')
            return render(request, 'user/register.html',
                          {
                              'no_user': no_user,
                          })
        else:
            user = User.objects.get(username=username)
            if check_password(password, user.password) and user.available is True:
                request.session['session_name'] = user.username
                print('登录成功！', request.session.get('session_name'), '        request.path:', request.path)

                print(request.session.set_test_cookie())
                # return HttpResponse("欢迎 %s ，登录成功！" % username)
                next_url = request.POST.get('next_url')
                print('POST登录后跳转：', next_url, type(next_url))
                # 登录成功就将url重定向到后台的url
                if next_url == 'None' or next_url == '':
                    # return redirect('/manage/select_default_image_control.html')
                    return redirect('/')
                else:
                    return redirect(next_url)

            else:
                if check_password(password, user.password) is False:
                    print('密码错误！重新登录')
                    password_correct = '密码错误！重新登录'
                else:
                    print('账号异常！联系管理员')
                    password_correct = '账号异常！联系管理员'

                return render(request, 'user/login.html',
                              {
                                  'password_correct': password_correct,
                              })
    # 登录不成功或第一访问就停留在登录页面
    return render(request, 'user/login.html', locals())

# 用户登出
def logout(request):
    try:
        del request.session['session_name']
        print('退出登录，删除session！')
    except KeyError:
        pass
    # return HttpResponse("退出登录！")
    return redirect('/user/login')


# 用户管理（登录用户只能是admin情况下才显示）
def user_management(request):
    if request.session['session_name'] == 'admin':
        if request.method == 'GET':
            user_list = User.objects.all().order_by('username')
            # print(user_list)

            return render(request, 'user/user_management.html',
                          {
                              'user_list': user_list,
                          })
        else:
            user_list = User.objects.all().order_by('username')
            auth_switch = request.POST.get('auth_switch')
            print(request.POST.get('username'))
            print(auth_switch)
            return render(request, 'user/user_management.html',
                          {
                              'user_list': user_list,
                          })
    else:
        return HttpResponse('Error!')


# 使用ajax显示用户的权限列表
def ajax_user_management_to_json(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword')
        # print('关键字：', keyword)
        if keyword is None:
            show_all = True
        elif keyword.strip().replace(' ', '') == '':
            show_all = True
        else:
            keyword = keyword.strip().replace(' ', '')
            show_all = False
        # print('是否显示全部：', show_all)
        if show_all:
            user_list = User.objects.all().order_by('username')
            find_num = user_list.count()
            if find_num == 0:
                can_find = False
            else:
                can_find = True
        else:
            user_list = User.objects.filter(
                Q(username__icontains=keyword) |
                Q(email__icontains=keyword)
            ).order_by('username')
            find_num = user_list.count()
        user_list_json = serializers.serialize('json', user_list)
        return HttpResponse(user_list_json)


# 使用ajax post修改用户的权限
def ajax_user_management_switch_auth(request):
    username = request.POST.get('username')
    authname = request.POST.get('authname')
    # print(username, authname)
    user_auth_ctrl = {'auth_search_on':
                          {'name': 'auth_search', 'switch': '1'},
                      'auth_search_off':
                          {'name': 'auth_search', 'switch': '0'},
                      'auth_add_on':
                          {'name': 'auth_add', 'switch': '1'},
                      'auth_add_off':
                          {'name': 'auth_add', 'switch': '0'},
                      'auth_del_on':
                          {'name': 'auth_del', 'switch': '1'},
                      'auth_del_off':
                          {'name': 'auth_del', 'switch': '0'},
                      'auth_update_on':
                          {'name': 'auth_update', 'switch': '1'},
                      'auth_update_off':
                          {'name': 'auth_update', 'switch': '0'},
                      }
    # print(user_auth_ctrl[authname]['name'], user_auth_ctrl[authname]['switch'])
    auth = user_auth_ctrl[authname]['name']
    switch = user_auth_ctrl[authname]['switch']
    if auth == 'auth_search':
        User.objects.filter(username=username).update(auth_search=switch)
        if switch == '1':
            ms = '打开'
        else:
            ms = '关闭'
        message = '用户 ' + username + ' 的<查找权限>已' + ms
    if auth == 'auth_add':
        User.objects.filter(username=username).update(auth_add=switch)
        if switch == '1':
            ms = '打开'
        else:
            ms = '关闭'
        message = '用户 ' + username + ' 的<增加权限>已' + ms
    if auth == 'auth_del':
        User.objects.filter(username=username).update(auth_del=switch)
        if switch == '1':
            ms = '打开'
        else:
            ms = '关闭'
        message = '用户 ' + username + ' 的<删除权限>已' + ms
    if auth == 'auth_update':
        User.objects.filter(username=username).update(auth_update=switch)
        if switch == '1':
            ms = '打开'
        else:
            ms = '关闭'
        message = '用户 ' + username + ' 的<修改权限>已' + ms
    return HttpResponse(message)


# 显示当前登录用户的权限
def show_current_user_permissions(request):
    try:
        username = request.session['session_name']
    except KeyError:
        pass
    user_permissions = User.objects.filter(username=username)
    user_permissions_json = serializers.serialize('json', user_permissions)
    return HttpResponse(user_permissions_json)


# 存储处理申请权限的数据
def user_apply_permissions(request):
    username = request.POST.get('username')
    auth_search = str(request.POST.get('auth_search'))
    auth_del = str(request.POST.get('auth_del'))
    auth_add = str(request.POST.get('auth_add'))
    auth_update = str(request.POST.get('auth_update'))
    time_now = timezone.now()
    print(auth_search)
    UserAuthApply.objects.create(
        username=username,
        auth_search=auth_search,
        auth_add=auth_add,
        auth_del=auth_del,
        auth_update=auth_update,
        statue='0'
    )
    print('用户 %s 正在申请权限' % username)
    return HttpResponse('权限申请成功，等待处理')


# 显示用户申请的未处理的权限
def show_user_apply_permissions(request):
    user_apply = UserAuthApply.objects.filter(statue='0')
    user_apply_json = serializers.serialize('json', user_apply)
    return HttpResponse(user_apply_json)


# 通过用户申请
def adopt_user_apply(request):
    username = request.POST.get('username')
    auth_search = str(request.POST.get('auth_search'))
    auth_del = str(request.POST.get('auth_del'))
    auth_add = str(request.POST.get('auth_add'))
    auth_update = str(request.POST.get('auth_update'))
    time_now = timezone.now()
    # print(username)
    # print(UserAuthApply.objects.filter(username=username, statue='0'))
    UserAuthApply.objects.filter(username=username, statue='0').update(
        updated=time_now,
        statue='1'
    )
    User.objects.filter(username=username).update(
        auth_search=auth_search,
        auth_del=auth_del,
        auth_add=auth_add,
        auth_update=auth_update,
        updated=time_now
    )
    print('用户 %s 权限已通过！' % username)
    return HttpResponse('权限已通过！')


# 拒绝用户申请
def refuse_user_apply(request):
    username = request.POST.get('username')
    time_now = timezone.now()
    UserAuthApply.objects.filter(username=username, statue='0').update(
        updated=time_now,
        statue='-1'
    )
    print('用户 %s 权限已拒绝！' % username)
    return HttpResponse('权限已拒绝！')


# 修改密码
def reset_password(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name']).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])
        if request.method == 'POST':
            reset = request.POST
            old_passwd = reset['old_passwd'].strip()
            new_passwd = reset['new_passwd'].strip()
            renew_passwd = reset['renew_passwd'].strip()

            mailbox = User.objects.get(username=request.session['session_name']).email

            if request.session['session_name'] == reset['username'] and new_passwd == renew_passwd and check_password(old_passwd, User.objects.get(username=reset['username']).password):
                User.objects.filter(username=reset['username']).update(password=make_password(new_passwd), updated=timezone.now())
                subject = 'PXE控制系统：密码修改'
                content = '''
                <html>
                    <body>
                    <h1>***欢迎使用PXE控制系统***</h1>
                    <h2>【%s】您的新密码是：%s</h2>
                    <p>网站地址：<a href="http://192.168.96.20/manage/select_default_image_control.html">点击跳转</a></p>
                    </body>
                </html>''' % (reset['username'], new_passwd)
                if send_mail(mailbox, subject, content) is True:
                    print('修改密码发送成功！')
                    return render(request, 'user/reset_password.html',
                                  {
                                      'status': '修改成功！退出登录【新密码已发送到邮箱，注意查收。】',
                                      'mailbox': mailbox,
                                  })
                else:
                    return render(request, 'user/reset_password.html',
                                  {
                                      'status': '修改成功！退出登录【尝试发送新密码到邮箱可能失败。】',
                                      'mailbox': mailbox,
                                  })
            else:
                return render(request, 'user/reset_password.html',
                              {
                                  'status': '修改失败！检查原密码，和新密码是否正确。',
                                  'mailbox': mailbox,
                              })
        else:
            mailbox = User.objects.get(username=request.session['session_name']).email
            return render(request, 'user/reset_password.html',
                          {
                              'mailbox': mailbox,
                          })
    else:
        print('未登录！请登陆后操作。')
        # return render(request, 'user/login.html')
        return HttpResponseRedirect('/user/login?next=%s' % request.path)