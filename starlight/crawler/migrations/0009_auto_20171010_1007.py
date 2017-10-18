# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-10-10 01:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0008_auto_20171009_1903'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='full_name',
        ),
        migrations.AddField(
            model_name='user',
            name='follower_count',
            field=models.IntegerField(null=True),
        ),
    ]