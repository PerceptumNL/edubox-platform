# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-22 15:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0005_auto_20160413_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='user_agent',
            field=models.CharField(default='unknown', max_length=255),
        ),
    ]
