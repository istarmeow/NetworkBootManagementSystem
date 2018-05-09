# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-08-11 01:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('networkbootsystem', '0051_auto_20170811_0928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disksmartinfo',
            name='capacity',
            field=models.CharField(blank=True, max_length=20, verbose_name='实际容量G'),
        ),
        migrations.AlterField(
            model_name='disksmartinfo',
            name='size',
            field=models.CharField(blank=True, max_length=20, verbose_name='硬盘大小G'),
        ),
    ]
