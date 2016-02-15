# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kb', '0003_auto_20160215_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='date_of_birth',
            field=models.DateField(null=True),
        ),
    ]
