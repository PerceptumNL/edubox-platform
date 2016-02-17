# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0001_initial'),
        ('settings', '0001_initial'),
        ('groups', '0002_auto_20151223_1838'),
        ('kb', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='flat_permissions',
            field=models.ManyToManyField(related_name='_userprofile_flat_permissions_+', to='permissions.Permission'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='groups',
            field=models.ManyToManyField(through='groups.Membership', related_name='users', to='groups.Group'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='institute',
            field=models.ForeignKey(related_name='users', default=1, to='groups.Institute'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='permissions',
            field=models.ManyToManyField(through='permissions.UserPermission', to='permissions.Permission'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='setting_defaults',
            field=models.ManyToManyField(through='settings.UserDefault', related_name='user_defaults', to='settings.SettingValue'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='setting_restrictions',
            field=models.ManyToManyField(through='settings.UserRestriction', related_name='user_restrictions', to='settings.SettingValue'),
        ),
    ]
