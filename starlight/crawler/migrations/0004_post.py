# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-09-23 06:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0003_auto_20170917_2014'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=200)),
                ('engagement_rate', models.DecimalField(decimal_places=20, max_digits=22, null=True)),
                ('num_likes', models.IntegerField(null=True)),
                ('num_commenters', models.IntegerField(null=True)),
                ('num_views', models.IntegerField(null=True)),
                ('captions', models.TextField(null=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
