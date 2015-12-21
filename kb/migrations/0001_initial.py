# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('permissions', '0001_initial'),
        ('groups', '__first__'),
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('flat_permissions', models.ManyToManyField(related_name='_userprofile_flat_permissions_+', to='permissions.Permission')),
                ('groups', models.ManyToManyField(related_name='users', to='groups.Group', through='groups.Membership')),
                ('institute', models.ForeignKey(related_name='users', to='groups.Institute')),
                ('permissions', models.ManyToManyField(to='permissions.Permission', through='permissions.UserPermission')),
                ('setting_defaults', models.ManyToManyField(related_name='user_defaults', to='settings.SettingValue', through='settings.UserDefault')),
                ('setting_restrictions', models.ManyToManyField(related_name='user_restrictions', to='settings.SettingValue', through='settings.UserRestriction')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
