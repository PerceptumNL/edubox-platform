# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lvs', '0001_initial'),
        ('groups', '0005_group_imported'),
    ]

    operations = [
        migrations.AddField(
            model_name='institute',
            name='xmls',
            field=models.ManyToManyField(to='lvs.XmlDump'),
        ),
    ]
