# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loader', '0005_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='identical_urls',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='identical_urls',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
