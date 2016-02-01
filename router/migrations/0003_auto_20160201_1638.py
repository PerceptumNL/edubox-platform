# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('router', '0002_servercredentials'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='servercredentials',
            options={'verbose_name_plural': 'server credentials'},
        ),
    ]
