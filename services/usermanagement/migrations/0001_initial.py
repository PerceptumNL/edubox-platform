# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('loader', '0005_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompactSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('string', models.CharField(max_length=511, default='')),
                ('app', models.ForeignKey(to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='Context',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('app', models.ForeignKey(to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('code', models.CharField(blank=True, max_length=255)),
                ('apps', models.ManyToManyField(blank=True, to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='GroupDefault',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('group', models.ForeignKey(to='usermanagement.Group')),
            ],
        ),
        migrations.CreateModel(
            name='GroupRestriction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('group', models.ForeignKey(to='usermanagement.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('apps', models.ManyToManyField(to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('group', models.ForeignKey(to='usermanagement.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('code', models.CharField(max_length=31, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('role', models.CharField(max_length=31)),
                ('permissions', models.ManyToManyField(to='usermanagement.Permission')),
            ],
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('code', models.CharField(max_length=31, primary_key=True, serialize=False)),
                ('description', models.TextField()),
                ('compact', models.BooleanField(default=True)),
                ('app', models.ForeignKey(null=True, to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='SettingValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('value', models.CharField(max_length=255)),
                ('setting', models.ForeignKey(to='usermanagement.Setting', related_name='values')),
            ],
        ),
        migrations.CreateModel(
            name='UserDefault',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('group', models.ForeignKey(to='usermanagement.Group', related_name='user_defaults')),
                ('setting', models.ForeignKey(to='usermanagement.Setting', related_name='user_defaults')),
                ('settingVal', models.ForeignKey(to='usermanagement.SettingValue')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('flat_permissions', models.ManyToManyField(to='usermanagement.Permission', related_name='+')),
                ('groups', models.ManyToManyField(through='usermanagement.Member', to='usermanagement.Group', related_name='users')),
                ('institute', models.ForeignKey(to='usermanagement.Institute', related_name='users')),
                ('permissions', models.ManyToManyField(through='usermanagement.Context', to='usermanagement.Permission')),
                ('setting_defaults', models.ManyToManyField(through='usermanagement.UserDefault', to='usermanagement.SettingValue', related_name='user_defaults')),
            ],
        ),
        migrations.CreateModel(
            name='UserRestriction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('group', models.ForeignKey(to='usermanagement.Group')),
                ('setting', models.ForeignKey(to='usermanagement.Setting')),
                ('settingVal', models.ForeignKey(to='usermanagement.SettingValue')),
                ('user', models.ForeignKey(to='usermanagement.UserProfile')),
            ],
        ),
        migrations.AddField(
            model_name='userprofile',
            name='setting_restrictions',
            field=models.ManyToManyField(through='usermanagement.UserRestriction', to='usermanagement.SettingValue', related_name='user_restrictions'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userdefault',
            name='user',
            field=models.ForeignKey(to='usermanagement.UserProfile'),
        ),
        migrations.AddField(
            model_name='setting',
            name='default',
            field=models.OneToOneField(null=True, to='usermanagement.SettingValue', related_name='+'),
        ),
        migrations.AddField(
            model_name='member',
            name='role',
            field=models.ForeignKey(to='usermanagement.Role', related_name='members'),
        ),
        migrations.AddField(
            model_name='member',
            name='user',
            field=models.ForeignKey(to='usermanagement.UserProfile'),
        ),
        migrations.AddField(
            model_name='grouprestriction',
            name='setting',
            field=models.ForeignKey(to='usermanagement.Setting'),
        ),
        migrations.AddField(
            model_name='grouprestriction',
            name='settingVal',
            field=models.ForeignKey(to='usermanagement.SettingValue'),
        ),
        migrations.AddField(
            model_name='groupdefault',
            name='setting',
            field=models.ForeignKey(to='usermanagement.Setting', related_name='group_defaults'),
        ),
        migrations.AddField(
            model_name='groupdefault',
            name='settingVal',
            field=models.ForeignKey(to='usermanagement.SettingValue'),
        ),
        migrations.AddField(
            model_name='group',
            name='institute',
            field=models.ForeignKey(to='usermanagement.Institute', related_name='groups'),
        ),
        migrations.AddField(
            model_name='group',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, to='usermanagement.Group', related_name='subgroups'),
        ),
        migrations.AddField(
            model_name='group',
            name='permissions',
            field=models.ManyToManyField(to='usermanagement.Permission'),
        ),
        migrations.AddField(
            model_name='group',
            name='setting_defaults',
            field=models.ManyToManyField(through='usermanagement.GroupDefault', to='usermanagement.SettingValue', related_name='group_defaults'),
        ),
        migrations.AddField(
            model_name='group',
            name='setting_restrictions',
            field=models.ManyToManyField(through='usermanagement.GroupRestriction', to='usermanagement.SettingValue', related_name='group_restrictions'),
        ),
        migrations.AddField(
            model_name='context',
            name='permission',
            field=models.ForeignKey(to='usermanagement.Permission'),
        ),
        migrations.AddField(
            model_name='context',
            name='user',
            field=models.ForeignKey(to='usermanagement.UserProfile'),
        ),
        migrations.AddField(
            model_name='compactsettings',
            name='group',
            field=models.ForeignKey(to='usermanagement.Group'),
        ),
        migrations.AddField(
            model_name='compactsettings',
            name='user',
            field=models.ForeignKey(to='usermanagement.UserProfile', related_name='compact_settings'),
        ),
    ]
