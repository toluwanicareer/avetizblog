# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-19 08:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_profile'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Profile',
            new_name='WriterProfile',
        ),
    ]
