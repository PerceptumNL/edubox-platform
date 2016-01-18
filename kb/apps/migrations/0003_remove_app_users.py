# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_app_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='app',
            name='users',
        ),
    ]
