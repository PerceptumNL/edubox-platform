# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loader', '0003_auto_20150617_2212'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='app',
            name='location',
        ),
        migrations.AlterField(
            model_name='app',
            name='root',
            field=models.CharField(verbose_name='URL/URLconf', max_length=255),
        ),
    ]
