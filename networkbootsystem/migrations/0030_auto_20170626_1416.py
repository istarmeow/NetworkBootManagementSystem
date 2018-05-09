# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-26 06:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('networkbootsystem', '0029_auto_20170626_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systeminstallstatus',
            name='complete_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='完成时间'),
        ),
        migrations.AlterField(
            model_name='systeminstallstatus',
            name='start_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='开始时间'),
        ),
    ]
