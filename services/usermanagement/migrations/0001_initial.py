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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('string', models.CharField(default='', max_length=511)),
                ('app', models.ForeignKey(to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('code', models.CharField(blank=True, max_length=255)),
                ('apps', models.ManyToManyField(to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='GroupDefault',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(to='usermanagement.Group')),
            ],
        ),
        migrations.CreateModel(
            name='GroupRestriction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(to='usermanagement.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('apps', models.ManyToManyField(to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(to='usermanagement.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('code', models.CharField(primary_key=True, serialize=False, max_length=31)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=31)),
                ('permissions', models.ManyToManyField(to='usermanagement.Permission')),
            ],
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('code', models.CharField(primary_key=True, serialize=False, max_length=31)),
                ('description', models.TextField()),
                ('compact', models.BooleanField(default=True)),
                ('app', models.ForeignKey(null=True, to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='SettingValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255)),
                ('setting', models.ForeignKey(related_name='values', to='usermanagement.Setting')),
            ],
        ),
        migrations.CreateModel(
            name='UserDefault',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(related_name='user_defaults', to='usermanagement.Group')),
                ('setting', models.ForeignKey(related_name='user_defaults', to='usermanagement.Setting')),
                ('settingVal', models.ForeignKey(to='usermanagement.SettingValue')),
            ],
        ),
        migrations.CreateModel(
            name='UserPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app', models.ForeignKey(to='loader.App')),
                ('permission', models.ForeignKey(to='usermanagement.Permission')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flat_permissions', models.ManyToManyField(related_name='+', to='usermanagement.Permission')),
                ('groups', models.ManyToManyField(through='usermanagement.Membership', related_name='users', to='usermanagement.Group')),
                ('institute', models.ForeignKey(related_name='users', to='usermanagement.Institute')),
                ('permissions', models.ManyToManyField(through='usermanagement.UserPermission', to='usermanagement.Permission')),
                ('setting_defaults', models.ManyToManyField(through='usermanagement.UserDefault', related_name='user_defaults', to='usermanagement.SettingValue')),
            ],
        ),
        migrations.CreateModel(
            name='UserRestriction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(to='usermanagement.Group')),
                ('setting', models.ForeignKey(to='usermanagement.Setting')),
                ('settingVal', models.ForeignKey(to='usermanagement.SettingValue')),
                ('user', models.ForeignKey(to='usermanagement.UserProfile')),
            ],
        ),
        migrations.AddField(
            model_name='userprofile',
            name='setting_restrictions',
            field=models.ManyToManyField(through='usermanagement.UserRestriction', related_name='user_restrictions', to='usermanagement.SettingValue'),
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
            field=models.OneToOneField(related_name='+', null=True, to='usermanagement.SettingValue'),
        ),
        migrations.AddField(
            model_name='membership',
            name='role',
            field=models.ForeignKey(related_name='members', to='usermanagement.Role'),
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
            field=models.ForeignKey(related_name='group_defaults', to='usermanagement.Setting'),
        ),
        migrations.AddField(
            model_name='groupdefault',
            name='settingVal',
            field=models.ForeignKey(to='usermanagement.SettingValue'),
        ),
        migrations.AddField(
            model_name='group',
            name='institute',
            field=models.ForeignKey(related_name='groups', to='usermanagement.Institute'),
        ),
        migrations.AddField(
            model_name='group',
            name='parent',
            field=models.ForeignKey(blank=True, related_name='subgroups', null=True, to='usermanagement.Group'),
        ),
        migrations.AddField(
            model_name='group',
            name='permissions',
            field=models.ManyToManyField(to='usermanagement.Permission'),
        ),
        migrations.AddField(
            model_name='group',
            name='setting_defaults',
            field=models.ManyToManyField(through='usermanagement.GroupDefault', related_name='group_defaults', to='usermanagement.SettingValue'),
        ),
        migrations.AddField(
            model_name='group',
            name='setting_restrictions',
            field=models.ManyToManyField(through='usermanagement.GroupRestriction', related_name='group_restrictions', to='usermanagement.SettingValue'),
        ),
        migrations.AddField(
            model_name='compactsettings',
            name='group',
            field=models.ForeignKey(to='usermanagement.Group'),
        ),
        migrations.AddField(
            model_name='compactsettings',
            name='user',
            field=models.ForeignKey(related_name='compact_settings', to='usermanagement.UserProfile'),
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
