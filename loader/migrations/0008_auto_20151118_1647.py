# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loader', '0007_auto_20151112_1010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='identical_urls',
            field=models.CharField(default='', max_length=255, blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='service',
            name='identical_urls',
            field=models.CharField(default='', max_length=255, blank=True),
            preserve_default=False,
        ),
    ]
