# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20151216_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clickedevent',
            name='app',
            field=models.ForeignKey(to='kb.App'),
        ),
        migrations.AlterField(
            model_name='genericevent',
            name='app',
            field=models.ForeignKey(to='kb.App'),
        ),
        migrations.AlterField(
            model_name='ratedevent',
            name='app',
            field=models.ForeignKey(to='kb.App'),
        ),
        migrations.AlterField(
            model_name='readevent',
            name='app',
            field=models.ForeignKey(to='kb.App'),
        ),
        migrations.AlterField(
            model_name='scoredevent',
            name='app',
            field=models.ForeignKey(to='kb.App'),
        ),
    ]
