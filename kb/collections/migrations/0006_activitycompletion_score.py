# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-20 12:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collections', '0005_learningunit_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitycompletion',
            name='score',
            field=models.FloatField(default=100),
            preserve_default=False,
        ),
    ]