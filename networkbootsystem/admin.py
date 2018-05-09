# -*- coding:utf-8 -*-

from django.contrib import admin
from .models import HttpServerList, SambaServerList, ImageFilesList, RestoreDiskNum, BootFromClonezilla
from .models import BootFromClonezillaLog, DefaultImageSelect, BootSelect, BootFromISO, BootFromISOLog
from .models import User, SystemInstallStatus, UserAuthApply, UpdateLog, UserVerificationCode, DiskSmartInfo
from .models import Employee, Schedule, LegalDay, WakeOnLan, QuestionBank
'''
admin:djangoadmin
'''
# Register your models here.


class HttpServerListAdmin(admin.ModelAdmin):
    list_display = ('http_name', 'http_ip', 'http_port', 'http_folder', 'available', 'default')
    list_editable = ('available', 'default')
    ordering = ('http_name',)
admin.site.register(HttpServerList, HttpServerListAdmin)


class SambaServerListAdmin(admin.ModelAdmin):
    list_display = ('samba_name', 'samba_ip', 'samba_folder', 'samba_user', 'samba_password', 'netspeed_port', 'netspeed_path', 'available', 'default')
    list_editable = ('available', 'default',)
    ordering = ('samba_name',)
admin.site.register(SambaServerList, SambaServerListAdmin)


class ImageFilesListAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_name', 'disk_type', 'disk_size', 'available_model', 'available')
    list_editable = ('available',)
    ordering = ('name',)
admin.site.register(ImageFilesList, ImageFilesListAdmin)


class RestoreDiskNumAdmin(admin.ModelAdmin):
    list_display = ('disk_name', 'disk_num', 'available')
    list_editable = ('available',)
    ordering = ('disk_name',)
admin.site.register(RestoreDiskNum, RestoreDiskNumAdmin)


class BootFromClonezillaAdmin(admin.ModelAdmin):
    list_display = ('name', 'mac', 'http_server', 'samba_server', 'image_file', 'image_path', 'restore_disk', 'available')
    list_editable = ('available',)
    ordering = ('name',)
admin.site.register(BootFromClonezilla, BootFromClonezillaAdmin)


class BootFromClonezillaLogAdmin(admin.ModelAdmin):
    list_display = ('mac', 'ip', 'serial', 'image', 'disk_num', 'http_path', 'samba_path', 'get_tag', 'get_way', 'updated')
admin.site.register(BootFromClonezillaLog, BootFromClonezillaLogAdmin)


class DefaultImageSelectAdmin(admin.ModelAdmin):
    list_display = ('select_name', 'image_file', 'http_server', 'samba_server', 'restore_disk', 'available')
    list_editable = ('available',)
    ordering = ('select_name',)
admin.site.register(DefaultImageSelect, DefaultImageSelectAdmin)


class BootSelectAdmin(admin.ModelAdmin):
    list_display = ('name', 'boot_name', 'available')
    list_editable = ('available',)
admin.site.register(BootSelect, BootSelectAdmin)


class BootFromISOAdmin(admin.ModelAdmin):
    list_display = ('name', 'http_server', 'iso_file', 'available')
    list_editable = ('available',)
admin.site.register(BootFromISO, BootFromISOAdmin)


class BootFromISOLogAdmin(admin.ModelAdmin):
    list_display = ('mac', 'ip', 'serial', 'http_path', 'iso_name', 'get_tag', 'updated')
admin.site.register(BootFromISOLog, BootFromISOLogAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'email', 'verify', 'auth_search', 'auth_add', 'auth_del', 'auth_update', 'available', 'boot_select', 'boot_clonezilla_id', 'boot_iso_id', 'created', 'updated',)
    list_editable = ('auth_search', 'auth_add', 'auth_del', 'auth_update', 'available')
admin.site.register(User, UserAdmin)


class SystemInstallStatusAdmin(admin.ModelAdmin):
    list_display = ('mac', 'get_time', 'start_time', 'complete_time', 'process_time', 'status')
admin.site.register(SystemInstallStatus, SystemInstallStatusAdmin)


class UserAuthApplyAdmin(admin.ModelAdmin):
    list_display = ('username', 'auth_search', 'auth_add', 'auth_del', 'auth_update', 'created', 'updated', 'statue')
    list_editable = ('auth_search', 'auth_add', 'auth_del', 'auth_update')
admin.site.register(UserAuthApply, UserAuthApplyAdmin)


class UpdateLogAdmin(admin.ModelAdmin):
    list_display = ('version', 'summary', 'created', 'updated', 'details')
admin.site.register(UpdateLog, UpdateLogAdmin)


class UserVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('username', 'verify', 'outbox', 'sendnum', 'retrynum', 'inbox', 'created', 'updated')
admin.site.register(UserVerificationCode, UserVerificationCodeAdmin)


class DiskSmartInfoAdmin(admin.ModelAdmin):
    list_display = ('serial', 'caption', 'size', 'capacity', 'reallocated', 'poweron', 'powercycle', 'currentpending', 'totalwritten', 'ip', 'mac', 'diskinfo', 'smartinfo')
admin.site.register(DiskSmartInfo, DiskSmartInfoAdmin)


# 以下为值班表
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'num', 'available', 'nightnum', 'meetnum', 'weekendnum')
    ordering = ('name',)
admin.site.register(Employee, EmployeeAdmin)


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('date', 'week', 'workday', 'nightduty', 'meetduty', 'weekendduty', 'staff', 'realstaff')
    ordering = ('date',)
admin.site.register(Schedule, ScheduleAdmin)


class LegalDayAdmin(admin.ModelAdmin):
    list_display = ('date', 'legalworkday', 'legalrestday')
    ordering = ('date',)
admin.site.register(LegalDay, LegalDayAdmin)


class WakeOnLanAdmin(admin.ModelAdmin):
    list_display = ('mac', 'created', 'updated')
    ordering = ('updated',)
admin.site.register(WakeOnLan, WakeOnLanAdmin)


class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ('category', 'level', 'questiontype', 'topic', 'text', 'image', 'answer')
    ordering = ('category',)
admin.site.register(QuestionBank, QuestionBankAdmin)
