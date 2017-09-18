# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-16 15:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advert', '0013_auto_20170916_1609'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advertplan',
            name='cost',
        ),
        migrations.RemoveField(
            model_name='advertplan',
            name='frequency',
        ),
        migrations.RemoveField(
            model_name='advertplan',
            name='page',
        ),
        migrations.AddField(
            model_name='advertplan',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
