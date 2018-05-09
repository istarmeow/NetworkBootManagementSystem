# -*- coding:utf-8 -*-

from django.conf.urls import url
from . import views_user

urlpatterns = [
    url(r'^login$', views_user.login, name='login'),
    url(r'^logout$', views_user.logout, name='logout'),
    url(r'^register$', views_user.register, name='register'),
    url(r'^user_management$', views_user.user_management, name='user_management'),
    url(r'^user_list_json$', views_user.ajax_user_management_to_json, name='ajax_user_management_to_json'),
    url(r'^switch_user_auth$', views_user.ajax_user_management_switch_auth, name='ajax_user_management_switch_auth'),
    # 使用ajax执行用户权限更新
    url(r'^show_current_user_permissions$', views_user.show_current_user_permissions, name='show_current_user_permissions'),
    # 显示用户权限的json
    url(r'^user_apply_permissions$', views_user.user_apply_permissions, name='user_apply_permissions'),
    # 用户申请权限，存储数据库
    url(r'^show_user_apply_permissions$', views_user.show_user_apply_permissions,
        name='show_user_apply_permissions'),
    # 查看权限，返回的是所有未处理的json数据
    url(r'^adopt_user_apply$', views_user.adopt_user_apply,
        name='adopt_user_apply'),
    url(r'^refuse_user_apply$', views_user.refuse_user_apply,
        name='refuse_user_apply'),
    url(r'^send_verify$', views_user.send_verify, name='send_verify'),
    url(r'^reset_password$', views_user.reset_password, name='reset_password'),



]
