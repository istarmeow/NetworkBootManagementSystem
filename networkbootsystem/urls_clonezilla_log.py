# -*- coding:utf-8 -*-

from django.conf.urls import url
from . import views_clonezilla_log

urlpatterns = [
    url(r'^boot_from_clonezilla_get_log.html', views_clonezilla_log.boot_from_clonezilla_get_log, name='boot_from_clonezilla_get_log'),
    url(r'^system_install_status_json$', views_clonezilla_log.system_install_status_json, name='system_install_status_json'),
    url(r'^system_install_status$', views_clonezilla_log.system_install_status, name='system_install_status'),
    url(r'^system_install_status_info$', views_clonezilla_log.system_install_status_info, name='system_install_status_info'),
    url(r'^show_netspeed$', views_clonezilla_log.show_netspeed, name='show_netspeed'),
    url(r'^system_install_status_num$', views_clonezilla_log.system_install_status_num, name='system_install_status_num'),
    url(r'^show_boot_auto_from_mac$', views_clonezilla_log.show_boot_auto_from_mac, name='show_boot_auto_from_mac'),

]