# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '__first__'),
        ('apps', '0001_initial'),
        ('kb', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompactSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('string', models.CharField(max_length=511, default='')),
                ('app', models.ForeignKey(to='apps.App')),
                ('group', models.ForeignKey(to='groups.Group')),
                ('user', models.ForeignKey(related_name='compact_settings', to='kb.UserProfile')),
            ],
            options={
                'verbose_name_plural': 'Compact settings',
            },
        ),
        migrations.CreateModel(
            name='GroupDefault',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('group', models.ForeignKey(to='groups.Group')),
            ],
        ),
        migrations.CreateModel(
            name='GroupRestriction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('group', models.ForeignKey(to='groups.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('code', models.CharField(max_length=31, primary_key=True, serialize=False)),
                ('description', models.TextField()),
                ('compact', models.BooleanField(default=True)),
                ('app', models.ForeignKey(blank=True, null=True, to='apps.App')),
            ],
        ),
        migrations.CreateModel(
            name='SettingValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('value', models.CharField(max_length=255)),
                ('setting', models.ForeignKey(related_name='values', to='settings.Setting')),
            ],
        ),
        migrations.CreateModel(
            name='UserDefault',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('group', models.ForeignKey(related_name='user_defaults', to='groups.Group')),
                ('setting', models.ForeignKey(related_name='user_defaults', to='settings.Setting')),
                ('settingVal', models.ForeignKey(to='settings.SettingValue')),
                ('user', models.ForeignKey(to='kb.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='UserRestriction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('group', models.ForeignKey(to='groups.Group')),
                ('setting', models.ForeignKey(to='settings.Setting')),
                ('settingVal', models.ForeignKey(to='settings.SettingValue')),
                ('user', models.ForeignKey(to='kb.UserProfile')),
            ],
        ),
        migrations.AddField(
            model_name='setting',
            name='default',
            field=models.OneToOneField(blank=True, to='settings.SettingValue', null=True, related_name='+'),
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
            field=models.ForeignKey(related_name='group_defaults', to='settings.Setting'),
        ),
        migrations.AddField(
            model_name='groupdefault',
            name='settingVal',
            field=models.ForeignKey(to='settings.SettingValue'),
        ),
    ]
