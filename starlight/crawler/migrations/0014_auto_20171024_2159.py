# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-24 12:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0013_auto_20171024_2157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='follow',
            name='object_pk',
            field=models.BigIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='follow',
            name='user_pk',
            field=models.BigIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='hashtag_dictionary',
            name='user_pk',
            field=models.BigIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(db_index=True, max_length=200),
        ),
    ]