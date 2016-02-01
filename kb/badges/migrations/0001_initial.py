# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kb', '0002_auto_20151223_1840'),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('code', models.CharField(max_length=31, primary_key=True, serialize=False)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='BadgeLevel',
            fields=[
                ('level', models.CharField(max_length=31, primary_key=True, serialize=False)),
                ('xp_thres', models.PositiveSmallIntegerField()),
                ('next_level', models.ForeignKey(null=True, to='badges.BadgeLevel', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserBadge',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('xp', models.PositiveSmallIntegerField()),
                ('badge', models.ForeignKey(to='badges.Badge')),
                ('level', models.ForeignKey(to='badges.BadgeLevel')),
                ('user', models.ForeignKey(to='kb.UserProfile')),
            ],
        ),
        migrations.AddField(
            model_name='badge',
            name='start_level',
            field=models.ForeignKey(to='badges.BadgeLevel'),
        ),
        migrations.AddField(
            model_name='badge',
            name='users',
            field=models.ManyToManyField(through='badges.UserBadge', to='kb.UserProfile'),
        ),
    ]
