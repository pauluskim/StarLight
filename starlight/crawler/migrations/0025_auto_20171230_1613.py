# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-30 07:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0024_scoreboard_created_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scoreboard',
            name='graph_type',
            field=models.CharField(db_index=True, max_length=10),
        ),
    ]
