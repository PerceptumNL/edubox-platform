# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-06 09:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0009_auto_20160302_1651'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('apps', '0006_auto_20160306_1245'),
        ('events', '0002_submittedevent'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompiledEvent',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('verb', models.URLField(max_length=255)),
                ('obj', models.URLField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('code', models.TextField()),
                ('code_type', models.CharField(default='javascript', max_length=50)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apps.App')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.Group')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
                'abstract': False,
            },
        ),
    ]
