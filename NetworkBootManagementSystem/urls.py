"""NetworkBootManagementSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
# -*- coding:utf-8 -*-
from django.conf.urls import url, include
from django.contrib import admin
from networkbootsystem import views
# 上传的文件能直接通过url打开，以及setting中设置
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^back_manage$', views.back_manage, name='back_manage'),

    url(r'^macupper$', views.mac_upper, name='macupper'),  # MAC转换成大写

    # url(r'^$', 'login.viewss.login_view', name='login_view'),
    url(r'^boot$', views.boot_select, name='boot_select'),
    url(r'^select_boot_control.html', views.select_boot_control, name='select_boot_control'),
    url(r'^manage/', include('networkbootsystem.urls_iso'), name='manage_iso'),
    url(r'^manage/', include('networkbootsystem.urls_clonezilla'), name='manage_clonezilla'),


    # url(r'^pxelog/', include('networkbootsystem.urls_iso_log'), name='pxelog_iso'),

    url(r'^logs/', include('networkbootsystem.urls_clonezilla_log'), name='log_clonezilla'),
    url(r'^logs/', include('networkbootsystem.urls_iso_log'), name='log_iso'),
    url(r'^document$', views.document, name='document'),
    url(r'^complete_request$', views.complete_request, name='complete_request'),
    url(r'^start_request$', views.start_request, name='start_request'),

    url(r'^user/', include('networkbootsystem.urls_user'), name='manage_user'),

    url(r'^update_logs$', views.update_logs, name='update_logs'),
    url(r'^get_new_version$', views.get_new_version, name='get_new_version'),

    url(r'^computer/', include('networkbootsystem.urls_computer_info'), name='computer'),

    url(r'^other/', include('networkbootsystem.urls_batfile'), name='other'),

    url(r'^show_current_select_boot$', views.show_current_select_boot, name='show_current_select_boot'),

    url(r'^schedule/', include('networkbootsystem.urls_schedule')),
    url(r'^questionbank/', include('networkbootsystem.urls_questionbank')),

]

# 上传的文件能直接通过url打开
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

