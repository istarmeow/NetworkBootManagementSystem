# -*- coding:utf-8 -*-

from django.db import models
import django.utils.timezone as timezone

# Create your models here.


class HttpServerList(models.Model):
    http_name = models.CharField(max_length=50, unique=True, verbose_name='Http服务器名称')
    http_ip = models.CharField(max_length=50, verbose_name='Http服务器IP')
    http_port = models.CharField(max_length=10, blank=True, verbose_name='Http服务器端口')
    http_folder = models.CharField(max_length=50, blank=True, verbose_name='文件目录')
    available = models.BooleanField(verbose_name='是否启用(必须至少有一项)')
    default = models.BooleanField(verbose_name='是否默认(必须只能选择一项)')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    explain = models.TextField(max_length=100, blank=True, verbose_name='说明')

    class Meta:
        verbose_name = 'Http服务器'
        verbose_name_plural = 'Http服务器列表'

    def __str__(self):
        return self.http_name


class SambaServerList(models.Model):
    samba_name = models.CharField(max_length=50, verbose_name='Samba服务器名称')
    samba_ip = models.CharField(max_length=50, verbose_name='Samba服务器IP')
    samba_folder = models.CharField(max_length=50, verbose_name='镜像目录')
    samba_user = models.CharField(max_length=10, verbose_name='服务器用户')
    samba_password = models.CharField(max_length=10, verbose_name='服务器密码')
    netspeed_port = models.CharField(max_length=10, blank=True, verbose_name='测速Http服务器端口')
    netspeed_path = models.CharField(max_length=20, blank=True, default='/netspeed', verbose_name='测速网速获取地址')
    available = models.BooleanField(verbose_name='是否启用(必须至少有一项)')
    default = models.BooleanField(verbose_name='是否默认(必须只能选择一项)')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    explain = models.TextField(max_length=100, blank=True, verbose_name='说明')

    class Meta:
        verbose_name = 'Samba服务器'
        verbose_name_plural = 'Samba服务器列表'

    def __str__(self):
        return self.samba_name


class ImageFilesList(models.Model):
    name = models.CharField(max_length=50, verbose_name='镜像名称')
    image_name = models.CharField(max_length=50, unique=True, verbose_name='镜像文件名称')
    disk_type = models.CharField(max_length=50, verbose_name='镜像硬盘类型')
    disk_size = models.CharField(max_length=50, verbose_name='镜像硬盘容量')
    available_model = models.CharField(max_length=100, verbose_name='可用电脑型号')
    available = models.BooleanField(verbose_name='是否启用')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    explain = models.TextField(max_length=100, blank=True, verbose_name='说明')

    class Meta:
        verbose_name = 'Clonezilla镜像文件'
        verbose_name_plural = 'Clonezilla镜像文件列表'

    def __str__(self):
        return self.name


class RestoreDiskNum(models.Model):
    disk_name = models.CharField(max_length=10, verbose_name='恢复硬盘名称')
    disk_num = models.CharField(max_length=10, verbose_name='恢复硬盘编号')
    available = models.BooleanField(verbose_name='是否启用')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    explain = models.TextField(max_length=100, blank=True, verbose_name='说明')

    class Meta:
        verbose_name = 'Clonezilla硬盘恢复'
        verbose_name_plural = 'Clonezilla硬盘恢复列表'

    def __str__(self):
        return self.disk_name


class BootFromClonezilla(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='启动名称')
    mac = models.CharField(max_length=20, unique=True, db_index=True, verbose_name='MAC地址')
    http_server = models.ForeignKey(HttpServerList, verbose_name='Clonezilla文件地址')
    samba_server = models.ForeignKey(SambaServerList, verbose_name='Samba镜像服务器')
    image_file = models.ForeignKey(ImageFilesList, verbose_name='镜像名称')
    image_path = models.CharField(max_length=100, default='/home/partimag', verbose_name='镜像加载路径')
    restore_disk = models.ForeignKey(RestoreDiskNum, verbose_name='恢复硬盘编号')
    available = models.BooleanField(verbose_name='是否启用')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    explain = models.TextField(max_length=1000, blank=True, verbose_name='说明')

    class Meta:
        verbose_name = 'Clonezilla自动启动选择'
        verbose_name_plural = 'Clonezilla自动启动列表'

    def __str__(self):
        return self.name


class BootFromClonezillaLog(models.Model):
    mac = models.CharField(max_length=20, db_index=True, verbose_name='MAC地址')
    ip = models.CharField(max_length=20, db_index=True, verbose_name='IP地址')
    serial = models.CharField(max_length=100, verbose_name='服务代码')
    image = models.CharField(max_length=100, verbose_name='镜像名称')
    disk_num = models.CharField(max_length=100, verbose_name='恢复硬盘编号')
    http_path = models.CharField(max_length=100, verbose_name='获取Http服务器')
    samba_path = models.CharField(max_length=100, verbose_name='获取Samba服务器')
    get_tag = models.BooleanField(verbose_name='是否获取')
    get_way = models.CharField(max_length=30, verbose_name='获取方式')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = 'Clonezilla获取日志'
        verbose_name_plural = 'Clonezilla获取日志列表'

    def __str__(self):
        return self.mac


class DefaultImageSelect(models.Model):
    select_name = models.CharField(max_length=60, unique=True, verbose_name='选择默认启动镜像')
    image_file = models.ForeignKey(ImageFilesList, verbose_name='镜像文件选择')
    http_server = models.ForeignKey(HttpServerList, verbose_name='Http服务器选择')
    samba_server = models.ForeignKey(SambaServerList, verbose_name='Samba服务器选择')
    restore_disk = models.ForeignKey(RestoreDiskNum, verbose_name='恢复硬盘编号')
    image_path = models.CharField(max_length=100, default='/home/partimag', verbose_name='镜像加载路径')
    available = models.BooleanField(verbose_name='是否启用(必须只能选择一项)')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    explain = models.TextField(max_length=100, blank=True, verbose_name='说明')

    class Meta:
        verbose_name = 'Clonezilla默认选择'
        verbose_name_plural = '1.1、Clonezilla默认选择列表'

    def __str__(self):
        return self.select_name


class BootSelect(models.Model):
    name = models.CharField(max_length=30, verbose_name='选择名称')
    boot_name = models.CharField(max_length=30, unique=True, verbose_name='选择启动方式')
    available = models.BooleanField(verbose_name='是否启用(只能选择一项)')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    explain = models.TextField(max_length=100, blank=True, verbose_name='说明')

    class Meta:
        verbose_name = '启动方式'
        verbose_name_plural = '0.0、选择启动方式'

    def __str__(self):
        return self.name


class BootFromISO(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='启动名称')
    http_server = models.ForeignKey(HttpServerList, verbose_name='ISO文件地址')
    iso_file = models.CharField(max_length=100, db_index=True, verbose_name='ISO名称')
    available = models.BooleanField(verbose_name='是否启用(有且仅有一个启用)')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    explain = models.TextField(max_length=100, blank=True, verbose_name='说明')

    class Meta:
        verbose_name = 'ISO启动选择'
        verbose_name_plural = '1.2、ISO启动选择列表'

    def __str__(self):
        return self.name


class BootFromISOLog(models.Model):
    mac = models.CharField(max_length=20, db_index=True, verbose_name='MAC地址')
    ip = models.CharField(max_length=20, db_index=True, verbose_name='IP地址')
    serial = models.CharField(max_length=100, verbose_name='服务代码')
    http_path = models.CharField(max_length=100, verbose_name='获取Http服务器')
    iso_name = models.CharField(max_length=100, verbose_name='获取ISO名称')
    get_tag = models.BooleanField(verbose_name='是否获取')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = 'ISO获取日志'
        verbose_name_plural = 'ISO获取日志列表'

    def __str__(self):
        return self.mac


# 用户注册登录模型
class User(models.Model):
    AUTH_CHOICES = (
        ('0', '否'),
        ('1', '是'),
    )
    username = models.CharField(max_length=50, db_index=True, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=200, verbose_name='密码')
    email = models.EmailField(verbose_name='邮箱')
    verify = models.CharField(max_length=10, blank=True, verbose_name='验证码')
    auth_search = models.CharField(max_length=2, choices=AUTH_CHOICES, verbose_name='查找权限')
    auth_add = models.CharField(max_length=2, choices=AUTH_CHOICES, verbose_name='增加权限')
    auth_del = models.CharField(max_length=2, choices=AUTH_CHOICES, verbose_name='删除权限')
    auth_update = models.CharField(max_length=2, choices=AUTH_CHOICES, verbose_name='更新权限')
    available = models.BooleanField(verbose_name='是否启用')
    created = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    # 用户独立启动选择记录
    boot_select = models.CharField(max_length=100, blank=True, verbose_name='启动方式名称')
    boot_clonezilla_id = models.DecimalField(default=0, max_digits=5, decimal_places=0, verbose_name='Clonezilla_ID')
    boot_iso_id = models.DecimalField(default=0, max_digits=5, decimal_places=0, verbose_name='Iso_ID')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户列表'

    def __str__(self):
        return self.username


# 装机进度模型
class SystemInstallStatus(models.Model):
    STATUS_CHOICES = (
        ('-1', '未获取'),
        ('0', '进行中'),
        ('1', '已完成'),
        ('error', '超时异常'),
    )
    mac = models.CharField(max_length=20, db_index=True, verbose_name='MAC地址')
    get_time = models.DateTimeField(auto_now_add=True, verbose_name='获取时间')
    start_time = models.DateTimeField(default=timezone.now, verbose_name='开始时间')
    complete_time = models.DateTimeField(default=timezone.now, verbose_name='完成时间')
    process_time = models.CharField(max_length=20, blank=True, verbose_name='安装时长(分钟)')
    status = models.CharField(max_length=10, default='-1', choices=STATUS_CHOICES, verbose_name='进度状态')

    class Meta:
        verbose_name = '装机进度'
        verbose_name_plural = '装机进度列表'

    def __str__(self):
        return self.mac


class UserAuthApply(models.Model):
    AUTH_CHOICES = (
        ('0', '否'),
        ('1', '是'),
    )
    STATUE_CHOICES = (
        ('-1', '已拒绝'),
        ('0', '未处理'),
        ('1', '已通过'),
    )
    username = models.CharField(max_length=50, verbose_name='用户名')
    auth_search = models.CharField(max_length=2, choices=AUTH_CHOICES, verbose_name='查找权限')
    auth_add = models.CharField(max_length=2, choices=AUTH_CHOICES, verbose_name='增加权限')
    auth_del = models.CharField(max_length=2, choices=AUTH_CHOICES, verbose_name='删除权限')
    auth_update = models.CharField(max_length=2, choices=AUTH_CHOICES, verbose_name='更新权限')
    created = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='处理时间')
    statue = models.CharField(max_length=20, choices=STATUE_CHOICES, verbose_name='处理状态')

    class Meta:
        verbose_name = '用户权限申请'
        verbose_name_plural = '用户权限申请列表'

    def __str__(self):
        return self.username


class UpdateLog(models.Model):
    version = models.CharField(max_length=50, verbose_name='版本')
    summary = models.CharField(max_length=100, verbose_name='摘要')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    details = models.TextField(max_length=1200, blank=True, verbose_name='详情')

    class Meta:
        verbose_name = '更新日志'
        verbose_name_plural = '更新日志列表'

    def __str__(self):
        return self.version


class UserVerificationCode(models.Model):
    username = models.CharField(max_length=50, verbose_name='用户名')
    verify = models.CharField(max_length=10, blank=True, verbose_name='验证码')
    outbox = models.CharField(max_length=50, blank=True, verbose_name='发件箱')
    inbox = models.CharField(max_length=50, blank=True, verbose_name='收件箱')
    sendnum = models.IntegerField(default=1, verbose_name='邮件发送次数')
    retrynum = models.IntegerField(default=0, verbose_name='验证码尝试次数')
    created = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='注册时间')

    class Meta:
        verbose_name = '验证码'
        verbose_name_plural = '验证码数据库'

    def __str__(self):
        return self.username


class DiskSmartInfo(models.Model):
    serial = models.CharField(max_length=50, db_index=True, unique=True, verbose_name='硬盘序列号')
    caption = models.CharField(max_length=50, blank=True, verbose_name='硬盘名称')
    size = models.CharField(max_length=10, blank=True, verbose_name='硬盘大小G')
    capacity = models.CharField(max_length=10, blank=True, verbose_name='实际容量G')
    pnpdeviceid = models.CharField(max_length=100, blank=True, verbose_name='硬盘设备ID')
    instancename = models.CharField(max_length=100, blank=True, verbose_name='硬盘实例名称')
    reallocated = models.CharField(max_length=10, blank=True, verbose_name='重定位扇区数05')
    poweron = models.CharField(max_length=10, blank=True, verbose_name='通电时间（小时）09')
    powercycle = models.CharField(max_length=10, blank=True, verbose_name='通电次数0C')
    currentpending = models.CharField(max_length=10, blank=True, verbose_name='等待重映射扇区数C5')
    totalwritten = models.CharField(max_length=20, blank=True, verbose_name='LBA写入总数F1')
    ip = models.CharField(max_length=20, verbose_name='IP地址')
    mac = models.CharField(max_length=20, verbose_name='MAC地址')
    diskinfo = models.BooleanField(default=False, verbose_name='磁盘信息获取状态')
    smartinfo = models.BooleanField(default=False, verbose_name='SMART信息获取状态')
    disktime = models.DateTimeField(auto_now_add=True, verbose_name='磁盘信息获取时间')
    smarttime = models.DateTimeField(auto_now_add=True, verbose_name='SMART信息获取时间')

    class Meta:
        verbose_name = '硬盘SMART信息'
        verbose_name_plural = '硬盘SMART信息'

    def __str__(self):
        return self.serial


# 以下是值班表
class Employee(models.Model):
    name = models.CharField(max_length=10, db_index=True, verbose_name='姓名')
    num = models.DecimalField(max_digits=5, decimal_places=0, verbose_name='序号')
    nightnum = models.DecimalField(default=0, max_digits=5, decimal_places=0, verbose_name='晚班临时序号')
    meetnum = models.DecimalField(default=0, max_digits=5, decimal_places=0, verbose_name='例会临时序号')
    weekendnum = models.DecimalField(default=0, max_digits=5, decimal_places=0, verbose_name='周末临时序号')
    available = models.BooleanField(verbose_name='是否排班')

    class Meta:
        verbose_name = '员工'
        verbose_name_plural = '值班表-所有员工'

    def __str__(self):
        return self.name


class Schedule(models.Model):
    date = models.DateField(unique=True, verbose_name='日期')
    week = models.CharField(max_length=10, blank=True, verbose_name='星期')
    workday = models.BooleanField(default=False, verbose_name='是否工作日')
    nightduty = models.BooleanField(default=False, verbose_name='是否晚上值班')
    meetduty = models.BooleanField(default=False, verbose_name='是否例会')
    weekendduty = models.BooleanField(default=False, verbose_name='是否周末值班')
    staff = models.CharField(max_length=10, null=True, verbose_name='值班人员')
    realstaff = models.CharField(max_length=10, null=True, verbose_name='实际值班人员')

    class Meta:
        verbose_name = '值班表'
        verbose_name_plural = '值班表-排班'

    def __str__(self):
        return str(self.date)


# 法定工作日，或法定休息日
class LegalDay(models.Model):
    date = models.DateField(verbose_name='日期')
    legalworkday = models.BooleanField(verbose_name='是否法定工作日')
    legalrestday = models.BooleanField(verbose_name='是否法定休息日')

    class Meta:
        verbose_name = '法定工作休息日'
        verbose_name_plural = '值班表-法定工作休息日'

    def __str__(self):
        return str(self.date)


# WOL记录
class WakeOnLan(models.Model):
    mac = models.CharField(max_length=20, unique=True, db_index=True, verbose_name='MAC地址')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='最近执行')

    class Meta:
        verbose_name = '网启开机'
        verbose_name_plural = '网启开机日志'

    def __str__(self):
        return str(self.mac)


# 题库
class QuestionBank(models.Model):
    category = models.CharField(max_length=10, verbose_name='分类')
    level = models.CharField(max_length=10, verbose_name='难易程度')
    questiontype = models.CharField(max_length=10, verbose_name='题型')
    topic = models.CharField(max_length=50, verbose_name='考察类型')
    text = models.TextField(max_length=200, blank=True, verbose_name='考题')
    image = models.ImageField(upload_to='images/%Y/%m/%d', blank=True, verbose_name='图片')
    answer = models.TextField(max_length=200, blank=True, verbose_name='答案')

    class Meta:
        verbose_name = 'IT笔试题'
        verbose_name_plural = 'IT笔试题库'

    def __str__(self):
        return str(self.topic)
