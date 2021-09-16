# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-04-16 13:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0005_bankinfo_account_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='competitionqainfo',
            name='correct_list',
            field=models.CharField(blank=True, help_text='正确答案列表', max_length=8000, null=True, verbose_name='正确答案列表'),
        ),
        migrations.AddField(
            model_name='competitionqainfo',
            name='wrong_list',
            field=models.CharField(blank=True, help_text='错误答案列表', max_length=8000, null=True, verbose_name='错误答案列表'),
        ),
    ]
