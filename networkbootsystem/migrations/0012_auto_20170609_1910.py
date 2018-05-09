# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-09 11:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('networkbootsystem', '0011_auto_20170609_1332'),
    ]

    operations = [
        migrations.CreateModel(
            name='BootFromISO',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='启动名称')),
                ('iso_file', models.CharField(db_index=True, max_length=100, verbose_name='ISO名称')),
                ('available', models.BooleanField(verbose_name='是否启用(有且仅有一个启用)')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('explain', models.TextField(blank=True, max_length=100, verbose_name='说明')),
                ('http_server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='networkbootsystem.HttpServerList', verbose_name='ISO文件地址')),
            ],
            options={
                'verbose_name': '一个ISO文件启动',
                'verbose_name_plural': '所有ISO文件启动',
            },
        ),
        migrations.AlterModelOptions(
            name='bootfromclonezillalog',
            options={'verbose_name': '获取日志-Clonezilla', 'verbose_name_plural': '所有获取日志-Clonezilla'},
        ),
        migrations.AlterModelOptions(
            name='bootselect',
            options={'verbose_name': '启动方式', 'verbose_name_plural': '一、选择启动方式'},
        ),
        migrations.AlterModelOptions(
            name='defaultimageselect',
            options={'verbose_name': '默认Clonezilla选择', 'verbose_name_plural': '二、默认Clonezilla选择列表'},
        ),
        migrations.AlterField(
            model_name='bootselect',
            name='available',
            field=models.BooleanField(verbose_name='是否启用(只能选择一项)'),
        ),
    ]
