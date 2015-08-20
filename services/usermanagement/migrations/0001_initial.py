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
            name='Context',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('app', models.ForeignKey(to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='Default',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('apps', models.ManyToManyField(to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
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
            name='Restriction',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('group', models.ForeignKey(to='usermanagement.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('role', models.CharField(choices=[('St', 'Student'), ('Te', 'Teacher'), ('Me', 'Mentor'), ('Ex', 'Executive')], max_length=2)),
                ('permissions', models.ManyToManyField(to='usermanagement.Permission')),
            ],
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('code', models.CharField(max_length=31, primary_key=True, serialize=False)),
                ('valueType', models.CharField(max_length=15)),
                ('description', models.TextField()),
                ('compact', models.BooleanField(default=True)),
                ('app', models.ForeignKey(to='loader.App', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SettingString',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('string', models.CharField(max_length=511)),
            ],
        ),
        migrations.CreateModel(
            name='SettingValue',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('value', models.CharField(max_length=255)),
                ('setting', models.ForeignKey(to='usermanagement.Setting', related_name='values')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('flat_permissions', models.ManyToManyField(related_name='+', to='usermanagement.Permission')),
                ('groups', models.ManyToManyField(related_name='users', through='usermanagement.Member', to='usermanagement.Group')),
                ('institute', models.ForeignKey(to='usermanagement.Institute', related_name='users')),
                ('permissions', models.ManyToManyField(to='usermanagement.Permission', through='usermanagement.Context')),
                ('setting_defaults', models.ManyToManyField(related_name='user_defaults', to='usermanagement.SettingValue')),
                ('setting_restrictions', models.ManyToManyField(related_name='user_restrictions', to='usermanagement.SettingValue')),
                ('setting_string', models.OneToOneField(to='usermanagement.SettingString', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='setting',
            name='default',
            field=models.OneToOneField(related_name='+', null=True, to='usermanagement.SettingValue'),
        ),
        migrations.AddField(
            model_name='restriction',
            name='setting',
            field=models.ForeignKey(to='usermanagement.Setting'),
        ),
        migrations.AddField(
            model_name='restriction',
            name='settingVal',
            field=models.ForeignKey(to='usermanagement.SettingValue'),
        ),
        migrations.AddField(
            model_name='member',
            name='role',
            field=models.ForeignKey(to='usermanagement.Role'),
        ),
        migrations.AddField(
            model_name='member',
            name='user',
            field=models.ForeignKey(to='usermanagement.UserProfile'),
        ),
        migrations.AddField(
            model_name='group',
            name='institute',
            field=models.ForeignKey(to='usermanagement.Institute', related_name='groups'),
        ),
        migrations.AddField(
            model_name='group',
            name='parent',
            field=models.ForeignKey(to='usermanagement.Group', related_name='subgroups', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='group',
            name='permissions',
            field=models.ManyToManyField(to='usermanagement.Permission'),
        ),
        migrations.AddField(
            model_name='group',
            name='setting_defaults',
            field=models.ManyToManyField(related_name='group_defaults', through='usermanagement.Default', to='usermanagement.SettingValue'),
        ),
        migrations.AddField(
            model_name='group',
            name='setting_restrictions',
            field=models.ManyToManyField(related_name='group_restrictions', through='usermanagement.Restriction', to='usermanagement.SettingValue'),
        ),
        migrations.AddField(
            model_name='default',
            name='group',
            field=models.ForeignKey(to='usermanagement.Group'),
        ),
        migrations.AddField(
            model_name='default',
            name='setting',
            field=models.ForeignKey(to='usermanagement.Setting', related_name='group_defaults'),
        ),
        migrations.AddField(
            model_name='default',
            name='settingVal',
            field=models.ForeignKey(to='usermanagement.SettingValue'),
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
    ]
