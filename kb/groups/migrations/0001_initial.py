# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kb', '0001_initial'),
        ('apps', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=255, blank=True)),
                ('apps', models.ManyToManyField(to='apps.App')),
            ],
        ),
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('apps', models.ManyToManyField(to='apps.App')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('group', models.ForeignKey(to='groups.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('role', models.CharField(max_length=31)),
            ],
        ),
        migrations.AddField(
            model_name='membership',
            name='role',
            field=models.ForeignKey(to='groups.Role', related_name='members'),
        ),
        migrations.AddField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(to='kb.UserProfile'),
        ),
        migrations.AddField(
            model_name='group',
            name='institute',
            field=models.ForeignKey(to='groups.Institute', related_name='groups'),
        ),
        migrations.AddField(
            model_name='group',
            name='parent',
            field=models.ForeignKey(to='groups.Group', null=True, blank=True, related_name='subgroups'),
        ),
    ]
