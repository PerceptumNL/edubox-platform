# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('kb', '0002_auto_20151223_1840'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='alias',
            field=models.CharField(unique=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='date_of_birth',
            field=models.DateField(default=datetime.date(1970, 1, 1), blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='gender',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='initials',
            field=models.CharField(max_length=15, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='surname_prefixes',
            field=models.CharField(max_length=127, blank=True),
        ),
    ]
