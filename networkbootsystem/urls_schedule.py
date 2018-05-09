# -*- coding:utf-8 -*-

from django.conf.urls import url
from networkbootsystem import views_schedule


urlpatterns = [
    url(r'^index$', views_schedule.index, name='schedule'),
    url(r'^workdayinfo$', views_schedule.workdayinfo, name='workdayinfo'),
    url(r'^createduty$', views_schedule.createduty, name='createduty'),
    url(r'^delayonce$', views_schedule.delayonce, name='delayonce'),
    url(r'^exchange$', views_schedule.exchange, name='exchange'),
    url(r'^getdateinfo$', views_schedule.getdateinfo, name='getdateinfo'),
    url(r'^delexchange$', views_schedule.delexchange, name='delexchange'),
    url(r'^exportexcel$', views_schedule.exportexcel, name='exportexcel'),
    url(r'^emptyfolder$', views_schedule.emptyfolder, name='emptyfolder'),
    url(r'^getlastduty$', views_schedule.getlastduty, name='getlastduty'),
    url(r'^legalday$', views_schedule.legalday, name='legalday'),
    url(r'^legalday_add$', views_schedule.legalday_add, name='legalday_add'),
    url(r'^legalday_del$', views_schedule.legalday_del, name='legalday_del'),
    url(r'^legalday_update$', views_schedule.legalday_update, name='legalday_update'),
    url(r'^employee_index$', views_schedule.employee_index, name='employee_index'),
    url(r'^employee_update$', views_schedule.employee_update, name='employee_update'),
    url(r'^employee_add$', views_schedule.employee_add, name='employee_add'),
    url(r'^employee_del$', views_schedule.employee_del, name='employee_del'),
]