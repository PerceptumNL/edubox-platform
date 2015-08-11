# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('loader', '0005_service'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Context',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('app', models.ForeignKey(to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('title', models.CharField(max_length=255)),
                ('code', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('title', models.CharField(max_length=255)),
                ('apps', models.ManyToManyField(to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('group', models.ForeignKey(to='usermanagement.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('code', models.CharField(max_length=31)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('role', models.CharField(max_length=2, choices=[('St', 'Student'), ('Te', 'Teacher'), ('Me', 'Mentor'), ('Ex', 'Executive')])),
                ('permissions', models.ManyToManyField(to='usermanagement.Permission')),
            ],
        ),
        migrations.CreateModel(
            name='Scope',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('group', models.ForeignKey(to='usermanagement.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('label', models.CharField(max_length=31)),
                ('valueType', models.CharField(max_length=15)),
                ('description', models.TextField()),
                ('compact', models.BooleanField(default=True)),
                ('app', models.ForeignKey(null=True, to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='SettingValue',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('value', models.CharField(max_length=255)),
                ('setting', models.ForeignKey(to='usermanagement.Setting')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('flatperms', models.ManyToManyField(to='usermanagement.Permission', related_name='+')),
                ('groups', models.ManyToManyField(to='usermanagement.Group', through='usermanagement.Member', related_name='users')),
                ('institute', models.ForeignKey(to='usermanagement.Institute', related_name='users')),
                ('permissions', models.ManyToManyField(to='usermanagement.Permission', through='usermanagement.Context')),
                ('settings', models.ManyToManyField(to='usermanagement.SettingValue')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='scope',
            name='setting',
            field=models.ForeignKey(to='usermanagement.Setting'),
        ),
        migrations.AddField(
            model_name='scope',
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
            field=models.ForeignKey(null=True, related_name='subgroups', blank=True, to='usermanagement.Group'),
        ),
        migrations.AddField(
            model_name='group',
            name='permissions',
            field=models.ManyToManyField(to='usermanagement.Permission'),
        ),
        migrations.AddField(
            model_name='group',
            name='settings',
            field=models.ManyToManyField(to='usermanagement.SettingValue', through='usermanagement.Scope'),
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
