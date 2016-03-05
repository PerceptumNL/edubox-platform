# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0004_auto_20160215_1236'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='imported',
            field=models.BooleanField(default=False),
        ),
    ]
