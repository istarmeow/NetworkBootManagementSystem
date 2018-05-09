# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-08 14:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('networkbootsystem', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bootfromclonezilla',
            name='disk_num',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='networkbootsystem.RestoreDiskNum', verbose_name='恢复硬盘编号'),
        ),
    ]
