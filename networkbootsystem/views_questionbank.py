# -*- coding:utf-8 -*-

from django.shortcuts import render, HttpResponse
from django.http import HttpResponseRedirect
from .models import QuestionBank, User
import random
from django.conf import settings
import os
import platform
import datetime
from . import ext_delemptydir
from django.db.models import Q
from . import ext_exportword
import platform


def questionadd(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_add=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == "POST":
            # 考题的分类
            selectcategory = request.POST.get('selectcategory')
            inputcategory = request.POST.get('inputcategory').strip()

            # 考题的类型
            selectquestiontype = request.POST.get('selectquestiontype')
            inputquestiontype = request.POST.get('inputquestiontype')

            flag1 = False
            flag2 = False
            # 题目分类判断
            if selectcategory == '' and inputcategory == '':
                status = '分类都为空，只能选择一项'
                flag1 = False
            elif selectcategory != '' and inputcategory != '':
                status = '分类都有值，只能选择一项'
                flag1 = False
            else:
                status = '提交成功！'
                flag1 = True
                if selectcategory != '':
                    category = selectcategory
                else:
                    category = inputcategory

            # 题目类型判断
            if selectquestiontype == '' and inputquestiontype == '':
                status = '题型都为空，只能选择一项'
                flag2 = False
            elif selectquestiontype != '' and inputquestiontype != '':
                status = '题型都有值，只能选择一项'
                flag2 = False
            else:
                flag2 = True
                if selectquestiontype != '':
                    questiontype = selectquestiontype
                else:
                    questiontype = inputquestiontype

            if flag1 is True and flag2 is True:
                status = '提交成功！'
                topic = request.POST.get('topic').strip()
                text = request.POST.get('text').strip()
                answer = request.POST.get('answer', None).strip()
                selectlevel = request.POST.get('selectlevel')
                image = request.FILES.get('image', None)  # # 获取上传的文件，如果没有文件，则默认为None
                # 如果用户上传图片
                if image is not None:
                    imagename = str(random.randint(0, 100000)) + '-' + request.FILES.get('image').name
                    print('文件？', image, imagename)
                    # 后台数据库中记录的路径是：images/2017/09/30/test.png

                    if platform.system() == 'Windows':
                        image_path = settings.MEDIA_ROOT + '\\images\\' + str(datetime.datetime.now().year) + '\\' + str(datetime.datetime.now().month) + '\\' + str(datetime.datetime.now().day)
                        if not os.path.exists(image_path):
                            os.makedirs(image_path)
                        image_file = image_path + '\\' + imagename
                        print(image_file)

                    if platform.system() == 'Linux':
                        image_path = settings.MEDIA_ROOT + '/images/' + str(datetime.datetime.now().year) + '/' + str(datetime.datetime.now().month) + '/' + str(datetime.datetime.now().day)
                        if not os.path.exists(image_path):
                            os.mkdirs(image_path)
                        image_file = image_path + '/' + imagename

                    destination = open(image_file, 'wb')
                    for chunk in image.chunks():  # 分块写入文件
                        destination.write(chunk)
                    destination.close()

                    # 保存在后台记录的路径
                    image_url = '/images/' + str(datetime.datetime.now().year) + '/' + str(datetime.datetime.now().month) + '/' + str(datetime.datetime.now().day) + '/' + imagename
                    print(image_url)
                    if QuestionBank.objects.filter(text=text).count() > 1:
                        status = '题库中已存在，不做添加！'
                    else:
                        print(category, selectlevel, questiontype, topic, text, image, status)
                        QuestionBank.objects.create(category=category, level=selectlevel, questiontype=questiontype, topic=topic, text=text, image=image_url, answer=answer)
                # 如果用户没有上传图片
                else:
                    if QuestionBank.objects.filter(text=text).count() > 1:
                        status = '题库中已存在，不做添加！'
                    else:
                        print(category, selectlevel, questiontype, topic, text, status)
                        QuestionBank.objects.create(category=category, level=selectlevel, questiontype=questiontype, topic=topic, text=text, answer=answer)

            # 题目分类
            category_list = []
            for cg in QuestionBank.objects.all():
                if cg.category not in category_list:
                    category_list.append(cg.category)
            # 提醒分类：选择、问答题
            questiontype_list = []
            for qt in QuestionBank.objects.all():
                if qt.questiontype not in questiontype_list:
                    questiontype_list.append(qt.questiontype)
            return render(request, 'questionbank/questionadd.html',
                          {
                              'category_list': category_list,
                              'status': status,
                              'questiontype_list': questiontype_list,
                          })
        else:
            # 题目分类
            category_list = []
            for cg in QuestionBank.objects.all():
                if cg.category not in category_list:
                    category_list.append(cg.category)
            # 提醒分类：选择、问答题
            questiontype_list = []
            for qt in QuestionBank.objects.all():
                if qt.questiontype not in questiontype_list:
                    questiontype_list.append(qt.questiontype)
            return render(request, 'questionbank/questionadd.html',
                          {
                              'category_list': category_list,
                              'questiontype_list': questiontype_list,
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


def index(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name']).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        questions = QuestionBank.objects.all()
        # 题目分类
        category_list = []
        for cg in QuestionBank.objects.all():
            if cg.category not in category_list:
                category_list.append(cg.category)
        # 提醒分类：选择、问答题
        questiontype_list = []
        for qt in QuestionBank.objects.all():
            if qt.questiontype not in questiontype_list:
                questiontype_list.append(qt.questiontype)
        # 难度
        level_list = []
        for lv in QuestionBank.objects.all():
            if lv.level not in level_list:
                level_list.append(lv.level)

        # 展示题库下载按钮
        if platform.system() == 'Windows':
            word_path = settings.MEDIA_ROOT + '\\static\\questionbank'
        if platform.system() == 'Linux':
            word_path = settings.MEDIA_ROOT + '/static/questionbank'
        file_list = os.listdir(word_path)

        # 筛选题库
        if request.method == 'GET':
            selectcategory = request.GET.get('selectcategory')
            selectlevel = request.GET.get('selectlevel')
            selectquestiontype = request.GET.get('selectquestiontype')
            # print(request.GET, len(request.GET))
            if len(request.GET) == 0:
                questions = QuestionBank.objects.all()
                return render(request, 'questionbank/index.html',
                              {
                                  'questions': questions,
                                  'category_list': category_list,
                                  'level_list': level_list,
                                  'questiontype_list': questiontype_list,
                                  'file_list': file_list,
                              })
            else:
                # 分类接收的值
                if selectcategory == '':
                    if selectlevel != '' and selectquestiontype != '':
                        query = {'level': selectlevel, 'questiontype': selectquestiontype}
                        questions = QuestionBank.objects.filter(**query)
                    elif selectlevel == '' and selectquestiontype != '':
                        query = {'questiontype': selectquestiontype}
                        questions = QuestionBank.objects.filter(**query)
                    elif selectlevel != '' and selectquestiontype == '':
                        query = {'level': selectlevel, }
                        questions = QuestionBank.objects.filter(**query)
                    else:
                        questions = QuestionBank.objects.all()
                else:
                    if selectlevel != '' and selectquestiontype != '':
                        query = {'category': selectcategory, 'level': selectlevel, 'questiontype': selectquestiontype}
                        questions = QuestionBank.objects.filter(**query)
                    elif selectlevel == '' and selectquestiontype != '':
                        query = {'category': selectcategory, 'questiontype': selectquestiontype}
                        questions = QuestionBank.objects.filter(**query)
                    elif selectlevel != '' and selectquestiontype == '':
                        query = {'category': selectcategory, 'level': selectlevel, }
                        questions = QuestionBank.objects.filter(**query)
                    else:
                        query = {'category': selectcategory, }
                        questions = QuestionBank.objects.filter(**query)
                return render(request, 'questionbank/index.html',
                              {
                                  'questions': questions,
                                  'category_list': category_list,
                                  'level_list': level_list,
                                  'questiontype_list': questiontype_list,
                                  'file_list': file_list,
                              })
        # 搜索题库
        else:
            keyword = request.POST.get('keyword')
            questions = QuestionBank.objects.filter(
                Q(topic__icontains=keyword) |
                Q(text__icontains=keyword)
            )
            return render(request, 'questionbank/index.html',
                          {
                              'questions': questions,
                              'category_list': category_list,
                              'level_list': level_list,
                              'questiontype_list': questiontype_list,
                              'file_list': file_list,
                          })
    else:
        print('未登录！请登陆后操作。')
        # return render(request, 'user/login.html')
        return HttpResponseRedirect('/user/login?next=%s' % request.path)


def questiondel(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_del=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        # 处理数据
        del_id = request.GET.get('del_id')
        print(del_id)
        del_question = QuestionBank.objects.filter(id=del_id)[0]
        print(del_question.image)
        # 删除上传的图片
        if del_question.image != '':
            print('------')
            # / images / 2017 / 10 / 2 / 617 - timg.jpg
            if platform.system() == 'Windows':
                image_path = settings.MEDIA_ROOT + '\\images\\'
                file_path = str(del_question.image).replace('/', '\\')
                image_file = settings.MEDIA_ROOT + file_path

            if platform.system() == 'Linux':
                image_path = settings.MEDIA_ROOT + '/images/'
                file_path = str(del_question.image)
                image_file = settings.MEDIA_ROOT + file_path

            try:
                print(image_file)
                os.remove(image_file)
                print(image_path)
                ext_delemptydir.delete_dir(image_path)
                print('删除该图片，且删除空目录完成！')
            except FileNotFoundError:
                print('文件不存在！')
        # 删除数据
        QuestionBank.objects.filter(id=del_id).delete()

        return HttpResponseRedirect('/questionbank/index')

    else:
        print('用户不存在！返回登录页面', request.path)
        if User.objects.filter(username=request.session['session_name']).count() == 1:
            print('用户 %s 无权限！' % request.session['session_name'])
            return render(request, 'user/unauth_access.html')
        else:
            print('未登录！请登陆后操作。')
            # return render(request, 'user/login.html')
            return HttpResponseRedirect('/user/login?next=%s' % request.path)


def exportword(request):
    # 导出相应难度的题库
    ext_exportword.exportword(request.GET.get('choose'))

    return HttpResponseRedirect('/questionbank/index')


# 清空导出的word
def emptyquestion(request):
    if platform.system() == 'Windows':
        word_path = settings.MEDIA_ROOT + '\\static\\questionbank'
    if platform.system() == 'Linux':
        word_path = settings.MEDIA_ROOT + '/static/questionbank'
    word_list = os.listdir(word_path)
    for word in word_list:
        print(word)
        if os.path.exists(os.path.join(word_path, word)):
            os.remove(os.path.join(word_path, word))
    return HttpResponseRedirect('/questionbank/index')


def questionupdate(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_update=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == "POST":
            update_id = request.POST.get('update_id')
            # 考题的分类
            selectcategory = request.POST.get('selectcategory')
            inputcategory = request.POST.get('inputcategory').strip()

            # 考题的类型
            selectquestiontype = request.POST.get('selectquestiontype')
            inputquestiontype = request.POST.get('inputquestiontype')

            flag1 = False
            flag2 = False
            # 题目分类判断
            if selectcategory == '' and inputcategory == '':
                status = '分类都为空，只能选择一项'
                flag1 = False
            elif selectcategory != '' and inputcategory != '':
                status = '分类都有值，只能选择一项'
                flag1 = False
            else:
                status = '更新成功！'
                flag1 = True
                if selectcategory != '':
                    category = selectcategory
                else:
                    category = inputcategory

            # 题目类型判断
            if selectquestiontype == '' and inputquestiontype == '':
                status = '题型都为空，只能选择一项'
                flag2 = False
            elif selectquestiontype != '' and inputquestiontype != '':
                status = '题型都有值，只能选择一项'
                flag2 = False
            else:
                flag2 = True
                if selectquestiontype != '':
                    questiontype = selectquestiontype
                else:
                    questiontype = inputquestiontype

            if flag1 is True and flag2 is True:
                status = '更新成功！'
                topic = request.POST.get('topic').strip()
                text = request.POST.get('text').strip()
                answer = request.POST.get('answer', None).strip()
                selectlevel = request.POST.get('selectlevel')
                image = request.FILES.get('image', None)  # # 获取上传的文件，如果没有文件，则默认为None
                # 如果用户上传图片
                if image is not None:
                    # 首先删除以前的图片

                    del_image = QuestionBank.objects.filter(id=update_id)[0]
                    print(del_image.image)
                    # 删除上传的图片
                    if del_image.image != '':
                        # / images / 2017 / 10 / 2 / 617 - timg.jpg
                        if platform.system() == 'Windows':
                            image_path = settings.MEDIA_ROOT + '\\images\\'
                            file_path = str(del_image.image).replace('/', '\\')
                            image_file = settings.MEDIA_ROOT + file_path

                        if platform.system() == 'Linux':
                            image_path = settings.MEDIA_ROOT + '/images/'
                            file_path = str(del_image.image)
                            image_file = settings.MEDIA_ROOT + file_path

                        try:
                            print('删除图片：', image_file)
                            os.remove(image_file)
                            ext_delemptydir.delete_dir(image_path)
                            print('删除该图片，且删除空目录完成！')
                        except FileNotFoundError:
                            print('文件不存在！')

                    # 再添加新的图片
                    imagename = str(random.randint(0, 100000)) + '-' + request.FILES.get('image').name
                    print('文件？', image, imagename)
                    # 后台数据库中记录的路径是：images/2017/09/30/test.png

                    if platform.system() == 'Windows':
                        image_path = settings.MEDIA_ROOT + '\\images\\' + str(datetime.datetime.now().year) + '\\' + str(datetime.datetime.now().month) + '\\' + str(datetime.datetime.now().day)
                        if not os.path.exists(image_path):
                            os.makedirs(image_path)
                        image_file = image_path + '\\' + imagename

                    if platform.system() == 'Linux':
                        image_path = settings.MEDIA_ROOT + '/images/' + str(datetime.datetime.now().year) + '/' + str(datetime.datetime.now().month) + '/' + str(datetime.datetime.now().day)
                        if not os.path.exists(image_path):
                            os.mkdirs(image_path)
                        image_file = image_path + '/' + imagename
                    print('增加图片：', image_file)

                    destination = open(image_file, 'wb')
                    for chunk in image.chunks():  # 分块写入文件
                        destination.write(chunk)
                    destination.close()

                    # 保存在后台记录的路径
                    image_url = '/images/' + str(datetime.datetime.now().year) + '/' + str(datetime.datetime.now().month) + '/' + str(datetime.datetime.now().day) + '/' + imagename
                    print(image_url)

                    print(category, selectlevel, questiontype, topic, text, image, status)
                    QuestionBank.objects.filter(id=update_id).update(category=category, level=selectlevel, questiontype=questiontype, topic=topic, text=text, image=image_url, answer=answer)
                # 如果用户没有上传图片
                else:
                    print(category, selectlevel, questiontype, topic, text, status)
                    QuestionBank.objects.filter(id=update_id).update(category=category, level=selectlevel, questiontype=questiontype, topic=topic, text=text, answer=answer)

            # 题目分类
            category_list = []
            for cg in QuestionBank.objects.all():
                if cg.category not in category_list:
                    category_list.append(cg.category)
            # 提醒分类：选择、问答题
            questiontype_list = []
            for qt in QuestionBank.objects.all():
                if qt.questiontype not in questiontype_list:
                    questiontype_list.append(qt.questiontype)
            update_question = QuestionBank.objects.filter(id=update_id)[0]
            return render(request, 'questionbank/questionupdate.html',
                          {
                              'category_list': category_list,
                              'status': status,
                              'questiontype_list': questiontype_list,
                              'update_question': update_question,
                          })
        else:
            # 题目分类
            category_list = []
            for cg in QuestionBank.objects.all():
                if cg.category not in category_list:
                    category_list.append(cg.category)
            # 提醒分类：选择、问答题
            questiontype_list = []
            for qt in QuestionBank.objects.all():
                if qt.questiontype not in questiontype_list:
                    questiontype_list.append(qt.questiontype)
            update_id = request.GET.get('update_id')
            update_question = QuestionBank.objects.filter(id=update_id)[0]

            return render(request, 'questionbank/questionupdate.html',
                          {
                              'category_list': category_list,
                              'questiontype_list': questiontype_list,
                              'update_question': update_question,
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
