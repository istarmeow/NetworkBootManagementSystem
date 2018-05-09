# -*- coding:utf-8 -*-

from django.conf.urls import url
from . import views_questionbank

urlpatterns = [
    url(r'^questionadd$', views_questionbank.questionadd, name='questionadd'),
    url(r'^index$', views_questionbank.index, name='questionlist'),
    url(r'^questiondel$', views_questionbank.questiondel, name='questiondel'),
    url(r'^exportword$', views_questionbank.exportword, name='exportword'),
    url(r'^emptyquestion$', views_questionbank.emptyquestion, name='emptyquestion'),
    url(r'^questionupdate$', views_questionbank.questionupdate, name='questionupdate'),
]
