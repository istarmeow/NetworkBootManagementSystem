# -*- coding:utf-8 -*-

from django.shortcuts import render
from .models import BootFromISOLog


# 查看ISO日志
def boot_from_iso_get_log(request):
    iso_get_log = BootFromISOLog.objects.order_by('-updated')[0:20]
    return render(request, 'logs/boot_from_iso/boot_from_iso_get_log.html',
                  {
                      'iso_get_log': iso_get_log,
                  })
