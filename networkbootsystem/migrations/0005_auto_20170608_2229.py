# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-08 14:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('networkbootsystem', '0004_auto_20170608_2227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='httpserverlist',
            name='explain',
            field=models.TextField(blank=True, default='说明', max_length=100, verbose_name='说明'),
            preserve_default=False,
        ),
    ]
