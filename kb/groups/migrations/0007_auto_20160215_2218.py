# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0006_institute_xmls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institute',
            name='xmls',
            field=models.ManyToManyField(blank=True, to='lvs.XmlDump'),
        ),
    ]
