# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-09-14 15:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0009_video_learn_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson',
            name='learn_time',
        ),
    ]
