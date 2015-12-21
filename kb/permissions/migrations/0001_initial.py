# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
        ('kb', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('code', models.CharField(primary_key=True, max_length=31, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='UserPermission',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('app', models.ForeignKey(to='apps.App')),
                ('permission', models.ForeignKey(to='permissions.Permission')),
                ('user', models.ForeignKey(to='kb.UserProfile')),
            ],
        ),
    ]
