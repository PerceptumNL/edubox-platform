# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('router', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CompactSettings',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('string', models.CharField(default='', max_length=511)),
                ('app', models.ForeignKey(to='router.App')),
            ],
            options={
                'verbose_name_plural': 'Compact settings',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=255, blank=True)),
                ('apps', models.ManyToManyField(to='router.App')),
            ],
        ),
        migrations.CreateModel(
            name='GroupDefault',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(to='usermanagement.Group')),
            ],
        ),
        migrations.CreateModel(
            name='GroupRestriction',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(to='usermanagement.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('apps', models.ManyToManyField(to='router.App')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
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
                ('app', models.ForeignKey(blank=True, to='router.App', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SettingValue',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255)),
                ('setting', models.ForeignKey(related_name='values', to='usermanagement.Setting')),
            ],
        ),
        migrations.CreateModel(
            name='UserDefault',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(related_name='user_defaults', to='usermanagement.Group')),
                ('setting', models.ForeignKey(related_name='user_defaults', to='usermanagement.Setting')),
                ('settingVal', models.ForeignKey(to='usermanagement.SettingValue')),
            ],
        ),
        migrations.CreateModel(
            name='UserPermission',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('app', models.ForeignKey(to='router.App')),
                ('permission', models.ForeignKey(to='usermanagement.Permission')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('flat_permissions', models.ManyToManyField(related_name='_userprofile_flat_permissions_+', to='usermanagement.Permission')),
                ('groups', models.ManyToManyField(related_name='users', through='usermanagement.Membership', to='usermanagement.Group')),
                ('institute', models.ForeignKey(related_name='users', to='usermanagement.Institute')),
                ('permissions', models.ManyToManyField(through='usermanagement.UserPermission', to='usermanagement.Permission')),
                ('setting_defaults', models.ManyToManyField(related_name='user_defaults', through='usermanagement.UserDefault', to='usermanagement.SettingValue')),
            ],
        ),
        migrations.CreateModel(
            name='UserRestriction',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(to='usermanagement.Group')),
                ('setting', models.ForeignKey(to='usermanagement.Setting')),
                ('settingVal', models.ForeignKey(to='usermanagement.SettingValue')),
                ('user', models.ForeignKey(to='usermanagement.UserProfile')),
            ],
        ),
        migrations.AddField(
            model_name='userprofile',
            name='setting_restrictions',
            field=models.ManyToManyField(related_name='user_restrictions', through='usermanagement.UserRestriction', to='usermanagement.SettingValue'),
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
            field=models.OneToOneField(null=True, related_name='+', blank=True, to='usermanagement.SettingValue'),
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
            field=models.ForeignKey(related_name='subgroups', blank=True, to='usermanagement.Group', null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='permissions',
            field=models.ManyToManyField(blank=True, to='usermanagement.Permission'),
        ),
        migrations.AddField(
            model_name='group',
            name='setting_defaults',
            field=models.ManyToManyField(related_name='group_defaults', through='usermanagement.GroupDefault', to='usermanagement.SettingValue'),
        ),
        migrations.AddField(
            model_name='group',
            name='setting_restrictions',
            field=models.ManyToManyField(related_name='group_restrictions', through='usermanagement.GroupRestriction', to='usermanagement.SettingValue'),
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
