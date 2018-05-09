# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-01 14:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('networkbootsystem', '0062_questionbank_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionbank',
            name='questiontype',
            field=models.CharField(default='选择题', max_length=10, verbose_name='题型'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='questionbank',
            name='image',
            field=models.ImageField(blank=True, upload_to='images/%Y/%m/%d', verbose_name='图片'),
        ),
    ]
