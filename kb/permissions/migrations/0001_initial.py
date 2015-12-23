# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
        ('kb', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('code', models.CharField(serialize=False, primary_key=True, max_length=31)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='UserPermission',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('app', models.ForeignKey(to='apps.App')),
                ('permission', models.ForeignKey(to='permissions.Permission')),
                ('user', models.ForeignKey(to='kb.UserProfile')),
            ],
        ),
    ]
