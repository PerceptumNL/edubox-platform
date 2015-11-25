# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loader', '0006_auto_20151111_2253'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='secure',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='service',
            name='secure',
            field=models.BooleanField(default=True),
        ),
    ]
