# -*- coding:utf-8 -*-

from django.conf.urls import url
from . import views_iso_log

urlpatterns = [
    url(r'^boot_from_iso_get_log.html', views_iso_log.boot_from_iso_get_log, name='boot_from_iso_get_log')
]