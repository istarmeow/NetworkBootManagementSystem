# -*- coding:utf-8 -*-

from django.shortcuts import render, HttpResponse
from django.http import HttpResponseRedirect
from .models import Employee, Schedule, LegalDay, User
import calendar
import datetime
import time
import os
import platform
import xlrd
import xlwt
import json


def index(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'

    if User.objects.filter(username=request.session['session_name']).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])
        start_date = datetime.date.today() - datetime.timedelta(10)  # 时间往前15天
        end_date = datetime.date.today() + datetime.timedelta(20)
        show_schedule = Schedule.objects.filter(date__range=(start_date, end_date))
        # print(show_schedule[0].date, type(show_schedule[0].date))
        schedule_num = show_schedule.count()
        # print(show_schedule)
        today = datetime.date.today()
        # today = datetime.date(2017, 8, 26)
        print(today)
        # 导出功能，显示月份
        mouth1 = today.month
        year1 = today.year
        date1 = str(year1) + '-' + str(mouth1)
        date1v = '导出%s年%s月数据' % (str(year1), str(mouth1))

        mouth0 = mouth1 - 1
        if mouth0 < 1:
            year0 = year1 - 1
            mouth0 = mouth0 + 12
        else:
            year0 = year1
        date0 = str(year0) + '-' + str(mouth0)
        date0v = '导出%s年%s月数据' % (str(year0), str(mouth0))

        mouth2 = mouth1 + 1
        if mouth2 > 12:
            year2 = year1 + 1
            mouth2 = mouth2 - 12
        else:
            year2 = year1
        date2 = str(year2) + '-' + str(mouth2)
        date2v = '导出%s年%s月数据' % (str(year2), str(mouth2))

        mouth3 = mouth1 + 2
        if mouth3 > 12:
            year3 = year1 + 1
            mouth3 = mouth3 - 12
        else:
            year3 = year1
        date3 = str(year3) + '-' + str(mouth3)
        date3v = '导出%s年%s月数据' % (str(year3), str(mouth3))

        # 显示导出的Excel文件名
        # print(os.getcwd())
        os.chdir(os.path.abspath('.'))
        if platform.system() == 'Windows':
            schedule_path = os.path.abspath('.') + '\\networkbootsystem\\static\\schedule\\'
        if platform.system() == 'Linux':
            schedule_path = os.path.abspath('.') + '/networkbootsystem/static/schedule/'
        schedule_excel = os.listdir(schedule_path)

        return render(request, 'schedule/index.html',
                      {
                          'show_schedule': show_schedule,
                          'schedule_num': schedule_num,
                          'today': today,
                          'date0': date0,
                          'date0v': date0v,
                          'date1': date1,
                          'date1v': date1v,
                          'date2': date2,
                          'date2v': date2v,
                          'date3': date3,
                          'date3v': date3v,
                          'schedule_excel': schedule_excel
                      })
    else:
        print('未登录！请登陆后操作。')
        # return render(request, 'user/login.html')
        return HttpResponseRedirect('/user/login?next=%s' % request.path)


def weekday(num):
    '''
    thisday = date(2017, 8, 1)
    thisday.isoweekday()
    :param num:
    :return:
    '''
    dayweek = {1: '星期一', 2: '星期二', 3: '星期三', 4: '星期四', 5: '星期五', 6: '星期六', 7: '星期日'}
    if num in dayweek.keys():
        return dayweek[num]
    else:
        return '错误'


# 创建工作日数据，是否该值班标记出来
def workdayinfo(request):
    if request.session['session_name'] == 'admin':
        if request.method == 'POST':
            legalworkday = []  # 法定工作日
            legalrestday = []  # 法定休息日，日历上标记的
            if LegalDay.objects.filter(legalworkday=True).count() > 0:
                for workday in LegalDay.objects.filter(legalworkday=True):
                    legalworkday.append(workday.date)
            if LegalDay.objects.filter(legalrestday=True).count() > 0:
                for restday in LegalDay.objects.filter(legalrestday=True):
                    legalrestday.append(restday.date)
            print('工作日：', legalworkday, '\n休息日', legalrestday)

            today = datetime.date.today()
            to_a_month = request.POST.get('to_a_month')
            print(to_a_month)
            if to_a_month.strip() != '':
                print('有输入值')
                try:
                    y = int(to_a_month.split('.')[0])
                    m = int(to_a_month.split('.')[1])
                    print(today.year, type(today.year))

                    if y not in range(today.year, 2020) or m not in range(1, 13) or (y == today.year and m in range(1, today.month+1)):
                        print('默认年月')
                        y = today.year
                        m = today.month
                except IndexError:
                    print('格式错误使用当月')
                    y = today.year
                    m = today.month
            else:
                y = today.year
                m = today.month
            print('日期止于 %s 年 %s 月：' % (str(y), str(m)))

            weekin = [1, 2, 3, 4, 5]
            weekend = [6, 7]

            firstday, daynum = calendar.monthrange(int(y), int(m))
            print('最后一月第一天：', weekday(firstday+1))
            print('本月一共 %s 天' % str(daynum))

            startdate = datetime.date(today.year, today.month, 1)  # 从本月1号开始创建
            enddate = datetime.date(int(y), int(m), calendar.monthrange(int(y), int(m))[1])
            days = (enddate - startdate).days

            thisday = startdate
            for i in range(days+1):
                # thisday = thisday.replace(day=i + 1)

                # 创建工作日：1.这天属于周内且这天不在法定休息日内、2.这天输入法定工作日
                if (thisday.isoweekday() in weekin and thisday not in legalrestday) or thisday in legalworkday:
                    print(thisday, weekday(thisday.isoweekday()), '是工作日')

                    if Schedule.objects.filter(date=thisday).count() > 0:
                        Schedule.objects.filter(date=thisday).update(
                            date=thisday,
                            week=weekday(thisday.isoweekday()),
                            workday=True,
                            nightduty=True,
                            meetduty=False,
                            weekendduty=False
                        )
                    else:
                        Schedule.objects.create(
                            date=thisday,
                            week=weekday(thisday.isoweekday()),
                            workday=True,
                            nightduty=True,
                            meetduty=False,
                            weekendduty=False
                        )

                    if i < 1:
                        # 1.如果这天是这个月1号且为周一且这天不在法定休息日中、2.这天在法定工作日中
                        if (thisday.isoweekday() == 1 and thisday not in legalrestday) or thisday in legalworkday:
                            print('开会')
                            Schedule.objects.filter(date=thisday).update(
                                nightduty=False,
                                meetduty=True,
                                weekendduty=False
                            )
                    else:
                        # 1.如果前天为周末且前天不在法定工作日、2.前天在法定休息日中
                        # daybefore = thisday.replace(day=i)
                        daybefore = thisday - datetime.timedelta(days=1)
                        if (daybefore.isoweekday() in weekend and daybefore not in legalworkday) or daybefore in legalrestday:
                            print('开会')
                            Schedule.objects.filter(date=thisday).update(
                                nightduty=False,
                                meetduty=True,
                                weekendduty=False
                            )
                # 创建休息日：1.这天属于周六或周日且这天不在法定工作日、2.这天输入法定休息日
                elif (thisday.isoweekday() in weekend and thisday not in legalworkday) or thisday in legalrestday:
                    print(thisday, weekday(thisday.isoweekday()), '真的是休息日')

                    if Schedule.objects.filter(date=thisday).count() > 0:
                        Schedule.objects.filter(date=thisday).update(
                            date=thisday,
                            week=weekday(thisday.isoweekday()),
                            workday=False,
                            nightduty=False,
                            meetduty=False,
                            weekendduty=False
                        )
                    else:
                        Schedule.objects.create(
                            date=thisday,
                            week=weekday(thisday.isoweekday()),
                            workday=False,
                            nightduty=False,
                            meetduty=False,
                            weekendduty=False
                        )

                    if thisday.isoweekday() == 6 and thisday not in legalworkday and thisday not in legalrestday:
                        print('值班:', thisday)
                        Schedule.objects.filter(date=thisday).update(
                            weekendduty=True
                        )
                else:
                    print('不明数据：', thisday, weekday(thisday.isoweekday()))
                thisday = thisday + datetime.timedelta(days=1)
                # 以上进行循环写入数据

            return HttpResponseRedirect('/schedule/index')
        else:
            return render(request, 'schedule/workdayinfo.html',
                          {

                          })
    else:
        return HttpResponse('真的没这功能！')


# 更新晚值班信息
def update_night_duty(default_duty_order, thisday, lastnight, nightduty, choose=0):
    # 如果晚值班历史不存在
    # print('上个月最后一个晚班：', lastnight)
    for n in Employee.objects.filter(available=True):
        if n.name in lastnight:
            # 该人员晚上排班放到最后
            Employee.objects.filter(available=True, name=n.name).update(
                nightnum=default_duty_order.count(),
            )
            diff = default_duty_order.count() - Employee.objects.filter(available=True, name=n.name)[0].num
            # print('差值：', diff)
            # 计算差值，循环改变排班表的顺序
            for m in Employee.objects.filter(available=True):
                num = Employee.objects.filter(available=True, name=m.name)[0].num
                if num + diff > default_duty_order.count():
                    Employee.objects.filter(available=True, name=m.name).update(
                        nightnum=num + diff - default_duty_order.count()
                    )
                else:
                    Employee.objects.filter(available=True, name=m.name).update(
                        nightnum=num + diff
                    )
    # 增加了一个临时晚班顺序后再进行排班
    print('更新晚上值班表，使用临时晚上值班顺序')
    tmp_night_order = Employee.objects.filter(available=True).order_by('nightnum')
    # print(nightduty.count())
    for i in range(nightduty.count()):
        # print(nightduty[i].date, tmp_night_order[i % tmp_night_order.count()].name)
        Schedule.objects.filter(date=nightduty[i].date).update(
            staff=tmp_night_order[i % tmp_night_order.count()].name,
            realstaff=None
        )
    if choose == 1:
        # 如果是推迟调用，则还要执行下面
        Schedule.objects.filter(date=thisday - datetime.timedelta(days=1)).update(staff=None, realstaff='推迟')


# 更新例会信息
def update_meet_duty(default_duty_order, thisday, lastmeet, meetduty, choose=0):
    # 如果例会值班历史不存在
    for n in Employee.objects.filter(available=True):
        if n.name in lastmeet:
            # 该人员晚上排班置为1
            Employee.objects.filter(available=True, name=n.name).update(
                meetnum=default_duty_order.count(),
            )
            diff = default_duty_order.count() - Employee.objects.filter(available=True, name=n.name)[0].num
            # print('差值：', diff)
            # 计算差值，循环改变排班表的顺序
            for m in Employee.objects.filter(available=True):
                num = Employee.objects.filter(available=True, name=m.name)[0].num
                if num + diff > default_duty_order.count():
                    Employee.objects.filter(available=True, name=m.name).update(
                        meetnum=num + diff - default_duty_order.count()
                    )
                else:
                    Employee.objects.filter(available=True, name=m.name).update(
                        meetnum=num + diff
                    )
    print('更新例会值班表，使用临时例会值班顺序')
    tmp_meet_order = Employee.objects.filter(available=True).order_by('meetnum')
    for j in range(meetduty.count()):
        Schedule.objects.filter(date=meetduty[j].date).update(
            staff='例会：' + tmp_meet_order[j % tmp_meet_order.count()].name,
            realstaff=None
            )
    if choose == 1:
        # 如果是推迟调用，则还要执行下面
        Schedule.objects.filter(date=thisday-datetime.timedelta(days=1)).update(staff=None, realstaff='例会推迟')


# 更新周末值班信息
def update_weekend_duty(default_duty_order, thisday, lastweekend, weekendduty, choose=0):
    # 如果周末值班历史不存在
    # print(Schedule.objects.filter(weekendduty=True, date__lt=thisday, staff__isnull=False))
    # print(Schedule.objects.filter(date=datetime.date(2017, 8, 10))[0].staff)

    for n in Employee.objects.filter(available=True):
        if n.name in lastweekend:
            # 该人员晚上排班置为1
            Employee.objects.filter(available=True, name=n.name).update(
                weekendnum=default_duty_order.count(),
            )
            diff = default_duty_order.count() - Employee.objects.filter(available=True, name=n.name)[0].num
            # print('差值：', diff)
            # 计算差值，循环改变排班表的顺序
            for m in Employee.objects.filter(available=True):
                num = Employee.objects.filter(available=True, name=m.name)[0].num
                if num + diff > default_duty_order.count():
                    Employee.objects.filter(available=True, name=m.name).update(
                        weekendnum=num + diff - default_duty_order.count()
                    )
                else:
                    Employee.objects.filter(available=True, name=m.name).update(
                        weekendnum=num + diff
                    )
    print('更新周末值班表，使用临时周末值班顺序')
    tmp_weekend_order = Employee.objects.filter(available=True).order_by('weekendnum')
    for k in range(weekendduty.count()):
        Schedule.objects.filter(date=weekendduty[k].date).update(
            staff='周末：' + tmp_weekend_order[k % tmp_weekend_order.count()].name,
            realstaff=None
        )
    if choose == 1:
        # 如果是推迟调用，则还要执行下面
        Schedule.objects.filter(date=thisday-datetime.timedelta(days=1)).update(staff=None, realstaff='周末推迟')


# 后面增加值班表使用
def createduty(request):
    if request.session['session_name'] == 'admin':
        if request.method == 'POST':
            default_duty_order = Employee.objects.filter(available=True).order_by('num')
            # 可值班人员按照序号进行排序，对于历史值班顺序不存在的情况，则采用员工序号进行
            # print(request.POST.get('thisday'))
            # thisday = datetime.date(2017, 9, 26)
            if request.POST.get('thisday') == '':
                thisday = datetime.date.today()
            else:
                yy, mm, dd = request.POST.get('thisday').split('-')
                thisday = datetime.date(int(yy), int(mm), int(dd))
            custom_lastnight = request.POST.get('custom_lastnight')
            custom_lastmeet = request.POST.get('custom_lastmeet')
            custom_lastweekend = request.POST.get('custom_lastweekend')
            # 获取自定义上次排班情况

            nightduty = Schedule.objects.filter(nightduty=True, date__gte=thisday).order_by('date')
            meetduty = Schedule.objects.filter(meetduty=True, date__gte=thisday).order_by('date')
            weekendduty = Schedule.objects.filter(weekendduty=True, date__gte=thisday).order_by('date')

            if Schedule.objects.filter(nightduty=True,
                                       date__lt=thisday,
                                       staff__isnull=False).count() >= 1 or custom_lastnight != '':
                if custom_lastnight != '':
                    lastnight = custom_lastnight
                else:
                    # 首先创建晚值班临时顺序，date__lt=thisday小于固定的日期，也就是获取上一次值班
                    lastnight_all = Schedule.objects.filter(
                        nightduty=True,
                        date__lt=thisday,
                        staff__isnull=False).order_by('-date')
                    flag = False
                    lastnight = ''
                    for night in lastnight_all:
                        for employee in default_duty_order:
                            if employee.name in night.staff:
                                lastnight = employee.name
                                flag = True
                                break
                        if flag is True:
                            break

                    # lastnight = Schedule.objects.filter(
                    #     nightduty=True,
                    #     date__lt=thisday,
                    #     staff__isnull=False).order_by('-date')[0].staff
                update_night_duty(default_duty_order, thisday, lastnight, nightduty)
            else:
                # 如果历史值班顺序不存在的，则按照员工列表序号进行排序default_duty_order
                print('创建晚上值班表')
                for i in range(nightduty.count()):
                    # print(nightduty[i].date, default_duty_order[i % default_duty_order.count()].name)
                    Schedule.objects.filter(date=nightduty[i].date).update(
                        staff=default_duty_order[i % default_duty_order.count()].name,
                        realstaff=None
                    )

            if Schedule.objects.filter(meetduty=True,
                                       date__lt=thisday,
                                       staff__isnull=False).count() >= 1 or custom_lastmeet != '':
                if custom_lastmeet != '':
                    lastmeet = custom_lastmeet
                else:
                    lastmeet_all = Schedule.objects.filter(
                        meetduty=True,
                        date__lt=thisday,
                        staff__isnull=False).order_by('-date')
                    flag = False
                    lastmeet = ''
                    for night in lastmeet_all:
                        for employee in default_duty_order:
                            if employee.name in night.staff:
                                lastmeet = employee.name
                                flag = True
                                break
                        if flag is True:
                            break
                    # lastmeet = Schedule.objects.filter(
                    #     meetduty=True,
                    #     date__lt=thisday,
                    #     staff__isnull=False
                    # ).order_by('-date')[0].staff
                update_meet_duty(default_duty_order, thisday, lastmeet, meetduty)
            else:
                print('创建例会值班表')
                for j in range(meetduty.count()):
                    Schedule.objects.filter(date=meetduty[j].date).update(
                        staff='例会：' + default_duty_order[j % default_duty_order.count()].name,
                        realstaff=None
                    )

            if Schedule.objects.filter(weekendduty=True,
                                       date__lt=thisday,
                                       staff__isnull=False).count() >= 1 or custom_lastweekend != '':
                # 如果自定义一个名字，就按照自定义排序
                if custom_lastweekend != '':
                    lastweekend = custom_lastweekend
                else:
                    lastweekend_all = Schedule.objects.filter(
                        weekendduty=True,
                        date__lt=thisday,
                        staff__isnull=False).order_by('-date')
                    flag = False
                    lastweekend = ''
                    for night in lastweekend_all:
                        for employee in default_duty_order:
                            if employee.name in night.staff:
                                lastweekend = employee.name
                                flag = True
                                break
                        if flag is True:
                            break

                    # lastweekend = Schedule.objects.filter(weekendduty=True,
                    #                                       date__lt=thisday,
                    #                                       staff__isnull=False).order_by('-date')[0].staff
                update_weekend_duty(default_duty_order, thisday, lastweekend, weekendduty)
            else:
                print('创建周末值班表')
                for k in range(weekendduty.count()):
                    Schedule.objects.filter(date=weekendduty[k].date).update(
                        staff='周末：' + default_duty_order[k % default_duty_order.count()].name,
                        realstaff=None
                    )

            start_date = datetime.date.today() - datetime.timedelta(10)  # 时间往前15天
            show_schedule = Schedule.objects.filter(date__gte=start_date)
            schedule_num = show_schedule.count()
            today = datetime.date.today()
            return HttpResponseRedirect('/schedule/index')
        else:
            employee = Employee.objects.filter(available=True).order_by('num')
            enddate = Schedule.objects.all().order_by('-date')[0].date
            print('值班安排到：', enddate)
            return render(request, 'schedule/createduty.html',
                          {
                              'employee': employee,
                              'enddate': enddate,
                          })
    else:
        return HttpResponse('真的没这功能！')


# 获取该日期上次值班的人员
def getlastduty(request):
    yy, mm, dd = request.GET.get('thisday').split('-')
    thisday = datetime.date(int(yy), int(mm), int(dd))

    default_duty_order = Employee.objects.filter(available=True).order_by('num')
    lastnight_all = Schedule.objects.filter(
        nightduty=True,
        date__lt=thisday,
        staff__isnull=False).order_by('-date')
    flag = False
    lastnight = ''
    for night in lastnight_all:
        for employee in default_duty_order:
            if employee.name in night.staff:
                lastnight = employee.name
                flag = True
                break
        if flag is True:
            break

    lastweekend_all = Schedule.objects.filter(
        weekendduty=True,
        date__lt=thisday,
        staff__isnull=False).order_by('-date')
    flag = False
    lastweekend = ''
    for night in lastweekend_all:
        for employee in default_duty_order:
            if employee.name in night.staff:
                lastweekend = employee.name
                flag = True
                break
        if flag is True:
            break

    lastmeet_all = Schedule.objects.filter(
        meetduty=True,
        date__lt=thisday,
        staff__isnull=False).order_by('-date')
    flag = False
    lastmeet = ''
    for night in lastmeet_all:
        for employee in default_duty_order:
            if employee.name in night.staff:
                lastmeet = employee.name
                flag = True
                break
        if flag is True:
            break

    last_info = dict()
    last_info['lastnight'] = lastnight
    last_info['lastmeet'] = lastmeet
    last_info['lastweekend'] = lastweekend
    # print(last_info)
    print(json.dumps(last_info))
    return HttpResponse(json.dumps(last_info))


# 转换时间格式%Y年%m月%d日
def strtodate(str):
    getdate = time.strptime(str, '%Y年%m月%d日')
    date = datetime.date(getdate.tm_year, getdate.tm_mon, getdate.tm_mday)
    return date


# 特殊假期值班推迟情况
def delayonce(request):
    if request.session['session_name'] == 'admin':
        getdate = request.GET.get('date')
        choosedate = strtodate(getdate)
        print(choosedate)

        default_duty_order = Employee.objects.filter(available=True).order_by('num')
        thisday = choosedate + datetime.timedelta(days=1)

        if Schedule.objects.filter(date=choosedate)[0].nightduty is True:
            # 调用函数，选择一个日期，传递的参数是前一天的值班人员，假如选择今天作为推迟，则要选择明天作为起点，则筛选前一天的值班，需要包含选择的那天
            choosenight = Schedule.objects.filter(nightduty=True, date__lte=choosedate, staff__isnull=False).order_by('-date')[0].staff

            for m in Employee.objects.filter(available=True):
                if m.name in choosenight:
                    num = m.num
                    if num > 1:
                        choosenum = num - 1
                    else:
                        choosenum = num + Employee.objects.filter(available=True).count() - 1
            lastnight = Employee.objects.filter(available=True, num=choosenum)[0].name

            nightduty = Schedule.objects.filter(nightduty=True, date__gte=thisday).order_by('date')  # 获取晚值班的日期，并按照日期进行排序
            print(lastnight)
            update_night_duty(default_duty_order, thisday, lastnight, nightduty, choose=1)

        if Schedule.objects.filter(date=choosedate)[0].meetduty is True:
            choosemeet = Schedule.objects.filter(meetduty=True, date__lte=choosedate, staff__isnull=False).order_by('-date')[0].staff

            for m in Employee.objects.filter(available=True):
                if m.name in choosemeet:
                    num = m.num
                    if num > 1:
                        choosenum = num - 1
                    else:
                        choosenum = num + Employee.objects.filter(available=True).count() - 1

            lastmeet = Employee.objects.filter(available=True, num=choosenum)[0].name
            meetduty = Schedule.objects.filter(meetduty=True, date__gte=thisday).order_by('date')

            update_meet_duty(default_duty_order, thisday, lastmeet, meetduty, choose=1)

        if Schedule.objects.filter(date=choosedate)[0].weekendduty is True:
            chooseweekend = Schedule.objects.filter(weekendduty=True, date__lte=choosedate, staff__isnull=False).order_by('-date')[0].staff
            for m in Employee.objects.filter(available=True):
                if m.name in chooseweekend:
                    num = m.num
                    if num > 1:
                        choosenum = num - 1
                    else:
                        choosenum = num + Employee.objects.filter(available=True).count() - 1

            lastweekend = Employee.objects.filter(available=True, num=choosenum)[0].name
            weekendduty = Schedule.objects.filter(weekendduty=True, date__gte=thisday).order_by('date')

            update_weekend_duty(default_duty_order, thisday, lastweekend, weekendduty, choose=1)

        return HttpResponseRedirect('/schedule/index')
    else:
        return HttpResponse('页面上天了！')


def getdateinfo(request):
    getdate = request.GET.get('date')
    date = strtodate(getdate)
    # print(date)
    today = datetime.date.today()

    if Schedule.objects.filter(date=date)[0].nightduty is True:
        nightduty = Schedule.objects.filter(date=date)[0].staff
        # print(nightduty)
        return HttpResponse(nightduty)

    if Schedule.objects.filter(date=date)[0].meetduty is True:
        meetduty = Schedule.objects.filter(date=date)[0].staff
        return HttpResponse(meetduty)

    if Schedule.objects.filter(date=date)[0].weekendduty is True:
        weekendduty = Schedule.objects.filter(date=date)[0].staff
        return HttpResponse(weekendduty)


# 切换值班
def exchange(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'

    if User.objects.filter(username=request.session['session_name']).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == 'GET':
            getdate = request.GET.get('date')
            date = strtodate(getdate)
            staff = Schedule.objects.filter(date=date)[0].staff
            today = datetime.date.today()

            if Schedule.objects.filter(date=date)[0].nightduty is True:
                nightduty = Schedule.objects.filter(date__gt=date, nightduty=True)
                firststaff = nightduty[0].staff  # 默认选择列表中字一个名字
                duty = nightduty

            if Schedule.objects.filter(date=date)[0].meetduty is True:
                meetduty = Schedule.objects.filter(date__gt=date, meetduty=True)
                firststaff = meetduty[0].staff
                duty = meetduty

            if Schedule.objects.filter(date=date)[0].weekendduty is True:
                weekendduty = Schedule.objects.filter(date__gt=date, weekendduty=True)
                firststaff = weekendduty[0].staff
                duty = weekendduty
            return render(request, 'schedule/exchange.html',
                          {
                              'duty': duty,
                              'date': date,
                              'staff': staff,
                              'firststaff': firststaff,
                          })
        else:
            date = strtodate(request.POST.get('date'))
            staff = request.POST.get('staff')
            exchangedate = strtodate(request.POST.get('exchangedate'))
            exchangestaff = request.POST.get('exchangestaff')
            print(staff, exchangestaff)
            if staff.strip() != exchangestaff.strip():
                Schedule.objects.filter(date=date).update(realstaff=exchangestaff)
                Schedule.objects.filter(date=exchangedate).update(realstaff=staff)
                print('已完成值班交换')
            else:
                print('不和自己交换。')
            return HttpResponseRedirect('/schedule/index')
    else:
        print('未登录！请登陆后操作。')
        # return render(request, 'user/login.html')
        return HttpResponseRedirect('/user/login?next=%s' % request.path)


# 删除调换
def delexchange(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'

    if User.objects.filter(username=request.session['session_name']).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])
        getdate = request.GET.get('date')
        date = strtodate(getdate)
        Schedule.objects.filter(date=date).update(realstaff=None)
        print('删除换班记录成功')
        return HttpResponseRedirect('/schedule/index')
    else:
        print('未登录！请登陆后操作。')
        # return render(request, 'user/login.html')
        return HttpResponseRedirect('/user/login?next=%s' % request.path)


# 表格写入
def createexcel(filename, schedule, year, month):
    if os.path.exists(filename):
        os.remove(filename)

    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet('排班表', cell_overwrite_ok=True)
    # 对一个单元格重复操作，会引发Attempt to overwrite cell: sheetname='排班表' rowx=5 colx=6，打开时加cell_overwrite_ok=True解决

    sheet.col(0).width = 256 * 20  # 256为衡量单位，20表示20个字符宽度
    sheet.col(1).width = 256 * 12
    sheet.col(2).width = 256 * 20
    sheet.col(3).width = 256 * 20
    sheet.col(4).width = 256 * 20

    head_style = xlwt.easyxf('font:height 220, bold on; align: wrap on, vert centre, horiz center;')
    # font:height 220, bold on; # 字体大小，粗体开
    # align: wrap on, vert centre, horiz center;  # 位置：自动换行， 水平居中，上下居中
    text_style = xlwt.easyxf('font:height 220; align: wrap on, vert centre, horiz center;')
    saturday_style = xlwt.easyxf('font:height 220; align: wrap on, vert centre, horiz center; pattern: pattern solid, fore_colour gray25')

    head = ['日期', '星期', '工作日', '周末', '换班记录']
    for i in range(len(head)):
        sheet.write(0, i, head[i], head_style)

    count = schedule.count()
    date_row = 1
    for j in schedule:
        if j.weekendduty is True:
            sheet.write(date_row, 0, str(j.date), saturday_style)
        else:
            sheet.write(date_row, 0, str(j.date), text_style)

        if j.weekendduty is True:
            sheet.write(date_row, 1, str(j.week), saturday_style)
        else:
            sheet.write(date_row, 1, str(j.week), text_style)

        if (j.nightduty is True or j.meetduty is True) and j.staff is not None:
            sheet.write(date_row, 2, str(j.staff), text_style)

        if (j.weekendduty is True) and j.staff is not None:
            sheet.write(date_row, 2, None, saturday_style)
            sheet.write(date_row, 3, str(j.staff), saturday_style)

        if j.realstaff is not None:
            sheet.write(date_row, 4, str(j.realstaff), text_style)
        date_row += 1

    # 右边显示换休日期
    sheet.col(5).width = 256 * 1  # 分割线
    sheet.col(6).width = 256 * 10  # 名字
    sheet.col(7).width = 256 * 15  # 值班日期
    sheet.col(8).width = 256 * 15  # 值班日期
    sheet.col(9).width = 256 * 15  # 值班日期
    sheet.col(10).width = 256 * 15  # 调休日期
    sheet.col(11).width = 256 * 15  # 调休日期
    sheet.col(12).width = 256 * 10  # 可调天数

    # 中间的分割线
    div_style = xlwt.easyxf('pattern: pattern solid, fore_colour gray80')
    for m in range(count+1):
        sheet.write(m, 5, None, div_style)

    # 设置下边框
    borders_bottom = xlwt.Borders()  # 创建边框
    # borders.left = xlwt.Borders.DASHED
    # DASHED虚线
    # NO_LINE没有
    # THIN实线
    # May be: NO_LINE, THIN, MEDIUM, DASHED, DOTTED, THICK, DOUBLE, HAIR, MEDIUM_DASHED, THIN_DASH_DOTTED, MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED, MEDIUM_DASH_DOT_DOTTED, SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.
    # borders.right = xlwt.Borders.DASHED
    # borders.top = xlwt.Borders.DASHED
    borders_bottom.bottom = xlwt.Borders.THIN
    # borders.left_colour = 0x40
    # borders.right_colour = 0x40
    # borders.top_colour = 0x40
    borders_bottom.bottom_colour = 0x40
    border_bottom_style = xlwt.XFStyle()  # 创建风格
    border_bottom_style.borders = borders_bottom  # 添加边框到风格中
    sheet.write_merge(12, 12, 6, 12, None, border_bottom_style)

    # 记录值班日期换休
    ot_row = 13
    overtime = ['名字', '值班日期', '值班日期', '值班日期', '调休日期', '调休日期', '可调天数']
    for ot in range(len(overtime)):
        sheet.write(ot_row, 6+ot, overtime[ot], head_style)

    ot_row += 1
    for staff in Employee.objects.filter(available=True):
        name_col = 6  # 名字开始列
        onduty_col = 7  # 值班日期开始列
        tuneoff_col = 10  # 调休日期开始列
        tuneoffnum_col = 12  # 可调天数开始列
        sheet.write(ot_row, name_col, staff.name, text_style)  # 填写人名
        # 筛选出本月值班人员信息
        filter_weenkend = Schedule.objects.filter(weekendduty=True, date__year=year, date__month=month, staff__contains=staff.name)
        # 写入值班日期
        for date_num in range(filter_weenkend.count()):
            # print(filter_weenkend.order_by('date')[date_num].date)
            sheet.write(ot_row, onduty_col, str(filter_weenkend.order_by('date')[date_num].date), text_style)
            onduty_col += 1
            date_num += 1
        # 写入可调休天数
        sheet.write(ot_row, tuneoffnum_col, str(filter_weenkend.count()/2)+'天', text_style)
        # 写入完成一个名字后，跳到下一行
        ot_row += 1

    # 设置上边框
    borders_top = xlwt.Borders()  # 创建边框
    borders_top.top = xlwt.Borders.THIN
    borders_top.top_colour = 0x40
    border_top_style = xlwt.XFStyle()  # 创建风格
    border_top_style.borders = borders_top  # 添加边框到风格中
    sheet.write_merge(ot_row, ot_row, 6, 12, None, border_top_style)

    # 写入说明
    info = '''说明：
    周例会由当天值班同学进行发言总结。
    工作日值班同学需提前到公司，检查刷卡机设备状态。
    周末值班，每值一天班，换休半天，换休当月有效，过期作废。
    '''
    info_style = xlwt.easyxf('font:height 220; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_colour gray25')

    # 设置页尾
    footer_style = xlwt.XFStyle()  # 初始化样式
    font = xlwt.Font()  # 为样式创建字体
    font.height = 300
    font.name = '华文行楷'
    font.bold = True  # 黑体

    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_RIGHT  # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
    alignment.vert = xlwt.Alignment.VERT_CENTER  # May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED

    footer_style.font = font
    footer_style.alignment = alignment

    sheet.write_merge(count+2, count+2, 0, 12, '由PXE提供导出', footer_style)

    sheet.write_merge(3, 7, 7, 11, info, info_style)  # 合并单元格，3,7表示第4行到第8行，7,11表示第8列到第12列，区间表格合并






    workbook.save(filename)


# 导出Excel
def exportexcel(request):
    getdate = request.GET.get('date')
    year = getdate.split('-')[0]
    month = getdate.split('-')[1]
    schedule = Schedule.objects.filter(date__year=int(year), date__month=int(month)).order_by('date')
    # print(schedule)

    os.chdir(os.path.abspath('.'))
    if platform.system() == 'Windows':
        schedule_path = os.path.abspath('.') + '\\networkbootsystem\\static\\schedule\\'
        file_name = schedule_path + year + '年' + month + '月' + '值班表（成都）' + '.xls'
    if platform.system() == 'Linux':
        schedule_path = os.path.abspath('.') + '/networkbootsystem/static/schedule/'
        file_name = schedule_path + year + '年' + month + '月' + '值班表（成都）' + '.xls'

    createexcel(file_name, schedule, int(year), int(month))
    # print('导出Excel！')
    return HttpResponseRedirect('/schedule/index')


# 清空导出的值班表
def emptyfolder(request):
    os.chdir(os.path.abspath('.'))
    if platform.system() == 'Windows':
        schedule_path = os.path.abspath('.') + '\\networkbootsystem\\static\\schedule\\'
    if platform.system() == 'Linux':
        schedule_path = os.path.abspath('.') + '/networkbootsystem/static/schedule/'
    schedule_excel = os.listdir(schedule_path)
    for excel in schedule_excel:
        print(excel)
        if os.path.exists(schedule_path + excel):
            os.remove(schedule_path + excel)
    return HttpResponseRedirect('/schedule/index')


# 法定工作休息日信息
def legalday(request):
    legalday_list = LegalDay.objects.all().order_by('date')
    return render(request, 'schedule/legalday.html',
                  {
                      'legalday_list': legalday_list,
                  })


# 法定日增加
def legalday_add(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_add=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])
        selectlegal = request.POST.get('selectlegal')
        yy, mm, dd = request.POST.get('selectdate').split('-')
        selectdate = datetime.date(int(yy), int(mm), int(dd))
        print(selectdate, type(selectdate))
        if LegalDay.objects.filter(date=selectdate).count() > 0:
            legalday_list = LegalDay.objects.all().order_by('date')
            return render(request, 'schedule/legalday.html',
                          {
                              'legalday_list': legalday_list,
                              'status': '添加的日期已存在！'
                          })
        else:
            if selectlegal == '工作日':
                LegalDay.objects.create(date=selectdate, legalworkday=True, legalrestday=False)
            if selectlegal == '休息日':
                LegalDay.objects.create(date=selectdate, legalworkday=False, legalrestday=True)
            return HttpResponseRedirect('/schedule/legalday')

    else:
        print('用户不存在！返回登录页面', request.path)
        if User.objects.filter(username=request.session['session_name']).count() == 1:
            print('用户 %s 无权限！' % request.session['session_name'])
            return render(request, 'user/unauth_access.html')
        else:
            print('未登录！请登陆后操作。')
            # return render(request, 'user/login.html')
            return HttpResponseRedirect('/user/login?next=%s' % request.path)


# 法定日删除
def legalday_del(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_del=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        delete_id = request.GET.get('delete_id')
        LegalDay.objects.filter(id=delete_id).delete()
        legalday_list = LegalDay.objects.all().order_by('date')
        return render(request, 'schedule/legalday.html',
                      {
                          'legalday_list': legalday_list,
                          'status': '删除完成！'
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


# 根据日期更新法定工作休息日信息
def legalday_update(request):
    try:
        print('当前用户：', request.session['session_name'])
    except KeyError:
        request.session['session_name'] = '匿名'
    if User.objects.filter(username=request.session['session_name'], auth_update=1).count() == 1:
        print('用户 %s 已有权限访问！' % request.session['session_name'])

        if request.method == 'POST':
            update_date = request.POST.get('update_date')
            date = strtodate(update_date)
            update_legal = request.POST.get('update_legal')

            if update_legal == '工作日':
                LegalDay.objects.filter(date=date).update(legalworkday=True, legalrestday=False)
            if update_legal == '休息日':
                LegalDay.objects.filter(date=date).update(legalworkday=False, legalrestday=True)

        return HttpResponseRedirect('/schedule/legalday')

    else:
        print('用户不存在！返回登录页面', request.path)
        if User.objects.filter(username=request.session['session_name']).count() == 1:
            print('用户 %s 无权限！' % request.session['session_name'])
            return render(request, 'user/unauth_access.html')
        else:
            print('未登录！请登陆后操作。')
            # return render(request, 'user/login.html')
            return HttpResponseRedirect('/user/login?next=%s' % request.path)


# 值班员工管理
def employee_index(request):
    all_employee = Employee.objects.all().order_by('num')
    all_employee_num = all_employee.count()
    able_employee_num = Employee.objects.filter(available=True).count()

    return render(request, 'schedule/employee_index.html',
                  {
                      'all_employee': all_employee,
                      'all_employee_num': all_employee_num,
                      'able_employee_num': able_employee_num,
                  })


# 更新值班成员信息
def employee_update(request):
    update_id = request.POST.get('update_id')
    update_num = request.POST.get('update_num')
    update_name = request.POST.get('update_name')
    update_available = request.POST.get('update_available')
    # print(update_available)
    if update_available == '是':
        Employee.objects.filter(id=update_id).update(num=update_num, name=update_name, available=True)
    else:
        Employee.objects.filter(id=update_id).update(num=update_num, name=update_name, available=False)
    return HttpResponseRedirect('/schedule/employee_index')


# 增加值班成员信息
def employee_add(request):
    add_num = request.POST.get('add_num')
    add_name = request.POST.get('add_name')
    add_available = request.POST.get('add_available')
    # print(add_name, add_num, add_available)
    if add_available == '是':
        Employee.objects.create(num=add_num, name=add_name, available=True)
    else:
        Employee.objects.create(num=add_num, name=add_name, available=False)
    return HttpResponseRedirect('/schedule/employee_index')


# 删除值班成员信息
def employee_del(request):
    del_id = request.GET.get('del_id')
    Employee.objects.filter(id=del_id).delete()
    return HttpResponseRedirect('/schedule/employee_index')