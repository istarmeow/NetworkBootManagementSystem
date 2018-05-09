# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-13 06:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('networkbootsystem', '0018_auto_20170611_2007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultimageselect',
            name='select_name',
            field=models.CharField(max_length=60, verbose_name='选择默认启动镜像'),
        ),
        migrations.AlterField(
            model_name='sambaserverlist',
            name='netspeed_path',
            field=models.CharField(blank=True, default='/netspeed', max_length=20, verbose_name='测速网速获取地址'),
        ),
    ]