# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-08-11 01:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('networkbootsystem', '0045_auto_20170811_0913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disksmartinfo',
            name='capacity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, verbose_name='实际容量G'),
        ),
        migrations.AlterField(
            model_name='disksmartinfo',
            name='currentpending',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, verbose_name='等待重映射扇区数C5'),
        ),
        migrations.AlterField(
            model_name='disksmartinfo',
            name='powercycle',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, verbose_name='通电次数0C'),
        ),
        migrations.AlterField(
            model_name='disksmartinfo',
            name='reallocated',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, verbose_name='重定位扇区数05'),
        ),
        migrations.AlterField(
            model_name='disksmartinfo',
            name='size',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, verbose_name='硬盘大小G'),
        ),
        migrations.AlterField(
            model_name='disksmartinfo',
            name='totalwritten',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=20, verbose_name='LBA写入总数F1'),
        ),
    ]
