# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loader', '0004_auto_20150617_2217'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('root', models.CharField(max_length=255, verbose_name='URL/URLconf')),
                ('name', models.CharField(primary_key=True, max_length=255, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('local', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
