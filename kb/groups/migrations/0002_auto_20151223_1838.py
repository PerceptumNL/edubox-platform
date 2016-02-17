# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0001_initial'),
        ('settings', '0001_initial'),
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='permissions',
            field=models.ManyToManyField(to='permissions.Permission', blank=True),
        ),
        migrations.AddField(
            model_name='group',
            name='setting_defaults',
            field=models.ManyToManyField(to='settings.SettingValue', related_name='group_defaults', through='settings.GroupDefault'),
        ),
        migrations.AddField(
            model_name='group',
            name='setting_restrictions',
            field=models.ManyToManyField(to='settings.SettingValue', related_name='group_restrictions', through='settings.GroupRestriction'),
        ),
        migrations.AddField(
            model_name='role',
            name='permissions',
            field=models.ManyToManyField(to='permissions.Permission'),
        ),
    ]
