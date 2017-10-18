# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-10-09 09:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0006_follow'),
    ]

    operations = [
        migrations.AddField(
            model_name='follow',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='user',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]