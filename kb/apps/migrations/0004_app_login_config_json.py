# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0003_remove_app_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='login_config_json',
            field=models.TextField(blank=True, default='{}'),
        ),
    ]
