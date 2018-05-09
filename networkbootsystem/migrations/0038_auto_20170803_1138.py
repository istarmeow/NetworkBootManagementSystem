# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-08-03 03:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('networkbootsystem', '0037_auto_20170712_1936'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='verify',
            field=models.CharField(blank=True, max_length=10, verbose_name='验证码'),
        ),
        migrations.AlterField(
            model_name='updatelog',
            name='details',
            field=models.TextField(blank=True, max_length=1200, verbose_name='详情'),
        ),
    ]
