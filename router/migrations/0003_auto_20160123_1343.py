# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('router', '0002_auto_20160122_1440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servercookiejar',
            name='contents',
            field=models.BinaryField(),
        ),
    ]
