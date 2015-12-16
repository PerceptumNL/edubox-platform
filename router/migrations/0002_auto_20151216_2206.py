# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20151216_2206'),
        ('usermanagement', '0002_auto_20151216_2206'),
        ('router', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='app',
            name='users',
        ),
        migrations.DeleteModel(
            name='Service',
        ),
        migrations.DeleteModel(
            name='App',
        ),
    ]
