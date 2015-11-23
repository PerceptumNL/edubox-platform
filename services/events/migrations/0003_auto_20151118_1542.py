# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usermanagement', '__first__'),
        ('events', '0002_auto_20150825_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clickedevent',
            name='group',
            field=models.ForeignKey(to='usermanagement.Group'),
        ),
        migrations.AlterField(
            model_name='genericevent',
            name='group',
            field=models.ForeignKey(to='usermanagement.Group'),
        ),
        migrations.AlterField(
            model_name='ratedevent',
            name='group',
            field=models.ForeignKey(to='usermanagement.Group'),
        ),
        migrations.AlterField(
            model_name='readevent',
            name='group',
            field=models.ForeignKey(to='usermanagement.Group'),
        ),
        migrations.AlterField(
            model_name='scoredevent',
            name='group',
            field=models.ForeignKey(to='usermanagement.Group'),
        ),
    ]
