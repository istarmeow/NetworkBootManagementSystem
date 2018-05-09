# -*- coding:utf-8 -*-

from django.conf.urls import url
from . import views_iso

urlpatterns = [
    url(r'^select_boot_iso_control.html$', views_iso.select_boot_iso_control, name='select_boot_iso_control'),
    url(r'^sync_iso_file$', views_iso.sync_iso_file, name='sync_iso_file'),
    url(r'^del_iso_selecte$', views_iso.del_iso_select, name='del_iso_select'),



    # http://172.16.66.66:8899/manage/select_boot_iso_control.html
    # # 使用get方式查询数据库
    # url(r'^manager/query_boot_from_iso_info_get.html$', views_iso.query_boot_from_iso_info_get, name='query_boot_from_iso_info_get'),
    #
    # # 使用post方法查询
    # url(r'^manager/query_boot_from_iso_info_post.html$', views_iso.query_boot_from_iso_info_post, name='query_boot_from_iso_info_post'),
    #
    # # 增加信息
    # url(r'^manager/add_boot_iso_info.html', views_iso.add_boot_iso_info, name='add_boot_iso_info'),
    #
    # # 综合查询删除更新操作
    # url(r'^manager/boot_from_iso_info_query_operation.html', views_iso.boot_from_iso_info_query_operation, name='boot_from_iso_info_query_operation'),
    # url(r'^manager/boot_iso_info_execute_delete', views_iso.boot_iso_info_execute_delete, name='boot_iso_info_execute_delete'),
    # # # http://172.16.66.66:8899/pxesvr/manage/ExecuteDeleteImageInfo?delete_mac=MAC
    # url(r'^manager/boot_iso_info_execute_update.html', views_iso.boot_iso_info_execute_update, name='boot_iso_info_execute_update'),
    # url(r'^manager/boot_iso_info_query_details.html', views_iso.boot_iso_info_query_details, name='boot_iso_info_query_details'),

]

