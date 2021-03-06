# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-09 14:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('kb', '0005_auto_20160215_2202'),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('badge_id', models.CharField(max_length=31, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('badge_type', models.PositiveSmallIntegerField(choices=[(0, 'System badge'), (1, 'Skill badge')], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='BadgeLevel',
            fields=[
                ('level', models.CharField(max_length=31, primary_key=True, serialize=False)),
                ('xp_thres', models.PositiveSmallIntegerField()),
                ('index', models.PositiveSmallIntegerField()),
                ('next_level', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='badges.BadgeLevel')),
            ],
        ),
        migrations.CreateModel(
            name='UserBadge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('xp', models.PositiveSmallIntegerField()),
                ('badge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='badges.Badge')),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='badges.BadgeLevel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kb.UserProfile')),
            ],
        ),
        migrations.AddField(
            model_name='badge',
            name='start_level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='badges.BadgeLevel'),
        ),
        migrations.AddField(
            model_name='badge',
            name='users',
            field=models.ManyToManyField(through='badges.UserBadge', to='kb.UserProfile'),
        ),
    ]
