# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-19 16:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_auto_20170914_1640'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscribeModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
    ]
