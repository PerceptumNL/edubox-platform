# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-07 15:34
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('inbox', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='datetime',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 4, 7, 15, 34, 44, 327329, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
