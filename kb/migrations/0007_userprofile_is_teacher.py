# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-28 14:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kb', '0006_auto_20160316_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_teacher',
            field=models.BooleanField(default=False),
        ),
    ]
