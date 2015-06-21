# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loader', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='root',
            field=models.CharField(default='', verbose_name='Root URL (Remote) or URLconf module name (Local)', max_length=255),
            preserve_default=False,
        ),
    ]
