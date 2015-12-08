# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usermanagement', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='compactsettings',
            options={'verbose_name_plural': 'Compact settings'},
        ),
        migrations.AlterField(
            model_name='group',
            name='permissions',
            field=models.ManyToManyField(blank=True, to='usermanagement.Permission'),
        ),
        migrations.AlterField(
            model_name='setting',
            name='app',
            field=models.ForeignKey(null=True, to='loader.App', blank=True),
        ),
        migrations.AlterField(
            model_name='setting',
            name='default',
            field=models.OneToOneField(null=True, related_name='+', blank=True, to='usermanagement.SettingValue'),
        ),
    ]
