# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-09-11 19:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0004_auto_20180910_1910'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='image',
            field=models.ImageField(default='', upload_to='org/%Y/%m', verbose_name='封面图'),
        ),
    ]
