# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_auto_20151223_1838'),
    ]

    operations = [
        migrations.AddField(
            model_name='institute',
            name='email_domain',
            field=models.CharField(default='perceptum.nl', max_length=255),
            preserve_default=False,
        ),
    ]
