# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='timestampedarticle',
            name='image',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='timestampedarticle',
            name='source',
            field=models.ForeignKey(blank=True, null=True, to='news.ContentSource'),
        ),
    ]
