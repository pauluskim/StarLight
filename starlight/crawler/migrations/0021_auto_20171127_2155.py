# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-27 12:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0020_auto_20171127_2152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='count_DM_sent',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='num_likes',
            field=models.IntegerField(null=True),
        ),
    ]
