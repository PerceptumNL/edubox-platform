# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_settings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='compact',
            field=models.BooleanField(default=True),
        ),
    ]
