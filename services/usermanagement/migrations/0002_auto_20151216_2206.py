# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usermanagement', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compactsettings',
            name='app',
            field=models.ForeignKey(to='kb.App'),
        ),
        migrations.AlterField(
            model_name='group',
            name='apps',
            field=models.ManyToManyField(to='kb.App'),
        ),
        migrations.AlterField(
            model_name='institute',
            name='apps',
            field=models.ManyToManyField(to='kb.App'),
        ),
        migrations.AlterField(
            model_name='setting',
            name='app',
            field=models.ForeignKey(to='kb.App', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userpermission',
            name='app',
            field=models.ForeignKey(to='kb.App'),
        ),
    ]
