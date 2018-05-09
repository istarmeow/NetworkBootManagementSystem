from django.conf.urls import url
from . import views_computer_info

urlpatterns = [
    url(r'^disk_smart_info$', views_computer_info.disk_smart_info, name='disk_smart_info'),
    url(r'^query_disk_smart_info$', views_computer_info.query_disk_smart_info, name='query_disk_smart_info'),
    url(r'^wakeonlan$', views_computer_info.wakeonlan, name='wakeonlan'),
    url(r'^dhcp_operate$', views_computer_info.dhcp_operate, name='dhcp_operate'),
    url(r'^dhcp_index$', views_computer_info.dhcp_index, name='dhcp_index'),
]
