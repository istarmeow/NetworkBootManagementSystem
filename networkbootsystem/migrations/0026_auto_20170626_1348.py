# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-26 05:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('networkbootsystem', '0025_auto_20170620_1651'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemInstallStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac', models.CharField(db_index=True, max_length=20, verbose_name='MAC地址')),
                ('get_time', models.DateTimeField(auto_now_add=True, verbose_name='获取时间')),
                ('start_time', models.DateTimeField(blank=True, verbose_name='开始时间')),
                ('complete_time', models.DateTimeField(blank=True, verbose_name='获取时间')),
                ('process_time', models.DateTimeField(blank=True, verbose_name='安装时间')),
                ('status', models.CharField(choices=[('-1', '失败'), ('0', '进行中'), ('1', '已完成')], max_length=10, verbose_name='进度状态')),
            ],
            options={
                'verbose_name': '装机进度',
                'verbose_name_plural': '装机进度列表',
            },
        ),
        migrations.AlterField(
            model_name='user',
            name='auth_add',
            field=models.CharField(choices=[('0', '否'), ('1', '是')], max_length=2, verbose_name='增加权限'),
        ),
        migrations.AlterField(
            model_name='user',
            name='auth_del',
            field=models.CharField(choices=[('0', '否'), ('1', '是')], max_length=2, verbose_name='删除权限'),
        ),
        migrations.AlterField(
            model_name='user',
            name='auth_search',
            field=models.CharField(choices=[('0', '否'), ('1', '是')], max_length=2, verbose_name='查找权限'),
        ),
        migrations.AlterField(
            model_name='user',
            name='auth_update',
            field=models.CharField(choices=[('0', '否'), ('1', '是')], max_length=2, verbose_name='更新权限'),
        ),
    ]
