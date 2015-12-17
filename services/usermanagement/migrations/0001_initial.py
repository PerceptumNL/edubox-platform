# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kb', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompactSettings',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('string', models.CharField(default='', max_length=511)),
                ('app', models.ForeignKey(to='kb.App')),
            ],
            options={
                'verbose_name_plural': 'Compact settings',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('code', models.CharField(blank=True, max_length=255)),
                ('apps', models.ManyToManyField(to='kb.App')),
            ],
        ),
        migrations.CreateModel(
            name='GroupDefault',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('group', models.ForeignKey(to='usermanagement.Group')),
            ],
        ),
        migrations.CreateModel(
            name='GroupRestriction',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('group', models.ForeignKey(to='usermanagement.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('apps', models.ManyToManyField(to='kb.App')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('group', models.ForeignKey(to='usermanagement.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('code', models.CharField(primary_key=True, max_length=31, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('role', models.CharField(max_length=31)),
                ('permissions', models.ManyToManyField(to='usermanagement.Permission')),
            ],
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('code', models.CharField(primary_key=True, max_length=31, serialize=False)),
                ('description', models.TextField()),
                ('compact', models.BooleanField(default=True)),
                ('app', models.ForeignKey(to='kb.App', null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SettingValue',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('value', models.CharField(max_length=255)),
                ('setting', models.ForeignKey(to='usermanagement.Setting', related_name='values')),
            ],
        ),
        migrations.CreateModel(
            name='UserDefault',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('group', models.ForeignKey(to='usermanagement.Group', related_name='user_defaults')),
                ('setting', models.ForeignKey(to='usermanagement.Setting', related_name='user_defaults')),
                ('settingVal', models.ForeignKey(to='usermanagement.SettingValue')),
            ],
        ),
        migrations.CreateModel(
            name='UserPermission',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('app', models.ForeignKey(to='kb.App')),
                ('permission', models.ForeignKey(to='usermanagement.Permission')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('flat_permissions', models.ManyToManyField(related_name='_userprofile_flat_permissions_+', to='usermanagement.Permission')),
                ('groups', models.ManyToManyField(related_name='users', to='usermanagement.Group', through='usermanagement.Membership')),
                ('institute', models.ForeignKey(to='usermanagement.Institute', related_name='users')),
                ('permissions', models.ManyToManyField(to='usermanagement.Permission', through='usermanagement.UserPermission')),
                ('setting_defaults', models.ManyToManyField(related_name='user_defaults', to='usermanagement.SettingValue', through='usermanagement.UserDefault')),
            ],
        ),
        migrations.CreateModel(
            name='UserRestriction',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('group', models.ForeignKey(to='usermanagement.Group')),
                ('setting', models.ForeignKey(to='usermanagement.Setting')),
                ('settingVal', models.ForeignKey(to='usermanagement.SettingValue')),
                ('user', models.ForeignKey(to='usermanagement.UserProfile')),
            ],
        ),
        migrations.AddField(
            model_name='userprofile',
            name='setting_restrictions',
            field=models.ManyToManyField(related_name='user_restrictions', to='usermanagement.SettingValue', through='usermanagement.UserRestriction'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userpermission',
            name='user',
            field=models.ForeignKey(to='usermanagement.UserProfile'),
        ),
        migrations.AddField(
            model_name='userdefault',
            name='user',
            field=models.ForeignKey(to='usermanagement.UserProfile'),
        ),
        migrations.AddField(
            model_name='setting',
            name='default',
            field=models.OneToOneField(related_name='+', to='usermanagement.SettingValue', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='membership',
            name='role',
            field=models.ForeignKey(to='usermanagement.Role', related_name='members'),
        ),
        migrations.AddField(
            model_name='membership',
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
            field=models.ForeignKey(related_name='subgroups', to='usermanagement.Group', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='group',
            name='permissions',
            field=models.ManyToManyField(blank=True, to='usermanagement.Permission'),
        ),
        migrations.AddField(
            model_name='group',
            name='setting_defaults',
            field=models.ManyToManyField(related_name='group_defaults', to='usermanagement.SettingValue', through='usermanagement.GroupDefault'),
        ),
        migrations.AddField(
            model_name='group',
            name='setting_restrictions',
            field=models.ManyToManyField(related_name='group_restrictions', to='usermanagement.SettingValue', through='usermanagement.GroupRestriction'),
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
        migrations.CreateModel(
            name='UserProfileProxy',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': 'User profile: Admin view',
            },
            bases=('usermanagement.userprofile',),
        ),
    ]
