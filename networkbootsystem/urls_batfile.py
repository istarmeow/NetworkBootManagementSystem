# -*- coding:utf-8 -*-

from django.conf.urls import url
from . import views_batfile

urlpatterns = [
    url(r'^generate_bat_file$', views_batfile.generate_bat_file, name='generate_bat_file'),

]