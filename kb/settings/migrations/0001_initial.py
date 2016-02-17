# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kb', '0001_initial'),
        ('apps', '0001_initial'),
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompactSettings',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('string', models.CharField(default='', max_length=511)),
                ('app', models.ForeignKey(to='apps.App')),
                ('group', models.ForeignKey(to='groups.Group')),
                ('user', models.ForeignKey(to='kb.UserProfile', related_name='compact_settings')),
            ],
            options={
                'verbose_name_plural': 'Compact settings',
            },
        ),
        migrations.CreateModel(
            name='GroupDefault',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('group', models.ForeignKey(to='groups.Group')),
            ],
        ),
        migrations.CreateModel(
            name='GroupRestriction',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('group', models.ForeignKey(to='groups.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('code', models.CharField(serialize=False, primary_key=True, max_length=31)),
                ('description', models.TextField()),
                ('compact', models.BooleanField(default=True)),
                ('app', models.ForeignKey(blank=True, null=True, to='apps.App')),
            ],
        ),
        migrations.CreateModel(
            name='SettingValue',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('value', models.CharField(max_length=255)),
                ('setting', models.ForeignKey(to='settings.Setting', related_name='values')),
            ],
        ),
        migrations.CreateModel(
            name='UserDefault',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('group', models.ForeignKey(to='groups.Group', related_name='user_defaults')),
                ('setting', models.ForeignKey(to='settings.Setting', related_name='user_defaults')),
                ('settingVal', models.ForeignKey(to='settings.SettingValue')),
                ('user', models.ForeignKey(to='kb.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='UserRestriction',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('group', models.ForeignKey(to='groups.Group')),
                ('setting', models.ForeignKey(to='settings.Setting')),
                ('settingVal', models.ForeignKey(to='settings.SettingValue')),
                ('user', models.ForeignKey(to='kb.UserProfile')),
            ],
        ),
        migrations.AddField(
            model_name='setting',
            name='default',
            field=models.OneToOneField(blank=True, null=True, to='settings.SettingValue', related_name='+'),
        ),
        migrations.AddField(
            model_name='grouprestriction',
            name='setting',
            field=models.ForeignKey(to='settings.Setting'),
        ),
        migrations.AddField(
            model_name='grouprestriction',
            name='settingVal',
            field=models.ForeignKey(to='settings.SettingValue'),
        ),
        migrations.AddField(
            model_name='groupdefault',
            name='setting',
            field=models.ForeignKey(to='settings.Setting', related_name='group_defaults'),
        ),
        migrations.AddField(
            model_name='groupdefault',
            name='settingVal',
            field=models.ForeignKey(to='settings.SettingValue'),
        ),
    ]
